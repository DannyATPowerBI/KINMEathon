"""Limited offline model for cases 2/3; does not execute KNIME or its views."""
import ast
from collections import defaultdict
import operator
import re
import xml.etree.ElementTree as ET
import zipfile

NS = {'k': 'http://www.knime.org/2008/09/XMLConfig'}


def config(element, key):
    return element.find(f"k:config[@key='{key}']", NS)


def value(element, key):
    item = element.find(f"k:entry[@key='{key}']", NS)
    return None if item is None or item.get('isnull') == 'true' else item.get('value')


def array(element, key):
    stored = config(element, key)
    return [value(stored, str(i)) for i in range(int(value(stored, 'array-size')))]


def expression(text, row):
    """Interpret the expression subset used here, without Python eval."""
    text = re.sub(r'MISSING \$([^$]+)\$', lambda m: f'missing({m[1]!r})', text)
    text = re.sub(r'\$([^$]+)\$', lambda m: f'col({m[1]!r})', text)
    for src, dest in [('AND', 'and'), ('OR', 'or'), ('NOT', 'not'), ('IN', 'in'),
                      ('TRUE', 'True'), ('FALSE', 'False')]:
        text = re.sub(r'\b' + src + r'\b', dest, text)
    text = re.sub(r'(?<![<>=!])=(?!=)', '==', text)

    def visit(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.Tuple, ast.List)):
            return [visit(x) for x in node.elts]
        if isinstance(node, ast.Call):
            assert isinstance(node.func, ast.Name) and node.func.id in ('col', 'missing')
            assert len(node.args) == 1 and not node.keywords
            key = visit(node.args[0]); assert key in row, ('unknown column', key)
            return row[key] is None if node.func.id == 'missing' else row[key]
        if isinstance(node, ast.UnaryOp):
            datum = visit(node.operand)
            if isinstance(node.op, ast.Not):
                return not datum
            assert isinstance(node.op, ast.USub)
            return None if datum is None else -datum
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(visit(x) for x in node.values)
            return any(visit(x) for x in node.values)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if left is None or right is None:
                return None
            return {ast.Add: operator.add, ast.Sub: operator.sub,
                    ast.Mult: operator.mul, ast.Div: operator.truediv}[type(node.op)](left, right)
        if isinstance(node, ast.Compare):
            assert len(node.ops) == len(node.comparators) == 1
            left, right = visit(node.left), visit(node.comparators[0])
            if left is None or right is None:
                return False
            return {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Gt: operator.gt,
                    ast.GtE: operator.ge, ast.Lt: operator.lt, ast.LtE: operator.le,
                    ast.In: lambda a, b: a in b}[type(node.ops[0])](left, right)
        raise AssertionError(('unsupported expression', ast.dump(node)))

    return visit(ast.parse(text.strip(), mode='eval').body)


def rules(model, row):
    for rule in array(model, 'rules'):
        condition, result = rule.split('=>', 1)
        if expression(condition, row):
            return expression(result, row)
    return None


def run(path, decode_table):
    """Read archived settings/connections and return modeled tables per node."""
    with zipfile.ZipFile(path) as archive:
        top = next(n for n in archive.namelist() if n.count('/') == 1 and n.endswith('/workflow.knime'))
        prefix = top.rsplit('/', 1)[0] + '/'
        root = ET.fromstring(archive.read(top))
        nodes = {int(value(n, 'id')): ET.fromstring(archive.read(prefix + value(n, 'node_settings_file')))
                 for n in config(root, 'nodes')}
        inputs = defaultdict(dict)
        for edge in config(root, 'connections'):
            assert value(edge, 'sourcePort') == '1'
            inputs[int(value(edge, 'destID'))][int(value(edge, 'destPort'))] = int(value(edge, 'sourceID'))
    cache = {}

    def execute(nid):
        if nid in cache:
            return cache[nid]
        settings = nodes[nid]; name = value(settings, 'node-name'); model = config(settings, 'model')
        data = {port: execute(src) for port, src in inputs[nid].items()}
        if name == 'Table Creator':
            rows = decode_table(settings)
        elif name == 'GroupBy':
            groups = array(config(model, 'grouByColumns'), 'InclList')
            agg = config(model, 'aggregationColumn')
            specs = list(zip(array(agg, 'columnNames'), array(agg, 'aggregationMethod')))
            assert value(model, 'columnNamePolicy') == 'Aggregation method (column name)'
            buckets = defaultdict(list)
            for row in data[1]:
                buckets[tuple(row[k] for k in groups)].append(row)
            rows = []
            for key, group in buckets.items():
                result = dict(zip(groups, key))
                for col, method in specs:
                    values = [r[col] for r in group if r[col] is not None]
                    assert len(values) == len(group), 'missing aggregates are outside this model'
                    assert method in ('Count', 'Sum_V2.5.2')
                    label = 'Count' if method == 'Count' else 'Sum'
                    result[f'{label}({col})'] = len(values) if method == 'Count' else sum(values)
                rows.append(result)
        elif name == 'Column Renamer':
            names = {value(n, 'oldName'): value(n, 'newName') for n in config(model, 'renamings')}
            assert set(names) <= set(data[1][0])
            rows = [{names.get(k, k): v for k, v in row.items()} for row in data[1]]
        elif name == 'Joiner':
            assert value(model, 'includeMatchesInOutput') == 'true'
            assert value(model, 'includeLeftUnmatchedInOutput') == 'true'
            assert value(model, 'includeRightUnmatchedInOutput') == 'false'
            pairs = [(value(config(c, 'leftTableColumnV2'), 'regularChoice'),
                      value(config(c, 'rightTableColumnV2'), 'regularChoice'))
                     for c in config(model, 'matchingCriteria')]
            selected = {side: array(config(config(model, side + 'ColumnSelectionConfigV2'), 'manualFilter'), 'manuallySelected')
                        for side in ('left', 'right')}
            index = defaultdict(list)
            for row in data[2]:
                index[tuple(row[k] for _, k in pairs)].append(row)
            rows = []
            for left in data[1]:
                for right in index.get(tuple(left[k] for k, _ in pairs), [None]):
                    result = {k: left[k] for k in selected['left']}
                    for key in selected['right']:
                        assert key not in result, ('column collision', key)
                        result[key] = None if right is None else right[key]
                    rows.append(result)
        elif name == 'Math Formula':
            assert value(model, 'append_column') == 'true'
            col = value(model, 'replaced_column')
            rows = [dict(r, **{col: expression(value(model, 'expression'), r)}) for r in data[1]]
        elif name == 'Rule Engine':
            assert value(model, 'append-column') == 'true'
            col = value(model, 'new-column-name')
            rows = [dict(r, **{col: rules(model, r)}) for r in data[1]]
        elif name == 'Rule-based Row Filter':
            rows = [r for r in data[1] if rules(model, r) is True]
        elif name == 'Sorter':
            rows = list(data[1])
            for criterion in reversed(list(config(model, 'sortingCriteria'))):
                col = value(config(criterion, 'columnV2'), 'regularChoice')
                assert all(r[col] is not None for r in rows)
                rows.sort(key=lambda r: r[col], reverse=value(criterion, 'sortingOrder') == 'DESCENDING')
        elif name in ('Table View', 'Line Plot', 'Generic JavaScript View'):
            rows = data[1]
            if name == 'Table View' and rows:
                filt = config(config(config(settings, 'view'), 'displayedColumnsV2'), 'manualFilter')
                assert set(array(filt, 'manuallySelected')) <= set(rows[0])
        else:
            raise AssertionError(('unsupported node', name))
        cache[nid] = rows
        return rows

    for nid in nodes:
        execute(nid)
    return cache

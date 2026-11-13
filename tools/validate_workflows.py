#!/usr/bin/env python3
"""Offline structure and fixture checks; this does not execute KNIME or HTTP."""
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import hashlib
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = {'k': 'http://www.knime.org/2008/09/XMLConfig'}
TASKS = ('01_Merkmalspruefung_AUFGABE.knwf', '02_Wetterlogistik_AUFGABE.knwf',
         '03_Standortmonitor_AUFGABE.knwf', '04_Stoerungsmeldungen_AUFGABE.knwf')
REFERENCES = tuple(name.replace('AUFGABE', 'REFERENZ') for name in TASKS)
PRESERVED = {
    'workflows/01_Merkmalspruefung_AUFGABE.knwf': 'a19507e90bbbea5bcc4085a3959d966cc05487a776fa6b4503deb8be861febe7',
    'workflows/04_Stoerungsmeldungen_AUFGABE.knwf': '8ffff90c7dacf84ac829da81e461e2144048d9df3f31d613bd18a536fa888080',
    'moderation/01_Merkmalspruefung_REFERENZ.knwf': '5c9e9bb923cc8b71d2e7b2e6ad9c4d24ae3e61aa797d19ad923bf27b59ffe2a3',
    'moderation/04_Stoerungsmeldungen_REFERENZ.knwf': 'c07b58fcba7eae91ceefbc5fd57c53b15955354f77ad55c184be5c6a7c7dfbba',
}


def config(element, key):
    return element.find(f"k:config[@key='{key}']", NS)


def value(element, key):
    entry = element.find(f"k:entry[@key='{key}']", NS)
    return None if entry is None or entry.get('isnull') == 'true' else entry.get('value')


def array(element, key):
    stored = config(element, key)
    return [value(stored, str(i)) for i in range(int(value(stored, 'array-size')))]


def decode_table(settings):
    model = config(settings, 'model')
    rows = list(map(int, array(model, 'rowIndices')))
    columns = list(map(int, array(model, 'columnIndices')))
    values = array(model, 'values')
    properties = config(model, 'columnProperties')
    names = [value(prop, 'ColumnName') for prop in properties]
    types = [value(config(prop, 'ColumnClass'), 'cell_class') for prop in properties]
    assert len(rows) == len(columns) == len(values)
    assert list(zip(rows, columns)) == sorted(set(zip(rows, columns)))
    count = max(rows) + 1
    assert len(values) == count * len(names)
    result = []
    for row in range(count):
        record = {}
        for col, (name, cell_type) in enumerate(zip(names, types)):
            text = values[row * len(names) + col]
            record[name] = (None if text == '' else int(text) if cell_type.endswith('IntCell')
                            else float(text) if cell_type.endswith('DoubleCell') else text)
        result.append(record)
    return result


def validate_workflow(path):
    tables, settings_by_factory = [], []
    is_api = path.name.startswith(('02_', '03_'))
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        members = archive.namelist()
        assert all(name.endswith(('.xml', '.knime', '.json')) for name in members)
        assert not any('/data/' in name for name in members)
        workflows = [name for name in members if name.endswith('/workflow.knime')]
        assert len([name for name in workflows if name.count('/') == 1]) == 1
        for name in workflows:
            root = ET.fromstring(archive.read(name))
            prefix = name.rsplit('/', 1)[0] + '/'
            saved_nodes = config(root, 'nodes')
            nodes = {int(value(n, 'id')): n for n in saved_nodes}
            assert len(nodes) == len(saved_nodes)
            edges, ports = [], set()
            for connection in config(root, 'connections'):
                source, dest, sp, dp = (int(value(connection, key))
                                      for key in ('sourceID', 'destID', 'sourcePort', 'destPort'))
                assert source in nodes and dest in nodes and sp >= 0 and dp >= 0
                assert (dest, dp) not in ports
                ports.add((dest, dp)); edges.append((source, dest))
            visited = set()
            while True:
                ready = {n for n in nodes if n not in visited
                         and all(s in visited for s, d in edges if d == n)}
                if not ready:
                    break
                visited.update(ready)
            assert visited == set(nodes), (path, 'cyclic graph')
            for node in nodes.values():
                settings_path = prefix + value(node, 'node_settings_file')
                assert settings_path in members
                settings = ET.fromstring(archive.read(settings_path))
                factory = value(settings, 'factory') or ''
                assert not any(part in factory for part in (
                    'CSVTableReader', 'ExcelTableReader', 'FileReaderNodeFactory',
                    'ExcelTableWriter', 'SendMail', 'python3', 'SecretRetriever',
                    'HubAuthentication', 'JDBC', 'DBReader'))
                settings_by_factory.append((factory, settings))
                if factory.endswith('TableCreator2NodeFactory'):
                    tables.append(decode_table(settings))
                if is_api and factory.endswith('GETRequestNodeFactory'):
                    model = config(settings, 'model')
                    assert value(model, 'Use constant URI') == 'false'
                    assert value(model, 'URI column') == 'API_URL'
                    assert value(model, 'None_enabled') == 'true'
                    assert value(model, 'SSL trust all') == 'false'
                    assert value(model, 'SSL ignore hostname errors') == 'false'
                    assert value(model, 'Proxy_enabled') == 'false'
                if is_api and factory.endswith('TableViewNodeFactory'):
                    selected = config(config(config(settings, 'view'), 'displayedColumnsV2'), 'manualFilter')
                    assert array(selected, 'manuallySelected') or value(selected, 'includeUnknownColumns') == 'true'
            if name.count('/') == 1:
                text = '\n'.join(value(a, 'text') for a in config(root, 'annotations'))
                assert all(title in text for title in ('EXTRACT', 'TRANSFORM', 'LOAD', 'OHNE ZUSÄTZLICHE DATEIEN'))
                if is_api:
                    assert 'SYNTHET' in text.upper() and 'LIVE' in text
        if path.name.startswith('03_') and '_REFERENZ' in path.name:
            assert len(workflows) == 2
            editor = next(ET.fromstring(archive.read(n)) for n in members
                          if '/Table Editor' in n and n.endswith('/settings.xml'))
            model = config(editor, 'model')
            editable = config(model, 'editableColumnsFilter')
            assert array(editable, 'included_names') == ['Einbeziehen', 'Warnschwelle_AQI']
            assert value(editable, 'enforce_option') == 'EnforceInclusion'
            assert array(config(model, 'dropdownColumnFilter'), 'included_names') == []
            settings_path = next(n for n in members if '/Pruefoberflaeche' in n and n.count('/') == 2 and n.endswith('/settings.xml'))
            assert 'Ansicht aktualisieren' in '\n'.join(archive.read(n).decode() for n in members if n.endswith('.xml'))
            assert value(ET.fromstring(archive.read(settings_path)), 'layoutJSON')
    return tables, settings_by_factory


def validate_weather(tables, settings, reference):
    request = next(t for t in tables if 'API_URL' in t[0])
    assert len(request) == 1
    uri = urlparse(request[0]['API_URL']); query = parse_qs(uri.query)
    assert uri.scheme == 'https' and uri.netloc == 'api.open-meteo.com'
    assert query['forecast_hours'] == ['48']
    assert set(query['hourly'][0].split(',')) == {'temperature_2m', 'relative_humidity_2m'}
    ships = next(t for t in tables if 'Liefer_ID' in t[0])
    products = {r['Produkt_ID']: r for r in next(t for t in tables if 'Max_Temperatur_C' in t[0])}
    weather = {r['Plan_Slot']: r for r in next(t for t in tables if 'Temperatur_C' in t[0])}
    assert len(ships) == 12 and len(weather) == 48 and set(weather) == set(range(1, 49))
    assert len({r['Liefer_ID'] for r in ships}) == 12
    for row in weather.values():
        assert row['Datenquelle'] == 'SYNTHETISCHER TEST'
        datetime.fromisoformat(row['Zeitpunkt'])
    def status(ship):
        p = products.get(ship['Produkt_ID'])
        w = weather.get(ship['Plan_Slot'], {})
        if p is None:
            return 'PRUEFEN'
        pairs = [(p['Max_Temperatur_C'], w.get('Temperatur_C')), (p['Max_Feuchte_pct'], w.get('Feuchte_pct'))]
        if any(limit is not None and datum is None for limit, datum in pairs):
            return 'PRUEFEN'
        return 'VERSCHIEBEN' if any(limit is not None and datum > limit for limit, datum in pairs) else 'FREIGABE'
    got = {s['Liefer_ID']: status(s) for s in ships}
    expected = {'FREIGABE': {'L01', 'L03', 'L09', 'L10', 'L12'},
                'VERSCHIEBEN': {'L02', 'L04', 'L06', 'L07', 'L08'}, 'PRUEFEN': {'L05', 'L11'}}
    for label, ids in expected.items():
        assert {key for key, result in got.items() if result == label} == ids
    if reference:
        jp = next(config(s, 'model') for f, s in settings if f.endswith('JSONPathNodeFactory'))
        assert array(jp, 'newColumnName') == ['Zeitpunkt', 'Temperatur_C', 'Feuchte_pct']
        assert array(jp, 'result.is.list') == ['true'] * 3
        rank = next(config(s, 'model') for f, s in settings if f.endswith('RankNodeFactory'))
        assert value(rank, 'RankOutFieldName') == 'Plan_Slot' and value(rank, 'rankDataType') == 'INT'
        # List values remain aligned; the native Ungroup is configured not to drop missing values.
        ug = next(config(s, 'model') for f, s in settings if f.endswith('UngroupNodeFactory'))
        assert value(ug, 'skipMissingValues') == 'false'
        rule = next(config(s, 'model') for f, s in settings if f.endswith('RuleEngineNodeFactory') and value(config(s, 'model'), 'new-column-name') == 'Lieferstatus')
        rules = array(rule, 'rules')
        assert rules[0] == 'MISSING $Produkt$ => "PRUEFEN"'
        assert rules.index('NOT MISSING $Max_Feuchte_pct$ AND MISSING $Feuchte_pct$ => "PRUEFEN"') < rules.index('NOT MISSING $Max_Temperatur_C$ AND $Temperatur_C$ > $Max_Temperatur_C$ => "VERSCHIEBEN"')


def validate_air(tables, settings, reference):
    locations = next(t for t in tables if 'API_URL' in t[0])
    fixture = next(t for t in tables if 'AQI' in t[0])
    assert len(locations) == len(fixture) == 4
    for row in locations:
        uri = urlparse(row['API_URL']); query = parse_qs(uri.query)
        assert uri.scheme == 'https' and uri.netloc == 'air-quality-api.open-meteo.com'
        assert set(query['current'][0].split(',')) == {'european_aqi', 'pm10', 'pm2_5'}
    def counts(rows):
        result = Counter()
        for r in rows:
            if r['Einbeziehen'] == 0:
                continue
            missing = r['Einbeziehen'] not in (0, 1) or r['Warnschwelle_AQI'] is None or r['Warnschwelle_AQI'] < 0 or not r['Prognosezeit']
            missing |= any(r[k] is None or r[k] < 0 for k in ['AQI', 'PM10', 'PM2_5'])
            state = 'PRUEFEN' if missing else 'BEOBACHTEN' if r['AQI'] > r['Warnschwelle_AQI'] else 'UNAUFFAELLIG'
            result[state] += 1
        return dict(result)
    assert counts(fixture) == {'UNAUFFAELLIG': 2, 'BEOBACHTEN': 1, 'PRUEFEN': 1}
    assert counts([dict(r, Einbeziehen=0 if r['Standort_ID'] == 'AUG' else 1) for r in fixture]) == {'UNAUFFAELLIG': 2, 'PRUEFEN': 1}
    assert counts([dict(r, Warnschwelle_AQI=90) for r in fixture]) == {'UNAUFFAELLIG': 3, 'PRUEFEN': 1}
    assert counts([dict(fixture[0], AQI=-1)]) == {'PRUEFEN': 1}
    if reference:
        jp = next(config(s, 'model') for f, s in settings if f.endswith('JSONPathNodeFactory'))
        assert array(jp, 'newColumnName') == ['Prognosezeit', 'AQI', 'PM10', 'PM2_5']
        assert array(jp, 'result.is.list') == ['false'] * 4
        joins = [config(s, 'model') for f, s in settings if f.endswith('Joiner3NodeFactory')]
        assert len(joins) == 1 and value(joins[0], 'includeLeftUnmatchedInOutput') == 'true'
        assert any(f.endswith('ColorManager2NodeFactory') for f, _ in settings)


def bundle(filename, folder, names):
    with zipfile.ZipFile(ROOT / 'downloads' / filename) as archive:
        assert archive.testzip() is None and set(archive.namelist()) == set(names)
        for name in names:
            assert archive.read(name) == (ROOT / folder / name).read_bytes()


def main():
    for path, digest in PRESERVED.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, ('accepted flow changed', path)
    for folder, names in [('workflows', TASKS), ('moderation', REFERENCES)]:
        assert {p.name for p in (ROOT / folder).glob('*.knwf')} == set(names)
        for name in names:
            path = ROOT / folder / name
            tables, settings = validate_workflow(path)
            if name.startswith('02_'):
                validate_weather(tables, settings, '_REFERENZ' in name)
            if name.startswith('03_'):
                validate_air(tables, settings, '_REFERENZ' in name)
            print('OK', path.relative_to(ROOT))
    bundle('Vier_Uebungsflows.zip', 'workflows', TASKS)
    bundle('Moderation_vier_Referenzflows.zip', 'moderation', REFERENCES)
    print('OK: cases 1/4 unchanged; eight native archives; graphs, API configuration, synthetic controls, app parameters and ZIP contents.')
    print('Not tested here: native KNIME execution/UI and live API responses (environment network restriction).')


if __name__ == '__main__':
    main()

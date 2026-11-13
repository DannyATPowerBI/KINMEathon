#!/usr/bin/env python3
"""Offline structure and fixture checks; this does not execute KNIME or HTTP."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET
import zipfile
from check_reference_graph import run

ROOT = Path(__file__).resolve().parents[1]
NS = {'k': 'http://www.knime.org/2008/09/XMLConfig'}
TASKS = ('01_Merkmalspruefung_AUFGABE.knwf', '02_Wetterlogistik_AUFGABE.knwf',
         '03_Rechnungspruefung_AUFGABE.knwf', '04_Stoerungsmeldungen_AUFGABE.knwf')
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
    is_new = path.name.startswith(('02_', '03_'))
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
                    'HubAuthentication', 'JDBC', 'DBReader', 'GETRequest', 'HTTPRequest', 'POSTRequest'))
                settings_by_factory.append((factory, settings))
                if factory.endswith('TableCreator2NodeFactory'):
                    tables.append(decode_table(settings))
                if is_new and factory.endswith('TableViewNodeFactory'):
                    selected = config(config(config(settings, 'view'), 'displayedColumnsV2'), 'manualFilter')
                    assert array(selected, 'manuallySelected') or value(selected, 'includeUnknownColumns') == 'true'
            if name.count('/') == 1:
                text = '\n'.join(value(a, 'text') for a in config(root, 'annotations'))
                assert all(title in text for title in ('EXTRACT', 'TRANSFORM', 'LOAD', 'OHNE ZUSÄTZLICHE DATEIEN'))
                if is_new:
                    assert 'SYNTHET' in text.upper()
    return tables, settings_by_factory


def validate_weather(tables, settings, reference):
    ships = next(t for t in tables if 'Liefer_ID' in t[0])
    products = {r['Produkt_ID']: r for r in next(t for t in tables if 'Max_Temperatur_C' in t[0])}
    weather = {r['Plan_Slot']: r for r in next(t for t in tables if 'Temperatur_C' in t[0])}
    assert len(ships) == 12 and len(weather) == 48 and set(weather) == set(range(1, 49))
    assert len({r['Liefer_ID'] for r in ships}) == 12
    for row in weather.values():
        assert row['Datenquelle'] == 'SYNTHETISCH'
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
        rule = next(config(s, 'model') for f, s in settings if f.endswith('RuleEngineNodeFactory') and value(config(s, 'model'), 'new-column-name') == 'Lieferstatus')
        rules = array(rule, 'rules')
        assert rules[0] == 'MISSING $Produkt$ => "PRUEFEN"'
        assert rules.index('NOT MISSING $Max_Feuchte_pct$ AND MISSING $Feuchte_pct$ => "PRUEFEN"') < rules.index('NOT MISSING $Max_Temperatur_C$ AND $Temperatur_C$ > $Max_Temperatur_C$ => "VERSCHIEBEN"')


INVOICE_EXPECTED = {
    'OK': {'I01', 'I02', 'I03', 'I06', 'I14', 'I18'},
    'DUPLIKATVERDACHT': {'I04', 'I05'},
    'WARENEINGANG_UEBERSCHRITTEN': {'I07', 'I08'},
    'PREISABWEICHUNG': {'I09'}, 'RECHENFEHLER': {'I10'},
    'BESTELLUNG_FEHLT': {'I11'}, 'WARENEINGANG_FEHLT': {'I12'},
    'LIEFERANT_ABWEICHEND': {'I13'}, 'DATEN_UNGUELTIG': {'I15', 'I19'},
    'DATEN_UNVOLLSTAENDIG': {'I16', 'I20'}, 'BESTELLMENGE_UEBERSCHRITTEN': {'I17'},
}


def validate_invoice(tables, settings, reference):
    invoices = next(t for t in tables if 'Rechnungsposition_ID' in t[0])
    orders = next(t for t in tables if 'Bestellpreis_Cent' in t[0])
    receipts = next(t for t in tables if 'Wareneingang_ID' in t[0])
    assert (len(invoices), len(orders), len(receipts)) == (20, 15, 17)
    assert len({r['Rechnungsposition_ID'] for r in invoices}) == 20
    assert len({r['Beleg_ID'] for r in invoices}) == 19
    assert len({(r['Bestell_ID'], r['Bestellposition']) for r in orders}) == 15
    assert len({r['Wareneingang_ID'] for r in receipts}) == 17
    assert {r['Rechnungsposition_ID'] for r in invoices} == set().union(*INVOICE_EXPECTED.values())
    if reference:
        assert sum(f.endswith('Joiner3NodeFactory') for f, _ in settings) == 4
        formulas = [config(s, 'model') for f, s in settings if f.endswith('JEPNodeFactory')]
        assert {value(m, 'replaced_column') for m in formulas} == {
            'Menge_nach_Stapel', 'Rechenabweichung_Cent', 'Preisabweichung_mal100', 'Preistoleranz_mal2'}


def validate_reference_graph(path):
    outputs = list(run(path, decode_table).values())
    if path.name.startswith('02_'):
        rows = next(t for t in outputs if t and 'Lieferstatus' in t[0])
        assert len(rows) == 12
        expected = {'FREIGABE': {'L01', 'L03', 'L09', 'L10', 'L12'},
                    'VERSCHIEBEN': {'L02', 'L04', 'L06', 'L07', 'L08'}, 'PRUEFEN': {'L05', 'L11'}}
        for label, ids in expected.items():
            assert {r['Liefer_ID'] for r in rows if r['Lieferstatus'] == label} == ids
        assert any(len(t) == 7 and {r['Lieferstatus'] for r in t} == {'VERSCHIEBEN', 'PRUEFEN'}
                   for t in outputs if t and 'Lieferstatus' in t[0])
    else:
        rows = next(t for t in outputs if t and 'Pruefstatus' in t[0])
        assert len(rows) == 20
        assert Counter(r['Pruefstatus'] for r in rows) == {'FREIGABE': 6, 'SPERREN': 7, 'PRUEFEN': 7}
        for reason, ids in INVOICE_EXPECTED.items():
            assert {r['Rechnungsposition_ID'] for r in rows if r['Pruefgrund'] == reason} == ids, reason
        by_id = {r['Rechnungsposition_ID']: r for r in rows}
        assert by_id['I06']['Aktuelle_Stapelmenge'] == 80
        assert by_id['I07']['Menge_nach_Stapel'] == by_id['I08']['Menge_nach_Stapel'] == 85
        assert by_id['I07']['Wareneingang_Gesamt'] == 80
        assert by_id['I14']['Rechenabweichung_Cent'] == 1
        assert by_id['I10']['Rechenabweichung_Cent'] == 2
        assert any(len(t) == 14 and {r['Pruefstatus'] for r in t} == {'SPERREN', 'PRUEFEN'}
                   for t in outputs if t and 'Pruefstatus' in t[0])


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
                validate_invoice(tables, settings, '_REFERENZ' in name)
            if name.startswith(('02_', '03_')) and '_REFERENZ' in name:
                validate_reference_graph(path)
            print('OK', path.relative_to(ROOT))
    bundle('Vier_Uebungsflows.zip', 'workflows', TASKS)
    bundle('Moderation_vier_Referenzflows.zip', 'moderation', REFERENCES)
    print('OK: cases 1/4 unchanged; eight native archives; graphs, generated data, invoice/weather controls, modeled reference results and ZIP contents.')
    print('Not tested here: native KNIME import, node execution and UI. The local model is not KNIME.')


if __name__ == '__main__':
    main()

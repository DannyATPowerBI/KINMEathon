#!/usr/bin/env python3
"""Validate packaged KNIME workflows without KNIME or third-party libraries."""

from collections import Counter
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
NS = {"k": "http://www.knime.org/2008/09/XMLConfig"}
TASKS = (
    "01_Merkmalspruefung_AUFGABE.knwf",
    "03_Grosse_Datenmenge_AUFGABE.knwf",
    "04_Stoerungsmeldungen_AUFGABE.knwf",
)
REFERENCES = tuple(name.replace("AUFGABE", "REFERENZ") for name in TASKS)


def config(element, key):
    return element.find(f"k:config[@key='{key}']", NS)


def value(element, key):
    entry = element.find(f"k:entry[@key='{key}']", NS)
    if entry is None or entry.get("isnull") == "true":
        return None
    return entry.get("value")


def array(element, key):
    stored = config(element, key)
    size = int(value(stored, "array-size"))
    return [value(stored, str(index)) for index in range(size)]


def decode_table(settings):
    model = config(settings, "model")
    rows = list(map(int, array(model, "rowIndices")))
    columns = list(map(int, array(model, "columnIndices")))
    values = array(model, "values")
    properties = config(model, "columnProperties")
    names = [value(prop, "ColumnName") for prop in properties]
    types = [value(config(prop, "ColumnClass"), "cell_class") for prop in properties]
    assert len(rows) == len(columns) == len(values)
    assert list(zip(rows, columns)) == sorted(set(zip(rows, columns)))
    count = max(rows) + 1
    assert len(values) == count * len(names)
    result = []
    for row in range(count):
        record = {}
        for column, (name, cell_type) in enumerate(zip(names, types)):
            text = values[row * len(names) + column]
            record[name] = (
                None if text == "" else int(text) if cell_type.endswith("IntCell")
                else float(text) if cell_type.endswith("DoubleCell") else text
            )
        result.append(record)
    return result


def validate_workflow(path):
    seeds = []
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, path
        members = archive.namelist()
        assert all(name.endswith((".xml", ".knime", ".json")) for name in members)
        assert not any("/data/" in name for name in members)
        workflows = [name for name in members if name.endswith("/workflow.knime")]
        assert len([name for name in workflows if name.count("/") == 1]) == 1
        for name in workflows:
            root = ET.fromstring(archive.read(name))
            prefix = name.rsplit("/", 1)[0] + "/"
            saved_nodes = config(root, "nodes")
            nodes = {int(value(node, "id")): node for node in saved_nodes}
            assert len(nodes) == len(saved_nodes)
            edges, inputs = [], set()
            for connection in config(root, "connections"):
                source, destination, source_port, destination_port = (
                    int(value(connection, key))
                    for key in ("sourceID", "destID", "sourcePort", "destPort")
                )
                assert source in nodes and destination in nodes
                assert source_port >= 0 and destination_port >= 0
                assert (destination, destination_port) not in inputs
                inputs.add((destination, destination_port))
                edges.append((source, destination))
            visited = set()
            while True:
                ready = {
                    node for node in nodes if node not in visited
                    and all(source in visited for source, dest in edges if dest == node)
                }
                if not ready:
                    break
                visited.update(ready)
            assert visited == set(nodes), (path, "cyclic graph")
            for node in nodes.values():
                settings_path = prefix + value(node, "node_settings_file")
                assert settings_path in members
                settings = ET.fromstring(archive.read(settings_path))
                factory = value(settings, "factory") or ""
                assert not any(part in factory for part in (
                    "CSVTableReader", "ExcelTableReader", "FileReaderNodeFactory",
                    "ExcelTableWriter", "SendMail", "python3", "SecretRetriever",
                    "HubAuthentication", "JDBC", "DBReader",
                )), (path, factory)
                if factory.endswith("TableCreator2NodeFactory"):
                    table = decode_table(settings)
                    if path.name.startswith("03_"):
                        seeds.append(table)
                if (path.name.startswith("03_")
                        and factory.endswith("TopKSelectorNodeFactory")
                        and value(config(settings, "model"), "amount") == "1500"):
                    entries = {entry.get("value") for entry in config(settings, "model").iter()}
                    assert {"Block", "ASCENDING"}.issubset(entries)
            if name.count("/") == 1:
                text = "\n".join(value(item, "text") for item in config(root, "annotations"))
                assert all(title in text for title in (
                    "EXTRACT", "TRANSFORM", "LOAD", "OHNE ZUSÄTZLICHE DATEIEN",
                ))
    return seeds


def validate_generator(seeds):
    blocks = next(table for table in seeds if "Block" in table[0])
    prototype = next(table for table in seeds if "Position" in table[0])
    assert len(blocks) == 1500 and len(prototype) == 1000
    assert [record["Block"] for record in blocks] == list(range(1500))
    assert 2 * len(prototype) == 2000
    profiles = Counter((row["Stunde_Text"], row["Lastprofil"]) for row in blocks)
    events = Counter((row["Programm_Basis"], row["Schema"], row["Objekt_Basis"])
                     for row in prototype)
    objects, hours, combinations = Counter(), Counter(), Counter()
    for (hour, profile), block_count in profiles.items():
        hours[hour] += block_count * len(prototype)
        for (program, schema, object_name), event_count in events.items():
            if profile == "Spitzenlast":
                program, object_name = "Fertigungsportal", "AUFTRAEGE"
            count = block_count * event_count
            objects[schema, object_name] += count
            combinations[hour, program, schema, object_name] += count
    assert sum(hours.values()) == sum(objects.values()) == sum(combinations.values()) == 1_500_000
    assert max(hours, key=hours.get) == "09" and hours["09"] == 322_000
    assert max(objects.items(), key=lambda item: item[1]) == (("WERK", "AUFTRAEGE"), 346_980)
    peak = max(((key, count) for key, count in combinations.items() if key[0] == "09"),
               key=lambda item: item[1])
    assert peak == (("09", "Fertigungsportal", "WERK", "AUFTRAEGE"), 160_508)
    for hour in hours:
        for row in prototype:
            datetime.fromisoformat("2026-02-05T" + hour + row["Zeit_Suffix"])


def validate_bundle(filename, folder, names):
    with zipfile.ZipFile(ROOT / "downloads" / filename) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(names)
        for name in names:
            assert archive.read(name) == (ROOT / folder / name).read_bytes()


def main():
    for folder, names in (("workflows", TASKS), ("moderation", REFERENCES)):
        for name in names:
            path = ROOT / folder / name
            seeds = validate_workflow(path)
            if name.startswith("03_"):
                validate_generator(seeds)
            print("OK", path.relative_to(ROOT))
    validate_bundle("Drei_Uebungsflows_ohne_Datendateien.zip", "workflows", TASKS)
    validate_bundle("Moderation_drei_Referenzflows.zip", "moderation", REFERENCES)
    print("OK: archive/XML structure, native data generation, controls, and ZIP contents.")
    print("KNIME import, execution, and interactive views still require a test in KNIME.")


if __name__ == "__main__":
    main()

# KINMEathon

Vier Teams bearbeiten parallel jeweils einen Fall in drei Stunden. Drei deutsche KNIME-Übungsflows sind enthalten. Fall 2 wird als Data App mit Databricks-Zugriff ergänzt, sobald Szenario und Tabellen feststehen.

## Dateien herunterladen

[Alle drei Aufgabenflows als ZIP herunterladen](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/downloads/Drei_Uebungsflows_ohne_Datendateien.zip)

| Fall | Thema | Workflow |
| --- | --- | --- |
| 1 | Merkmalskombinationen manuell prüfen und eine Historie ergänzen | [01_Merkmalspruefung_AUFGABE.knwf](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/01_Merkmalspruefung_AUFGABE.knwf) |
| 2 | Data App mit Databricks-Zugriff | Szenario und Tabellen stehen noch aus |
| 3 | Große Datenmenge erzeugen, auswerten und die Laufzeit verbessern | [03_Grosse_Datenmenge_AUFGABE.knwf](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/03_Grosse_Datenmenge_AUFGABE.knwf) |
| 4 | Störungsmeldungen priorisieren, zuordnen und fachlich freigeben | [04_Stoerungsmeldungen_AUFGABE.knwf](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/04_Stoerungsmeldungen_AUFGABE.knwf) |

Die [Referenzflows](moderation/) liegen separat. Das [Moderationspaket als ZIP](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/downloads/Moderation_drei_Referenzflows.zip) enthält die drei Referenzflows.

## In KNIME starten

1. Die passende `.knwf`-Datei herunterladen oder das Aufgaben-ZIP entpacken.
2. Den KNIME-Workflow-Import öffnen und die Datei importieren.
3. Die vorbereiteten Eingabe-Nodes ausführen. Story, Aufgaben, Fachregeln und Zusatzaufgaben stehen direkt als farbige Annotationen im Flow.
4. Den Flow um Verarbeitung, Prüfoberfläche und Ergebnistabellen ergänzen.
5. Den ausgeführten Workflow einschließlich seiner Ergebnisse als `.knwf` exportieren.

Die drei enthaltenen Fälle erzeugen ihre Eingabedaten vollständig im Flow. Sie benötigen keine zusätzlichen CSV-, Excel- oder sonstigen Datendateien. Die Ergebnisse bleiben als Tabellen und Ansichten im Flow; ein Dateiexport ist freiwillig.

Die Dateien wurden für KNIME Analytics Platform 5.5.1 aufgebaut. Verwendet werden KNIME Base Nodes, KNIME Views sowie für die interaktiven Prüfoberflächen KNIME JavaScript Views und Quick Forms. Standardisierte Node-Namen bleiben erhalten; Aufgaben und Beschriftungen sind deutsch.

## Datenerzeugung

| Fall | Daten im Flow |
| --- | --- |
| 1 | Table Creator erzeugen 200 bewertete und zwölf neue Merkmalskombinationen. |
| 3 | Zwei kleine Table-Creator-Tabellen und ein Cross Joiner erzeugen 1.500.000 fiktive Zugriffe. Für 2.000 Testzeilen die Node **Anzahl Blöcke** auf **2** setzen; für den Vollmodus auf **1.500**. |
| 4 | Table Creator erzeugen 24 neue Meldungen, sechs Historienfälle und drei Bereichszuständigkeiten. |

Ein Reset erzeugt wieder den definierten Startbestand. Die ergänzte Historie ist eine eigene Ergebnistabelle. Alle Daten sind fiktiv.

## Gemeinsamer Ablauf

| Minuten | Aktivität |
| --- | --- |
| 0–15 | Auftrag verstehen und Rollen verteilen |
| 15–45 | Daten erzeugen und prüfen |
| 45–105 | Verarbeitung, Regeln und Auswertung |
| 105–135 | Prüfoberfläche und Ergebnisansichten |
| 135–150 | Qualitätsprüfung und Maßnahmen |
| 150–165 | Workflow sichern und Pitch vorbereiten |
| 165–180 | Vier Pitches à drei Minuten und gemeinsamer Abschluss |

Die Zeitplanung ist für Teams mit KNIME-Grundkenntnissen ausgelegt. Für den vierten Teamplatz wird der Databricks-Fall noch ergänzt.

## Prüfung

```sh
python3 tools/validate_workflows.py
```

Die Prüfung verwendet ausschließlich die Python-Standardbibliothek. Sie kontrolliert die Archive, XML-Struktur, Verbindungen, eingebetteten Grundtabellen, Generator-Kontrollwerte und die Übereinstimmung der ZIP-Pakete mit den Einzeldateien.

**Der Import und die Ausführung in KNIME sowie die interaktiven Komponenten wurden in der Erstellungsumgebung nicht getestet.** Vor dem Termin einen Probelauf auf den Teamgeräten durchführen.

Weitere Hinweise und Kontrollwerte stehen unter [Moderation](docs/Moderation.md).

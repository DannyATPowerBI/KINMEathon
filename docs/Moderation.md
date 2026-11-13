# Durchführung und Kontrollwerte

Jedes Team erhält seinen Aufgabenflow. Die Referenzflows unterstützen die Moderation bei Aufbau und Auswertung.

## Fall 1: Merkmalsprüfung

Die Starthistorie enthält 200 Entscheidungen. Zwölf neue Kombinationen werden in einer bearbeitbaren Tabellenansicht geprüft. Nur `Ueberschneidung` ist editierbar. Erlaubte Werte sind `JA`, `NEIN` und `PRUEFEN`; ein leeres Feld bleibt offen.

Bei `n` gültigen neuen Entscheidungen enthält die aktualisierte Historie `200 + n` Zeilen, bei vollständiger Prüfung 212. Die Starthistorie bleibt unverändert. Die aktualisierte Historie wird als eigene Tabelle im Flow angezeigt.

## Fall 2: Databricks-Data-App

Dieser Fall ist für den Databricks-Zugriff reserviert. Das fachliche Szenario und die Tabellen werden noch bereitgestellt. Im Repository liegt dafür derzeit kein Workflow.

## Fall 3: Große Datenmenge

Die vorbereitete Generatorkette besteht aus Table Creator, Top k Row Filter, Cross Joiner, String Manipulation, Rule Engine und Column Filter. Sie benötigt weder eine Eingabedatei noch Python-Nodes.

Die Node **Anzahl Blöcke** wählt die Zahl der Blöcke:

- **1.500** Blöcke mit jeweils **1.000** Vorgängen: **1.500.000** Zeilen.
- **2** Blöcke mit jeweils **1.000** Vorgängen: **2.000** Testzeilen.

Die Auswertung verwendet den Objektschlüssel `Schema + Objekt`. Zuerst wird die Stunde mit den meisten Zugriffen insgesamt bestimmt. Erst anschließend wird innerhalb dieser Stunde nach Programm, Schema und Objekt gruppiert.

| Kontrollwert im Vollmodus | Ergebnis |
| --- | --- |
| Summe der Objektgruppen | 1.500.000 |
| Summe der Stundengruppen | 1.500.000 |
| Spitzenstunde am 05.02.2026 | 09:00–10:00 |
| Zugriffe in der Spitzenstunde | 322.000 |
| Häufigstes Objekt | WERK / AUFTRAEGE |
| Zugriffe auf das häufigste Objekt | 346.980 |
| Häufigste Kombination innerhalb der Spitzenstunde | Fertigungsportal / WERK / AUFTRAEGE |
| Zugriffe dieser Kombination in der Spitzenstunde | 160.508 |

Für den Laufzeitvergleich drei Durchläufe mit identischer Generatorgröße auf demselben Gerät messen und den Median vergleichen. Vor jedem Lauf die Generator- und Auswertungsnodes zurücksetzen. Die Messung umfasst Datengenerierung und vollständige Ergebnisberechnung. Hardware, Einstellungen und Cache-Effekte dokumentieren. Eine Optimierung muss die fachlichen Ergebnisse beibehalten.

Es gibt keinen vorgegebenen Beschleunigungsfaktor. Häufigkeit allein erklärt keine reale Wartezeit.

## Fall 4: Störungsmeldungen

Die Daten enthalten 24 neue Meldungen, sechs dokumentierte Historienfälle und drei Bereichszuständigkeiten. Die automatische Priorität folgt diesen Regeln in der angegebenen Reihenfolge:

1. `SOFORT`, wenn `Sicherheitsrelevant = 1`.
2. Sonst `HOCH`, wenn `Stillstand = 1` oder `Reststunden < 4`.
3. Sonst `NORMAL`, wenn `Reststunden < 24`.
4. Sonst `NIEDRIG`.

Erwartete Verteilung: **3 SOFORT, 9 HOCH, 8 NORMAL und 4 NIEDRIG**. Die Grenzwerte 4 und 24 gehören jeweils zum nächsten Zweig.

In der Prüfoberfläche dürfen nur `Entscheidung` und `Begruendung` geändert werden. Erlaubte Entscheidungen sind `FREIGEBEN`, `SPERREN` und `RUECKFRAGE`. Eine übernommene Entscheidung benötigt eine nicht leere Begründung. Die Priorität ist eine Empfehlung und ersetzt die fachliche Entscheidung nicht.

Bei `n` gültigen neuen Entscheidungen enthält die aktualisierte Historie `6 + n` Zeilen, bei vollständiger Prüfung 30.

## Bewertung

Einheitlich 100 Punkte je Team:

- Datenqualität und Schlüssel: 20.
- Fachlogik und korrekte Auswertung: 35.
- Nutzbare Prüfoberfläche und Ergebnisansichten: 20.
- Nachvollziehbarer, erneut ausführbarer Workflow: 15.
- Pitch, Erkenntnisse und Maßnahmen: 10.

Zusatzaufgaben können bei Punktgleichheit entscheiden. Ein Reset erzeugt den definierten Startbestand; zum Weitergeben den ausgeführten Workflow einschließlich seiner Ergebnisse exportieren.

## Prüfstand

Die lokale Strukturprüfung kontrolliert alle sechs Workflow-Archive, ihre XML-Dateien, Node-Verbindungen und internen Grundtabellen. Die Kontrollwerte der großen Datenmenge werden unabhängig aus den gespeicherten Grundtabellen nachgerechnet. Die ZIP-Pakete werden gegen die Einzeldateien geprüft.

Ein nativer KNIME-Import, die Ausführung der Nodes und die interaktiven Ansichten wurden noch nicht in KNIME geprüft. Laufzeiten müssen auf den Teamgeräten gemessen werden.

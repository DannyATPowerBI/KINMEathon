# Durchführung und Kontrollwerte

Jedes Team erhält seinen Aufgabenflow. Die Referenzflows unterstützen die Moderation bei Aufbau und Auswertung.

## Fall 1: Merkmalsprüfung

Die Starthistorie enthält 200 Entscheidungen. Zwölf neue Kombinationen werden in einer bearbeitbaren Tabellenansicht geprüft. Nur `Ueberschneidung` ist editierbar. Erlaubte Werte sind `JA`, `NEIN` und `PRUEFEN`; ein leeres Feld bleibt offen.

Bei `n` gültigen neuen Entscheidungen enthält die aktualisierte Historie `200 + n` Zeilen, bei vollständiger Prüfung 212. Die Starthistorie bleibt unverändert. Die aktualisierte Historie wird als eigene Tabelle im Flow angezeigt.

## Fall 2: Wetterlogistik

Zwölf Lieferungen werden mit drei Produktstammsätzen und 48 im Flow erzeugten Wetterstunden verbunden. Schwerpunkte sind Left Joins, produktabhängige Regeln, Datenlücken und Dispoliste. [Detaillierte Aufgaben und Kontrollwerte](02_Wetterlogistik.md)

Erwartet werden **5 FREIGABE, 5 VERSCHIEBEN und 2 PRUEFEN**. Gleichheit mit einem Produktlimit ist zulässig. Fehlende relevante Werte und unbekannte Produkte haben Vorrang vor einer bekannten Überschreitung. Alle zwölf Lieferungen müssen genau einmal erhalten bleiben.

## Fall 3: Fertigungsplanung mit grafischer Plantafel

Zwölf Aufträge und drei Montagezellen entstehen im Flow. Die Kernverarbeitung besteht aus einem Left Join und zwei Formeln für Dauer und Endzeit. Die vorbereitete Plantafel liefert ein Gantt-Diagramm und exportiert SVG oder HTML; das Team ergänzt eine Arbeitslastübersicht und verbessert den Plan. [Aufgaben, Vorschau und Kontrollwerte](03_Fertigungsplanung.md)

Belegungsdauer: **M1 465 min, M2 360 min, M3 250 min**, jeweils vier Aufträge. Arbeitslast: rund **96,9 %, 75,0 %, 52,1 %**. A04 dauert 105 Minuten und endet als einziger Auftrag im Ausgangsplan nach Schichtende: 14:30. Es gibt keine Überschneidungen.

Eine einfache Verbesserung schließt nur die drei Lücken auf M1: Start_Min für A02 = 90, A03 = 225 und A04 = 360. Dann endet A04 um 13:45. Alle Aufträge passen in die Schicht, ohne Mengen, Dauer oder Maschinenzuordnung zu ändern. Die Arbeitslast bleibt gleich. Andere überschneidungsfreie Verbesserungen sind ebenfalls gültig.

Wichtig für die Bewertung sind verständliche Zeitachsen, korrekte Balken, ein gespeicherter Ausgangsplan und ein begründeter Verbesserungsvorschlag. Ein automatischer Optimierungsalgorithmus oder eigene JavaScript-Programmierung wird nicht vorausgesetzt.

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

Die lokale Prüfung kontrolliert alle acht Workflow-Archive, XML-Dateien, Node-Verbindungen, intern erzeugten Daten und ZIP-Pakete. Sie rechnet die neuen Referenzgraphen für Fall 2 und 3 mit einem begrenzten lokalen Prüfmodell nach. Fälle 1, 2 und 4 sind bytegleich erhalten geblieben. Alle Fälle verwenden ausschließlich synthetische Daten aus ihren Table Creators.

Die eingebettete Plantafel wurde separat in Chromium geprüft, einschließlich SVG-/HTML-Export, verbessertem Plan und Aufgabenhinweis. Ein nativer KNIME-Import, Node-Ausführung und die Einbettung der interaktiven Ansichten sind noch auf den Teamgeräten zu prüfen. Die Browserprüfung und das lokale Prüfmodell ersetzen KNIME nicht.

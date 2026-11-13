# Durchführung und Kontrollwerte

Jedes Team erhält seinen Aufgabenflow. Die Referenzflows unterstützen die Moderation bei Aufbau und Auswertung.

## Fall 1: Merkmalsprüfung

Die Starthistorie enthält 200 Entscheidungen. Zwölf neue Kombinationen werden in einer bearbeitbaren Tabellenansicht geprüft. Nur `Ueberschneidung` ist editierbar. Erlaubte Werte sind `JA`, `NEIN` und `PRUEFEN`; ein leeres Feld bleibt offen.

Bei `n` gültigen neuen Entscheidungen enthält die aktualisierte Historie `200 + n` Zeilen, bei vollständiger Prüfung 212. Die Starthistorie bleibt unverändert. Die aktualisierte Historie wird als eigene Tabelle im Flow angezeigt.

## Fall 2: Wetterlogistik

Zwölf Lieferungen werden mit drei Produktstammsätzen und 48 im Flow erzeugten Wetterstunden verbunden. Schwerpunkte sind Left Joins, produktabhängige Regeln, Datenlücken und Dispoliste. [Detaillierte Aufgaben und Kontrollwerte](02_Wetterlogistik.md)

Erwartet werden **5 FREIGABE, 5 VERSCHIEBEN und 2 PRUEFEN**. Gleichheit mit einem Produktlimit ist zulässig. Fehlende relevante Werte und unbekannte Produkte haben Vorrang vor einer bekannten Überschreitung. Alle zwölf Lieferungen müssen genau einmal erhalten bleiben.

## Fall 3: Rechnungsprüfung

20 Rechnungspositionen aus 19 eingegangenen Belegen werden mit 15 Bestellpositionen und 17 Wareneingängen abgeglichen. Alle Daten entstehen im Flow. [Detaillierte Aufgaben und Kontrollwerte](03_Rechnungspruefung.md)

Erwartet werden **6 FREIGABE, 7 SPERREN und 7 PRUEFEN**; die Klärungsliste enthält 14 Positionen. Die Auswertung zählt Positionen. Eine Freigabeempfehlung auf Positionsebene ist noch keine Freigabe des gesamten Belegs.

Die häufigsten Stolperstellen: Positionen desselben Belegs irrtümlich als Duplikate zählen; Wareneingänge vor ihrer Aggregation verbinden; bereits berechnete Mengen vergessen; mehrere aktuelle Rechnungen einzeln statt kumuliert prüfen; Duplikate in den aktuellen Mengenstapel aufnehmen. I03 und I14 testen exakt die erlaubten Preis- und Rechentoleranzen. Die im Flow angegebene Reihenfolge bestimmt den ersten Prüfgrund.

Die optionale manuelle Klärungsansicht und der Belegstatus gehören zur Vertiefung. Für die Kernaufgabe reichen Prüfliste, Klärungsliste und Zählung nach Status/Grund.

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

Die lokale Prüfung kontrolliert alle acht Workflow-Archive, XML-Dateien, Node-Verbindungen, intern erzeugten Daten und ZIP-Pakete. Sie rechnet die neuen Referenzgraphen für Fall 2 und 3 mit einem begrenzten lokalen Prüfmodell nach. Fälle 1 und 4 sind bytegleich erhalten geblieben. Alle Fälle verwenden ausschließlich synthetische Daten aus ihren Table Creators.

Ein nativer KNIME-Import, Node-Ausführung und die interaktiven Ansichten sind noch auf den Teamgeräten zu prüfen. Das lokale Prüfmodell ersetzt KNIME nicht.

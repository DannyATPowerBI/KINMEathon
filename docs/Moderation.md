# Durchführung und Kontrollwerte

Jedes Team erhält seinen Aufgabenflow. Die Referenzflows unterstützen die Moderation bei Aufbau und Auswertung.

## Fall 1: Merkmalsprüfung

Die Starthistorie enthält 200 Entscheidungen. Zwölf neue Kombinationen werden in einer bearbeitbaren Tabellenansicht geprüft. Nur `Ueberschneidung` ist editierbar. Erlaubte Werte sind `JA`, `NEIN` und `PRUEFEN`; ein leeres Feld bleibt offen.

Bei `n` gültigen neuen Entscheidungen enthält die aktualisierte Historie `200 + n` Zeilen, bei vollständiger Prüfung 212. Die Starthistorie bleibt unverändert. Die aktualisierte Historie wird als eigene Tabelle im Flow angezeigt.

## Fall 2: Wetterlogistik

Der neue Fall verbindet zwölf fiktive Lieferungen und drei Produktstammsätze mit einer 48-Stunden-Prognose von Open-Meteo. Schwerpunkte sind die Verarbeitung paralleler JSON-Listen, eindeutige Prognose-Slots und produktabhängige Regeln. [Detaillierte Aufgaben und Kontrollwerte](02_Wetterlogistik.md)

Der Referenzflow nutzt zunächst den Live-Zweig. Für einen Test die internen Wetterwerte mit dem zweiten Eingang von **GEMEINSAMER WETTER-EINGANG** verbinden. Erwartet werden **5 FREIGABE, 5 VERSCHIEBEN und 2 PRUEFEN**. Gleichheit mit einem Produktlimit ist zulässig; fehlende relevante Werte und unbekannte Produkte werden zuerst geprüft.

Technische Fehler dürfen keine Lieferungen verschwinden lassen. Zwölf Lieferungen müssen zwölf Bewertungen ergeben. Die Live-Verteilung ist prognoseabhängig.

## Fall 3: Standortmonitor als Data App

Vier Standorte werden über aktuelle modellierte Luftqualitätswerte verglichen. Die App bietet eine veränderbare Standortauswahl und eine fiktive Beobachtungsschwelle. [Detaillierte Aufgaben und Kontrollwerte](03_Standortmonitor.md)

Der Referenzflow ist mit dem Live-Zweig verbunden. Für reproduzierbare Tests den Eingang der Komponente mit **INTERNE TESTDATEN** verbinden. Bei vier ausgewählten Standorten und Schwelle 60 ergeben sich **2 UNAUFFAELLIG, 1 BEOBACHTEN und 1 PRUEFEN**. Bei Schwelle 90 bleiben **3 UNAUFFAELLIG und 1 PRUEFEN**.

Die App darf ausschließlich Einbeziehen und Warnschwelle_AQI zur Änderung freigeben. Fehlende Werte bleiben auch bei hoher Schwelle ungeklärt. Die Schwelle ist eine didaktische Einstellung und keine gesetzliche oder medizinische Bewertung.

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

Die lokale Prüfung kontrolliert alle acht Workflow-Archive, XML-Dateien, Node-Verbindungen, internen Testdaten, API-Konfigurationen und ZIP-Pakete. Fälle 1 und 4 wurden nicht verändert. Die neuen Kontrollwerte gelten ausschließlich für synthetische Testdaten.

Ein nativer KNIME-Import, Node-Ausführung und die interaktiven Ansichten sind noch vor Ort zu prüfen. Direkte API-Aufrufe aus der Erstellungsumgebung werden mit HTTP 403 durch die Netzwerkfreigabe blockiert. Die Endpunkte und Parameter wurden anhand der offiziellen API-Dokumentation konfiguriert; Live-Antworten wurden hier nicht geprüft.

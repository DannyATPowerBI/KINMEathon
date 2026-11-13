# KINMEathon

Vier Teams bearbeiten parallel jeweils einen deutschen KNIME-Fall in drei Stunden. Story, Aufgaben, Fachregeln und Zusatzaufgaben stehen direkt als farbige Annotationen im Flow.

## Dateien herunterladen

[Alle vier Aufgabenflows als ZIP herunterladen](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/downloads/Vier_Uebungsflows.zip)

| Fall | Thema | Workflow |
| --- | --- | --- |
| 1 | Merkmalskombinationen manuell prüfen und eine Historie ergänzen | [Merkmalsprüfung](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/01_Merkmalspruefung_AUFGABE.knwf) |
| 2 | Wetterprognosen mit Produktgrenzen und Lieferungen verbinden | [Wetterlogistik](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/02_Wetterlogistik_AUFGABE.knwf) |
| 3 | Modellierte Umweltdaten als interaktive Standort-Data-App vergleichen | [Standortmonitor](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/03_Standortmonitor_AUFGABE.knwf) |
| 4 | Störungsmeldungen priorisieren, zuordnen und fachlich freigeben | [Störungsmeldungen](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/workflows/04_Stoerungsmeldungen_AUFGABE.knwf) |

Die Dateien von Fall 1 und 4 sind unverändert. Die [Referenzflows](moderation/) liegen separat; das [Moderationspaket als ZIP](https://github.com/DannyATPowerBI/KINMEathon/raw/refs/heads/main/downloads/Moderation_vier_Referenzflows.zip) enthält alle vier Referenzflows.

## In KNIME starten

1. `.knwf` herunterladen oder das Aufgaben-ZIP entpacken.
2. Über den KNIME-Workflow-Import importieren.
3. Eingabe-Nodes ausführen und die Aufgaben im Canvas lesen.
4. Verarbeitung, Prüfoberfläche und Ergebnisansichten ergänzen.
5. Den ausgeführten Workflow einschließlich Ergebnisse als `.knwf` exportieren.

Eigene Geschäfts- und Testdaten entstehen durch Table Creator im Flow. Zusätzliche CSV- oder Excel-Eingabedateien sind nicht erforderlich. Ergebnisse bleiben als Tabellen und Ansichten im Flow; ein Dateiexport ist freiwillig.

Aufgebaut für KNIME Analytics Platform 5.5.1 mit KNIME Base Nodes und KNIME Views. Prüfoberflächen verwenden zusätzlich KNIME JavaScript Views und Quick Forms. Fälle 2 und 3 benötigen die KNIME REST Client Extension und die KNIME JSON-Processing-Erweiterung.

## Die neuen API-Fälle

**Fall 2 – Wetterfest liefern:** Zwölf fiktive Lieferungen, drei Produkte und eine 48-Stunden-Prognose für Bamberg. Schwerpunkt: parallele JSON-Listen, Produktgrenzen, Datenlücken und priorisierte Dispoliste. [Aufgaben und Hinweise](docs/02_Wetterlogistik.md)

**Fall 3 – Standortmonitor:** Vier Standorte mit modellierten Luftqualitätswerten. Schwerpunkt: skalare API-Felder und eine lokale Data App mit Standortauswahl, änderbarer Beobachtungsschwelle, Rangfolge und farbiger Datenqualitätsanzeige. [Aufgaben und Hinweise](docs/03_Standortmonitor.md)

Die Live-Zweige verwenden die öffentlichen Endpunkte der [Open-Meteo Wetter-API](https://open-meteo.com/en/docs) und [Luftqualitäts-API](https://open-meteo.com/en/docs/air-quality-api). Die offene API ist für nichtkommerzielle Nutzung vorgesehen; es gelten die [Nutzungsbedingungen](https://open-meteo.com/en/terms).

### Live- und Testbetrieb

In den neuen Referenzflows sind die Auswertungen zunächst mit dem **LIVE-Zweig** verbunden. GET Request ruft die Daten erst beim Ausführen ab. Die getrennt beschrifteten **INTERNEN TESTDATEN** sind synthetische Beispiele und keine gespeicherten Live-Abfragen.

Für einen reproduzierbaren Test oder bei fehlendem Netzzugang:

- Fall 2: Den **zweiten Eingang** von **GEMEINSAMER WETTER-EINGANG** auf den Table Creator **INTERNE TESTDATEN** umstecken.
- Fall 3: Den **Eingang der Komponente Standortmonitor** auf den Table Creator **INTERNE TESTDATEN** umstecken.

Datenquelle und Prognosezeit werden mitgeführt. Die festen Kontrollzahlen gelten ausschließlich für die internen Testdaten.

## Gemeinsamer Ablauf

| Minuten | Aktivität |
| --- | --- |
| 0–15 | Auftrag und Rollen |
| 15–45 | Daten erzeugen, API abrufen, Datenqualität prüfen |
| 45–105 | Verarbeitung, Regeln oder Data App |
| 105–135 | Ergebnisansichten und Visualisierung |
| 135–150 | Qualitätsprüfung und Maßnahmen |
| 150–165 | Sicherung und Pitch-Vorbereitung |
| 165–180 | Vier Pitches à drei Minuten und gemeinsamer Abschluss |

Vorausgesetzt werden KNIME-Grundkenntnisse. Die Zeitplanung ist eine Schätzung für die jeweilige Teamaufgabe.

## Prüfung

```sh
python3 tools/validate_workflows.py
```

Die Prüfung benötigt ausschließlich die Python-Standardbibliothek. Sie kontrolliert Archive, XML, Verbindungen, interne Testdaten, API-Konfigurationen, App-Parameter und die Übereinstimmung der ZIP-Pakete mit den Einzeldateien. [Kontrollwerte und Moderation](docs/Moderation.md)

**KNIME-Import, Node-Ausführung und interaktive Ansichten wurden hier nicht getestet.** Die Netzwerkfreigabe der Erstellungsumgebung blockiert direkte API-Aufrufe mit HTTP 403; die API-Konfiguration ist dokumentationsbasiert geprüft. Vor dem Termin auf den Teamgeräten testen.

## Datenquellen

- Wetterprognosen: [Open-Meteo](https://open-meteo.com/en/docs), CC BY 4.0.
- Modellierte Luftqualitätsdaten: CAMS ENSEMBLE / Copernicus Atmosphere Monitoring Service, über [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api).
- Alle Lieferungen, Produkte, Beobachtungsschwellen und internen Testwerte sind fiktive Trainingsdaten.

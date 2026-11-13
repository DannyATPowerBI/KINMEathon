# Fall 3 – Interaktiver Standortmonitor

Das fiktive Umweltcontrolling vergleicht modellierte Werte für Bamberg, Augsburg, Köln und Wien. Ein Team baut in drei Stunden eine lokale Data App mit Standortauswahl, Beobachtungsschwelle und Datenqualitätsanzeige. [Aufgabenflow](../workflows/03_Standortmonitor_AUFGABE.knwf) · [Referenzflow](../moderation/03_Standortmonitor_REFERENZ.knwf)

## Daten und API

Die Standorttabelle entsteht im Table Creator. Sie enthält ungefähre Stadtkoordinaten, eine URL je Standort, `Einbeziehen = 1` und `Warnschwelle_AQI = 60`.

Ein Beispielaufruf der [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api):

```text
https://air-quality-api.open-meteo.com/v1/air-quality?latitude=49.9&longitude=10.9&current=european_aqi,pm10,pm2_5&timezone=Europe%2FBerlin
```

JSON Path extrahiert diese skalaren Felder:

| Spalte | JSON Path | Bedeutung |
| --- | --- | --- |
| Prognosezeit | `$['current']['time']` | Zeit des Modellwerts |
| AQI | `$['current']['european_aqi']` | Europäischer Luftqualitätsindex |
| PM10 | `$['current']['pm10']` | Konzentration in µg/m³ |
| PM2_5 | `$['current']['pm2_5']` | Konzentration in µg/m³ |

Ein Left Join führt erfolgreich gelesene Werte zurück an alle vier Standorte. Fehlgeschlagene Abfragen verschwinden dadurch nicht aus der Liste. Ein eigener View zeigt HTTP-Fehlerfälle.

## App bedienen

Die Komponente **Standortmonitor – Parameter und Ergebnisse** ausführen und ihre interaktive Ansicht öffnen. Ausschließlich diese Felder dürfen geändert werden:

- `Einbeziehen`: **1** anzeigen, **0** ausblenden.
- `Warnschwelle_AQI`: nicht negative fiktive Beobachtungsschwelle.

**Ansicht aktualisieren** bewertet die vorhandenen Daten mit den geänderten Parametern neu. Die Ergebnisansicht zeigt ausgewählte Standorte nach AQI absteigend, farbige Statuswerte und die Anzahl je Status. Eine reine Parameteränderung benötigt keinen neuen API-Aufruf.

Die Schwelle ist eine didaktische App-Einstellung. Die Statuswerte sind keine gesetzlichen Grenzwertbewertungen, Gesundheits- oder Arbeitsschutzfreigaben.

## Regeln

1. Fehlende oder ungültige Auswahlwerte: `PRUEFEN`.
2. `Einbeziehen = 0`: ausblenden.
3. Fehlende oder negative Schwelle, fehlende Zeit oder fehlende/negative Fachwerte: `PRUEFEN`.
4. Vollständiger Datensatz mit `AQI > Warnschwelle_AQI`: `BEOBACHTEN`.
5. Sonst: `UNAUFFAELLIG`.

Gleichheit ist zulässig. Prognosezeit und Datenquelle bleiben sichtbar. AQI ist ein Index; die beiden PM-Spalten haben die Einheit µg/m³.

## Interner Test

Den **Eingang der Komponente** vorübergehend mit **INTERNE TESTDATEN** statt mit **LIVE-APP-DATEN** verbinden.

| Beispiel | Erwartung |
| --- | --- |
| Alle vier Standorte, Schwelle 60 | 2 UNAUFFAELLIG, 1 BEOBACHTEN, 1 PRUEFEN |
| AUG ausblenden, übrige Schwellen 60 | 2 UNAUFFAELLIG, 1 PRUEFEN |
| Alle vier Standorte, Schwelle 90 | 3 UNAUFFAELLIG, 1 PRUEFEN |

Köln liegt im Test exakt auf 60. Beim Wiener Testdatensatz fehlen Werte. Eine höhere Schwelle darf daraus keinen unauffälligen Datensatz machen.

## Abnahme und Vertiefung

Abnahme: vier Standorte vor der Auswahl, funktionierende Parameteränderung, korrekte Ausblendung, sichtbare Datenlücken, getrennte Einheiten und drei Erkenntnisse zur Datenlage.

Für schnelle Teams: Verlauf über `hourly` ergänzen oder mit einem im Flow gehaltenen Vergleichsstand arbeiten. Modellprognosen als solche kennzeichnen.

Attribution: CAMS ENSEMBLE / Copernicus Atmosphere Monitoring Service, bereitgestellt über [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api). [Nutzungsbedingungen](https://open-meteo.com/en/terms).

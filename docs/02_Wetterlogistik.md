# Fall 2 – Wetterfest liefern

Ein Team verbindet in drei Stunden eine offene Wetterprognose mit zwölf fiktiven Lieferungen. Die vollständigen Aufgaben stehen im [Aufgabenflow](../workflows/02_Wetterlogistik_AUFGABE.knwf). Der [Referenzflow](../moderation/02_Wetterlogistik_REFERENZ.knwf) enthält zusätzlich JSON-Auflösung, Joins, Regeln, Dispoliste und Feuchtediagramm.

## Daten und API

Table Creator erzeugen zwölf Lieferungen und drei Produkte. Der Live-Zweig verwendet die [Open-Meteo Weather Forecast API](https://open-meteo.com/en/docs):

```text
https://api.open-meteo.com/v1/forecast?latitude=49.9&longitude=10.9&hourly=temperature_2m,relative_humidity_2m&forecast_hours=48&timezone=Europe%2FBerlin
```

`forecast_hours=48` bezieht sich auf den aktuellen Stunden-Zeitschritt. Die tatsächlich zurückgegebenen Zeitstempel sind für die Zuordnung maßgeblich. JSON Path extrahiert drei Listen:

| Neue Spalte | JSON Path |
| --- | --- |
| Zeitpunkt | `$['hourly']['time'][*]` |
| Temperatur_C | `$['hourly']['temperature_2m'][*]` |
| Feuchte_pct | `$['hourly']['relative_humidity_2m'][*]` |

Ungroup löst die Listen gemeinsam auf. Rank vergibt nach Zeitpunkt aufsteigend die Integer-Slots **1 bis 48**. Slot 1 ist der erste API-Zeitpunkt und kein festes Kalenderdatum. Fehlende Werte dürfen die Zuordnung der parallelen Listen nicht verschieben.

## Fachregeln

| Produkt | Temperatur maximal | Relative Feuchte maximal |
| --- | --- | --- |
| P100 – Klebstoff | 25 °C | 70 % |
| P200 – Elektronik | 30 °C | 80 % |
| P300 – Stahlhalter | Keine Einschränkung | Keine Einschränkung |

1. Unbekanntes Produkt: `PRUEFEN`.
2. Beide Limits leer: `FREIGABE`.
3. Für eine eingeschränkte Eigenschaft fehlt der Wetterwert: `PRUEFEN`; diese Prüfung hat Vorrang vor einer bekannten Überschreitung.
4. Ein relevanter Wert ist **größer** als sein Produktlimit: `VERSCHIEBEN`.
5. Sonst: `FREIGABE`.

Gleichheit ist zulässig. Left Joins nach `Produkt_ID` und `Plan_Slot` müssen alle zwölf Lieferungen erhalten. Die Dispoliste zeigt nur Eingriffe, sortiert nach Priorität und Slot.

## Interner Test

Den Ausgang von **INTERNE TESTDATEN** an den **zweiten Eingang** des Joiners **GEMEINSAMER WETTER-EINGANG** anschließen und dort den Live-Zweig trennen.

| Lieferungen | Status |
| --- | --- |
| L01, L03, L09, L10, L12 | FREIGABE |
| L02, L04, L06, L07, L08 | VERSCHIEBEN |
| L05, L11 | PRUEFEN |

L03 und L09 liegen exakt auf Grenzwerten. Bei L05 fehlt eine relevante Feuchte; L11 hat ein unbekanntes Produkt. L10 und L12 sind wetterunempfindlich. Die Testdaten sind synthetisch; Live-Zahlen ändern sich mit der Prognose.

## Abnahme und Vertiefung

- HTTP 200 und technische Fehler getrennt zeigen.
- Zwölf vollständige Bewertungen, sichtbare Datenquelle und Prognosezeit.
- Korrekte Grenztests, Dispoliste, Statusanzahl und Feuchteverlauf.
- Drei konkrete Maßnahmen für die Disposition.

Für schnelle Teams: den frühesten sicheren späteren Prognose-Slot bestimmen und fiktive Verzugskosten ergänzen. Nur vorhandene Prognosen verwenden.

Quelle: Wetterprognosen von [Open-Meteo](https://open-meteo.com/en/docs), CC BY 4.0. [Nutzungsbedingungen](https://open-meteo.com/en/terms).

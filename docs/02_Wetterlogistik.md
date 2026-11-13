# Fall 2 – Wetterfest liefern

Ein Team verbindet in drei Stunden zwölf fiktive Lieferungen mit Produktgrenzen und 48 synthetischen Wetterstunden. Die vollständigen Aufgaben stehen im [Aufgabenflow](../workflows/02_Wetterlogistik_AUFGABE.knwf). Der [Referenzflow](../moderation/02_Wetterlogistik_REFERENZ.knwf) ergänzt Joins, Regeln, Dispoliste, Statusübersicht und Feuchtediagramm.

## Daten im Flow

Drei Table Creator erzeugen zwölf Lieferungen, drei Produkte und 48 Wetterstunden. `Plan_Slot` 1 bis 48 bezeichnet aufeinanderfolgende Stunden ab **15.06.2026, 09:00**. `Zeitpunkt` und `Datenquelle = SYNTHETISCH` bleiben bis zum Ergebnis erhalten. Es sind keine externen Datenquellen erforderlich.

Prüft `Produkt_ID` im Stamm und `Plan_Slot` im Wetter auf Eindeutigkeit. Verknüpft Lieferungen per Left Join mit den Produktgrenzen und danach per Left Join mit dem Wetter. Alle zwölf Lieferungen müssen genau einmal erhalten bleiben.

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

Gleichheit ist zulässig. Die Dispoliste zeigt nur Eingriffe, sortiert nach Priorität `HOCH` vor `NORMAL`, danach nach Slot aufsteigend.

## Kontrollwerte

| Lieferungen | Status |
| --- | --- |
| L01, L03, L09, L10, L12 | FREIGABE |
| L02, L04, L06, L07, L08 | VERSCHIEBEN |
| L05, L11 | PRUEFEN |

L03 und L09 liegen exakt auf Grenzwerten. Bei L05 fehlt eine relevante Feuchte; L11 hat ein unbekanntes Produkt. L10 und L12 sind wetterunempfindlich. Die Verteilung lautet **5 / 5 / 2**; alle Werte entstehen reproduzierbar im Flow.

## Abgabe und Vertiefung

- Vollständige Bewertung mit Produktgrenzen, Wetterwerten, Zeitpunkt und Datenquelle.
- Dispoliste, Statusanzahl und Feuchteverlauf über alle 48 Slots.
- Drei konkrete Maßnahmen für die Disposition und ein ausgeführter Workflow.

Für schnelle Teams: frühesten vollständig zulässigen späteren Slot innerhalb der 48 Stunden bestimmen; falls keiner existiert, `KEIN ZEITFENSTER` anzeigen. Fiktive Verzugskosten je Stunde ergänzen und Alternativen vergleichen.

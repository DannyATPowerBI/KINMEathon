# Fall 3 – Rechnungsprüfung

Die fiktive FrankenWerk GmbH bereitet ihren Monatsabschluss vor. Einkauf, Lager und Kreditorenbuchhaltung brauchen eine nachvollziehbare Vorprüfung der eingegangenen Rechnungen. Ein Team baut die Auswertung in drei Stunden. Die vollständigen Aufgaben stehen im [Aufgabenflow](../workflows/03_Rechnungspruefung_AUFGABE.knwf); die [Referenz](../moderation/03_Rechnungspruefung_REFERENZ.knwf) enthält die Verarbeitung und Ergebnisansichten.

## Daten im Flow

| Table Creator | Zeilen | Schlüssel und Bedeutung |
| --- | --- | --- |
| Rechnungspositionen | 20 | Eindeutige Rechnungsposition_ID; 19 eingegangene Beleg_ID |
| Bestellpositionen | 15 | Bestell_ID + Bestellposition; bestellte Menge, Preis, Lieferant und bereits gebuchte Rechnungsmenge |
| Wareneingänge | 17 | Eindeutige Wareneingang_ID; mehrere Eingänge je Bestellposition möglich |

Alle Daten sind erzeugte Trainingsdaten. Beträge und Stückpreise sind **netto in Cent**, Mengen in Stück. `Bereits_berechnet_Menge` bezeichnet den gebuchten Bestand **vor** dem aktuellen Rechnungsstapel. Es gibt in diesem Fall ausschließlich Eingangsrechnungen, keine Gutschriften. Alle Toleranzen sind fiktive interne Übungsregeln.

`Beleg_ID` bezeichnet einen konkreten Rechnungseingang. Mehrere Positionen desselben Belegs sind zulässig. Derselbe Lieferant und dieselbe Rechnungsnummer auf verschiedenen Beleg_ID lösen Duplikatverdacht aus. Rechnungsnummern sind im Startbestand bereits einheitlich formatiert.

## Verarbeitung

1. Zählt die unterschiedlichen Beleg_ID je `Lieferant_ID + Rechnungsnummer`. Mit zwei GroupBy-Nodes: zuerst nach diesen beiden Feldern und Beleg_ID gruppieren, dann je Lieferant und Rechnungsnummer die Beleg_ID zählen. Verbindet die Anzahl zurück an alle Positionen.
2. Summiert die Wareneingangsmenge nach `Bestell_ID + Bestellposition`, bevor ihr sie an Rechnungen verbindet. Verknüpft Bestellung, kumulierten Wareneingang und Duplikatanzahl mit Left Joins. Ergebnis: genau 20 Rechnungspositionen.
3. Bildet den aktuellen Mengenstapel aus Positionen mit positiver Rechnungsmenge, bekanntem Bestellschlüssel, passendem Lieferanten und ohne Duplikatverdacht. Summiert nach Bestellschlüssel. Preis- und Betragsfehler schließen eine ansonsten relevante Menge dabei nicht aus.
4. Verbindet die aktuelle Stapelmenge per Left Join zurück an **alle** Rechnungspositionen. `Menge_nach_Stapel = Bereits_berechnet_Menge + Aktuelle_Stapelmenge`.
5. Berechnet `Rechenabweichung_Cent = Positionsbetrag_Cent − Rechnungsmenge × Rechnungspreis_Cent` sowie die Preisvergleichswerte unten. Fehlende Werte bleiben fehlend.
6. Bestimmt je Position den ersten Prüfgrund in der folgenden Tabelle und daraus den Status. Ein früherer Fehler hat Vorrang vor späteren Prüfungen.

## Prüfgründe in ihrer Reihenfolge

| Rang | Bedingung | Prüfgrund | Status |
| --- | --- | --- | --- |
| 1 | Mehr als eine Beleg_ID je Lieferant und Rechnungsnummer | DUPLIKATVERDACHT | SPERREN |
| 2 | Menge, Preis oder Positionsbetrag fehlt | DATEN_UNVOLLSTAENDIG | PRUEFEN |
| 3 | Menge ≤ 0, Preis < 0 oder Positionsbetrag < 0 | DATEN_UNGUELTIG | PRUEFEN |
| 4 | Bestellposition nicht gefunden | BESTELLUNG_FEHLT | PRUEFEN |
| 5 | Rechnungslieferant weicht vom Bestelllieferanten ab | LIEFERANT_ABWEICHEND | PRUEFEN |
| 6 | Kein kumulierter Wareneingang vorhanden | WARENEINGANG_FEHLT | PRUEFEN |
| 7 | Rechenabweichung größer als +1 oder kleiner als −1 Cent | RECHENFEHLER | SPERREN |
| 8 | Menge nach Stapel > bestellte Menge | BESTELLMENGE_UEBERSCHRITTEN | SPERREN |
| 9 | Menge nach Stapel > kumulierter Wareneingang | WARENEINGANG_UEBERSCHRITTEN | SPERREN |
| 10 | Preisaufschlag > 2 % | PREISABWEICHUNG | SPERREN |
| 11 | Keine Regel trifft zu | OK | FREIGABE |

Für Rang 8 und 9 werden alle ansonsten prüfbaren Positionen der betroffenen Bestellposition gesperrt. Es wird nicht willkürlich eine einzelne Rechnung freigegeben. Preise bis einschließlich 2 % Aufschlag und Nachlässe sind zulässig. Prüft ohne Division:

```text
(Rechnungspreis_Cent − Bestellpreis_Cent) × 100 > Bestellpreis_Cent × 2
```

Die Empfehlung gilt auf **Positionsebene**. Sie löst keine Buchung oder Zahlung aus.

## Kontrollwerte

| Positionen | Prüfgrund | Status |
| --- | --- | --- |
| I01, I02, I03, I06, I14, I18 | OK | FREIGABE |
| I04, I05 | DUPLIKATVERDACHT | SPERREN |
| I07, I08 | WARENEINGANG_UEBERSCHRITTEN | SPERREN |
| I09 | PREISABWEICHUNG | SPERREN |
| I10 | RECHENFEHLER | SPERREN |
| I11 | BESTELLUNG_FEHLT | PRUEFEN |
| I12 | WARENEINGANG_FEHLT | PRUEFEN |
| I13 | LIEFERANT_ABWEICHEND | PRUEFEN |
| I15, I19 | DATEN_UNGUELTIG | PRUEFEN |
| I16, I20 | DATEN_UNVOLLSTAENDIG | PRUEFEN |
| I17 | BESTELLMENGE_UEBERSCHRITTEN | SPERREN |

Damit ergeben sich **6 FREIGABE, 7 SPERREN und 7 PRUEFEN**. Die Klärungsliste enthält 14 Positionen.

Besonders aufschlussreich:

- I01 und I02 gehören zum selben Beleg und dürfen keinen Duplikatverdacht erzeugen.
- I04 und I05 sind zwei Eingänge derselben Rechnung. Beide werden gesperrt; ihre Mengen dürfen I06 nicht künstlich blockieren.
- Für I07 und I08 ergeben 30 bereits berechnete Stück plus 30 + 25 aktuelle Stück insgesamt 85 Stück gegenüber 80 eingegangenen Stück. Beide Positionen werden gesperrt.
- I03 liegt mit 1.020 gegenüber 1.000 Cent exakt bei 2 % und ist zulässig. I09 liegt mit 1.021 Cent darüber.
- I14 enthält genau 1 Cent Rechenabweichung und ist zulässig; I10 enthält 2 Cent.
- Bei I17 reichen 15 eingegangene Stück für 11 berechnete Stück, bestellt wurden aber nur 10. Die Bestellmenge begrenzt die Freigabe ebenfalls.

## Abgabe und Vertiefung

Abzugeben sind eine vollständige Prüfliste, eine getrennte Klärungsliste, eine Positionszählung nach Status und Prüfgrund sowie drei konkrete Rückfragen an Einkauf, Lager oder Buchhaltung.

Für schnelle Teams: Belegstatus aus den Positionen ableiten (`SPERREN` vor `PRUEFEN` vor `FREIGABE`) und alle Gründe sammeln. Alternativ eine bearbeitbare Klärungsansicht mit Zuständigkeit, Entscheidung und Begründung bauen; automatische Empfehlung und manuelle Entscheidung bleiben getrennte Spalten.

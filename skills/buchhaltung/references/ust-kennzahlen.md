# Umsatzsteuer-Voranmeldung — Kennzahlen (Kz)

Die wichtigsten Kennzahlen der USt-Voranmeldung (Formular UStVA). Beträge der
**Bemessungsgrundlage** immer *netto und volle Euro* (abgerundet), Steuerbeträge
mit Cent. Bei Sonderfällen (EU, § 13b) lieber `PRÜFEN` markieren und den Nutzer
auf Steuerberatung hinweisen, als falsch einzuordnen.

## Standard — steuerpflichtige Umsätze (Ausgangsseite)

| Kz | Inhalt |
|----|--------|
| 81 | Umsätze zu 19 % — Bemessungsgrundlage (netto) |
| 86 | Umsätze zu 7 % — Bemessungsgrundlage (netto) |
| 35 / 36 | Umsätze zu anderen Steuersätzen (BMG / Steuer) |

Die Steuer zu Kz 81/86 rechnet das Formular automatisch (19 % bzw. 7 %).

## Vorsteuer (Eingangsseite)

| Kz | Inhalt |
|----|--------|
| 66 | abziehbare Vorsteuer aus Rechnungen anderer Unternehmer |
| 61 | Vorsteuer aus i.g. Erwerb |
| 62 | entrichtete Einfuhrumsatzsteuer |
| 67 | Vorsteuer nach § 13b (Leistungsempfänger) |

## Ergebnis

| Kz | Inhalt |
|----|--------|
| 83 | verbleibende USt-Vorauszahlung (>0) oder Überschuss/Erstattung (<0) |

Berechnung: `USt (aus 81/86 + Sonderfälle) − Vorsteuer (66 + 61 + 62 + 67) = 83`.

## Sonderfälle (immer `PRÜFEN` und Nutzer informieren)

| Kz | Inhalt | Hinweis |
|----|--------|---------|
| 41 | steuerfreie i.g. Lieferungen (an EU-Unternehmer m. USt-IdNr.) | + Zusammenfassende Meldung nötig |
| 89 | i.g. Erwerbe 19 % (BMG) | Erwerbsteuer, meist zugleich Kz 61 Vorsteuer |
| 93 | i.g. Erwerbe 7 % (BMG) | |
| 21 | § 13b: bezogene Leistungen, Steuer schuldet Empfänger | zugleich Kz 67 Vorsteuer |
| 60 | § 13b: erbrachte Leistungen, Empfänger schuldet Steuer | Rechnung ohne USt, Hinweis „Steuerschuldnerschaft des Leistungsempfängers" |
| 48 | Umsätze § 19 (Kleinunternehmer) | i. d. R. keine Voranmeldung |

**Reverse Charge (§ 13b)** und **innergemeinschaftlicher Erwerb** heben sich bei
voll vorsteuerabzugsberechtigten Unternehmern oft auf (Steuer = Vorsteuer),
müssen aber trotzdem korrekt in beiden Kz erscheinen. Bei EU-B2B-Geschäften
zusätzlich prüfen: gültige USt-IdNr. des Partners und ggf. Zusammenfassende
Meldung (ZM).

## Turnus & Fristen

- **Monatlich:** wenn USt-Vorjahr > 7.500 € (im Gründungsjahr und Folgejahr
  i. d. R. immer monatlich).
- **Vierteljährlich:** USt-Vorjahr 1.000 – 7.500 €.
- **Jährlich (keine Voranmeldung):** USt-Vorjahr < 1.000 €.
- **Abgabefrist:** bis zum **10.** des Folgemonats/-quartals; mit
  Dauerfristverlängerung um **1 Monat** verlängert (bei Monatszahlern gegen
  Sondervorauszahlung von 1/11 der Vorjahres-Zahllast).
- Abgabe elektronisch authentifiziert über ELSTER.

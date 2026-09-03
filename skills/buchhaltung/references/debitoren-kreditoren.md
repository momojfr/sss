# Debitoren, Kreditoren, Zahlungsverkehr & Mahnwesen

Verwaltung der **offenen Posten** (OP) — unbezahlte Rechnungen auf beiden Seiten:

- **Debitoren** = Kunden, die **uns** Geld schulden (Forderungen, Aktivseite).
- **Kreditoren** = Lieferanten, denen **wir** Geld schulden (Verbindlichkeiten,
  Passivseite).

Das Skript `scripts/offene_posten.py` wertet eine Rechnungsliste aus (OP-Liste,
Aging, Mahnvorschlag, Zahlungsvorschlag) — siehe SKILL.md, Bereiche 6 & 7, und
`scripts/beispiel_rechnungen.csv`.

## Der Lebensweg einer Rechnung (Debitor)

```
Rechnung an Kunden      1400 Forderungen aLuL   an  8400 Erlöse      (+ 1776 USt)
Kunde zahlt (Bank)      1200 Bank               an  1400 Forderungen aLuL
Teilzahlung             1200 Bank               an  1400 Forderungen aLuL  (Restbetrag bleibt offen)
Forderung uneinbringlich 2400 Abschreibung Ford. an 1400 Forderungen aLuL  (+ USt-Korrektur) → PRÜFEN
```

## Der Lebensweg einer Rechnung (Kreditor)

```
Eingangsrechnung        3200 Wareneingang       an  1600 Verbindlichkeiten aLuL  (+ 1576 Vorsteuer)
Wir zahlen (Bank)       1600 Verbindlichkeiten  an  1200 Bank
Zahlung mit Skonto      1600 Verbindlichkeiten  an  1200 Bank
                                                 an  8730 erhaltene Skonti (+ VSt-Korrektur) → PRÜFEN
```

## Rechnungsprüfung Kreditoren (vor der Zahlung)

Vor jeder Zahlung prüfen: sachlich (Leistung erhalten? Menge/Preis korrekt?),
rechnerisch (Summen, USt) und formal (§ 14 UStG erfüllt → Vorsteuerabzug?).
Erst dann zur Zahlung freigeben. Fehlt etwas → `PRÜFEN`, nicht zahlen.

## Zahlungsverkehr

- **SEPA-Überweisung:** Empfänger, IBAN, Betrag, Verwendungszweck (Rechnungs-/
  Kundennummer!) sammeln; Fälligkeiten und Skontofristen im Blick behalten.
  Das Skript liefert dafür einen Zahlungsvorschlag (fällige Posten, Skonto
  zuerst).
- **Skonto:** Preisnachlass bei schneller Zahlung, z. B. „2 % Skonto bei Zahlung
  innerhalb 14 Tagen, netto 30 Tage". Skonto lohnt fast immer — der effektive
  Jahreszins des Verzichts ist sehr hoch. `zahlbetrag = brutto × (1 − skonto%)`.
- **Kontenabstimmung (Bank/Kasse):** jede Bankbewegung einem offenen Posten oder
  Konto zuordnen; Saldo laut Kontoauszug muss dem Saldo des Bankkontos in der
  Buchhaltung entsprechen. Die **Kasse** wird über ein Kassenbuch geführt
  (GoBD: täglich, vollständig, kein negativer Kassenbestand).

## Mahnwesen (Debitoren)

Zahlt ein Kunde nicht, folgt ein gestuftes Verfahren. Übliche Stufen (Konvention,
im Skript hinterlegt und anpassbar):

| Überfällig | Stufe |
|-----------|-------|
| 0 Tage | nicht fällig |
| ab 1 Tag | fällig |
| ab ~14 Tage | Zahlungserinnerung (freundlich) |
| ab ~28 Tage | 1. Mahnung |
| ab ~42 Tage | 2. Mahnung |
| ab ~56 Tage | 3. Mahnung / Inkasso / Mahnbescheid |

**Verzug (§ 286 BGB):** Der Schuldner kommt spätestens 30 Tage nach Fälligkeit
und Zugang der Rechnung in Verzug (bei Verbrauchern nur, wenn darauf hingewiesen
wurde), oder sofort mit einer Mahnung nach Fälligkeit.

**Verzugszinsen (§ 288 BGB):** ab Verzug — bei Geschäften ohne Verbraucher­beteiligung
9 Prozentpunkte über dem Basiszinssatz, sonst 5 Prozentpunkte. Bei B2B zusätzlich
eine **Mahnpauschale von 40 €** (§ 288 Abs. 5 BGB). Konkrete Zinshöhe und
Beitreibung sind Rechtsfragen → im Zweifel `PRÜFEN` und auf anwaltliche/Inkasso-
Beratung hinweisen.

## Aging (Fälligkeitsstruktur)

Die OP-Liste wird nach Überfälligkeit gestaffelt (nicht fällig / 1–30 / 31–60 /
61–90 / über 90 Tage). Das zeigt auf einen Blick, wie viel Geld wie lange
aussteht — wichtig für Liquiditätsplanung und Risikobewertung (alte Forderungen
sind ausfallgefährdet; ggf. Einzelwertberichtigung → `PRÜFEN`).

## Grenzen

Das Skript verwaltet offene Posten und schlägt Mahn-/Zahlschritte vor. Es
verschickt nichts, bucht nicht automatisch und ist keine Rechtsberatung. Für den
Zahlungslauf (SEPA-XML/Bank), das gerichtliche Mahnverfahren und
Wertberichtigungen Fachsoftware bzw. Fachkraft/Anwalt einbinden.

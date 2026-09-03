---
name: buchhaltung
description: >-
  Use when the user works on bookkeeping / accounting / payroll tasks
  (Buchhaltung, Lohn, Gehalt) — reading invoices and receipts (Belege,
  Rechnungen), extracting amounts, VAT (USt/MwSt) and dates into a table,
  categorising and posting transactions (Kontierung, SKR03/SKR04), preparing an
  Einnahmen-Überschuss-Rechnung (EÜR), calculating VAT and the USt-Voranmeldung,
  and running payroll: gross-to-net (Brutto→Netto), Lohnsteuer & social security
  (KV/PV/RV/AV), building a payslip (Gehaltsabrechnung/Lohnzettel), posting
  wages, and the Lohnsteuer-Anmeldung / SV-Beitragsnachweis. Triggers on
  "Buchhaltung", "Beleg", "Rechnung erfassen", "Kontierung", "EÜR",
  "Einnahmen-Überschuss", "Umsatzsteuer", "USt-Voranmeldung", "Vorsteuer",
  "Ausgaben kategorisieren", "Gehalt", "Lohn", "Gehaltsabrechnung",
  "Lohnabrechnung", "Brutto Netto", "Lohnsteuer", "Sozialversicherung",
  "bookkeeping", "payroll", "categorise these receipts", "prepare my VAT return",
  even when the user only drops a folder of PDFs and says "mach mal Buchhaltung".
---

# Buchhaltung — Belege erfassen, buchen, EÜR & USt

Dieser Skill hilft bei der laufenden Buchhaltung für Selbstständige und kleine
Unternehmen im deutschsprachigen Raum. Er deckt drei Bereiche ab, die
aufeinander aufbauen:

1. **Belege & Rechnungen** — Daten aus PDF/Bild-Belegen strukturiert erfassen.
2. **Kontierung & Buchführung** — Buchungen kategorisieren (SKR03/SKR04) und
   eine EÜR aufbauen.
3. **USt & Steuer** — Umsatz- und Vorsteuer berechnen, USt-Voranmeldung
   vorbereiten.

Fast jede Aufgabe folgt derselben Kette: **Beleg → Buchungssatz → Auswertung.**
Erfasse einmal sauber, dann fallen EÜR und USt-Voranmeldung fast von selbst ab.

> **Wichtig — kein Ersatz für Steuerberatung.** Dieser Skill bereitet Zahlen
> vor und rechnet nach klaren Regeln. Er trifft keine rechtsverbindlichen
> Aussagen. Bei unklaren Sachverhalten (Bewirtung, Privatanteil, Reverse
> Charge, § 13b, innergemeinschaftlicher Erwerb) markiere den Vorgang als
> **„PRÜFEN"** und weise den Nutzer darauf hin, statt zu raten. Lieber eine
> ehrliche Lücke als eine falsche Buchung.

---

## Schritt 0 — Kontext klären (kurz, einmalig)

Bevor du buchst, kläre die drei Angaben, die alles Weitere bestimmen. Frag nur,
was du nicht schon aus dem Gespräch oder den Dateien weißt:

- **Kontenrahmen:** SKR03 oder SKR04? (Standard in DE: SKR04 bei
  bilanzierenden GmbHs, SKR03 bei vielen EÜR-Selbstständigen. Im Zweifel SKR03
  für Freiberufler/Einzelunternehmer.)
- **USt-Status:** Regelbesteuerung oder **Kleinunternehmer (§ 19 UStG)**? Bei
  Kleinunternehmern gibt es keine USt/Vorsteuer und keine Voranmeldung — das
  vereinfacht alles und du darfst keine USt ausweisen.
- **Gewinnermittlung:** EÜR (§ 4 Abs. 3 EStG) oder Bilanz? Dieser Skill ist auf
  **EÜR** ausgelegt (Zufluss-/Abfluss-Prinzip).

Halte die Antworten fest und wende sie durchgängig an.

---

## Bereich 1 — Belege & Rechnungen erfassen

Ziel: aus einem Stapel PDFs/Bildern eine saubere Buchungstabelle machen.

**Vorgehen pro Beleg:**

1. **Lesen.** PDFs mit dem `pdf`-Skill / Textextraktion öffnen; bei Scans/Fotos
   OCR nutzen. Bei mehrseitigen Sammel-PDFs jede Rechnung einzeln behandeln.
2. **Pflichtfelder ziehen** — diese acht Felder pro Beleg:

   | Feld | Beispiel | Hinweis |
   |------|----------|---------|
   | `datum` | 2026-02-14 | Rechnungs-/Leistungsdatum, ISO-Format |
   | `beleg_nr` | RE-2026-0042 | Rechnungsnummer des Ausstellers |
   | `partner` | Telekom Deutschland GmbH | Lieferant (Ausgabe) / Kunde (Einnahme) |
   | `netto` | 84.03 | Nettobetrag |
   | `ust_satz` | 19 | 19, 7 oder 0 (%) |
   | `ust_betrag` | 15.97 | Steuerbetrag |
   | `brutto` | 100.00 | Rechnungsbetrag |
   | `beschreibung` | Mobilfunk Februar | kurze Sachbezeichnung |

3. **Prüfen (Rechenprobe).** `netto + ust_betrag == brutto` und
   `netto * ust_satz/100 ≈ ust_betrag` (Rundung ±0,02 €). Weicht es ab, ist
   meist ein Feld falsch gelesen — nachschauen, nicht überschreiben.
4. **Pflichtangaben checken.** Für den Vorsteuerabzug muss eine Rechnung §14
   UStG erfüllen (vollständiger Name/Anschrift von Aussteller *und* Empfänger,
   Steuernummer/USt-IdNr., Rechnungsnummer, Datum, Menge/Art, Entgelt, Steuer).
   Fehlt Wesentliches → `status = "PRÜFEN: §14"`.
   Kleinbetragsrechnungen bis 250 € brutto (§ 33 UStDV) brauchen weniger.

**Ausgabeformat.** Standardmäßig eine CSV/Tabelle mit genau diesen Spalten
(zusätzlich `richtung` = `einnahme`/`ausgabe`, `konto`, `status`). Für echte
Tabellen den `xlsx`-Skill nutzen. Nie Werte erfinden — leer lassen und als
`PRÜFEN` markieren, wenn ein Feld nicht lesbar ist.

Beispielzeile:
```
datum,beleg_nr,partner,richtung,netto,ust_satz,ust_betrag,brutto,konto,beschreibung,status
2026-02-14,RE-2026-0042,Telekom Deutschland GmbH,ausgabe,84.03,19,15.97,100.00,4920,Mobilfunk Februar,OK
```

---

## Bereich 2 — Kontierung & Buchführung (EÜR)

Ziel: jedem erfassten Beleg ein Konto zuordnen und daraus die EÜR bauen.

**Kontierung.** Ordne jeder Zeile ein Sachkonto zu. Die häufigsten Konten für
EÜR-Selbstständige stehen in `references/kontenrahmen.md` (SKR03 **und** SKR04
nebeneinander) — lies die Datei, wenn du eine Zuordnung brauchst oder unsicher
bist. Faustregeln:

- Ordne nach dem **wirtschaftlichen Zweck**, nicht nach dem Lieferantennamen
  (Amazon kann Büromaterial *oder* Anlagevermögen sein).
- **GWG / Anlagevermögen:** Wirtschaftsgüter über 800 € netto sind nicht sofort
  voll abziehbar, sondern zu aktivieren/abzuschreiben (AfA) → als `PRÜFEN: AfA`
  markieren statt als laufende Ausgabe zu verbuchen.
- **Teilweise privat** (Handy, Kfz, Arbeitszimmer): Privatanteil kennzeichnen,
  nicht stillschweigend 100 % ansetzen → `PRÜFEN: Privatanteil`.
- **Bewirtung:** nur 70 % abziehbar, Vorsteuer aber zu 100 % → `PRÜFEN`.

**EÜR aufbauen (Zufluss-/Abfluss-Prinzip).** Maßgeblich ist das *Zahlungs*datum,
nicht das Rechnungsdatum. Gruppiere die gebuchten Zeilen:

```
EÜR <Zeitraum>
Betriebseinnahmen
  Umsatzerlöse (netto)                     .......
  vereinnahmte Umsatzsteuer                .......
Summe Einnahmen                            =======
Betriebsausgaben
  <je Kategorie, netto>                    .......
  gezahlte Vorsteuer                       .......
  Abschreibungen (AfA)                     .......
Summe Ausgaben                             =======
Gewinn / Verlust                           =======
```

Bei Regelbesteuerung ist die EÜR eine **Netto**-Rechnung: USt und Vorsteuer sind
durchlaufende Posten (eigene Zeilen), sie erhöhen/mindern den Gewinn nicht.
Bei Kleinunternehmern rechnest du in **Brutto**beträgen ohne USt-Zeilen.

Für die amtliche Anlage EÜR gibt es feste Zeilennummern — die gängigsten sind
in `references/euer-anlage.md` gemappt; lies die Datei, wenn der Nutzer die
Formularzeilen braucht.

---

## Bereich 3 — Umsatzsteuer & USt-Voranmeldung

Nur relevant bei **Regelbesteuerung** (Kleinunternehmer überspringen).

**Grundrechnung je Zeitraum:**
```
  vereinnahmte Umsatzsteuer (aus Einnahmen)      USt
- gezahlte Vorsteuer        (aus Ausgaben)     − VSt
= Zahllast (>0) oder Erstattung (<0)             ===
```

**USt-Voranmeldung — Kennzahlen (die wichtigsten Kz):**

| Kz | Bedeutung |
|----|-----------|
| 81 | Umsätze zu 19 % (Bemessungsgrundlage netto) |
| 86 | Umsätze zu 7 % (Bemessungsgrundlage netto) |
| 66 | abziehbare Vorsteuer |
| 83 | verbleibende Zahllast / Überschuss |

Rechne **je Steuersatz getrennt** und weise Bemessungsgrundlage (netto) und
Steuer getrennt aus. Weitere Fälle (§ 13b Reverse Charge, i.g. Erwerb/Lieferung,
Kz 89/61/21/46) in `references/ust-kennzahlen.md` — lies die Datei bei
Auslands-/B2B-EU-Sachverhalten und markiere sie sonst als `PRÜFEN`.

**Turnus & Frist.** Voranmeldung i. d. R. monatlich oder vierteljährlich, Abgabe
bis zum **10.** des Folgemonats (mit Dauerfristverlängerung +1 Monat). Nenne die
konkrete Frist, wenn der Nutzer einen Zeitraum abrechnet.

---

## Bereich 4 — Löhne & Gehälter

Ziel: aus einem Bruttogehalt die Abrechnung machen (Brutto → Netto), sie als
Dokument ausgeben, korrekt verbuchen und die Meldungen ans FA/an die
Krankenkasse vorbereiten.

> **Genauigkeit & Grenzen.** Die **Sozialversicherung** wird mit festen
> Prozentsätzen und Beitragsbemessungsgrenzen exakt gerechnet. Die **Lohnsteuer**
> berechnet `scripts/lohnsteuer_2026.py` nach dem **amtlichen BMF-Programmablauf­plan
> 2026** (§ 39b EStG) — das Skript ist per Selbsttest gegen die amtlichen
> Prüftabellen verifiziert (Steuerklassen I–VI, laufender Arbeitslohn). Noch
> nicht abgebildet sind Sonderfälle: Versorgungsbezüge, Altersentlastungs­betrag,
> sonstige Bezüge (Einmalzahlungen), Faktorverfahren und ELStAM-Freibeträge —
> in diesen Fällen `PRÜFEN` markieren. Für einen verbindlichen, laufenden
> Abrechnungsbetrieb mit ELStAM-Abruf und elektronischen Meldungen bleibt
> zertifizierte Lohnsoftware (DATEV, Lexware, sv.net + ELSTER) Pflicht.

**Vorgehen je Mitarbeiter und Monat:**

1. **Eckdaten sammeln:** Bruttogehalt, Steuerklasse (I–VI), Kinderfreibeträge,
   Konfession (Kirchensteuer 8 %/9 %), KV-Typ (gesetzlich/privat), Zusatzbeitrag
   der Krankenkasse, Bundesland (Sachsen weicht bei der PV ab), Alter/Kinder
   (Pflegeversicherungs-Zuschlag bzw. -Abschläge), sonstige Bezüge.
2. **Sozialversicherung rechnen** — je Zweig `Beitrag = min(Brutto, BBG) × Satz`,
   aufgeteilt in Arbeitnehmer- und Arbeitgeberanteil. Sätze,
   Beitragsbemessungsgrenzen und Sonderregeln stehen in
   `references/lohn-gehalt.md` — **lies die Datei**, bevor du rechnest, und prüfe,
   ob die dort genannten Werte für das abzurechnende Jahr noch aktuell sind
   (sie ändern sich jährlich).
3. **Lohnsteuer/Soli/KiSt** rechnet das Skript exakt nach dem amtlichen PAP
   (siehe unten). Bei Sonderfällen (Versorgungsbezüge, Einmalzahlungen …) als
   `PRÜFEN: LSt` markieren.

**Rechen-Skript.** Für Standardfälle `scripts/gehaltsabrechnung.py` nutzen,
statt von Hand zu rechnen — es liefert die komplette Abrechnung (SV exakt +
Lohnsteuer nach amtlichem BMF-PAP 2026):

```bash
python3 scripts/gehaltsabrechnung.py --brutto 4000 --steuerklasse 1 \
    --kinderlos --bundesland NW --konfession keine
```
Weitere Optionen: `--kinder N`, `--zkf N` (Kinderfreibeträge für Soli/KiSt),
`--kv-zusatz 2.9`, `--bundesland SN` (Sachsen), `--konfession ev|rk`.
Die Lohnsteuer-Logik steckt in `scripts/lohnsteuer_2026.py`; deren Korrektheit
lässt sich jederzeit prüfen mit `python3 scripts/lohnsteuer_2026.py --selftest`
(rechnet die amtlichen Prüftabellen nach).
4. **Netto ermitteln:** `Netto = Brutto − LSt − Soli − KiSt − AN-Anteil SV`.
5. **Arbeitgeberkosten:** `AG-brutto = Brutto + AG-Anteil SV + Umlagen (U1/U2,
   Insolvenzgeldumlage) + gesetzliche Unfallversicherung`. Das ist die Zahl, die
   den Arbeitgeber real kostet — wichtig für die EÜR.
6. **Rechenprobe:** AN-Anteil + AG-Anteil je SV-Zweig muss dem Gesamtbeitrag
   entsprechen; bei vielen Zeilen mit einem kleinen Python-Skript rechnen.

**Abrechnung als Dokument.** Standard-Aufbau des Lohnzettels — für ein echtes
PDF/eine Tabelle den `pdf`- bzw. `xlsx`-Skill nutzen:

```
Gehaltsabrechnung <Monat/Jahr> — <Name> (Steuerklasse <…>)
Bruttobezüge
  Grundgehalt                                .......
  ggf. Zulagen / Sachbezüge                  .......
= Gesamtbrutto                               =======
Gesetzliche Abzüge (Arbeitnehmer)
  Lohnsteuer                               − .......
  Solidaritätszuschlag                     − .......
  Kirchensteuer                            − .......
  Krankenversicherung (AN)                 − .......
  Pflegeversicherung (AN)                  − .......
  Rentenversicherung (AN)                  − .......
  Arbeitslosenversicherung (AN)            − .......
= Nettoverdienst / Auszahlungsbetrag         =======
Nachrichtlich: Arbeitgeberanteil SV + Umlagen  .......
```

**Verbuchen.** Kontonummern (SKR03/SKR04) und Buchungssätze stehen in
`references/lohn-gehalt.md`. Grundmuster:
- Aufwand: Löhne/Gehälter (Bruttolohn) + gesetzliche soziale Aufwendungen
  (AG-Anteil).
- Gegenkonten: Verbindlichkeiten aus Lohn/Gehalt (Nettoauszahlung),
  Verbindlichkeiten Finanzamt (LSt/Soli/KiSt), Verbindlichkeiten SV (AN+AG-Anteil).

In der **EÜR** (Zufluss-/Abfluss-Prinzip) zählt der Aufwand im Monat der
*Zahlung*: Nettolohn, Lohnsteuer und SV-Beiträge sind Betriebsausgaben, wenn sie
abfließen — der volle Personalaufwand ist AG-brutto.

**Meldungen & Fristen** (Details + aktuelle Schwellen in `references/lohn-gehalt.md`):
- **Lohnsteuer-Anmeldung** ans Finanzamt (ELSTER), bis 10. des Folgemonats;
  Turnus monatlich/vierteljährlich/jährlich je nach Vorjahres-Lohnsteuer.
- **SV-Beitragsnachweis** an die Krankenkasse (Einzugsstelle); Beiträge fällig am
  drittletzten Bankarbeitstag des Monats.
- **DEÜV-Meldungen** (An-/Abmeldung, Jahresmeldung) via Lohnprogramm/sv.net.
- Jährlich: **Lohnsteuerbescheinigung** an FA/Arbeitnehmer, Meldung an
  Berufsgenossenschaft (Unfallversicherung).

---

## Arbeitsprinzipien (für alle Bereiche)

- **Nachvollziehbarkeit vor Vollständigkeit.** Jede Zahl muss auf einen Beleg
  zurückführbar sein. Lieber eine Zeile als `PRÜFEN` offenlassen als sie zu
  raten — eine falsche Buchung kostet später mehr Zeit als eine ehrliche Lücke.
- **Rechenproben laufen lassen.** Summen kontrollieren (Netto+USt=Brutto;
  Summe Einnahmen − Summe Ausgaben = Gewinn; USt − VSt = Zahllast). Wenn du
  viele Zeilen summierst, schreib ein kleines Python-Skript statt im Kopf zu
  rechnen — reproduzierbar und fehlerfrei.
- **Einheiten & Format.** Beträge mit zwei Nachkommastellen, Datum ISO
  (YYYY-MM-DD), Prozent als Zahl (19, nicht "19%"). Konsistenz erleichtert
  spätere Weiterverarbeitung.
- **Datenschutz.** Belege enthalten personenbezogene und geschäftliche Daten.
  Verarbeite sie lokal; lade sie nicht ungefragt zu externen Diensten hoch.
- **Am Ende zusammenfassen.** Kurzer Überblick: wie viele Belege erfasst, Summe
  Einnahmen/Ausgaben, Gewinn, USt-Zahllast — und eine Liste aller `PRÜFEN`-
  Fälle, damit der Nutzer weiß, was noch offen ist.

---

## Referenzdateien

- `references/kontenrahmen.md` — häufige Sachkonten SKR03/SKR04 nebeneinander,
  mit typischen Buchungen. Lesen für die Kontierung.
- `references/euer-anlage.md` — Mapping der wichtigsten Zeilen der amtlichen
  Anlage EÜR. Lesen, wenn der Nutzer das Formular ausfüllen will.
- `references/ust-kennzahlen.md` — Kennzahlen der USt-Voranmeldung inkl.
  Sonderfälle (§ 13b, EU). Lesen bei USt-Voranmeldung und Auslandssachverhalten.
- `references/lohn-gehalt.md` — SV-Beitragssätze, Beitragsbemessungsgrenzen,
  Lohnsteuerklassen, Lohnkonten/Buchungssätze und Melde­fristen. Lesen für jede
  Gehalts-/Lohnabrechnung und vor dem Verbuchen von Löhnen.
- `scripts/gehaltsabrechnung.py` — Brutto→Netto-Rechner (SV + Lohnsteuer), gibt
  die komplette Abrechnung aus. Für Standard-Gehaltsabrechnungen nutzen.
- `scripts/lohnsteuer_2026.py` — amtliche Lohnsteuer 2026 (BMF-PAP, § 39b EStG),
  gegen die amtlichen Prüftabellen verifiziert (`--selftest`).

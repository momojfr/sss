# Lohn & Gehalt — Sätze, Grenzen, Konten, Meldungen (Deutschland)

Nachschlagewerk für die Gehaltsabrechnung. **Alle Zahlen jährlich prüfen** —
Beitragssätze und Beitragsbemessungsgrenzen (BBG) ändern sich jedes Jahr. Die
unten genannten Werte sind der Stand **2026** und dienen als Ausgangspunkt;
für einen anderen Abrechnungsmonat die amtlichen Werte des jeweiligen Jahres
einsetzen (Quellen: BMF, GKV-Spitzenverband, Deutsche Rentenversicherung).

> **Lohnsteuer ist hier NICHT tabelliert.** Sie folgt dem amtlichen
> Programmablaufplan (PAP) des BMF und hängt von Steuerklasse, ELStAM-Freibeträgen
> und Jahr ab. Ohne offizielle Tabelle/PAP oder Lohnsoftware die Lohnsteuer nur
> als Schätzung ausgeben und `PRÜFEN: LSt` markieren.

## Sozialversicherung — Beitragssätze (Stand 2026)

Aufteilung grundsätzlich hälftig zwischen Arbeitnehmer (AN) und Arbeitgeber (AG),
mit Ausnahmen (siehe Fußnoten).

| Zweig | Gesamt | AN-Anteil | AG-Anteil |
|-------|--------|-----------|-----------|
| Rentenversicherung (RV) | 18,6 % | 9,3 % | 9,3 % |
| Arbeitslosenversicherung (AV) | 2,6 % | 1,3 % | 1,3 % |
| Krankenversicherung (KV), allgemein | 14,6 % | 7,3 % | 7,3 % |
| KV-Zusatzbeitrag¹ | ⌀ 2,9 % (kassenindividuell) | hälftig | hälftig |
| Pflegeversicherung (PV)² | 3,6 % | 1,8 % | 1,8 % |

¹ **Zusatzbeitrag:** jede Krankenkasse legt ihn selbst fest; der vom BMF
veröffentlichte *durchschnittliche* Zusatzbeitrag 2026 (**2,9 %**) dient nur als
Rechengröße — die einzelnen Kassen liegen ca. 2,2 – 4,4 %. Den tatsächlichen Satz
der konkreten Kasse verwenden. Wird hälftig getragen.

² **Pflegeversicherung – Sonderregeln (2026):**
- Grundsatz 3,6 % (hälftig).
- **Kinderlose** ab 23 Jahren zahlen einen Zuschlag von **0,6 %** allein als AN
  → Gesamtsatz 4,2 %, AN-Anteil 2,4 %.
- Ab dem **2. bis 5. Kind** (unter 25 J.) sinkt der Beitrag um je 0,25
  Beitragssatzpunkte je Kind → niedrigster Satz 2,4 % bei 5+ Kindern.
- In **Sachsen** trägt der AN einen höheren Anteil (wegen Buß- und Bettag):
  AN 2,3 % / AG 1,3 % (plus ggf. Kinderlosenzuschlag beim AN).

## Beitragsbemessungsgrenzen (BBG) & Grenzen (Stand 2026)

Beiträge nur bis zur BBG; darüber liegendes Entgelt ist beitragsfrei.
`beitragspflichtiges Entgelt = min(Bruttogehalt, BBG)`.

| Grenze | monatlich | jährlich |
|--------|-----------|----------|
| BBG KV/PV | 5.812,50 € | 69.750 € |
| BBG RV/AV (bundeseinheitlich) | 8.450,00 € | 101.400 € |
| Versicherungspflichtgrenze KV (JAEG) | 6.450,00 € | 77.400 € |

- Über der **JAEG** kann sich der AN privat krankenversichern; dann zahlt der AG
  einen Zuschuss (max. hälftiger allgemeiner KV/PV-Beitrag bis zur BBG).
- **Minijob:** bis 603 €/Monat (Stand 2026, dynamisch am Mindestlohn von
  13,90 €/h) — pauschale AG-Abgaben an die Minijob-Zentrale, kein regulärer
  Lohnsteuer-/SV-Abzug. Eigener Sonderfall → bei Minijobs `PRÜFEN` und
  gesondert behandeln.
- **Midijob (Übergangsbereich):** 603,01 – 2.000 €/Monat — reduzierter
  AN-Beitrag nach Gleitzonenformel → `PRÜFEN`.

## Umlagen & Unfallversicherung (nur/überwiegend Arbeitgeber)

| Umlage | Zweck | wer |
|--------|-------|-----|
| U1 | Erstattung Entgeltfortzahlung Krankheit (nur Betriebe ≤ 30 AN) | AG |
| U2 | Erstattung Mutterschaftsaufwendungen (alle Betriebe) | AG |
| U3 (Insolvenzgeldumlage) | Insolvenzgeld | AG |
| Gesetzliche Unfallversicherung | Berufsgenossenschaft | AG allein |

U1/U2/U3-Sätze legt die jeweilige Krankenkasse fest; die Unfallversicherung
rechnet die Berufsgenossenschaft jährlich ab (Gefahrtarif).

## Lohnsteuer — Steuerklassen (nur Zuordnung, keine Beträge)

| Kl. | typischer Fall |
|-----|----------------|
| I | ledig / geschieden / verwitwet ohne Kind |
| II | Alleinerziehende (mit Entlastungsbetrag) |
| III | verheiratet, höher verdienend (Partner in V) |
| IV | verheiratet, beide etwa gleich (optional mit Faktor) |
| V | verheiratet, geringer verdienend (Partner in III) |
| VI | zweites/weiteres Dienstverhältnis |

Zusätzlich: **Solidaritätszuschlag** 5,5 % der Lohnsteuer (nur oberhalb der
Freigrenze; für die meisten AN entfällt er) und **Kirchensteuer** 8 % (BY, BW)
bzw. 9 % (übrige Länder) der Lohnsteuer bei Kirchenmitgliedschaft.

## Verbuchen — Konten (SKR03 / SKR04)

**Aufwandskonten:**

| Zweck | SKR03 | SKR04 |
|-------|-------|-------|
| Gehälter | 4120 | 6020 |
| Löhne | 4110 | 6010 |
| gesetzliche soziale Aufwendungen (AG-Anteil SV) | 4130 | 6110 |
| Beiträge Berufsgenossenschaft | 4138 | 6120 |

**Verbindlichkeitskonten:**

| Zweck | SKR03 | SKR04 |
|-------|-------|-------|
| Verbindlichkeiten aus Lohn und Gehalt (Nettoauszahlung) | 1740 | 3720 |
| Verbindlichkeiten Lohn-/Kirchensteuer (an FA) | 1741 | 3730 |
| Verbindlichkeiten soziale Sicherheit (an Krankenkassen) | 1742 | 3740 |

**Beispiel-Buchungssatz (Gehalt, Regelbuchung):**
```
Gehälter (4120/6020)                 an  Verb. Lohn/Gehalt (1740/3720)  [Netto]
gesetzl. soz. Aufwendungen (4130/6110) an  Verb. soz. Sicherheit (1742/3740) [AG-SV]
                                     an  Verb. Lohn-/KiSt (1741/3730)   [LSt+Soli+KiSt]
                                     an  Verb. soz. Sicherheit (1742/3740) [AN-SV]
```
Der AN-Anteil SV und die Lohnsteuer werden vom Bruttolohn einbehalten (mindern
also nicht zusätzlich den Aufwand — der Aufwand ist der Bruttolohn), der AG-Anteil
ist zusätzlicher Aufwand. Bei **EÜR** wird jeweils im Zahlungsmonat als
Betriebsausgabe erfasst.

## Meldungen & Fristen

**Lohnsteuer-Anmeldung** (an Finanzamt, elektronisch über ELSTER):
- Turnus nach abzuführender **Vorjahres-Lohnsteuer**:
  - > 5.000 € → monatlich
  - 1.080 – 5.000 € → vierteljährlich
  - ≤ 1.080 € → jährlich
- Frist: bis zum **10.** des Folgemonats/-quartals.

**Sozialversicherung** (an die jeweilige Krankenkasse als Einzugsstelle):
- **Beitragsnachweis** spätestens zwei Arbeitstage vor Fälligkeit (fünftletzter
  Bankarbeitstag) elektronisch übermitteln.
- **Fälligkeit der Beiträge:** drittletzter Bankarbeitstag des laufenden Monats
  (voraussichtliche Beiträge; Differenz im Folgemonat ausgleichen).

**DEÜV-Meldungen** (elektronisch, via Lohnprogramm oder sv.net):
- Anmeldung bei Beschäftigungsbeginn, Abmeldung bei Ende,
  Jahresmeldung (bis 15.02. des Folgejahres), Unterbrechungsmeldungen.

**Jährlich:**
- **Lohnsteuerbescheinigung** an Finanzamt (elektronisch) und Arbeitnehmer.
- **Lohnnachweis** an die Berufsgenossenschaft (Unfallversicherung).

## Grenzen dieses Skills

Für einen verbindlichen, mehrfachen Abrechnungslauf ist **zertifizierte
Lohnsoftware** (DATEV, Lexware, sv.net + ELSTER etc.) erforderlich — u. a. wegen
der amtlichen Lohnsteuerberechnung, der ELStAM-Abfrage und der pflichtigen
elektronischen Meldeverfahren. Dieser Skill rechnet und strukturiert, ersetzt
aber keine Lohnbuchhaltung durch Fachkraft/Steuerberater.

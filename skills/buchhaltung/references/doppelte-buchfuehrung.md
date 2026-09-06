# Doppelte Buchführung — Soll/Haben, GuV, Bilanz

Für Bilanzierungspflichtige (Kaufleute, GmbH/UG, oder bei Überschreiten der
Grenzen nach § 241a HGB / § 141 AO — ca. 800.000 € Umsatz bzw. 80.000 € Gewinn).
Wer nur eine EÜR macht, braucht diesen Teil nicht (siehe SKILL.md, Bereich 2).

## Kontenarten und die Soll/Haben-Regel

Jede Buchung berührt **zwei** Konten: einmal im **Soll** (links), einmal im
**Haben** (rechts). Merksatz des Buchungssatzes: **„Soll an Haben"**. Die Summe
aller Soll-Buchungen ist immer gleich der Summe aller Haben-Buchungen.

Wo ein Konto *zunimmt*, hängt von seiner Art ab:

| Kontenart | Beispiele | Zugang bucht man im … | Saldo |
|-----------|-----------|------------------------|-------|
| **Aktivkonto** (Vermögen) | Bank, Kasse, Forderungen, Anlagen | **Soll** | Sollsaldo |
| **Passivkonto** (Schulden) | Verbindlichkeiten, Darlehen | **Haben** | Habensaldo |
| **Eigenkapital** | Kapital, Privatkonten | **Haben** | Habensaldo |
| **Aufwandskonto** | Miete, Löhne, Material | **Soll** | Sollsaldo |
| **Ertragskonto** | Umsatzerlöse, Zinserträge | **Haben** | Habensaldo |

Faustregel: **Aktiv- und Aufwandskonten nehmen im Soll zu**, **Passiv-, Eigen­kapital-
und Ertragskonten im Haben.** Ein Abgang läuft jeweils auf der Gegenseite.

## Beispiel-Buchungssätze

```
Vorgang                              Soll            an  Haben           Betrag
Kunde zahlt Rechnung (Bank)          1200 Bank           1400 Ford.      1.190
Wareneinkauf auf Ziel (netto+VSt)    3200 Wareneing.     1600 Verb.      5.000
                                     1576 Vorsteuer      1600 Verb.        950
Warenverkauf (Bank, brutto)          1200 Bank           8400 Erlöse    20.000
                                     1200 Bank           1776 USt        3.800
Miete abgebucht                      4210 Miete          1200 Bank       1.200
Abschreibung Anlage                  4830 AfA            0410 BGA        2.000
```
Ein Vorgang kann mehrere Soll- oder Haben-Zeilen haben (Splitbuchung), solange
die Summen gleich sind. Im Journal (siehe unten) schreibt man je Zeile ein
Soll- und ein Haben-Konto; Splits werden auf mehrere Zeilen verteilt.

## Vom Journal zur Auswertung (Skript)

`scripts/buchhaltung_auswertung.py` liest ein **Buchungsjournal** (CSV) und
erzeugt Saldenliste, GuV und Bilanz mit Kontrollsummen. Beispiel liegt bei:
`scripts/beispiel_journal.csv`.

Journal-Format (CSV, Kopfzeile):
```
datum,soll,haben,betrag,text
2026-03-15,1200,8400,20000,Warenverkauf netto
```

Aufruf:
```bash
# Gesamtkostenverfahren (Standard)
python3 scripts/buchhaltung_auswertung.py --journal scripts/beispiel_journal.csv

# Umsatzkostenverfahren (braucht Funktionszuordnung, s. u.)
python3 scripts/buchhaltung_auswertung.py --journal scripts/beispiel_journal.csv \
    --konten scripts/beispiel_konten.csv --verfahren ukv

# nur ein Teil: saldenliste | guv | bilanz | alle
python3 scripts/buchhaltung_auswertung.py --journal <datei> --was bilanz
```

Das Skript kennt die gängigen SKR03-Konten (Zuordnung Aktiv/Passiv/Ertrag/
Aufwand + GuV-/Bilanzposten) eingebaut. **Unbekannte Konten** werden gemeldet,
nie geraten — dann in einer `--konten`-CSV ergänzen:
```
konto,name,typ,gkv_posten,funktion
7000,Kfz-Kosten,aufwand,sonstige betriebliche Aufwendungen,Vertrieb
```
`typ` ∈ `aktiv | passiv | eigenkapital | ertrag | aufwand`. Die `--konten`-Datei
**überlagert** die eingebaute Zuordnung feldweise; um nur UKV-Funktionen zu
ergänzen, genügen die Spalten `konto,funktion` (siehe `beispiel_konten.csv`).

## GuV nach § 275 HGB — zwei Verfahren

Beide führen zum selben Jahresüberschuss, gliedern die Aufwendungen aber anders:

**Gesamtkostenverfahren (GKV)** — nach *Aufwandsarten*. Üblich für kleine/
mittlere Firmen.
```
  Umsatzerlöse
+ Bestandsveränderungen / andere aktivierte Eigenleistungen
+ sonstige betriebliche Erträge
- Materialaufwand
- Personalaufwand
- Abschreibungen
- sonstige betriebliche Aufwendungen
= Betriebsergebnis
±  Finanzergebnis (Zinsen)
-  Steuern
= Jahresüberschuss / -fehlbetrag
```

**Umsatzkostenverfahren (UKV)** — nach *Funktionsbereichen*. Braucht je
Aufwandskonto eine Funktion (`Herstellung | Vertrieb | Verwaltung`).
```
  Umsatzerlöse
- Herstellungskosten der zur Erzielung der Umsatzerlöse erbrachten Leistungen
- Vertriebskosten
- allgemeine Verwaltungskosten
+ sonstige betriebliche Erträge
= Betriebsergebnis  → … → Jahresüberschuss
```

## Bilanz (Grobgliederung § 266 HGB)

```
AKTIVA                              PASSIVA
A. Anlagevermögen                   A. Eigenkapital
   - immaterielle VG                   (+ Jahresüberschuss)
   - Sachanlagen                    B. Rückstellungen
B. Umlaufvermögen                   C. Verbindlichkeiten
   - Vorräte                           - aus Lieferungen/Leistungen
   - Forderungen                       - sonstige (Steuern, Löhne, SV)
   - Kasse/Bank
```
Es muss stets gelten: **Summe Aktiva = Summe Passiva**. Der Jahresüberschuss aus
der GuV erhöht das Eigenkapital (Verlust mindert es). Das Skript setzt ihn
automatisch ins Eigenkapital und prüft die Bilanzgleichung.

## Grenzen

Das Skript deckt den laufenden Buchungsstoff, GuV und eine Grobbilanz ab. Nicht
enthalten: Eröffnungs-/Abschlussbuchungen-Automatik, Rechnungsabgrenzung,
Rückstellungsbewertung, Anhang/Lagebericht, E-Bilanz-Taxonomie. Für den
verbindlichen Jahresabschluss Fachkraft/Steuerberater und zertifizierte Software.

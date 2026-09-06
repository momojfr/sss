# CFO-Projekt auleas-shop — Briefing

Kurzbriefing, damit jede/r (Mensch oder Claude) sofort weiß, worum es geht.

## Ziel
Den Online-Shop **auleas-shop.de** wirtschaftlich aufräumen — aus CFO-Sicht
verstehen, **wo Geld verdient und wo es verloren wird**:
- Deckungsbeitrag (DB) je Produkt: was bleibt nach Ware, Verpackung, Versand,
  Zahlungsgebühren wirklich übrig?
- Fixkostenblock und **Break-even** (welcher Umsatz deckt alles?)
- Bestand & Kapitalbindung (Ladenhüter, Reichweite)
- Versandkosten — **aktuell nur Hermes, soll geändert werden** (Alternativen
  gegenrechnen)
- Offene Posten / Liquidität (wer schuldet wem)

## Eckdaten
- Sortiment: **20–100 Produkte (SKUs)**.
- Es gibt einen **Shop-Export (CSV)** für Produkte und Bestellungen.
- Rechtsform / USt-Status / Gewinnermittlung: siehe Tab `01_Stammdaten` (vom
  Nutzer auszufüllen).

## Arbeitsdatei
`cfo/CFO-Datenerfassung_auleas.xlsx` — 12 Tabs:
`00_Anleitung, 01_Stammdaten, 02_Produkte_DB, 03_Bestand, 04_Verpackung,
05_Versand, 06_Fixkosten, 07_Variable_Regeln, 08_Umsatz_Monat, 09_Marketing,
10_Offene_Posten, 11_Lieferanten`.
Konvention: **gelbe** Zeile = Beispiel (nicht überschreiben), **grüne** Spalten =
Formeln (nicht ausfüllen).

## Nächste Schritte (Reihenfolge)
1. **Shop-Export** (Produkte + Bestellungen der letzten 12 Monate) hochladen →
   daraus die Tabs `02_Produkte_DB`, `03_Bestand`, `08_Umsatz_Monat` befüllen.
   Fehlt der Einkaufspreis (EK) im Export, kurze EK-Liste je SKU nachtragen.
2. Tabs **`06_Fixkosten`** und **`02_Produkte_DB`** füllen (zeigen am schnellsten,
   wo es brennt).
3. Belege beilegen (PDF): **Hermes-Rechnung**, 1–2 **Wareneinkaufs-Rechnungen**,
   **3 Monate Kontoauszug**, eine **PayPal/Stripe-Abrechnung**.
4. Rest der Tabs nachziehen (Verpackung, Versand, variable Regeln, Lieferanten).

## Was daraus entsteht
- DB je SKU + Rangliste Gewinnbringer/Verlustbringer
- Fixkosten-Übersicht + Break-even
- Bestandsanalyse (Kapitalbindung, Reichweite, Ladenhüter)
- Versand-Check Hermes vs. Alternativen (DHL/DPD/GLS) + Verpackungsoptimierung
- Offene Posten + Zahlungs-/Mahnvorschlag (Skript
  `skills/buchhaltung/scripts/offene_posten.py`)

Für Buchungen/GuV/Bilanz und Lohn nutzt dieses Projekt den **Buchhaltungs-Skill**
in `skills/buchhaltung/` (inkl. Rechen-Skripte).

## Grenzen / Vertraulichkeit
Kein Ersatz für Steuerberatung; unklare Fälle als `PRÜFEN` markieren. **Echte
Finanzdaten** (ausgefüllte Excel, Auszüge, Rechnungen) vertraulich behandeln und
**nicht** in ein geteiltes/öffentliches Repo committen — nur die leere Vorlage
gehört hier rein.

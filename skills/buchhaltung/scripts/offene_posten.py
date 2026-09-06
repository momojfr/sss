#!/usr/bin/env python3
"""Offene Posten — Debitoren, Kreditoren, Mahnwesen und Zahlungsvorschlag.

Liest eine Rechnungsliste (CSV) und erzeugt:
  * Offene-Posten-Liste Debitoren (unbezahlte Kundenforderungen) mit
    Fälligkeits-/Überfälligkeits-Analyse (Aging) und Mahnstufen-Vorschlag.
  * Offene-Posten-Liste Kreditoren (unbezahlte Lieferantenrechnungen) mit
    Zahlungsvorschlag inkl. Skonto-Prüfung.
  * Kurzübersicht: Summe Forderungen, Summe Verbindlichkeiten, Saldo.

Eingabe-CSV (Kopfzeile; Trennzeichen ',' oder ';'):
    art,partner,beleg_nr,rechnungsdatum,faelligkeit,betrag,bezahlt_betrag,skonto_prozent,skonto_tage
  * art:            debitor (Kunde schuldet uns) | kreditor (wir schulden)
  * betrag:         Bruttorechnungsbetrag
  * bezahlt_betrag: bereits gezahlt (ggf. leer/0); offen = betrag - bezahlt_betrag
  * faelligkeit:    ISO-Datum; fehlt sie, wird rechnungsdatum + 14 Tage angenommen
  * skonto_prozent/skonto_tage: optional, nur Kreditoren (für Zahlungsvorschlag)

Aufruf:
    python3 offene_posten.py --datei rechnungen.csv [--stichtag 2026-09-03]

Mahnstufen und Skonto sind kaufmännische Konventionen, keine Rechtsberatung.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt

# Mahnstufen nach Überfälligkeit in Tagen (Konvention, anpassbar).
MAHNSTUFEN = [
    (0, "nicht fällig"),
    (1, "fällig"),
    (14, "Zahlungserinnerung"),
    (28, "1. Mahnung"),
    (42, "2. Mahnung"),
    (56, "3. Mahnung / Inkasso"),
]

AGING = [(0, "nicht fällig"), (1, "1–30 Tage"), (31, "31–60 Tage"),
         (61, "61–90 Tage"), (91, "über 90 Tage")]


def _num(s: str) -> float:
    s = (s or "").strip().replace(" ", "")
    if not s:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)


def _datum(s: str) -> dt.date | None:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Datum nicht lesbar: {s!r} (erwartet z. B. 2026-09-03)")


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        delim = ";" if sample.count(";") > sample.count(",") else ","
        return list(csv.DictReader(f, delimiter=delim))


def _stufe(tage_ueberfaellig: int) -> str:
    label = MAHNSTUFEN[0][1]
    for grenze, txt in MAHNSTUFEN:
        if tage_ueberfaellig >= grenze:
            label = txt
    return label


def _aging(tage_ueberfaellig: int) -> str:
    label = AGING[0][1]
    for grenze, txt in AGING:
        if tage_ueberfaellig >= grenze:
            label = txt
    return label


def lade_posten(path: str, stichtag: dt.date) -> list[dict]:
    posten = []
    for row in _read_csv(path):
        betrag = _num(row.get("betrag"))
        bezahlt = _num(row.get("bezahlt_betrag"))
        offen = round(betrag - bezahlt, 2)
        if offen <= 0.005:
            continue  # ausgeglichen -> kein offener Posten
        rgdat = _datum(row.get("rechnungsdatum"))
        faellig = _datum(row.get("faelligkeit"))
        if faellig is None and rgdat is not None:
            faellig = rgdat + dt.timedelta(days=14)
        ueberf = (stichtag - faellig).days if faellig else 0
        posten.append({
            "art": (row.get("art") or "").strip().lower(),
            "partner": (row.get("partner") or "").strip(),
            "beleg_nr": (row.get("beleg_nr") or "").strip(),
            "rechnungsdatum": rgdat,
            "faelligkeit": faellig,
            "offen": offen,
            "ueberfaellig": ueberf,
            "skonto_prozent": _num(row.get("skonto_prozent")),
            "skonto_tage": int(_num(row.get("skonto_tage"))),
            "rgdat": rgdat,
        })
    return posten


def _z(v: float) -> str:
    return f"{v:>12,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def druck_debitoren(posten: list[dict], stichtag: dt.date) -> str:
    deb = [p for p in posten if p["art"] == "debitor"]
    deb.sort(key=lambda p: -p["ueberfaellig"])
    lines = ["OFFENE POSTEN DEBITOREN (Kundenforderungen)", "=" * 78,
             f"{'Kunde':<22}{'Beleg':<12}{'fällig':<12}{'offen':>12}  {'Status'}"]
    summe = 0.0
    aging_summen: dict[str, float] = {}
    for p in deb:
        summe += p["offen"]
        stufe = _stufe(p["ueberfaellig"]) if p["ueberfaellig"] >= 1 else "nicht fällig"
        bucket = _aging(max(p["ueberfaellig"], 0))
        aging_summen[bucket] = aging_summen.get(bucket, 0.0) + p["offen"]
        fd = p["faelligkeit"].isoformat() if p["faelligkeit"] else "—"
        hinweis = f"{stufe} ({p['ueberfaellig']} T.)" if p["ueberfaellig"] >= 1 else stufe
        lines.append(f"{p['partner'][:21]:<22}{p['beleg_nr'][:11]:<12}{fd:<12}"
                     f"{p['offen']:>12.2f}  {hinweis}")
    lines.append("-" * 78)
    lines.append(f"{'Summe Forderungen':<46}{summe:>12.2f}")
    if aging_summen:
        lines.append("Fälligkeitsstruktur (Aging):")
        for _, bucket in AGING:
            if aging_summen.get(bucket):
                lines.append(f"  {bucket:<20}{aging_summen[bucket]:>12.2f}")
    return "\n".join(lines), summe


def druck_kreditoren(posten: list[dict], stichtag: dt.date) -> str:
    kred = [p for p in posten if p["art"] == "kreditor"]
    kred.sort(key=lambda p: (p["faelligkeit"] or dt.date.max))
    lines = ["OFFENE POSTEN KREDITOREN (Verbindlichkeiten) — Zahlungsvorschlag", "=" * 78,
             f"{'Lieferant':<20}{'Beleg':<11}{'fällig':<12}{'offen':>11}{'zahlen':>11}  Empfehlung"]
    summe = 0.0
    for p in kred:
        summe += p["offen"]
        fd = p["faelligkeit"].isoformat() if p["faelligkeit"] else "—"
        zahlbetrag = p["offen"]
        empfehlung = ""
        # Skonto-Prüfung
        if p["skonto_prozent"] > 0 and p["rgdat"]:
            skontofrist = p["rgdat"] + dt.timedelta(days=p["skonto_tage"])
            if stichtag <= skontofrist:
                zahlbetrag = round(p["offen"] * (1 - p["skonto_prozent"] / 100), 2)
                empfehlung = (f"JETZT zahlen — {p['skonto_prozent']:.1f}% Skonto "
                              f"bis {skontofrist.isoformat()}")
        if not empfehlung:
            if p["ueberfaellig"] >= 1:
                empfehlung = f"überfällig ({p['ueberfaellig']} T.) — sofort zahlen"
            elif p["faelligkeit"] and (p["faelligkeit"] - stichtag).days <= 7:
                empfehlung = "bald fällig"
            else:
                empfehlung = "planen"
        lines.append(f"{p['partner'][:19]:<20}{p['beleg_nr'][:10]:<11}{fd:<12}"
                     f"{p['offen']:>11.2f}{zahlbetrag:>11.2f}  {empfehlung}")
    lines.append("-" * 78)
    lines.append(f"{'Summe Verbindlichkeiten':<42}{summe:>11.2f}")
    return "\n".join(lines), summe


def _cli() -> None:
    p = argparse.ArgumentParser(description="Offene Posten, Mahnwesen, Zahlungsvorschlag")
    p.add_argument("--datei", required=True, help="Rechnungsliste (CSV)")
    p.add_argument("--stichtag", default=None, help="ISO-Datum; Default: heute")
    p.add_argument("--was", choices=("debitoren", "kreditoren", "alle"), default="alle")
    args = p.parse_args()

    stichtag = _datum(args.stichtag) if args.stichtag else dt.date.today()
    posten = lade_posten(args.datei, stichtag)

    blocks = [f"Stichtag: {stichtag.isoformat()}"]
    forderungen = verbindlichkeiten = 0.0
    if args.was in ("debitoren", "alle"):
        block, forderungen = druck_debitoren(posten, stichtag)
        blocks.append(block)
    if args.was in ("kreditoren", "alle"):
        block, verbindlichkeiten = druck_kreditoren(posten, stichtag)
        blocks.append(block)
    if args.was == "alle":
        saldo = forderungen - verbindlichkeiten
        blocks.append("ÜBERSICHT\n" + "=" * 40
                      + f"\n  Summe Forderungen (Debitoren)   {forderungen:>12.2f}"
                      + f"\n  Summe Verbindl. (Kreditoren)  ./.{verbindlichkeiten:>12.2f}"
                      + f"\n  Saldo (Netto-Position)          {saldo:>12.2f}")
    print("\n\n".join(blocks))


if __name__ == "__main__":
    _cli()

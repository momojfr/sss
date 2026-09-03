#!/usr/bin/env python3
"""Doppelte Buchführung — Journal → Saldenliste, GuV und Bilanz.

Liest ein Buchungsjournal (Soll/Haben) ein und erzeugt:
  * Saldenliste (je Konto Soll-, Haben-Summe und Saldo)
  * Gewinn- und Verlustrechnung (GuV) nach § 275 HGB — GKV oder UKV
  * Bilanz (Aktiva / Passiva) inkl. Jahresüberschuss im Eigenkapital

Es prüft die Grundregel der doppelten Buchführung: die Summe aller Soll-Buchungen
muss der Summe aller Haben-Buchungen entsprechen, und die Bilanzsumme der Aktiva
der der Passiva.

Eingaben
--------
--journal PATH   CSV mit Spalten: datum, soll, haben, betrag, text
                 (Trennzeichen ',' oder ';'; Betrag mit '.' oder ',' als Komma)
--konten PATH    optional; CSV mit: konto, name, typ[, gkv_posten, funktion]
                 typ ∈ aktiv|passiv|eigenkapital|ertrag|aufwand
                 Fehlt die Datei, wird die eingebaute SKR03-Standardzuordnung
                 (KONTEN unten) verwendet. Unbekannte Konten werden gemeldet,
                 nie stillschweigend eingeordnet.
--verfahren gkv|ukv   GuV-Gliederung (Default: gkv). UKV braucht je Aufwandskonto
                 eine 'funktion' (Herstellung|Vertrieb|Verwaltung) in --konten.
--was            saldenliste|guv|bilanz|alle (Default: alle)

Kein Ersatz für Steuerberatung. Für den verbindlichen Abschluss zertifizierte
Software/Fachkraft nutzen.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Eingebaute SKR03-Standardzuordnung: konto -> (name, typ, gkv_posten)
# typ: aktiv | passiv | eigenkapital | ertrag | aufwand
# gkv_posten (nur Erfolgskonten): GuV-Zeile im Gesamtkostenverfahren;
#            (Bestandskonten): Bilanzposten.
# ---------------------------------------------------------------------------
KONTEN: dict[str, tuple[str, str, str]] = {
    # Anlagevermögen (Aktiv)
    "0027": ("Immaterielle Vermögensgegenstände", "aktiv", "Immaterielle Vermögensgegenstände"),
    "0410": ("Betriebs- und Geschäftsausstattung", "aktiv", "Sachanlagen"),
    "0420": ("Büroeinrichtung / EDV", "aktiv", "Sachanlagen"),
    # Eigenkapital
    "0800": ("Eigenkapital / Gezeichnetes Kapital", "eigenkapital", "Eigenkapital"),
    # Finanz- und Privatkonten
    "1000": ("Kasse", "aktiv", "Kassenbestand, Bank"),
    "1200": ("Bank", "aktiv", "Kassenbestand, Bank"),
    "1400": ("Forderungen aus Lieferungen und Leistungen", "aktiv", "Forderungen aLuL"),
    "1571": ("Abziehbare Vorsteuer 7 %", "aktiv", "sonstige Vermögensgegenstände"),
    "1576": ("Abziehbare Vorsteuer 19 %", "aktiv", "sonstige Vermögensgegenstände"),
    "1600": ("Verbindlichkeiten aus Lieferungen und Leistungen", "passiv", "Verbindlichkeiten aLuL"),
    "1740": ("Verbindlichkeiten Lohn und Gehalt", "passiv", "sonstige Verbindlichkeiten"),
    "1741": ("Verbindlichkeiten Lohn-/Kirchensteuer", "passiv", "sonstige Verbindlichkeiten"),
    "1742": ("Verbindlichkeiten soziale Sicherheit", "passiv", "sonstige Verbindlichkeiten"),
    "1771": ("Umsatzsteuer 7 %", "passiv", "sonstige Verbindlichkeiten"),
    "1776": ("Umsatzsteuer 19 %", "passiv", "sonstige Verbindlichkeiten"),
    "1780": ("Umsatzsteuer-Vorauszahlungen", "passiv", "sonstige Verbindlichkeiten"),
    "1800": ("Privatentnahme", "eigenkapital", "Eigenkapital"),
    "1890": ("Privateinlage", "eigenkapital", "Eigenkapital"),
    # Wareneingang / Fremdleistungen (Aufwand)
    "3100": ("Fremdleistungen", "aufwand", "Materialaufwand"),
    "3200": ("Wareneingang", "aufwand", "Materialaufwand"),
    # Betriebliche Aufwendungen
    "4110": ("Löhne", "aufwand", "Personalaufwand"),
    "4120": ("Gehälter", "aufwand", "Personalaufwand"),
    "4130": ("Gesetzliche soziale Aufwendungen", "aufwand", "Personalaufwand"),
    "4210": ("Miete", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4240": ("Gas, Strom, Wasser", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4600": ("Werbekosten", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4650": ("Bewirtungskosten", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4830": ("Abschreibungen auf Sachanlagen", "aufwand", "Abschreibungen"),
    "4910": ("Porto", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4920": ("Telefon / Internet", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4930": ("Bürobedarf", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4940": ("Software / Lizenzen", "aufwand", "sonstige betriebliche Aufwendungen"),
    "4970": ("Nebenkosten des Geldverkehrs", "aufwand", "sonstige betriebliche Aufwendungen"),
    # Zinsen (Finanzergebnis)
    "2100": ("Zinsaufwendungen", "aufwand", "Zinsen und ähnliche Aufwendungen"),
    "2650": ("Zinserträge", "ertrag", "Zinsen und ähnliche Erträge"),
    # Erlöse (Ertrag)
    "8300": ("Erlöse 7 % USt", "ertrag", "Umsatzerlöse"),
    "8400": ("Erlöse 19 % USt", "ertrag", "Umsatzerlöse"),
    "8500": ("Sonstige betriebliche Erträge", "ertrag", "sonstige betriebliche Erträge"),
}

# Reihenfolge der GuV-Posten im Gesamtkostenverfahren (§ 275 Abs. 2 HGB).
GKV_ERTRAG = ["Umsatzerlöse", "sonstige betriebliche Erträge", "Zinsen und ähnliche Erträge"]
GKV_AUFWAND = ["Materialaufwand", "Personalaufwand", "Abschreibungen",
               "sonstige betriebliche Aufwendungen", "Zinsen und ähnliche Aufwendungen",
               "Steuern vom Einkommen und Ertrag"]

# Reihenfolge der Bilanzposten.
AKTIVA_ORDER = ["Immaterielle Vermögensgegenstände", "Sachanlagen", "Forderungen aLuL",
                "sonstige Vermögensgegenstände", "Kassenbestand, Bank"]
PASSIVA_ORDER = ["Eigenkapital", "Verbindlichkeiten aLuL", "sonstige Verbindlichkeiten"]


@dataclass
class Konto:
    name: str
    typ: str
    posten: str
    funktion: str = ""


def _num(s: str) -> float:
    """Betrag mit '.' oder ',' als Dezimaltrenner nach float."""
    s = s.strip().replace(" ", "")
    if "," in s and "." in s:          # 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                      # 1234,56 -> 1234.56
        s = s.replace(",", ".")
    return float(s)


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        delim = ";" if sample.count(";") > sample.count(",") else ","
        return [row for row in csv.DictReader(f, delimiter=delim)]


def lade_konten(path: str | None) -> dict[str, Konto]:
    """Eingebaute SKR03-Zuordnung; --konten überlagert sie feldweise.

    So genügt es, in --konten z. B. nur die 'funktion' für das UKV zu ergänzen;
    Name/Typ/Posten bleiben aus der Standardzuordnung erhalten. Neue Konten
    brauchen mindestens 'typ'.
    """
    konten = {k: Konto(n, t, p) for k, (n, t, p) in KONTEN.items()}
    if path is None:
        return konten
    for row in _read_csv(path):
        k = row["konto"].strip()
        vorh = konten.get(k)
        konten[k] = Konto(
            name=(row.get("name") or (vorh.name if vorh else k)).strip(),
            typ=(row.get("typ") or (vorh.typ if vorh else "")).strip().lower(),
            posten=(row.get("gkv_posten") or (vorh.posten if vorh else "")).strip(),
            funktion=(row.get("funktion") or (vorh.funktion if vorh else "")).strip(),
        )
    return konten


def lade_journal(path: str) -> list[dict]:
    buchungen = []
    for i, row in enumerate(_read_csv(path), start=1):
        buchungen.append({
            "nr": i,
            "datum": row.get("datum", "").strip(),
            "soll": row["soll"].strip(),
            "haben": row["haben"].strip(),
            "betrag": _num(row["betrag"]),
            "text": row.get("text", "").strip(),
        })
    return buchungen


# ---------------------------------------------------------------------------
# Auswertung
# ---------------------------------------------------------------------------
def salden(buchungen: list[dict]) -> tuple[dict[str, float], dict[str, float]]:
    soll = defaultdict(float)
    haben = defaultdict(float)
    for b in buchungen:
        soll[b["soll"]] += b["betrag"]
        haben[b["haben"]] += b["betrag"]
    return dict(soll), dict(haben)


def pruefe_konten(buchungen: list[dict], konten: dict[str, Konto]) -> list[str]:
    verwendet = {b["soll"] for b in buchungen} | {b["haben"] for b in buchungen}
    return sorted(k for k in verwendet if k not in konten)


def _saldo(konto: str, soll: dict, haben: dict) -> float:
    return soll.get(konto, 0.0) - haben.get(konto, 0.0)  # >0 = Sollsaldo


def guv_gkv(soll, haben, konten) -> dict:
    ertrag = defaultdict(float)
    aufwand = defaultdict(float)
    for k, konto in konten.items():
        s = _saldo(k, soll, haben)
        if konto.typ == "ertrag":
            ertrag[konto.posten] += -s          # Habensaldo
        elif konto.typ == "aufwand":
            aufwand[konto.posten] += s           # Sollsaldo
    summe_ertrag = sum(ertrag.values())
    summe_aufwand = sum(aufwand.values())
    return {"ertrag": dict(ertrag), "aufwand": dict(aufwand),
            "jahresueberschuss": round(summe_ertrag - summe_aufwand, 2)}


def guv_ukv(soll, haben, konten) -> dict:
    """Umsatzkostenverfahren — braucht 'funktion' je Aufwandskonto."""
    fehlend = [k for k, ko in konten.items()
               if ko.typ == "aufwand" and _saldo(k, soll, haben) != 0
               and not ko.funktion]
    if fehlend:
        return {"fehler": "UKV nicht möglich: es fehlt die 'funktion' "
                          f"(Herstellung/Vertrieb/Verwaltung) für Konten: "
                          f"{', '.join(sorted(fehlend))}. In --konten ergänzen "
                          f"oder --verfahren gkv nutzen."}
    umsatz = 0.0
    funktionen = defaultdict(float)
    sonstige_ertrag = 0.0
    for k, konto in konten.items():
        s = _saldo(k, soll, haben)
        if konto.typ == "ertrag":
            if konto.posten == "Umsatzerlöse":
                umsatz += -s
            else:
                sonstige_ertrag += -s
        elif konto.typ == "aufwand":
            funktionen[konto.funktion.capitalize()] += s
    jü = umsatz - sum(funktionen.values()) + sonstige_ertrag
    return {"umsatzerloese": round(umsatz, 2), "funktionen": dict(funktionen),
            "sonstige_ertraege": round(sonstige_ertrag, 2),
            "jahresueberschuss": round(jü, 2)}


def bilanz(soll, haben, konten, jahresueberschuss: float) -> dict:
    aktiva = defaultdict(float)
    passiva = defaultdict(float)
    for k, konto in konten.items():
        s = _saldo(k, soll, haben)
        if konto.typ == "aktiv":
            aktiva[konto.posten] += s
        elif konto.typ == "passiv":
            passiva[konto.posten] += -s
        elif konto.typ == "eigenkapital":
            passiva["Eigenkapital"] += -s
    passiva["Eigenkapital"] += jahresueberschuss  # Jahresergebnis ins EK
    return {"aktiva": dict(aktiva), "passiva": dict(passiva),
            "summe_aktiva": round(sum(aktiva.values()), 2),
            "summe_passiva": round(sum(passiva.values()), 2)}


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------
def _z(v: float) -> str:
    return f"{v:>14,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def druck_saldenliste(soll, haben, konten) -> str:
    lines = ["Saldenliste", "=" * 60,
             f"{'Konto':<6}{'Bezeichnung':<34}{'Soll':>10}{'Haben':>10}"]
    alle = sorted(set(soll) | set(haben))
    ts = th = 0.0
    for k in alle:
        s, h = soll.get(k, 0.0), haben.get(k, 0.0)
        ts += s; th += h
        name = konten[k].name if k in konten else "(unbekannt)"
        lines.append(f"{k:<6}{name[:33]:<34}{s:>10.2f}{h:>10.2f}")
    lines.append("-" * 60)
    lines.append(f"{'Summe':<40}{ts:>10.2f}{th:>10.2f}")
    lines.append(f"Kontrolle Soll = Haben: "
                 + ("OK" if abs(ts - th) < 0.005 else f"FEHLER Differenz {ts-th:.2f}"))
    return "\n".join(lines)


def druck_guv_gkv(g: dict) -> str:
    lines = ["Gewinn- und Verlustrechnung (Gesamtkostenverfahren, § 275 HGB)",
             "=" * 60]
    for p in GKV_ERTRAG:
        if g["ertrag"].get(p):
            lines.append(f"  {p:<44}{_z(g['ertrag'][p])}")
    for p in GKV_AUFWAND:
        if g["aufwand"].get(p):
            lines.append(f"  ./. {p:<40}{_z(-g['aufwand'][p])}")
    lines.append("-" * 60)
    jü = g["jahresueberschuss"]
    label = "Jahresüberschuss" if jü >= 0 else "Jahresfehlbetrag"
    lines.append(f"  {label:<44}{_z(jü)}")
    return "\n".join(lines)


def druck_guv_ukv(g: dict) -> str:
    if "fehler" in g:
        return "Gewinn- und Verlustrechnung (Umsatzkostenverfahren)\n" + "=" * 60 + \
               "\n  " + g["fehler"]
    lines = ["Gewinn- und Verlustrechnung (Umsatzkostenverfahren, § 275 HGB)",
             "=" * 60, f"  {'Umsatzerlöse':<44}{_z(g['umsatzerloese'])}"]
    for f in ("Herstellung", "Vertrieb", "Verwaltung"):
        if g["funktionen"].get(f):
            lines.append(f"  ./. Kosten {f:<34}{_z(-g['funktionen'][f])}")
    if g["sonstige_ertraege"]:
        lines.append(f"  {'sonstige betriebliche Erträge':<44}{_z(g['sonstige_ertraege'])}")
    lines.append("-" * 60)
    jü = g["jahresueberschuss"]
    label = "Jahresüberschuss" if jü >= 0 else "Jahresfehlbetrag"
    lines.append(f"  {label:<44}{_z(jü)}")
    return "\n".join(lines)


def druck_bilanz(b: dict) -> str:
    lines = ["Bilanz", "=" * 60, f"{'AKTIVA':<30}{'PASSIVA':>30}"]
    ak = [(p, b["aktiva"][p]) for p in AKTIVA_ORDER if b["aktiva"].get(p)]
    pa = [(p, b["passiva"][p]) for p in PASSIVA_ORDER if b["passiva"].get(p)]
    for i in range(max(len(ak), len(pa))):
        la = f"{ak[i][0][:20]:<20}{ak[i][1]:>10.2f}" if i < len(ak) else " " * 30
        lp = f"{pa[i][0][:20]:<20}{pa[i][1]:>10.2f}" if i < len(pa) else ""
        lines.append(f"{la}   {lp}")
    lines.append("-" * 60)
    lines.append(f"{'Summe Aktiva':<20}{b['summe_aktiva']:>10.2f}   "
                 f"{'Summe Passiva':<20}{b['summe_passiva']:>10.2f}")
    diff = b["summe_aktiva"] - b["summe_passiva"]
    lines.append("Kontrolle Aktiva = Passiva: "
                 + ("OK" if abs(diff) < 0.005 else f"FEHLER Differenz {diff:.2f}"))
    return "\n".join(lines)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Doppelte Buchführung: Journal -> GuV/Bilanz")
    p.add_argument("--journal", required=True)
    p.add_argument("--konten", default=None)
    p.add_argument("--verfahren", choices=("gkv", "ukv"), default="gkv")
    p.add_argument("--was", choices=("saldenliste", "guv", "bilanz", "alle"), default="alle")
    args = p.parse_args()

    konten = lade_konten(args.konten)
    buchungen = lade_journal(args.journal)

    unbekannt = pruefe_konten(buchungen, konten)
    if unbekannt:
        print("FEHLER: unbekannte Konten im Journal (in --konten ergänzen): "
              + ", ".join(unbekannt), file=sys.stderr)
        raise SystemExit(2)

    soll, haben = salden(buchungen)
    g = guv_ukv(soll, haben, konten) if args.verfahren == "ukv" \
        else guv_gkv(soll, haben, konten)
    jü = g.get("jahresueberschuss", 0.0)

    blocks = []
    if args.was in ("saldenliste", "alle"):
        blocks.append(druck_saldenliste(soll, haben, konten))
    if args.was in ("guv", "alle"):
        blocks.append(druck_guv_ukv(g) if args.verfahren == "ukv"
                      else druck_guv_gkv(g))
    if args.was in ("bilanz", "alle"):
        blocks.append(druck_bilanz(bilanz(soll, haben, konten, jü)))
    print("\n\n".join(blocks))


if __name__ == "__main__":
    _cli()

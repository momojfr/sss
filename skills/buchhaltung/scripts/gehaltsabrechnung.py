#!/usr/bin/env python3
"""Gehaltsabrechnung Deutschland — Brutto -> Netto (Stand 2026).

Beide Teile sind exakt:

  * SOZIALVERSICHERUNG — feste Beitragssätze und Beitragsbemessungsgrenzen 2026,
    hälftig geteilt (mit Sonderregeln für Kinderlose, Kinder und Sachsen).

  * LOHNSTEUER — über das Modul ``lohnsteuer_2026`` berechnet, das den amtlichen
    BMF-Programmablaufplan 2026 (§ 39b EStG) umsetzt und per Selbsttest gegen die
    amtlichen Prüftabellen verifiziert ist (``python3 lohnsteuer_2026.py
    --selftest``). Abgedeckt ist der laufende Arbeitslohn der Steuerklassen I–VI;
    Sonderfälle (Versorgungsbezüge, sonstige Bezüge, Faktorverfahren, ELStAM-
    Freibeträge) sind dort noch nicht abgebildet.

Aufruf (Beispiel):
    python3 gehaltsabrechnung.py --brutto 4000 --steuerklasse 1 \
        --kv-zusatz 2.9 --kinder 0 --bundesland NW --konfession keine

Alle Beträge in Euro. Keine Gewähr — kein Ersatz für Lohnsoftware/Steuerberatung.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lohnsteuer_2026 import lohnsteuer_lzz

JAHR = 2026

# ---------------------------------------------------------------------------
# SOZIALVERSICHERUNG — Sätze & Grenzen 2026 (exakt)
# ---------------------------------------------------------------------------
RV_SATZ = 18.6          # Rentenversicherung
AV_SATZ = 2.6           # Arbeitslosenversicherung
KV_SATZ = 14.6          # Krankenversicherung, allgemeiner Beitragssatz
KV_ZUSATZ_DURCHSCHNITT = 2.9   # durchschnittl. Zusatzbeitrag 2026 (kassenindividuell!)
PV_SATZ = 3.6           # Pflegeversicherung, Grundsatz
PV_KINDERLOS_ZUSCHLAG = 0.6    # Zuschlag kinderlose AN ab 23 J. (allein AN)
PV_KIND_ABSCHLAG = 0.25        # je Kind ab dem 2. bis 5. Kind (unter 25 J.)

BBG_KV_PV_MONAT = 5812.50      # KV + PV
BBG_RV_AV_MONAT = 8450.00      # RV + AV


@dataclass
class SVErgebnis:
    kv_an: float
    kv_ag: float
    pv_an: float
    pv_ag: float
    rv_an: float
    rv_ag: float
    av_an: float
    av_ag: float

    @property
    def an_summe(self) -> float:
        return self.kv_an + self.pv_an + self.rv_an + self.av_an

    @property
    def ag_summe(self) -> float:
        return self.kv_ag + self.pv_ag + self.rv_ag + self.av_ag


def _pv_saetze(kinderlos: bool, kinder: int, bundesland: str) -> tuple[float, float]:
    """AN- und AG-Satz der Pflegeversicherung in Prozent (Sonderregeln 2026)."""
    an = PV_SATZ / 2
    ag = PV_SATZ / 2
    if bundesland.upper() in {"SN", "SACHSEN"}:  # AN trägt 0,5 Punkte mehr
        an += 0.5
        ag -= 0.5
    if kinderlos:
        an += PV_KINDERLOS_ZUSCHLAG
    elif kinder >= 2:
        an -= PV_KIND_ABSCHLAG * min(kinder - 1, 4)
    return an, ag


def berechne_sv(brutto_monat: float, *, kv_zusatz: float = KV_ZUSATZ_DURCHSCHNITT,
                kinderlos: bool = True, kinder: int = 0,
                bundesland: str = "NW") -> SVErgebnis:
    """Exakte SV-Beiträge (Arbeitnehmer pflichtversichert, Regelfall)."""
    bg_kvpv = min(brutto_monat, BBG_KV_PV_MONAT)
    bg_rvav = min(brutto_monat, BBG_RV_AV_MONAT)

    kv_an_satz = KV_SATZ / 2 + kv_zusatz / 2
    kv_ag_satz = KV_SATZ / 2 + kv_zusatz / 2
    pv_an_satz, pv_ag_satz = _pv_saetze(kinderlos, kinder, bundesland)

    r = lambda x: round(x, 2)
    return SVErgebnis(
        kv_an=r(bg_kvpv * kv_an_satz / 100), kv_ag=r(bg_kvpv * kv_ag_satz / 100),
        pv_an=r(bg_kvpv * pv_an_satz / 100), pv_ag=r(bg_kvpv * pv_ag_satz / 100),
        rv_an=r(bg_rvav * (RV_SATZ / 2) / 100), rv_ag=r(bg_rvav * (RV_SATZ / 2) / 100),
        av_an=r(bg_rvav * (AV_SATZ / 2) / 100), av_ag=r(bg_rvav * (AV_SATZ / 2) / 100),
    )


# ---------------------------------------------------------------------------
# Gesamtabrechnung
# ---------------------------------------------------------------------------
def _kist_satz(konfession: str, bundesland: str) -> float:
    if konfession.lower() in {"rk", "ev", "katholisch", "evangelisch", "kirche"}:
        return 0.08 if bundesland.upper() in {"BY", "BW"} else 0.09
    return 0.0


def abrechnung(brutto_monat: float, *, steuerklasse: int = 1,
               kv_zusatz: float = KV_ZUSATZ_DURCHSCHNITT, kinderlos: bool = True,
               kinder: int = 0, bundesland: str = "NW", konfession: str = "keine",
               zkf: float = 0.0) -> dict:
    sv = berechne_sv(brutto_monat, kv_zusatz=kv_zusatz, kinderlos=kinderlos,
                     kinder=kinder, bundesland=bundesland)

    kist_satz = _kist_satz(konfession, bundesland)
    steuer = lohnsteuer_lzz(
        brutto_monat, lzz=2, kirchensteuer_satz=kist_satz,
        steuerklasse=steuerklasse, kvz=kv_zusatz, kinderlos=kinderlos,
        kinder=kinder, sachsen=bundesland.upper() in {"SN", "SACHSEN"},
        zkf=zkf, religion=kist_satz > 0,
    )

    abzuege_an = (steuer["lohnsteuer"] + steuer["soli"] + steuer["kirchensteuer"]
                  + sv.an_summe)
    netto = round(brutto_monat - abzuege_an, 2)
    ag_brutto = round(brutto_monat + sv.ag_summe, 2)  # ohne Umlagen U1/U2/U3, UV

    return {"brutto": brutto_monat, "sv": sv, "steuer": steuer,
            "netto": netto, "ag_brutto": ag_brutto}


def formatiere(res: dict, name: str = "") -> str:
    sv: SVErgebnis = res["sv"]
    st = res["steuer"]
    z = lambda v: f"{v:>10.2f}"
    kopf = f"Gehaltsabrechnung {JAHR}" + (f" — {name}" if name else "")
    lines = [
        kopf,
        "=" * len(kopf),
        f"Bruttolohn                 {z(res['brutto'])}",
        "-" * 40,
        "Gesetzliche Abzüge (Arbeitnehmer)",
        f"  Lohnsteuer               {z(-st['lohnsteuer'])}",
        f"  Solidaritätszuschlag     {z(-st['soli'])}",
        f"  Kirchensteuer            {z(-st['kirchensteuer'])}",
        f"  Krankenversicherung      {z(-sv.kv_an)}",
        f"  Pflegeversicherung       {z(-sv.pv_an)}",
        f"  Rentenversicherung       {z(-sv.rv_an)}",
        f"  Arbeitslosenvers.        {z(-sv.av_an)}",
        "-" * 40,
        f"Nettoverdienst             {z(res['netto'])}",
        "",
        f"Arbeitgeberanteil SV       {z(sv.ag_summe)}",
        f"Arbeitgeber-Brutto *       {z(res['ag_brutto'])}",
        "",
        "Lohnsteuer nach amtlichem BMF-Programmablaufplan 2026 (§ 39b EStG).",
        "* ohne Umlagen U1/U2/Insolvenzgeld und gesetzliche Unfallversicherung.",
    ]
    return "\n".join(lines)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Gehaltsabrechnung DE (Brutto->Netto)")
    p.add_argument("--brutto", type=float, required=True, help="Monatsbrutto in Euro")
    p.add_argument("--steuerklasse", type=int, default=1, choices=range(1, 7))
    p.add_argument("--kv-zusatz", type=float, default=KV_ZUSATZ_DURCHSCHNITT,
                   help="KV-Zusatzbeitrag der Kasse in %% (Default: Durchschnitt 2,9)")
    p.add_argument("--kinder", type=int, default=0)
    p.add_argument("--kinderlos", action="store_true",
                   help="AN ist kinderlos (>=23 J.) -> PV-Zuschlag")
    p.add_argument("--zkf", type=float, default=0.0,
                   help="Zahl der Kinderfreibeträge (für Soli/KiSt)")
    p.add_argument("--bundesland", default="NW", help="z. B. NW, BY, BW, SN")
    p.add_argument("--konfession", default="keine",
                   help="keine | ev | rk (für Kirchensteuer)")
    p.add_argument("--name", default="")
    args = p.parse_args()

    kinderlos = args.kinderlos or args.kinder == 0
    res = abrechnung(args.brutto, steuerklasse=args.steuerklasse,
                     kv_zusatz=args.kv_zusatz, kinderlos=kinderlos,
                     kinder=args.kinder, bundesland=args.bundesland,
                     konfession=args.konfession, zkf=args.zkf)
    print(formatiere(res, args.name))


if __name__ == "__main__":
    _cli()

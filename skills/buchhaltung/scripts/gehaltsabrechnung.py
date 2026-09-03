#!/usr/bin/env python3
"""Gehaltsabrechnung Deutschland — Brutto -> Netto (Stand 2026).

Zwei Genauigkeitsstufen, bewusst getrennt gehalten:

  * SOZIALVERSICHERUNG  -> exakt. Feste Beitragssätze und
    Beitragsbemessungsgrenzen, hälftig geteilt (mit Sonderfällen).

  * LOHNSTEUER          -> NÄHERUNG. Nachbildung des Einkommensteuer-Tarifs
    nach § 32a EStG plus vereinfachte Vorsorgepauschale. Sie ersetzt NICHT den
    amtlichen "Programmablaufplan für die maschinelle Lohnsteuerberechnung"
    (PAP) des BMF. Die Werte weichen um einige Euro ab, weil die exakten
    Rundungsschritte, die Mindestvorsorgepauschale und die Formeln für die
    Steuerklassen V/VI hier nur vereinfacht abgebildet sind.

    => Sobald die BMF-PAP-2026-PDF (Anlage 1) vorliegt, sollte der Block
       "LOHNSTEUER (NÄHERUNG)" durch die exakte PAP-Umsetzung ersetzt werden.
       Die §32a-Tarifparameter für 2026 sind unten als VORLÄUFIG markiert und
       vor dem produktiven Einsatz gegen § 32a EStG 2026 / den PAP zu prüfen.

Aufruf (Beispiel):
    python3 gehaltsabrechnung.py --brutto 4000 --steuerklasse 1 \
        --kv-zusatz 2.9 --kinder 0 --bundesland NW --konfession keine

Alle Beträge in Euro. Keine Gewähr — kein Ersatz für Lohnsoftware/Steuerberatung.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# SOZIALVERSICHERUNG — Sätze & Grenzen 2026 (exakt)
# ---------------------------------------------------------------------------
JAHR = 2026

# Beitragssätze (gesamt, in Prozent)
RV_SATZ = 18.6          # Rentenversicherung
AV_SATZ = 2.6           # Arbeitslosenversicherung
KV_SATZ = 14.6          # Krankenversicherung, allgemeiner Beitragssatz
KV_ZUSATZ_DURCHSCHNITT = 2.9   # durchschnittl. Zusatzbeitrag 2026 (kassenindividuell!)
PV_SATZ = 3.6           # Pflegeversicherung, Grundsatz
PV_KINDERLOS_ZUSCHLAG = 0.6    # Zuschlag kinderlose AN ab 23 J. (allein AN)
PV_KIND_ABSCHLAG = 0.25        # je Kind ab dem 2. bis 5. Kind (unter 25 J.)

# Beitragsbemessungsgrenzen (monatlich)
BBG_KV_PV_MONAT = 5812.50      # KV + PV
BBG_RV_AV_MONAT = 8450.00      # RV + AV

# Sachsen trägt bei der PV einen anderen AN/AG-Split (Buß- und Bettag).
# Grundsatz bundesweit: hälftig. Sachsen: AN + 0,5 Punkte, AG - 0,5 Punkte.


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
    # Sachsen: AN trägt 0,5 Punkte mehr, AG 0,5 Punkte weniger.
    if bundesland.upper() in {"SN", "SACHSEN"}:
        an += 0.5
        ag -= 0.5
    # Kinderlosenzuschlag: allein vom AN.
    if kinderlos:
        an += PV_KINDERLOS_ZUSCHLAG
    # Abschläge ab dem 2. Kind (bis 5.), je 0,25 Punkte, nur AN-seitig.
    elif kinder >= 2:
        an -= PV_KIND_ABSCHLAG * min(kinder - 1, 4)
    return an, ag


def berechne_sv(brutto_monat: float, *, kv_zusatz: float = KV_ZUSATZ_DURCHSCHNITT,
                kinderlos: bool = True, kinder: int = 0,
                bundesland: str = "NW") -> SVErgebnis:
    """Exakte SV-Beiträge (Arbeitnehmer nur pflichtversichert, Regelfall)."""
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
# LOHNSTEUER (NÄHERUNG) — § 32a-Tarif + vereinfachte Vorsorgepauschale
# ---------------------------------------------------------------------------
# Arbeitnehmer-Pauschbetrag (Werbungskosten) und Sonderausgaben-Pauschbetrag.
ARBEITNEHMER_PAUSCHBETRAG = 1230.0
SONDERAUSGABEN_PAUSCHBETRAG = 36.0
ENTLASTUNGSBETRAG_ALLEINERZ = 4260.0      # StKl II, 1. Kind
ENTLASTUNGSBETRAG_JE_WEITERES = 240.0     # je weiteres Kind


@dataclass
class Tarif:
    """Parameter des § 32a-Einkommensteuertarifs (Jahreswerte)."""
    jahr: int
    grundfreibetrag: int
    eckwert1: int      # Ende der 1. Progressionszone
    eckwert2: int      # Ende der 2. Progressionszone / Beginn 42 %
    eckwert3: int      # Beginn 45 % (Reichensteuer)
    a1: float; b1: float                 # Zone 2: (a1*y + b1)*y
    a2: float; b2: float; c2: float      # Zone 3: (a2*z + b2)*z + c2
    m42: float; n42: float               # Zone 4: m42*x - n42
    m45: float; n45: float               # Zone 5: m45*x - n45

    def est(self, zve: float) -> float:
        """Einkommensteuer auf ein zu versteuerndes Einkommen (Jahr)."""
        x = int(zve)  # auf volle Euro abgerundet
        if x <= self.grundfreibetrag:
            return 0.0
        if x <= self.eckwert1:
            y = (x - self.grundfreibetrag) / 10000
            return _floor_euro((self.a1 * y + self.b1) * y)
        if x <= self.eckwert2:
            z = (x - self.eckwert1) / 10000
            return _floor_euro((self.a2 * z + self.b2) * z + self.c2)
        if x <= self.eckwert3:
            return _floor_euro(self.m42 * x - self.n42)
        return _floor_euro(self.m45 * x - self.n45)


def _floor_euro(x: float) -> float:
    return float(int(x))  # der Steuerbetrag wird auf volle Euro abgerundet


# 2025 — VALIDIERT (§ 32a EStG 2025). Als Referenz/Fallback nutzbar.
TARIF_2025 = Tarif(
    jahr=2025, grundfreibetrag=12096, eckwert1=17443, eckwert2=68480, eckwert3=277825,
    a1=932.30, b1=1400.0,
    a2=176.64, b2=2397.0, c2=1015.13,
    m42=0.42, n42=10911.92,
    m45=0.45, n45=19246.67,
)

# 2026 — VORLÄUFIG. Grundfreibetrag 12.348 € ist gesichert; die Eckwerte und
# Koeffizienten sind eine Schätzung auf Basis der Fortschreibung 2025 und MÜSSEN
# gegen § 32a EStG 2026 / den BMF-PAP 2026 geprüft werden, bevor damit
# verbindlich abgerechnet wird.
TARIF_2026 = Tarif(
    jahr=2026, grundfreibetrag=12348, eckwert1=17799, eckwert2=69878, eckwert3=277825,
    a1=914.51, b1=1400.0,
    a2=173.10, b2=2397.0, c2=1034.87,
    m42=0.42, n42=11232.34,
    m45=0.45, n45=19561.09,
)

TARIF_UNSICHER = True  # solange TARIF_2026 nicht gegen den PAP geprüft ist


def vorsorgepauschale(jahresbrutto: float, *, kv_zusatz: float, pv_an_satz: float,
                      steuerklasse: int) -> float:
    """Vereinfachte Vorsorgepauschale (§ 39b Abs. 2 Satz 5 Nr. 3 EStG).

    Teilbetrag RV: seit 2023 zu 100 % ansetzbar (AN-Anteil).
    Teilbetrag KV/PV: tatsächlicher AN-Anteil, gedeckelt über die BBG.
    Die Mindestvorsorgepauschale ist hier vereinfacht ausgelassen -> Näherung.
    """
    bg_rv = min(jahresbrutto, BBG_RV_AV_MONAT * 12)
    bg_kv = min(jahresbrutto, BBG_KV_PV_MONAT * 12)
    teil_rv = bg_rv * (RV_SATZ / 2) / 100
    kv_an_satz = KV_SATZ / 2 + kv_zusatz / 2
    teil_kvpv = bg_kv * (kv_an_satz + pv_an_satz) / 100
    return teil_rv + teil_kvpv


def lohnsteuer_monat(brutto_monat: float, *, steuerklasse: int, kv_zusatz: float,
                     kinderlos: bool, kinder: int, bundesland: str,
                     konfession: str, tarif: Tarif) -> dict:
    """Monatliche Lohnsteuer, Soli und Kirchensteuer (NÄHERUNG)."""
    jahresbrutto = brutto_monat * 12
    pv_an_satz, _ = _pv_saetze(kinderlos, kinder, bundesland)

    vsp = vorsorgepauschale(jahresbrutto, kv_zusatz=kv_zusatz,
                            pv_an_satz=pv_an_satz, steuerklasse=steuerklasse)

    abzuege = ARBEITNEHMER_PAUSCHBETRAG + SONDERAUSGABEN_PAUSCHBETRAG + vsp
    if steuerklasse == 2:
        abzuege += ENTLASTUNGSBETRAG_ALLEINERZ + \
            ENTLASTUNGSBETRAG_JE_WEITERES * max(kinder - 1, 0)

    zve = max(jahresbrutto - abzuege, 0)

    if steuerklasse == 3:
        # Splitting: Steuer = 2 x ESt(halbes zvE)
        est_jahr = 2 * tarif.est(zve / 2)
    elif steuerklasse in (5, 6):
        # V/VI: kein Grundfreibetrag; PAP nutzt ein Vergleichsverfahren.
        # Hier grobe Näherung -> als PRÜFEN behandeln.
        est_jahr = tarif.est(zve + tarif.grundfreibetrag)
    else:  # I, II, IV
        est_jahr = tarif.est(zve)

    lst_jahr = _floor_euro(est_jahr)
    lst_monat = round(lst_jahr / 12, 2)

    # Solidaritätszuschlag: 5,5 % der Lohnsteuer, aber erst oberhalb der
    # Freigrenze -> für die meisten Arbeitnehmer 0. Vereinfacht: nur bei sehr
    # hoher Jahres-LSt (Näherung, Milderungszone ausgelassen).
    freigrenze_jahr = 39900 if steuerklasse == 3 else 19950
    soli_jahr = 0.055 * lst_jahr if lst_jahr > freigrenze_jahr else 0.0
    soli_monat = round(soli_jahr / 12, 2)

    # Kirchensteuer: 8 % (BY, BW) bzw. 9 % der Lohnsteuer.
    kist_satz = 0.0
    if konfession.lower() in {"rk", "ev", "katholisch", "evangelisch", "kirche"}:
        kist_satz = 0.08 if bundesland.upper() in {"BY", "BW"} else 0.09
    kist_monat = round(kist_satz * lst_monat, 2)

    return {
        "lohnsteuer": lst_monat,
        "soli": soli_monat,
        "kirchensteuer": kist_monat,
        "vorsorgepauschale_jahr": round(vsp, 2),
        "zve_jahr": round(zve, 2),
    }


# ---------------------------------------------------------------------------
# Gesamtabrechnung
# ---------------------------------------------------------------------------
def abrechnung(brutto_monat: float, *, steuerklasse: int = 1,
               kv_zusatz: float = KV_ZUSATZ_DURCHSCHNITT, kinderlos: bool = True,
               kinder: int = 0, bundesland: str = "NW", konfession: str = "keine",
               tarif: Tarif = TARIF_2026) -> dict:
    sv = berechne_sv(brutto_monat, kv_zusatz=kv_zusatz, kinderlos=kinderlos,
                     kinder=kinder, bundesland=bundesland)
    steuer = lohnsteuer_monat(brutto_monat, steuerklasse=steuerklasse,
                              kv_zusatz=kv_zusatz, kinderlos=kinderlos,
                              kinder=kinder, bundesland=bundesland,
                              konfession=konfession, tarif=tarif)

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
        f"  Lohnsteuer *             {z(-st['lohnsteuer'])}",
        f"  Solidaritätszuschlag *   {z(-st['soli'])}",
        f"  Kirchensteuer *          {z(-st['kirchensteuer'])}",
        f"  Krankenversicherung      {z(-sv.kv_an)}",
        f"  Pflegeversicherung       {z(-sv.pv_an)}",
        f"  Rentenversicherung       {z(-sv.rv_an)}",
        f"  Arbeitslosenvers.        {z(-sv.av_an)}",
        "-" * 40,
        f"Nettoverdienst             {z(res['netto'])}",
        "",
        f"Arbeitgeberanteil SV       {z(sv.ag_summe)}",
        f"Arbeitgeber-Brutto **      {z(res['ag_brutto'])}",
        "",
        "* Lohnsteuer/Soli/KiSt = NÄHERUNG (nicht amtlicher PAP). Bitte prüfen.",
        "** ohne Umlagen U1/U2/Insolvenzgeld und gesetzliche Unfallversicherung.",
    ]
    if TARIF_UNSICHER:
        lines.append("! §32a-Tarif 2026 ist VORLÄUFIG — gegen BMF-PAP 2026 verifizieren.")
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
    p.add_argument("--bundesland", default="NW", help="z. B. NW, BY, BW, SN")
    p.add_argument("--konfession", default="keine",
                   help="keine | ev | rk (für Kirchensteuer)")
    p.add_argument("--name", default="")
    p.add_argument("--jahr", type=int, default=2026, choices=(2025, 2026))
    args = p.parse_args()

    tarif = TARIF_2026 if args.jahr == 2026 else TARIF_2025
    kinderlos = args.kinderlos or args.kinder == 0
    res = abrechnung(args.brutto, steuerklasse=args.steuerklasse,
                     kv_zusatz=args.kv_zusatz, kinderlos=kinderlos,
                     kinder=args.kinder, bundesland=args.bundesland,
                     konfession=args.konfession, tarif=tarif)
    print(formatiere(res, args.name))


if __name__ == "__main__":
    _cli()

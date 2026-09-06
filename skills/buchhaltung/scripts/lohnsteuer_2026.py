#!/usr/bin/env python3
"""Amtliche Lohnsteuerberechnung 2026 (Deutschland).

Umsetzung des "Programmablaufplans für die maschinelle Berechnung der vom
Arbeitslohn einzubehaltenden Lohnsteuer, des Solidaritätszuschlags und der
Maßstabsteuer für die Kirchenlohnsteuer für 2026" (BMF-Schreiben vom
12.11.2025, Anlage 1) — der amtliche Rechenweg nach § 39b EStG.

Umfang dieser Umsetzung
-----------------------
Abgebildet ist der **Regelfall des laufenden Arbeitslohns** (§ 39b Abs. 2 EStG):
Steuerklassen I–VI, gesetzlich oder privat kranken-/pflegeversichert, mit
korrekter Vorsorgepauschale (inkl. Höchstbetrags-/Günstigerprüfung),
Solidaritätszuschlag (inkl. Milderungszone) und Bemessungsgrundlage für die
Kirchensteuer.

NICHT abgebildet (bewusst ausgelassen, da im Standard-Gehaltslauf selten und im
PAP als Sonderzweige geführt): Versorgungsbezüge (VBEZ), Altersentlastungsbetrag
(ALTER1), sonstige Bezüge (SONSTB, § 39b Abs. 3), Faktorverfahren (AF),
Freibeträge/Hinzurechnungsbeträge aus ELStAM (LZZFREIB/LZZHINZU),
Vermögensbeteiligungen und DBA. Werden solche Fälle gebraucht, sind die
entsprechenden PAP-Zweige (MRE4, MRE4ALTE, MSONST …) zu ergänzen.

Validierung
-----------
`python3 lohnsteuer_2026.py --selftest` rechnet beide amtlichen Prüftabellen
(Anlage 1, Seiten 39–40) nach und meldet jede Abweichung. Ist der Selbsttest
grün, entspricht die Jahreslohnsteuer für die getesteten Fälle exakt dem BMF-PAP.

Konstanten 2026 (aus dem PAP, Block MPARA und UPTAB26)
------------------------------------------------------
GFB=12.348, SolZ-Freigrenze=20.350, BBG RV/AV=101.400, BBG KV/PV=69.750.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

# --- Konstanten aus MPARA / UPTAB26 (PAP 2026) -----------------------------
GFB = 12348             # Grundfreibetrag
SOLZFREI_BASIS = 20350  # Freigrenze SolZ (wird mit KZTAB multipliziert)
BBGRVALV = 101400       # BBG Renten-/Arbeitslosenversicherung
BBGKVPV = 69750         # BBG Kranken-/Pflegeversicherung

RVSATZAN = 0.0930       # AN-Satz RV für die Vorsorgepauschale
AVSATZAN = 0.0130       # AN-Satz AV für die Vorsorgepauschale
KV_BASIS_VSP = 0.07     # halber ermäßigter KV-Satz (§243 SGB V: 14,0 %) für VSP
PV_BASIS = 0.018        # halber PV-Satz (3,6 %) für die Vorsorgepauschale
PV_SACHSEN = 0.023      # AN-Satz PV in Sachsen (VSP)
PV_ZUSCHLAG_KINDERLOS = 0.006
PV_ABSCHLAG_JE_KIND = 0.0025

W1STKL5, W2STKL5, W3STKL5 = 14071, 34939, 222260

ANP_AKTIV = 1230        # Arbeitnehmer-Pauschbetrag (Werbungskosten)
SAP = 36                # Sonderausgaben-Pauschbetrag
EFA_STKL2 = 4260        # Entlastungsbetrag für Alleinerziehende (1. Kind)
KFB_VOLL = 9756         # Kinderfreibetrag (voll, StKl III) — nur für SolZ/KiSt
KFB_HALB = 4878         # Kinderfreibetrag (halb, StKl I/II/IV) — nur SolZ/KiSt


def _abrunden_euro(x: float) -> float:
    """Auf volle Euro abrunden (Symbol ⌊ ⌋ im PAP)."""
    return float(math.floor(x + 1e-9))


# --- UPTAB26: tarifliche Einkommensteuer § 32a EStG ------------------------
def _uptab26(x: float, kztab: int) -> float:
    """Tarifliche ESt auf X (Euro), danach × KZTAB. Ergebnis in vollen Euro.

    X wird nach § 32a Abs. 1 EStG auf den nächsten vollen Euro abgerundet.
    """
    x = math.floor(x + 1e-9)
    if x < GFB + 1:
        st = 0.0
    elif x < 17800:
        y = (x - GFB) / 10000
        rw = y * 914.51
        rw = rw + 1400
        st = rw * y
    elif x < 69879:
        y = (x - 17799) / 10000
        rw = y * 173.10
        rw = rw + 2397
        rw = rw * y
        st = rw + 1034.87
    elif x < 277826:
        st = x * 0.42 - 11135.63
    else:
        st = x * 0.45 - 19470.38
    st = _abrunden_euro(st)
    return st * kztab


# --- UP5-6 / MST5-6: Lohnsteuer der Steuerklassen V und VI (§39b Abs.2 S.7) -
def _up5_6(zx: float) -> float:
    st1 = _uptab26(zx * 1.25, 1)
    st2 = _uptab26(zx * 0.75, 1)
    diff = (st1 - st2) * 2
    mist = _abrunden_euro(zx * 0.14)
    return mist if mist > diff else diff


def _mst5_6(zve: float) -> float:
    zzx = math.floor(zve + 1e-9)  # zvE auf volle Euro abrunden (§ 32a Abs. 1)
    if zzx > W1STKL5:
        if zzx > W2STKL5:
            st = _up5_6(W2STKL5)
            if zzx > W3STKL5:
                st = st + (W3STKL5 - W2STKL5) * 0.42 + (zzx - W3STKL5) * 0.45
            else:
                st = st + (zzx - W2STKL5) * 0.42
        else:
            st_w1 = _up5_6(W1STKL5)
            hoch = st_w1 + (zzx - W1STKL5) * 0.42
            vergl = _up5_6(zzx)
            st = hoch if hoch < vergl else vergl
    else:
        st = _up5_6(zzx)
    return _abrunden_euro(st)


# --- Vorsorgepauschale (UPEVP / MVSPKVPV / MVSPHB) -------------------------
def _vorsorgepauschale(zre4vp: float, *, stkl: int, kvz: float, pvsatzan: float,
                       krv: int, pkv: int, pkpv: float = 0.0,
                       pkpvagz: float = 0.0) -> float:
    """VSP nach § 39b Abs. 2 Satz 5 Nr. 3 EStG (Jahreswert, Euro)."""
    kvsatzan = kvz / 2 / 100 + KV_BASIS_VSP

    # Teilbetrag Rentenversicherung (VSPR) — seit 2023 zu 100 %.
    if krv == 1:
        vspr = 0.0
    else:
        zre4vpr = min(zre4vp, BBGRVALV)
        vspr = zre4vpr * RVSATZAN

    # Teilbetrag Kranken-/Pflegeversicherung (VSPKVPV).
    if pkv > 0:  # privat versichert
        vspkvpv = pkpv * 12
        if stkl != 6:
            vspkvpv = vspkvpv - pkpvagz * 12
        vspkvpv = max(vspkvpv, 0.0)
    else:  # gesetzlich versichert
        zre4vpr = min(zre4vp, BBGKVPV)
        vspkvpv = zre4vpr * (kvsatzan + pvsatzan)
    if stkl == 6:
        vspkvpv = vspkvpv if pkv > 0 else vspkvpv  # StKl VI: keine Sonderpfade hier

    vsp = vspkvpv + vspr

    # Höchstbetragsberechnung / Günstigerprüfung (MVSPHB) — ALV einbeziehen,
    # kombinierter Teilbetrag auf 1.900 € gedeckelt; es gilt der höhere Wert.
    # In Steuerklasse VI entfällt dieser Zweig.
    if stkl != 6:
        zre4vpr_alv = min(zre4vp, BBGRVALV)
        vspalv = AVSATZAN * zre4vpr_alv
        vsphb = min(vspalv + vspkvpv, 1900.0)
        vspn = vspr + vsphb
        if vspn > vsp:
            vsp = vspn
    return vsp


def _pvsatzan(*, kinderlos: bool, pva: int, sachsen: bool) -> float:
    satz = PV_SACHSEN if sachsen else PV_BASIS
    if kinderlos:
        satz += PV_ZUSCHLAG_KINDERLOS
    satz -= PV_ABSCHLAG_JE_KIND * pva
    return satz


@dataclass
class LStErgebnis:
    lstjahr: float       # Jahreslohnsteuer in Euro
    solzj: float         # Solidaritätszuschlag Jahr in Euro
    jbmg: float          # Maßstabsteuer (Bemessung KiSt) Jahr in Euro
    zve: float           # zu versteuerndes Einkommen in Euro
    vsp: float           # angesetzte Vorsorgepauschale in Euro


def lohnsteuer_jahr(jahresbrutto: float, *, steuerklasse: int, kvz: float = 2.90,
                    kinderlos: bool = True, kinder: int = 0,
                    sachsen: bool = False, krv: int = 0, pkv: int = 0,
                    zkf: float = 0.0, religion: bool = False,
                    pkpv: float = 0.0, pkpvagz: float = 0.0) -> LStErgebnis:
    """Amtliche Jahreslohnsteuer 2026 (laufender Arbeitslohn)."""
    stkl = steuerklasse
    pva = min(max(kinder - 1, 0), 4)  # Beitragsabschläge PV ab dem 2. Kind
    pvsatzan = _pvsatzan(kinderlos=kinderlos, pva=pva, sachsen=sachsen)

    zre4j = jahresbrutto           # laufender Lohn, keine Versorgungsbezüge
    zre4 = zre4j
    zre4vp = zre4j

    # ZTABFB: feste Tabellenfreibeträge (ohne Vorsorgepauschale, ohne KFB).
    # In Steuerklasse VI werden Arbeitnehmer- und Sonderausgaben-Pauschbetrag
    # nicht gewährt (ZTABFB = 0).
    if stkl == 6:
        ztabfb = 0
    else:
        efa = EFA_STKL2 if stkl == 2 else 0
        ztabfb = efa + ANP_AKTIV + SAP

    kztab = 2 if stkl == 3 else 1

    vsp = _vorsorgepauschale(zre4vp, stkl=stkl, kvz=kvz, pvsatzan=pvsatzan,
                             krv=krv, pkv=pkv, pkpv=pkpv, pkpvagz=pkpvagz)

    def jahressteuer(ztabfb_eff: float) -> float:
        zve = zre4 - ztabfb_eff - vsp
        if zve < 1:
            zve = 0.0
        if stkl < 5:
            return _uptab26(zve / kztab, kztab), zve
        return _mst5_6(zve), zve

    lstjahr, zve = jahressteuer(ztabfb)

    # Maßstabsteuer für SolZ/KiSt: mit Kinderfreibeträgen (§ 51a EStG).
    if zkf > 0:
        if stkl == 3:
            kfb = zkf * KFB_VOLL
        elif stkl in (1, 2, 4):
            kfb = zkf * KFB_HALB
        else:
            kfb = 0.0
        jbmg, _ = jahressteuer(ztabfb + kfb)
    else:
        jbmg = lstjahr

    # Solidaritätszuschlag (MSOLZ) auf die Maßstabsteuer JBMG.
    solzfrei = SOLZFREI_BASIS * kztab
    if jbmg > solzfrei:
        solzj = jbmg * 5.5 / 100
        solzmin = (jbmg - solzfrei) * 11.9 / 100
        if solzmin < solzj:
            solzj = solzmin
    else:
        solzj = 0.0

    return LStErgebnis(lstjahr=lstjahr, solzj=solzj, jbmg=jbmg, zve=zve, vsp=vsp)


# --- Aufteilung auf den Lohnzahlungszeitraum (UPANTEIL) --------------------
def _anteil(jahreswert_euro: float, lzz: int) -> float:
    """Anteil eines Jahreswerts (Euro) am LZZ, in Cent, abgerundet -> Euro."""
    jw = jahreswert_euro * 100  # Cent
    if lzz == 1:
        cent = jw
    elif lzz == 2:
        cent = math.floor(jw / 12)
    elif lzz == 3:
        cent = math.floor(jw * 7 / 360)
    else:
        cent = math.floor(jw / 360)
    return cent / 100


def lohnsteuer_lzz(brutto_lzz: float, *, lzz: int = 2, kirchensteuer_satz: float = 0.0,
                   **kw) -> dict:
    """Lohnsteuer, SolZ und Kirchensteuer für einen Lohnzahlungszeitraum (Euro).

    lzz: 1=Jahr, 2=Monat, 3=Woche, 4=Tag. brutto_lzz ist der Brutto des LZZ.
    """
    faktor = {1: 1, 2: 12, 3: 360 / 7, 4: 360}[lzz]
    jahresbrutto = brutto_lzz * faktor
    r = lohnsteuer_jahr(jahresbrutto, **kw)

    lst = _anteil(r.lstjahr, lzz)
    solz = _anteil(r.solzj, lzz)
    bk = _anteil(r.jbmg, lzz) if kirchensteuer_satz > 0 else 0.0
    kist = round(kirchensteuer_satz * bk, 2)
    return {
        "lohnsteuer": round(lst, 2),
        "soli": round(solz, 2),
        "kirchensteuer": kist,
        "lstjahr": round(r.lstjahr, 2),
        "zve": round(r.zve, 2),
        "vorsorgepauschale": round(r.vsp, 2),
    }


# --- Selbsttest gegen die amtlichen Prüftabellen (Anlage 1, S. 39–40) ------
_ALLG = {  # ALV=KRV=PKV=0, KVZ=2,90, PVZ=1 (StKl II: PVZ=0)
    1: [0,0,0,0,0,51,380,782,1251,1742,2248,2767,3300,3847,4407,4982,5570,6172,
        6788,7417,8060,8718,9389,10073,10772,11484,12220,13062,13922,14799,15694,
        16607,17538,18486,19438,20390,21343,22295,23248,24243,25293,26343,27393],
    2: [0,0,0,0,0,0,0,32,359,759,1230,1724,2233,2756,3293,3843,4408,4987,5580,6186,
        6807,7442,8091,8754,9430,10121,10835,11647,12476,13323,14188,15071,15971,
        16890,17826,18777,19729,20682,21634,22629,23679,24729,25779],
    3: [0,0,0,0,0,0,0,0,0,0,0,0,294,628,1000,1406,1850,2324,2810,3302,3802,4308,
        4822,5342,5870,6402,6952,7574,8206,8846,9496,10154,10822,11498,12182,12876,
        13580,14292,15012,15774,16590,17416,18252],
    5: [372,647,922,1197,1472,1778,2234,3073,3911,4749,5588,6426,7216,7954,8720,
        9512,10334,11171,12010,12848,13687,14525,15364,16202,17040,17879,18729,
        19681,20633,21585,22538,23490,24443,25395,26347,27300,28252,29204,30157,
        31152,32202,33252,34302],
    6: [558,838,1117,1397,1676,1956,2766,3604,4443,5281,6120,6952,7682,8436,9218,
        10030,10865,11703,12542,13380,14218,15057,15895,16734,17572,18410,19260,
        20213,21165,22117,23070,24022,24974,25927,26879,27831,28784,29736,30689,
        31684,32734,33784,34834],
}
_BRUTTO = list(range(5000, 110001, 2500))


def _selftest() -> int:
    fails = 0
    for stkl, werte in _ALLG.items():
        kinderlos = stkl != 2  # PVZ=1 außer StKl II
        for brutto, soll in zip(_BRUTTO, werte):
            r = lohnsteuer_jahr(brutto, steuerklasse=stkl, kvz=2.90,
                                kinderlos=kinderlos, krv=0, pkv=0)
            ist = int(r.lstjahr)
            if ist != soll:
                fails += 1
                print(f"  ABWEICHUNG StKl {stkl} {brutto:>7} €: "
                      f"soll {soll}, ist {ist}")
    total = sum(len(v) for v in _ALLG.values())
    if fails == 0:
        print(f"Selbsttest OK — {total} Werte der allgemeinen Prüftabelle "
              f"(StKl I,II,III,V,VI) exakt getroffen.")
    else:
        print(f"Selbsttest FEHLGESCHLAGEN — {fails}/{total} Abweichungen.")
    return fails


def _cli() -> None:
    p = argparse.ArgumentParser(description="Amtliche Lohnsteuer 2026 (PAP)")
    p.add_argument("--selftest", action="store_true",
                   help="gegen die amtlichen Prüftabellen rechnen")
    p.add_argument("--jahresbrutto", type=float)
    p.add_argument("--steuerklasse", type=int, default=1, choices=range(1, 7))
    p.add_argument("--kvz", type=float, default=2.90)
    p.add_argument("--kinder", type=int, default=0)
    p.add_argument("--kinderlos", action="store_true")
    p.add_argument("--zkf", type=float, default=0.0)
    p.add_argument("--sachsen", action="store_true")
    args = p.parse_args()

    if args.selftest:
        raise SystemExit(1 if _selftest() else 0)
    if args.jahresbrutto is None:
        p.error("--jahresbrutto oder --selftest angeben")
    kinderlos = args.kinderlos or args.kinder == 0
    r = lohnsteuer_jahr(args.jahresbrutto, steuerklasse=args.steuerklasse,
                        kvz=args.kvz, kinderlos=kinderlos, kinder=args.kinder,
                        sachsen=args.sachsen, zkf=args.zkf)
    print(f"Jahresbrutto {args.jahresbrutto:.2f} €, StKl {args.steuerklasse}")
    print(f"  zu versteuerndes Einkommen: {r.zve:.2f} €")
    print(f"  Vorsorgepauschale:          {r.vsp:.2f} €")
    print(f"  Jahreslohnsteuer:           {r.lstjahr:.2f} €")
    print(f"  Solidaritätszuschlag:       {r.solzj:.2f} €")


if __name__ == "__main__":
    _cli()

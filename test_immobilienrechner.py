"""
Tests für den Immobilienrechner.

Getestet werden die reinen Berechnungsformeln aus logic.py
sowie die Farblogik von get_rendite_color.
Streamlit-Aufrufe werden vollständig gemockt.
"""

import sys
import unittest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Streamlit vollständig mocken, bevor das Modul importiert wird
# ---------------------------------------------------------------------------

def _build_st_mock():
    st = MagicMock()
    # session_state als echtes Dict-ähnliches Objekt, damit Attribut-Zugriffe
    # und Item-Zugriffe wie im echten Streamlit funktionieren.
    session_state = {}
    st.session_state = session_state
    # stop() soll den Code-Fluss unterbrechen – wir mappen es auf SystemExit
    st.stop.side_effect = SystemExit("st.stop called")
    return st


_st_mock = _build_st_mock()
sys.modules["streamlit"] = _st_mock

import pandas as pd  # noqa: E402

from logic import (  # noqa: E402
    berechne_kredit,
    berechne_kredit_schnell,
    berechne_rate_monatl,
    berechne_zins_monatl,
    berechne_tilgung_monatl,
    calculate_kaufnebenkosten,
    calculate_privatkredit,
    calculate_renditen,
    calculate_steuer,
    calculate_deckung,
    calculate_cashflow_summary,
    get_rendite_color,
)


# ---------------------------------------------------------------------------
# Lokale Adapter-Funktionen mit einheitlicher Signatur für die Tests
# ---------------------------------------------------------------------------

def calc_hoehe_kredit(kaufpreis: float, finanzierungssatz: float) -> float:
    return berechne_kredit_schnell(kaufpreis, finanzierungssatz)["hoehe_kredit"]


def calc_eigenkapital(gesamtkosten: float, hoehe_kredit: float) -> float:
    return gesamtkosten - hoehe_kredit


def calc_rate_monatlich(hoehe_kredit: float, zins_pct: float, tilgung_pct: float) -> float:
    return berechne_rate_monatl(hoehe_kredit, zins_pct, tilgung_pct)


def calc_maklercourtage(kaufpreis: float, maklerprovision_pct: float) -> float:
    return calculate_kaufnebenkosten(kaufpreis, maklerprovision_pct, 0.0, 0.0, 0.0)["maklercourtage"]


def calc_kaufnebenkosten(
    kaufpreis: float,
    maklerprovision_pct: float,
    grunderwerbssteuer_pct: float,
    notarkosten_pct: float,
    grundbuchkosten_pct: float,
) -> float:
    return calculate_kaufnebenkosten(
        kaufpreis, maklerprovision_pct, grunderwerbssteuer_pct, notarkosten_pct, grundbuchkosten_pct
    )["kaufnebenkosten_gesamt"]


def calc_gesamtkosten(kaufpreis: float, kaufnebenkosten: float) -> float:
    return kaufpreis + kaufnebenkosten


def calc_bruttorealrendite(kaltmiete: float, kaufpreis: float) -> float:
    return calculate_renditen(kaltmiete, kaufpreis, kaufpreis)["bruttorealrendite"]


def calc_nettorealrendite(kaltmiete: float, gesamtkosten: float) -> float:
    return calculate_renditen(kaltmiete, gesamtkosten, gesamtkosten)["nettorealrendite"]



def calc_deckung(
    kaltmiete: float,
    hoehe_kredit: float,
    zins_pct: float,
    tilgung_pct: float,
    nicht_umlagefaehig: float = 0.0,
    privatkredit_monatl: float = 0.0,
) -> dict:
    result = calculate_deckung(
        kaltmiete, hoehe_kredit, zins_pct, tilgung_pct, nicht_umlagefaehig,
        privatkredit=(privatkredit_monatl > 0),
        rueckzahlung_ek_monatl=privatkredit_monatl,
    )
    return {
        "zins": result["deckungZins"],
        "zins_tilgung": result["deckungZinsTilgung"],
        "zins_tilgung_nk": result["deckungZinsTilgungNichtUmlagefähig"],
        "zins_tilgung_nk_pk": result.get("deckungZinsTilgungNichtUmlagefähigPrivatkredit", False),
    }


def _rendite_color(value: float) -> str:
    return get_rendite_color(value)


# ---------------------------------------------------------------------------
# Testklassen
# ---------------------------------------------------------------------------

class TestFinanzierungsberechnungen(unittest.TestCase):

    def test_hoehe_kredit_vollfinanzierung(self):
        self.assertAlmostEqual(calc_hoehe_kredit(300_000, 1.0), 300_000.0)

    def test_hoehe_kredit_80_prozent(self):
        self.assertAlmostEqual(calc_hoehe_kredit(300_000, 0.80), 240_000.0)

    def test_hoehe_kredit_50_prozent(self):
        self.assertAlmostEqual(calc_hoehe_kredit(200_000, 0.50), 100_000.0)

    def test_eigenkapital_berechnung(self):
        # gesamtkosten 330_000 (inkl. NK), kredit 240_000 → EK = 90_000
        self.assertAlmostEqual(calc_eigenkapital(330_000, 240_000), 90_000.0)

    def test_eigenkapital_vollfinanzierung_ohne_nk(self):
        # EK deckt mindestens die Nebenkosten
        gesamtkosten = 330_000
        kredit = 300_000  # nur Kaufpreis finanziert
        self.assertAlmostEqual(calc_eigenkapital(gesamtkosten, kredit), 30_000.0)

    def test_rate_monatlich_standard(self):
        # 240_000 € Kredit, 4% Zins, 2% Tilgung → 6% p.a. → 1440 € / Monat
        result = calc_rate_monatlich(240_000, 4.0, 2.0)
        self.assertAlmostEqual(result, 1200.0)

    def test_rate_monatlich_nur_zins(self):
        result = calc_rate_monatlich(100_000, 4.0, 0.0)
        self.assertAlmostEqual(result, 100_000 * 0.04 / 12)


class TestKaufnebenkosten(unittest.TestCase):

    def setUp(self):
        self.kaufpreis = 300_000.0

    def test_maklercourtage_3_57_prozent(self):
        result = calc_maklercourtage(self.kaufpreis, 3.57)
        self.assertAlmostEqual(result, 10_710.0)

    def test_maklercourtage_null(self):
        self.assertAlmostEqual(calc_maklercourtage(self.kaufpreis, 0.0), 0.0)

    def test_kaufnebenkosten_summe(self):
        # 3.57 % Makler + 6.5 % GrESt + 1.5 % Notar + 0.5 % Grundbuch
        result = calc_kaufnebenkosten(self.kaufpreis, 3.57, 6.5, 1.5, 0.5)
        expected = (
            300_000 * 0.0357
            + 300_000 * 0.065
            + 300_000 * 0.015
            + 300_000 * 0.005
        )
        self.assertAlmostEqual(result, expected, places=2)

    def test_gesamtkosten(self):
        nk = calc_kaufnebenkosten(self.kaufpreis, 3.57, 6.5, 1.5, 0.5)
        gesamt = calc_gesamtkosten(self.kaufpreis, nk)
        self.assertAlmostEqual(gesamt, self.kaufpreis + nk)

    def test_gesamtkosten_groesser_kaufpreis(self):
        nk = calc_kaufnebenkosten(self.kaufpreis, 3.57, 6.5, 1.5, 0.5)
        gesamt = calc_gesamtkosten(self.kaufpreis, nk)
        self.assertGreater(gesamt, self.kaufpreis)


class TestRenditeberechnungen(unittest.TestCase):

    def test_bruttorealrendite_typisch(self):
        # 1000 € Kaltmiete, 300_000 € Kaufpreis → 4 %
        result = calc_bruttorealrendite(1000, 300_000)
        self.assertAlmostEqual(result, 4.0)

    def test_bruttorealrendite_steigt_mit_miete(self):
        r1 = calc_bruttorealrendite(900, 300_000)
        r2 = calc_bruttorealrendite(1100, 300_000)
        self.assertLess(r1, r2)

    def test_nettorealrendite_kleiner_als_brutto(self):
        kaufpreis = 300_000.0
        nk = calc_kaufnebenkosten(kaufpreis, 3.57, 6.5, 1.5, 0.5)
        gesamt = calc_gesamtkosten(kaufpreis, nk)
        brutto = calc_bruttorealrendite(1000, kaufpreis)
        netto = calc_nettorealrendite(1000, gesamt)
        self.assertLess(netto, brutto)

    def test_nettorealrendite_formel(self):
        result = calc_nettorealrendite(1000, 350_000)
        self.assertAlmostEqual(result, 1000 * 12 / 350_000 * 100)


class TestSteuerberechnung(unittest.TestCase):

    def test_abschreibung_standard(self):
        result = calculate_steuer(300_000, 0.0, 0.0, 0.0, 85, 2.0, 0)
        self.assertAlmostEqual(result["abschreibung"], 300_000 * 0.85 * 0.02)

    def test_abschreibung_null_afa(self):
        result = calculate_steuer(300_000, 0.0, 0.0, 0.0, 85, 0.0, 0)
        self.assertAlmostEqual(result["abschreibung"], 0.0)

    def test_steuereffekt_verlust_erzeugt_ersparnis(self):
        # Hohe Zinsen + AfA → Verlust → positiver steuer_effekt (Ersparnis)
        result = calculate_steuer(300_000, 240_000, 800, 4.0, 85, 2.0, 42)
        self.assertGreater(result["steuer_effekt"], 0)

    def test_steuereffekt_positives_ergebnis_ergibt_steuerlast(self):
        # Sehr hohe Miete, geringe Zinsen → positives Ergebnis → negativer steuer_effekt (Steuerlast)
        result = calculate_steuer(100_000, 50_000, 3000, 2.0, 85, 2.0, 25)
        self.assertLess(result["steuer_effekt"], 0)


class TestDeckungslogik(unittest.TestCase):

    def _deckung(self, kaltmiete, hoehe_kredit=240_000, zins=4.0, tilgung=1.2,
                 nicht_umlagefaehig=0.0, privatkredit=0.0):
        return calc_deckung(kaltmiete, hoehe_kredit, zins, tilgung,
                             nicht_umlagefaehig, privatkredit)

    def test_zinsen_gedeckt(self):
        zins_monatl = 240_000 * 0.04 / 12  # = 800 €
        d = self._deckung(kaltmiete=900)
        self.assertTrue(d["zins"])

    def test_zinsen_nicht_gedeckt(self):
        zins_monatl = 240_000 * 0.04 / 12  # = 800 €
        d = self._deckung(kaltmiete=700)
        self.assertFalse(d["zins"])

    def test_zins_und_tilgung_gedeckt(self):
        zins_monatl = 240_000 * 0.04 / 12   # 800
        tilg_monatl = 240_000 * 0.012 / 12  # 240
        d = self._deckung(kaltmiete=1100)
        self.assertTrue(d["zins_tilgung"])

    def test_zins_und_tilgung_nicht_gedeckt(self):
        d = self._deckung(kaltmiete=900)  # 800 + 240 = 1040 > 900
        self.assertFalse(d["zins_tilgung"])

    def test_nk_nicht_umlagefaehig_gedeckt(self):
        d = self._deckung(kaltmiete=1200, nicht_umlagefaehig=100)
        self.assertTrue(d["zins_tilgung_nk"])

    def test_nk_nicht_umlagefaehig_nicht_gedeckt(self):
        d = self._deckung(kaltmiete=1050, nicht_umlagefaehig=100)
        self.assertFalse(d["zins_tilgung_nk"])

    def test_privatkredit_gedeckt(self):
        d = self._deckung(kaltmiete=1500, nicht_umlagefaehig=100, privatkredit=200)
        self.assertTrue(d["zins_tilgung_nk_pk"])

    def test_privatkredit_nicht_gedeckt(self):
        d = self._deckung(kaltmiete=1200, nicht_umlagefaehig=100, privatkredit=200)
        self.assertFalse(d["zins_tilgung_nk_pk"])


class TestRenditeKpiFarbe(unittest.TestCase):
    """Testet die Farbschwellen aus render_rendite_kpi."""

    def test_gruen_oberhalb_4_5(self):
        self.assertEqual(_rendite_color(4.51), "green")
        self.assertEqual(_rendite_color(7.0), "green")

    def test_gruen_nicht_bei_genau_4_5(self):
        self.assertNotEqual(_rendite_color(4.5), "green")

    def test_gelb_bei_genau_4_5(self):
        self.assertEqual(_rendite_color(4.5), "#F2C464")

    def test_gelb_zwischen_3_9_und_4_5(self):
        self.assertEqual(_rendite_color(4.0), "#F2C464")
        self.assertEqual(_rendite_color(3.9), "#F2C464")

    def test_rot_unterhalb_3_9(self):
        self.assertEqual(_rendite_color(3.89), "red")
        self.assertEqual(_rendite_color(0.0), "red")
        self.assertEqual(_rendite_color(-1.0), "red")

    def test_grenzwert_4_5_gelb_nicht_gruen(self):
        """Grenzwert: genau 4.5 → gelb (nicht grün, da > 4.5 erforderlich)."""
        color = _rendite_color(4.5)
        self.assertNotEqual(color, "green")
        self.assertEqual(color, "#F2C464")


class TestCashflowDict(unittest.TestCase):
    """Testet die update_cashflow_dict-Logik isoliert."""

    def setUp(self):
        self.cashflow_dict = {"Posten": [], "Betrag": [], "Einnahme": []}

    def _update(self, posten, betrag, einnahme):
        self.cashflow_dict["Posten"].append(posten)
        self.cashflow_dict["Betrag"].append(betrag)
        self.cashflow_dict["Einnahme"].append(einnahme)

    def test_einnahme_wird_hinzugefuegt(self):
        self._update("Kaltmiete", 1000.0, True)
        self.assertEqual(self.cashflow_dict["Posten"], ["Kaltmiete"])
        self.assertEqual(self.cashflow_dict["Betrag"], [1000.0])
        self.assertEqual(self.cashflow_dict["Einnahme"], [True])

    def test_ausgabe_wird_hinzugefuegt(self):
        self._update("Zins", 800.0, False)
        self.assertFalse(self.cashflow_dict["Einnahme"][0])

    def test_mehrere_eintraege(self):
        self._update("Kaltmiete", 1000.0, True)
        self._update("Zins", 800.0, False)
        self._update("Tilgung", 240.0, False)
        df = pd.DataFrame(self.cashflow_dict)
        einnahmen = df[df["Einnahme"] == True]["Betrag"].sum()
        ausgaben = df[df["Einnahme"] == False]["Betrag"].sum()
        self.assertAlmostEqual(einnahmen, 1000.0)
        self.assertAlmostEqual(ausgaben, 1040.0)
        ueberschuss = einnahmen - ausgaben
        self.assertAlmostEqual(ueberschuss, -40.0)


class TestBerechneKredit(unittest.TestCase):
    """Testet berechne_kredit (Hauptseite-Variante mit Gesamtkosten inkl. NK)."""

    def test_hoehe_kredit_entspricht_kaufpreis_mal_finanzierungsart(self):
        result = berechne_kredit(300_000, 0.80, 330_000)
        self.assertAlmostEqual(result["hoehe_kredit"], 240_000.0)

    def test_eigenkapital_ist_gesamtkosten_minus_kredit(self):
        # Gesamtkosten 330_000, Kredit 240_000 → EK = 90_000
        result = berechne_kredit(300_000, 0.80, 330_000)
        self.assertAlmostEqual(result["eigenkapital"], 90_000.0)

    def test_vollfinanzierung_eigenkapital_entspricht_nebenkosten(self):
        # Kredit = Kaufpreis → EK deckt nur die Nebenkosten
        result = berechne_kredit(300_000, 1.0, 330_000)
        self.assertAlmostEqual(result["hoehe_kredit"], 300_000.0)
        self.assertAlmostEqual(result["eigenkapital"], 30_000.0)


class TestCalculatePrivatkredit(unittest.TestCase):
    """Testet calculate_privatkredit (Eigenkapital-Rückzahlung an Drittperson)."""

    def test_jaehrliche_rueckzahlung_korrekt(self):
        # 60_000 € EK über 5 Jahre → 12_000 € / Jahr
        result = calculate_privatkredit(60_000, 5)
        self.assertAlmostEqual(result["rueckzahlung_ek_jaehrl"], 12_000.0)

    def test_monatliche_rueckzahlung_korrekt(self):
        # 60_000 € über 5 Jahre → 1_000 € / Monat
        result = calculate_privatkredit(60_000, 5)
        self.assertAlmostEqual(result["rueckzahlung_ek_monatl"], 1_000.0)

    def test_laengere_laufzeit_ergibt_geringere_rate(self):
        kurz = calculate_privatkredit(60_000, 5)
        lang = calculate_privatkredit(60_000, 10)
        self.assertGreater(kurz["rueckzahlung_ek_monatl"], lang["rueckzahlung_ek_monatl"])


class TestCalculateCashflowSummary(unittest.TestCase):
    """Testet calculate_cashflow_summary mit echten DataFrames."""

    def _make_df(self, rows):
        return pd.DataFrame(rows, columns=["Posten", "Betrag", "Einnahme"])

    def test_einnahmen_und_ausgaben_korrekt(self):
        df = self._make_df([
            ("Kaltmiete", 1000.0, True),
            ("Zins",       800.0, False),
            ("Tilgung",    240.0, False),
        ])
        result = calculate_cashflow_summary(df)
        self.assertAlmostEqual(result["einnahmen_gesamt"], 1000.0)
        self.assertAlmostEqual(result["ausgaben_gesamt"], 1040.0)

    def test_ueberschuss_korrekt(self):
        df = self._make_df([
            ("Kaltmiete", 1200.0, True),
            ("Zins",       800.0, False),
            ("Tilgung",    240.0, False),
        ])
        result = calculate_cashflow_summary(df)
        self.assertAlmostEqual(result["ueberschuss_gesamt"], 160.0)

    def test_negativer_ueberschuss_bei_unterdeckung(self):
        df = self._make_df([
            ("Kaltmiete", 900.0, True),
            ("Zins",      800.0, False),
            ("Tilgung",   240.0, False),
        ])
        result = calculate_cashflow_summary(df)
        self.assertLess(result["ueberschuss_gesamt"], 0)


if __name__ == "__main__":
    unittest.main()

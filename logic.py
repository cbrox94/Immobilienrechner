import pandas as pd


def get_rendite_color(value: float) -> str:
    if value > 4.5:
        return "green"
    elif value >= 3.9:
        return "#F2C464"
    return "red"


def berechne_kredit_schnell(kaufpreis: float, finanzierungsart: float) -> dict:
    """Quick-Maths: Eigenkapital = Kaufpreis - Kredit."""
    hoehe_kredit = kaufpreis * finanzierungsart
    return {"hoehe_kredit": hoehe_kredit, "eigenkapital": kaufpreis - hoehe_kredit}


def berechne_kredit(kaufpreis: float, finanzierungsart: float, gesamtkosten: float) -> dict:
    """Hauptseite: Eigenkapital = Gesamtkosten (inkl. Nebenkosten) - Kredit."""
    hoehe_kredit = kaufpreis * finanzierungsart
    return {"hoehe_kredit": hoehe_kredit, "eigenkapital": gesamtkosten - hoehe_kredit}


def berechne_zins_monatl(hoehe_kredit: float, zins: float) -> float:
    return hoehe_kredit * zins / 100 / 12


def berechne_tilgung_monatl(hoehe_kredit: float, tilgung: float) -> float:
    return hoehe_kredit * tilgung / 100 / 12


def berechne_rate_monatl(hoehe_kredit: float, zins: float, tilgung: float) -> float:
    return berechne_zins_monatl(hoehe_kredit, zins) + berechne_tilgung_monatl(hoehe_kredit, tilgung)


def calculate_kaufnebenkosten(
    kaufpreis: float,
    maklerprovision_pct: float,
    grunderwerbssteuer_pct: float,
    notarkosten_pct: float,
    grundbuchkosten_pct: float,
) -> dict:
    maklercourtage = kaufpreis * maklerprovision_pct / 100
    grunderwerbssteuer = kaufpreis * grunderwerbssteuer_pct / 100
    notarkosten = kaufpreis * notarkosten_pct / 100
    grundbuchkosten = kaufpreis * grundbuchkosten_pct / 100
    kaufnebenkosten_gesamt = maklercourtage + grunderwerbssteuer + notarkosten + grundbuchkosten
    return {
        "maklercourtage": maklercourtage,
        "grunderwerbssteuer": grunderwerbssteuer,
        "notarkosten": notarkosten,
        "grundbuchkosten": grundbuchkosten,
        "kaufnebenkosten_gesamt": kaufnebenkosten_gesamt,
        "gesamtkosten": kaufnebenkosten_gesamt + kaufpreis,
    }


def calculate_privatkredit(eigenkapital: float, dauer_rueckzahlung_ek: float) -> dict:
    rueckzahlung_ek_jaehrl = round(eigenkapital / dauer_rueckzahlung_ek, 2)
    rueckzahlung_ek_monatl = round(rueckzahlung_ek_jaehrl / 12, 2)
    return {
        "rueckzahlung_ek_jaehrl": rueckzahlung_ek_jaehrl,
        "rueckzahlung_ek_monatl": rueckzahlung_ek_monatl,
    }


def calculate_renditen(kaltmiete: float, kaufpreis: float, gesamtkosten: float) -> dict:
    return {
        "bruttorealrendite": kaltmiete * 12 / kaufpreis * 100,
        "nettorealrendite": kaltmiete * 12 / gesamtkosten * 100,
    }


def calculate_cashflow_summary(cashflow: pd.DataFrame) -> dict:
    einnahmen = cashflow.loc[cashflow["Einnahme"] == True, "Betrag"].sum()
    ausgaben = cashflow.loc[cashflow["Einnahme"] == False, "Betrag"].sum()
    return {
        "einnahmen_gesamt": einnahmen,
        "ausgaben_gesamt": ausgaben,
        "ueberschuss_gesamt": einnahmen - ausgaben,
    }


def calculate_deckung(
    kaltmiete: float,
    hoehe_kredit: float,
    zins: float,
    tilgung: float,
    nicht_umlagefähig: float,
    privatkredit: bool = False,
    rueckzahlung_ek_monatl: float = 0.0,
) -> dict:
    zins_monatl = berechne_zins_monatl(hoehe_kredit, zins)
    tilgung_monatl = berechne_tilgung_monatl(hoehe_kredit, tilgung)
    result = {
        "deckungZins": kaltmiete >= zins_monatl,
        "deckungZinsTilgung": kaltmiete >= zins_monatl + tilgung_monatl,
        "deckungZinsTilgungNichtUmlagefähig": kaltmiete >= zins_monatl + tilgung_monatl + nicht_umlagefähig,
    }
    if privatkredit:
        result["deckungZinsTilgungNichtUmlagefähigPrivatkredit"] = (
            kaltmiete >= zins_monatl + tilgung_monatl + nicht_umlagefähig + rueckzahlung_ek_monatl
        )
    return result


def calculate_steuer(
    kaufpreis: float,
    hoehe_kredit: float,
    kaltmiete: float,
    zins: float,
    anteil_gebaude: float,
    afa_satz: float,
    steuersatz: float,
) -> dict:
    zins_kosten = hoehe_kredit * (zins / 100)
    abschreibung = (kaufpreis * anteil_gebaude / 100) * (afa_satz / 100)
    mieteinnahmen = kaltmiete * 12
    ergebnis = mieteinnahmen - (zins_kosten + abschreibung)
    steuer_effekt = ergebnis * (steuersatz / 100) * (-1)
    return {
        "zins_kosten": zins_kosten,
        "abschreibung": abschreibung,
        "mieteinnahmen": mieteinnahmen,
        "ergebnis": ergebnis,
        "steuer_effekt": steuer_effekt,
    }

import streamlit as st
import pandas as pd
from PIL import Image
from logic import (
    get_rendite_color,
    berechne_kredit_schnell,
    berechne_kredit,
    berechne_rate_monatl,
    calculate_kaufnebenkosten,
    calculate_privatkredit,
    calculate_renditen,
    calculate_cashflow_summary,
    calculate_deckung,
    calculate_steuer,
)

############################################ KPI-Hilfsfunktion ############################################
def render_rendite_kpi(label: str, value: float) -> None:
    color = get_rendite_color(value)
    st.markdown(f"<span style='color:{color};'>{label}: {round(value, 2)} %</span>", unsafe_allow_html=True)


############################################ Initiale Informationen über Dialogfenster eingeben ############################################
@st.dialog("Basisinformationen")
def objekt_initialisieren():
    """Öffnet einen Dialog zur Eingabe der Basisinformationen einer Immobilie."""
    link = st.text_input("Link zum Immobilien-Inserat")
    name = st.text_input("Name der Immobilie")
    lage = st.text_input("Lage")
    kaufpreis_initial = st.number_input("Kaufpreis*", min_value=1.0, step=1000.00, format="%.2f", value=1.0)
    groesse_wohnung = st.number_input("Größe der Wohnung (qm)*", min_value=1.0, step=1.0, format="%.2f")
    zimmeranzahl = st.number_input("Zimmeranzahl", min_value=0.0, step=0.5, format="%.1f")
    hausgeld = st.number_input("Hausgeld", min_value=0.0, step=1.0, format="%.2f")
    nicht_umlagefähig = st.number_input("Davon nicht umlagefähig", min_value=0.0, step=1.0, format="%.2f")
    # Eingabe als Prozentwert (z. B. 3.57 für 3,57 %)
    maklerprovision = st.number_input("Maklerprovision (in %)", min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
    baujahr = st.number_input("Baujahr", min_value=0, step=1)
    heizungsart = st.selectbox("Heizungsart", ["Fernwärme", "Gas", "Öl"])
    energieklasse = st.selectbox("Energieklasse", ["A", "B", "C", "D", "E", "F", "G"])

    uploaded_files = st.file_uploader(
        "Wähle Bilder aus", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state["bilder"] = uploaded_files
        st.success(f"{len(uploaded_files)} Bild(er) gespeichert.")

    if st.button("Übernehmen"):
        st.session_state.objekte = []
        st.session_state.objekte.append({
            "link": link,
            "name": name,
            "lage": lage,
            "groesse_wohnung": groesse_wohnung,
            "zimmeranzahl": zimmeranzahl,
            "kaufpreis_initial": kaufpreis_initial,
            "hausgeld": hausgeld,
            "nicht_umlagefähig": nicht_umlagefähig,
            "maklerprovision": maklerprovision,
            "baujahr": baujahr,
            "heizungsart": heizungsart,
            "energieklasse": energieklasse,
            "Eindrücke": uploaded_files,
        })
        st.rerun()


if "objekte" not in st.session_state:

    ############ Quick Maths ############
    st.subheader("Quick Maths", divider=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        kaufpreis = st.number_input("Kaufpreis", min_value=0.01, value=300000.00, step=500.00)
    with col2:
        finanzierungsart = st.selectbox("Finanzierungssatz", [1.00, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50], index=2)

    kredit_schnell = berechne_kredit_schnell(kaufpreis, finanzierungsart)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Kredithoehe**:", "{:,.2f} €".format(kredit_schnell["hoehe_kredit"]))
    with col2:
        st.write("**Eigenkapital**:", "{:,.2f} €".format(kredit_schnell["eigenkapital"]))
    col1, col2 = st.columns(2)
    with col1:
        zins = st.number_input("Zins", min_value=0.0, value=4.0, step=0.05, format="%.2f")
    with col2:
        tilgung = st.number_input("Tilgung", min_value=0.0, value=2.0, step=0.05, format="%.2f")
    rate_monatl = berechne_rate_monatl(kredit_schnell["hoehe_kredit"], zins, tilgung)
    st.write("**Rate (monatl.):**", "{:,.2f} €".format(round(rate_monatl, 2)))

    ############ Erstellung Exposé ############
    st.subheader("Exposé", divider=True)
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Exposé"):
            objekt_initialisieren()
    with col1:
        st.write("Erstellung Exposé inkl. Wirtschaftlichkeitsrechnung")

    ############ Erläuterungen ############
    st.subheader("Erläuterungen", divider=True)
    st.write("**Abschnitt 'Details'**")
    st.write("Darstellung der Eingegebenen Basisinformationen.")
    st.write("**Abschnitt 'Finanzierung'**")
    st.write("Aus Kaufpreis und Finanzierungsart wird die Kredithoehe berechnet.")
    st.write("Über Zins und Tilgung wird die monatliche Kreditrate berechnet.")
    st.write("**Abschnitt 'Einnahmen'**")
    st.write("Die Einnahmen (Kaltmiete) können entweder direkt eingegeben oder über den Quadratmeterpreis berechnet werden.")
    st.write("**Cashflow Analyse**")
    st.write("Ergebnis der Kalkulation. Einnahmen und Ausgaben werden gegenübergestellt.")
    st.write("1 Grüner Haken, wenn die Kaltmiete Zins und Tilgung deckt.")
    st.write("2 Grüne Haken, wenn die Kaltmiete zusätzlich die nicht-umlagefähigen Nebenkosten deckt.")

    ############ Kontakt ############
    st.subheader("Kontakt", divider=True)
    st.write("Github: https://github.com/cbrox94")
    st.write("Discord: cbrox1994")

    st.stop()


# iterativ zu befuellen (wird bei jedem Render neu aufgebaut, da Widget-Werte sich ändern können)
st.session_state.cashflow_dict = {"Posten": [], "Betrag": [], "Einnahme": []}


def update_cashflow_dict(posten: str, betrag: float, einnahme: bool) -> None:
    st.session_state.cashflow_dict["Posten"].append(posten)
    st.session_state.cashflow_dict["Betrag"].append(betrag)
    st.session_state.cashflow_dict["Einnahme"].append(einnahme)


obj = st.session_state.objekte[0]

st.title(obj["name"])

############################################ Details ############################################
st.header("Details", divider=True)
# Link als reiner Text ausgeben, kein HTML-Rendering von Nutzerdaten
st.write(obj["link"])
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Lage:", obj["lage"])
    st.write("Größe:", f"{obj['groesse_wohnung']:.1f} qm")
with col2:
    st.write("Angebotspreis:", f"{obj['kaufpreis_initial']:,.2f} €")
    st.write("Zimmer:", format(obj["zimmeranzahl"], ".1f"))
with col3:
    st.write("Quadratmeterpreis:", f"{obj['kaufpreis_initial'] / obj['groesse_wohnung']:,.2f} €")

col1, col2, col3 = st.columns(3)
with col1:
    st.write("Baujahr:", f"{obj['baujahr']:.0f}")
    st.write("Hausgeld:", f"{obj['hausgeld']:,.2f} €")
with col2:
    st.write("Heizungsart:", obj["heizungsart"])
    st.write("davon nicht-umlagefähig:", f"{obj['nicht_umlagefähig']:,.2f}", "€")
with col3:
    st.write("Energieklasse:", obj["energieklasse"])
    st.write("Maklerprovision:", f"{obj['maklerprovision']:,.2f}", "%")

update_cashflow_dict("NK (nicht umlagefähig)", obj["nicht_umlagefähig"], False)

############################################ Kosten ############################################
st.header("Kosten", divider=True)

with st.expander("Steuersätze konfigurieren"):
    col1, col2, col3 = st.columns(3)
    with col1:
        grunderwerbssteuer_pct = st.number_input(
            "Grunderwerbssteuer (%)", min_value=0.0, max_value=10.0, value=6.5, step=0.5, format="%.1f"
        )
    with col2:
        notarkosten_pct = st.number_input(
            "Notarkosten (%)", min_value=0.0, max_value=5.0, value=1.5, step=0.1, format="%.1f"
        )
    with col3:
        grundbuchkosten_pct = st.number_input(
            "Grundbuchkosten (%)", min_value=0.0, max_value=5.0, value=0.5, step=0.1, format="%.1f"
        )

kaufnebenkosten = calculate_kaufnebenkosten(
    obj["kaufpreis_initial"],
    obj["maklerprovision"],
    grunderwerbssteuer_pct,
    notarkosten_pct,
    grundbuchkosten_pct,
)
gesamtkosten = kaufnebenkosten["gesamtkosten"]

col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Kaufpreis**")
    st.write("**Kaufnebenkosten**")
    st.write("**Gesamtkosten**")
with col2:
    st.write("{:,.2f} €".format(obj["kaufpreis_initial"]))
    st.write("{:,.2f} €".format(kaufnebenkosten["kaufnebenkosten_gesamt"]))
    st.write("{:,.2f} €".format(gesamtkosten))

with st.expander("**Kaufnebenkosten**"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("Maklercourtage ({}%)".format(obj["maklerprovision"]))
        st.markdown("Grunderwerbssteuer ({}%)".format(grunderwerbssteuer_pct))
        st.markdown("Notarkosten ({}%)".format(notarkosten_pct))
        st.markdown("Grundbucheintrag ({}%)".format(grundbuchkosten_pct))
    with col2:
        st.write("{:,.2f} €".format(kaufnebenkosten["maklercourtage"]))
        st.write("{:,.2f} €".format(kaufnebenkosten["grunderwerbssteuer"]))
        st.write("{:,.2f} €".format(kaufnebenkosten["notarkosten"]))
        st.write("{:,.2f} €".format(kaufnebenkosten["grundbuchkosten"]))

############################################ Finanzierung ############################################
st.header("Finanzierung", divider=True)
col1, col2 = st.columns([3, 1])
with col1:
    kaufpreis = st.number_input(
        "Kaufpreis", min_value=0.01, value=obj["kaufpreis_initial"],
        max_value=obj["kaufpreis_initial"], step=500.00
    )
with col2:
    finanzierungsart = st.selectbox(
        "Finanzierungssatz",
        [1.00, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50],
        index=0,
    )

kredit = berechne_kredit(kaufpreis, finanzierungsart, gesamtkosten)
hoehe_kredit = kredit["hoehe_kredit"]
eigenkapital = kredit["eigenkapital"]

col1, col2 = st.columns(2)
with col1:
    st.write("**Kredithoehe**:", "{:,.2f} €".format(hoehe_kredit))
with col2:
    st.write("**Eigenkapital**:", "{:,.2f} €".format(eigenkapital))

col1, col2 = st.columns(2)
with col1:
    zins = st.number_input("Zins", min_value=0.0, value=4.0, step=0.05, format="%.2f")
with col2:
    tilgung = st.number_input("Tilgung", min_value=0.0, value=1.20, step=0.05, format="%.2f")

rate_monatl = berechne_rate_monatl(hoehe_kredit, zins, tilgung)
st.write("**Rate (monatl.):**", "{:,.2f} €".format(round(rate_monatl, 2)))

update_cashflow_dict("Zins", hoehe_kredit * (zins / 100) / 12, False)
update_cashflow_dict("Tilgung", hoehe_kredit * (tilgung / 100) / 12, False)

privatkredit = st.checkbox("Fremdfinanzierung der Kaufnebenkosten", value=False)

rueckzahlung_ek_monatl = 0.0
if privatkredit:
    st.write("Einzubringendes Eigenkapital:", eigenkapital, "€")
    dauer_rueckzahlung_ek = st.number_input("Laufzeit Privatkredit", min_value=1.0, value=10.0, step=0.5, format="%.1f")
    pk = calculate_privatkredit(eigenkapital, dauer_rueckzahlung_ek)
    rueckzahlung_ek_monatl = pk["rueckzahlung_ek_monatl"]
    st.write("Rückzahlung Privatkredit (monatl.):", rueckzahlung_ek_monatl, "€")
    update_cashflow_dict("Rückzahlung Privatkredit", rueckzahlung_ek_monatl, False)

############################################ Einnahmen ############################################
st.header("Einnahmen", divider=True)
st.subheader("Mieteinnahmen")
col1, col2 = st.columns(2)
with col1:
    eingabe_kaltmiete = st.radio(
        "Eingabe Kaltmiete",
        ["Gesamt", "Quadratmeterpreis"],
        index=0,
        horizontal=True,
    )
with col2:
    if eingabe_kaltmiete == "Gesamt":
        kaltmiete = st.number_input("Kaltmiete:", min_value=1.0, step=5.0, format="%.2f")
        quadratmeterpreis = kaltmiete / obj["groesse_wohnung"]
        st.write("(", "{:,.2f}".format(quadratmeterpreis), "€/qm)")
    else:
        quadratmeterpreis = st.number_input("Quadratmeterpreis:", min_value=1.0, step=0.5, format="%.2f")
        kaltmiete = quadratmeterpreis * obj["groesse_wohnung"]
        st.write("(Kaltmiete: {:,.2f} €)".format(kaltmiete))

update_cashflow_dict("Kaltmiete", kaltmiete, True)

#### KPIs ####
renditen = calculate_renditen(kaltmiete, kaufpreis, gesamtkosten)
col1, col2 = st.columns(2)
with col1:
    render_rendite_kpi("Bruttorealrendite", renditen["bruttorealrendite"])
with col2:
    render_rendite_kpi("Nettorealrendite", renditen["nettorealrendite"])

cashflow = pd.DataFrame(st.session_state.cashflow_dict)

############################################ Cashflow Analyse ############################################
st.header("Cashflow Analyse", divider=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Einnahmen**")
    col4, col5 = st.columns(2)
    for i in range(len(cashflow)):
        if cashflow.iloc[i, 2]:
            with col4:
                st.write(cashflow.iloc[i, 0])
            with col5:
                if cashflow.iloc[i, 1] < 0:
                    st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(cashflow.iloc[i, 1]), unsafe_allow_html=True)
                else:
                    st.write("{0:,.2f} €".format(cashflow.iloc[i, 1]))

with col2:
    st.write("**Ausgaben**")
    col4, col5 = st.columns(2)
    for i in range(len(cashflow)):
        if not cashflow.iloc[i, 2]:
            with col4:
                st.write(cashflow.iloc[i, 0])
            with col5:
                if cashflow.iloc[i, 1] < 0:
                    st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(cashflow.iloc[i, 1]), unsafe_allow_html=True)
                else:
                    st.write("{0:,.2f} €".format(cashflow.iloc[i, 1]))

cf_summary = calculate_cashflow_summary(cashflow)
einnahmen_gesamt = cf_summary["einnahmen_gesamt"]
ausgaben_gesamt = cf_summary["ausgaben_gesamt"]
ueberschuss_gesamt = cf_summary["ueberschuss_gesamt"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("**Gesamt**")
with col2:
    if einnahmen_gesamt < 0:
        st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(einnahmen_gesamt), unsafe_allow_html=True)
    else:
        st.write("{0:,.2f} €".format(einnahmen_gesamt))
with col3:
    st.write("**Gesamt**")
with col4:
    if ausgaben_gesamt < 0:
        st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(ausgaben_gesamt), unsafe_allow_html=True)
    else:
        st.write("{0:,.2f} €".format(ausgaben_gesamt))

col4, col5 = st.columns([1, 3])
with col4:
    st.write("**Überschuss**")
with col5:
    if ueberschuss_gesamt < 0:
        st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(ueberschuss_gesamt), unsafe_allow_html=True)
    else:
        st.write("{0:,.2f} €".format(ueberschuss_gesamt))

deckung = calculate_deckung(
    kaltmiete, hoehe_kredit, zins, tilgung, obj["nicht_umlagefähig"],
    privatkredit=privatkredit, rueckzahlung_ek_monatl=rueckzahlung_ek_monatl,
)

col4, col5 = st.columns([1, 3])

with col4:
    st.write("✅" if deckung["deckungZins"] else "❌")
with col5:
    st.write("Zinsen gedeckt")

with col4:
    st.write("✅" if deckung["deckungZinsTilgung"] else "❌")
with col5:
    st.write("Tilgung gedeckt")

with col4:
    st.write("✅" if deckung["deckungZinsTilgungNichtUmlagefähig"] else "❌")
with col5:
    st.write("NK (nicht umlagefähig gedeckt)")

if privatkredit:
    with col4:
        st.write("✅" if deckung["deckungZinsTilgungNichtUmlagefähigPrivatkredit"] else "❌")
    with col5:
        st.write("Privatkredit gedeckt")

############################################ Steuer ############################################
st.header("Steuer", divider=True)

col1, col2, col3 = st.columns(3)
with col1:
    afa_satz = st.number_input("AfA Satz (%)", min_value=0.0, step=0.01, format="%.2f", value=2.00)
with col2:
    anteil_gebaude = st.number_input("Anteil Gebäude (%)", min_value=0, step=1, value=85)
with col3:
    steuersatz = st.number_input("Persönlicher Steuersatz", min_value=0, step=1, value=25)

steuer = calculate_steuer(kaufpreis, hoehe_kredit, kaltmiete, zins, anteil_gebaude, afa_satz, steuersatz)

col1, col2 = st.columns(2)
with col1:
    col3, col4 = st.columns([2, 1])
    with col3:
        st.markdown("Mietteinnahmen:")
        st.write("Zinsen:")
        st.write("Abschreibung:")
        st.write("**Ergebnis:**")
        st.write("**Steuerersparnis:**")
    with col4:
        st.write("➕", "{:,.2f} €".format(steuer["mieteinnahmen"]))
        st.write("➖", "{:,.2f} €".format(steuer["zins_kosten"]))
        st.write("➖", "{:,.2f} €".format(steuer["abschreibung"]))
        st.write("🟰", "{:,.2f} €".format(steuer["ergebnis"]))
        st.write("**{:,.2f} €**".format(steuer["steuerersparnis"]))

############################################ Eindrücke ############################################
st.header("Eindrücke", divider=True)

if "bilder" in st.session_state:
    for file in st.session_state["bilder"]:
        try:
            img = Image.open(file)
            st.image(img, caption=file.name, use_container_width=True)
        except (Image.UnidentifiedImageError, OSError) as e:
            st.error(f"{file.name} konnte nicht geladen werden: {e}")
else:
    st.info("Noch keine Bilder hochgeladen.")

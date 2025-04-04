import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.title("Willkommen auf dem Realvaluator")
##### Initiale Informationen über Dialogfenster eingeben #####
@st.dialog("Basisinformationen")
def objekt_initialisieren():
    link = st.text_input("Link zum Immobilien-Inserat")
    name = st.text_input("Name der Immobilie")
    lage = st.text_input("Lage")
    kaufpreis_initial = st.number_input("Kaufpreis*", min_value=1.0, step=1000.00, format="%.2f")
    groesse_wohnung = st.number_input("Größe der Wohnung (qm)*", min_value=1.0, step=1.0, format="%.2f")
    zimmeranzahl = st.number_input("Zimmeranzahl", min_value=0.0, step=0.5, format="%.1f")
    hausgeld = st.number_input("Hausgeld", min_value=0.0, step=1.0, format="%.2f")
    nicht_umlagefähig = st.number_input("Davon nicht umlagefähig", min_value=0.0, step=1.0, format="%.2f")
    maklerprovision = st.number_input("Maklerprovision", min_value=0.0, step=0.1, format="%.2f")
    baujahr = st.number_input("Baujahr", min_value=0, step=1)
    heizungsart = st.selectbox("Heizungsart", ["Fernwärme", "Gas", "Öl"])
    energieklasse = st.selectbox("Energieklasse", ["A", "B", "C", "D", "E", "F", "G"])
        
    st.session_state.objekte = []
    
    if st.button("Übernehmen"):
        st.session_state.objekte.append({"link": link, 
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
                                         "energieklasse": energieklasse})
        st.rerun()

if "objekte" not in st.session_state:
    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("+ Eingabe Basisinformationen"):
            objekt_initialisieren()
    with col1:
        st.write("Geben Sie zuerst die Basisinformationen der Immobilie ein:")
    st.subheader("Erste Schritte", divider=True)
    st.write("- Klicken Sie auf den Button **'Eingabe Basisinformationen'**.")
    st.write("- Machen Sie zumindest Angaben über **Kaufpreis** und **Größe**, um alle Berechnungen darzustellen.")
    st.write("- Die übrigen Abfragen sind optional.")
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
    st.subheader("Kontakt", divider=True)
    st.write("Github: https://github.com/cbrox94")
    st.write("Discord: cbrox1994")

    

# iterativ zu befuellen
st.session_state.cashflow_dict = {"Posten": [], "Betrag": [], "Einnahme": []}

# Eine Funktion, die das cashflow_dict aktualisiert
def update_cashflow_dict(posten, betrag, einnahme):
    st.session_state.cashflow_dict["Posten"].append(posten)
    st.session_state.cashflow_dict["Betrag"].append(betrag)
    st.session_state.cashflow_dict["Einnahme"].append(einnahme)

#### Stammdaten der Wohnung darstellen ####
st.title(st.session_state.objekte[0]["name"])

st.header("Details", divider=True)
st.markdown(st.session_state.objekte[0]["link"])
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Lage:", st.session_state.objekte[0]["lage"])
    st.write("Größe:", format(st.session_state.objekte[0]["groesse_wohnung"], ".1f"), "$m^2$")
with col2:
    st.write("Angebotspreis:", round(st.session_state.objekte[0]["kaufpreis_initial"],2), "€")
    st.write("Zimmer:", format(st.session_state.objekte[0]["zimmeranzahl"], ".1f"))

col1, col2, col3 = st.columns(3)
with col1:
    st.write("Baujahr:", st.session_state.objekte[0]["baujahr"])
    st.write("Hausgeld:", st.session_state.objekte[0]["hausgeld"], "€")

with col2:
    st.write("Heizungsart:", st.session_state.objekte[0]["heizungsart"])
    st.write("davon nicht-umlagefähig:", st.session_state.objekte[0]["nicht_umlagefähig"], "€")
with col3:
    st.write("Energieklasse:", st.session_state.objekte[0]["energieklasse"])
    st.write("Maklerprovision:", st.session_state.objekte[0]["maklerprovision"], "%")

# 2 Reiter
tab_finanzierung, tab_gesamtkosten = st.tabs(["Finanzierung", "Gesamtkosten"])

with tab_finanzierung:
    st.header("Finanzierung", divider=True)
    col1, col2 = st.columns([3,1])
    with col1:
        kaufpreis = st.slider("Kaufpreis", 0.5*st.session_state.objekte[0]["kaufpreis_initial"], 1.2*st.session_state.objekte[0]["kaufpreis_initial"], st.session_state.objekte[0]["kaufpreis_initial"], step=500.00)
    with col2:
        finanzierungsart = st.selectbox("Finanzierungsart", [1.00, 0.95, 0.90])

    hoehe_kredit = kaufpreis * finanzierungsart
    st.write("Kredithoehe:", round(hoehe_kredit,2), "€")    

    col1, col2 = st.columns(2)
    with col1:
        zins =st.number_input("Zins", min_value=0.0, value=3.4, step=0.05, format="%.2f")
    with col2:
        tilgung = st.number_input("Tilgung", min_value=0.0, value=1.20, step=0.05, format="%.2f")
    rate_jaehrl = hoehe_kredit * (zins/100 + tilgung/100)
    rate_monatl = rate_jaehrl / 12
    st.write("Rate (monatl.):", round(rate_monatl,2), "€")

    # monatliche Kreditrate als Ausgabe in Dict aufnehmen
    update_cashflow_dict("Kreditrate", rate_monatl, False)

with tab_gesamtkosten:
    #### Kosten ####
    st.subheader("Kosten")

    # Steuersätze
    prozentsatz_grunderwerbssteuer = 0.065
    prozentsatz_notarkosten = 0.015
    prozentsatz_grundbuchkosten = 0.005

    # Einzelkosten    
    maklercourtage = kaufpreis * st.session_state.objekte[0]["maklerprovision"] / 100
    grunderwerbssteuer = prozentsatz_grunderwerbssteuer * kaufpreis
    notarkosten = prozentsatz_notarkosten * kaufpreis
    grundbuchkosten = prozentsatz_grundbuchkosten * kaufpreis

    Kosten_Liste = [kaufpreis, maklercourtage, grunderwerbssteuer, notarkosten, grundbuchkosten]
    gesamtkosten = sum(Kosten_Liste)

    col1, col2 = st.columns(2)
    with col1:
        col3, col4 = st.columns(2)
        with col3:
            st.write("Kaufpreis:")
            st.write("Maklercourtage (", str(st.session_state.objekte[0]["maklerprovision"]), "%):")
            st.write("Grunderwerbssteuer:")
            st.write("Notarkosten:")
            st.write("Grundbucheintrag:")
            st.write("**Gesamtkosten:**")
        with col4:
            st.write(kaufpreis, "€")
            st.write(maklercourtage, "€")
            st.write(grunderwerbssteuer, "€")
            st.write(notarkosten, "€")
            st.write(grundbuchkosten, "€")
            st.write(gesamtkosten, "€")
    with col2:
        # Daten
        kategorien = ['Kaufpreis', 'Maklercourtage', 'Grunderwerbssteuer', 'Notarkosten', 'Grundbucheintrag']
        werte = [kaufpreis, maklercourtage, grunderwerbssteuer, notarkosten, grundbuchkosten]

        # Kreisdiagramm erstellen
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=kategorien,
                    values=werte,
                    hole=0.5,  # Donut-Style
                    pull=[0, 0.2, 0.2, 0.2, 0.2],  # Herausgezogene Segmente
                    textinfo='none',  # Nur Label + Wert anzeigen
                    marker=dict(colors=px.colors.qualitative.Pastel1)  # Hier Farben setzen
                )
            ]
        )
        #Legende ausblenden
        fig.update_layout(showlegend=False)
        # In Streamlit anzeigen
        st.plotly_chart(fig)

with tab_finanzierung:
    # "Finanzierung" Eigenkapital
    privatkredit = st.checkbox("Fremdfinanzierung der Kaufnebenkosten", value = False)
    
    if privatkredit:
        # Einzubringendes eigenkapital
        eigenkapital = gesamtkosten - hoehe_kredit
        st.write("Einzubringendes Eigenkapital:", eigenkapital, "€")
        dauer_rueckzahlung_ek = st.number_input("Laufzeit Privatkredit", min_value=1.0, value=10.0, step=0.5, format="%.1f")
        rueckzahlung_ek_jaehrl = round(eigenkapital / dauer_rueckzahlung_ek,2)
        rueckzahlung_ek_monatl = round(rueckzahlung_ek_jaehrl / 12,2)
        st.write("Rückzahlung Privatkredit (monatl.):", rueckzahlung_ek_monatl, "€")
        update_cashflow_dict("Rückzahlung Privatkredit", rueckzahlung_ek_monatl, False)

    # Radio
    st.header("Einnahmen", divider=True)
    col1, col2 = st.columns(2)
    with col1:
        eingabe_kaltmiete = st.radio(
        "Eingabe Kaltmiete",
        ["Gesamt", "Quadratmeterpreis"],
        index=0, horizontal=True
        ) 
    with col2:
        if eingabe_kaltmiete == "Gesamt":
            kaltmiete = st.number_input("Kaltmiete:", min_value=1.0, value=11.50 * st.session_state.objekte[0]["groesse_wohnung"], step=5.0, format="%.2f")
            quadratmeterpreis = kaltmiete/st.session_state.objekte[0]["groesse_wohnung"]
            st.write("(", round(quadratmeterpreis,2), "€/m^2)")
        else:
            quadratmeterpreis = st.number_input("Quadratmeterpreis:", min_value=1.0, value=11.50, step=0.5, format="%.2f")
            kaltmiete = quadratmeterpreis * st.session_state.objekte[0]["groesse_wohnung"]
            st.write("(Kaltmiete:", round(kaltmiete,2), "€)")

    # Kaltmiete als Ausgabe in Dict aufnehmen
    update_cashflow_dict("Kaltmiete", kaltmiete, True)

    #### KPIs ####
    bruttorealrendite = kaltmiete * 12 / kaufpreis * 100
    nettorealrendite = kaltmiete * 12 / gesamtkosten * 100

    col1, col2 = st.columns(2)
    with col1:
        if bruttorealrendite > 4.5:
            st.markdown("<span style='color: green;'>Bruttorealrendite: " + str(round(bruttorealrendite,2)) + "%</span>", unsafe_allow_html=True)
        elif bruttorealrendite <= 4.5 and bruttorealrendite > 3.9:
            st.markdown("<span style='color: #F2C464;'>Bruttorealrendite: " + str(round(bruttorealrendite,2)) + "%</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: red;'>Bruttorealrendite: " + str(round(bruttorealrendite,2)) + "%</span>", unsafe_allow_html=True)
    with col2:
        if bruttorealrendite > 4.5:
            st.markdown("<span style='color: green;'>Nettorealrendite: " + str(round(nettorealrendite,2)) + "%</span>", unsafe_allow_html=True)
        elif bruttorealrendite <= 4.5 and bruttorealrendite > 3.9:
            st.markdown("<span style='color: #F2C464;'>Nettorealrendite: " + str(round(nettorealrendite,2)) + "%</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: red;'>Nettorealrendite: " + str(round(nettorealrendite,2)) + "%</span>", unsafe_allow_html=True)

cashflow = pd.DataFrame(st.session_state.cashflow_dict)

##### Cashflow Analyse #####
st.header("Cashflow Analyse", divider = True)

col1, col2 = st.columns(2)
# Einnahmen
with col1:
    col4, col5 = st.columns(2)
    # Summe der Einnahmen
    einnahmen_gesamt = 0
    for i in range(len(cashflow)):
        if cashflow.iloc[i, 2]:
            einnahmen_gesamt += cashflow.iloc[i, 1]
    with col4:
        st.markdown ("**Einnahmen**")
    with col5:
        st.write(round(einnahmen_gesamt,2), "€")
        
    with st.expander("Aufschlüsselung"):
        for i in range(len(cashflow)):
            if cashflow.iloc[i, 2]:
                with col4:  
                    st.write(cashflow.iloc[i, 0])
                with col5:
                    st.write(cashflow.iloc[i, 1], "€")


# Ausgaben
with col2:
    col4, col5 = st.columns(2)
    # Summe der Ausgaben
    ausgaben_gesamt = 0
    for i in range(len(cashflow)):
        if not cashflow.iloc[i, 2]:
            ausgaben_gesamt += cashflow.iloc[i, 1]
    with col4:
        st.write("**Ausgaben**")
    with col5:
        st.write(round(ausgaben_gesamt,2), "€")
        
    with st.expander("Aufschlüsselung"):
        for i in range(len(cashflow)):
            if not cashflow.iloc[i, 2]:
                with col4:  
                    st.write(cashflow.iloc[i, 0])
                with col5:
                    st.write(cashflow.iloc[i, 1], "€")

# Überschuss
col4, col5 = st.columns([1,3])
with col4:
    st.write("**Überschuss**")
    
#Überschuss berechnen
ueberschuss_gesamt = einnahmen_gesamt - ausgaben_gesamt
with col5:
    st.write(round(ueberschuss_gesamt,2), "€")

if kaltmiete >= rate_monatl:
    kaltmieteZinsTilgung = True
else:
    kaltmieteZinsTilgung = False

if kaltmiete >= rate_monatl + st.session_state.objekte[0]["nicht_umlagefähig"]:
    deckungNichtUmlagefähig = True
else:
    deckungNichtUmlagefähig = False
    
if privatkredit:
    if kaltmiete >= rate_monatl + st.session_state.objekte[0]["nicht_umlagefähig"] + rueckzahlung_ek_monatl:
        deckungRatePrivatkredit = True
    else:
        deckungRatePrivatkredit = False

col4, col5 = st.columns([1,3])

if kaltmieteZinsTilgung:
    with col4:
        st.write("✅")
    with col5:
        st.write("Kaltmiete deckt Zins und Tilgung")
else:
    with col4:
        st.write("❌")
    with col5:
        st.write("Kaltmiete kleiner als Zins und Tilgung")
        
if deckungNichtUmlagefähig:
    with col4:
        st.write("✅")
    with col5:
        st.write("Überschuss deckt nicht-Umlagefähige Nebenkosten")
else:
    with col4:
        st.write("❌")
    with col5:
        st.write("Überschuss kleiner als nicht Umlagefähige Nebenkosten")

if privatkredit:
    if deckungRatePrivatkredit:
        with col4:
            st.write("✅")
        with col5:
            st.write("Überschuss deckt Rückzahlung Privatkredit")
    else:
        with col4:
            st.write("❌")
        with col5:
            st.write("Überschuss kleiner als Rueckzahlung Privatkredit")
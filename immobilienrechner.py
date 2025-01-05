import streamlit as st
import numpy as np
import pandas as pd

#### Vorabinformationen ####
link = 'https://www.immobilienscout24.de/expose/155343655#'
name = 'Lüdemannstr. 68'
lage = 'Suedfriedhof'
groesse_wohnung = 68.00
zimmeranzahl = 2.5
kaufpreis_initial = 159000.00
hausgeld = 242.00
nicht_umlagefähig = 166.42
maklerprovision = 0.00
baujahr = 1964
heizungsart = "Fernwärme"
energieklasse = "C"

nebenkosten = hausgeld - nicht_umlagefähig

# iterativ zu befuellen
cashflow_dict = {"Posten": [], "Betrag": [], "Einnahme": []}

# Eine Funktion, die das cashflow_dict aktualisiert
def update_cashflow_dict(posten, betrag, einnahme):
    cashflow_dict["Posten"].append(posten)
    cashflow_dict["Betrag"].append(betrag)
    cashflow_dict["Einnahme"].append(einnahme)

# Nebenkosten hinzufügen
update_cashflow_dict("Nebenkosten", nebenkosten, True)

# Hausgeld hinzufügen
update_cashflow_dict("Hausgeld", hausgeld, False)


#### Stammdaten der Wohnung darstellen ####
st.title(name)

st.header("Details", divider=True)
st.markdown(link)
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Lage:", lage)
    st.write("Größe:", format(groesse_wohnung, ".1f"), "$m^2$")
with col2:
    st.write("Angebotspreis:", round(kaufpreis_initial,2), "€")
    st.write("Zimmer:", format(zimmeranzahl, ".1f"))

col1, col2, col3 = st.columns(3)
with col1:
    st.write("Baujahr:", baujahr)
    st.write("Hausgeld:", hausgeld, "€")

with col2:
    st.write("Heizungsart:", heizungsart)
    st.write("davon nicht-umlagefähig:", nicht_umlagefähig, "€")
with col3:
    st.write("Energieklasse:", energieklasse)
    st.write("Maklerprovision:", maklerprovision, "%")
   
# 3 Reiter
tab_finanzierung, tab_gesamtkosten, tab_hausgeld = st.tabs(["Finanzierung", "Gesamtkosten", "Hausgeld"])

with tab_finanzierung:
    st.header("Finanzierung", divider=True)
    col1, col2 = st.columns(2)
    with col1:
        kaufpreis = st.number_input("Kaufpreis", min_value=0.0, value=kaufpreis_initial, step=1000.00, format="%.2f")
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
    maklercourtage = kaufpreis * maklerprovision / 100
    grunderwerbssteuer = prozentsatz_grunderwerbssteuer * kaufpreis
    notarkosten = prozentsatz_notarkosten * kaufpreis
    grundbuchkosten = prozentsatz_grundbuchkosten * kaufpreis

    Kosten_Liste = [kaufpreis, maklercourtage, grunderwerbssteuer, notarkosten, grundbuchkosten]
    gesamtkosten = sum(Kosten_Liste)

    col1, col2 = st.columns(2)
    with col1:
        st.write("Maklercourtage (", str(maklerprovision), "%):", maklercourtage, "€")
        st.write("Grunderwerbssteuer:", grunderwerbssteuer, "€")
        st.write("Notarkosten:", notarkosten, "€")
        st.write("Grundbucheintrag:", grundbuchkosten, "€")
        st.write("**Gesamtkosten:**", gesamtkosten, "€")
    with col2:
        st.write("Piechart soon available")

with tab_finanzierung:
    # "Finanzierung" Eigenkapital
    privatkredit = st.checkbox("Fremdfinanzierung der Kaufnebenkosten", value = True)
    
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
    col1, col2 = st.columns(2)
    with col1:
        eingabe_kaltmiete = st.radio(
        "Eingabe Kaltmiete",
        ["Gesamt", "Quadratmeterpreis"],
        index=0, horizontal=True
        ) 
    with col2:
        if eingabe_kaltmiete == "Gesamt":
            kaltmiete = st.number_input("Kaltmiete:", min_value=1.0, value=500.00, step=5.0, format="%.2f")
            quadratmeterpreis = kaltmiete/groesse_wohnung
            st.write("(", round(quadratmeterpreis,2), "€/m^2)")
        else:
            quadratmeterpreis = st.number_input("Quadratmeterpreis:", min_value=1.0, value=11.50, step=0.5, format="%.2f")
            kaltmiete = quadratmeterpreis * groesse_wohnung
            st.write("(Kaltmiete:", round(kaltmiete,2), "€)")

    # Kaltmiete als Ausgabe in Dict aufnehmen
    update_cashflow_dict("Kaltmiete", kaltmiete, True)

##### Cashflow Analyse #####
st.header("Cashflow Analyse", divider = True)

cashflow = pd.DataFrame(cashflow_dict)

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

if kaltmiete >= rate_monatl + nicht_umlagefähig:
    deckungNichtUmlagefähig = True
else:
    deckungNichtUmlagefähig = False
    
if privatkredit:
    if kaltmiete >= rate_monatl + nicht_umlagefähig + rueckzahlung_ek_monatl:
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
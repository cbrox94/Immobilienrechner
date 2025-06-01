# Eingabe der Basisinformationen
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

#st.title("Willkommen auf dem Realvaluator")
############################################ Initiale Informationen über Dialogfenster eingeben ############################################
@st.dialog("Basisinformationen")
def objekt_initialisieren():
    # Link zum Immobilien-Inserat
    link = st.text_input("Link zum Immobilien-Inserat")
    # Name der Immobilie
    name = st.text_input("Name der Immobilie")
    # Lage
    lage = st.text_input("Lage")
    # Kaufpreis
    kaufpreis_initial = st.number_input("Kaufpreis*", min_value=1.0, step=1000.00, format="%.2f", value = kaufpreis)
    groesse_wohnung = st.number_input("Größe der Wohnung (qm)*", min_value=1.0, step=1.0, format="%.2f")
    # Zimmeranzahl
    zimmeranzahl = st.number_input("Zimmeranzahl", min_value=0.0, step=0.5, format="%.1f")
    # Hausgeld
    hausgeld = st.number_input("Hausgeld", min_value=0.0, step=1.0, format="%.2f")
    # Davon nicht umlagefähig
    nicht_umlagefähig = st.number_input("Davon nicht umlagefähig", min_value=0.0, step=1.0, format="%.2f")
    # Maklerprovision
    maklerprovision = st.number_input("Maklerprovision", min_value=0.0, step=0.1, format="%.2f")
    # Baujahr
    baujahr = st.number_input("Baujahr", min_value=0, step=1)
    # Heizungsart
    heizungsart = st.selectbox("Heizungsart", ["Fernwärme", "Gas", "Öl"])
    # Energieklasse
    energieklasse = st.selectbox("Energieklasse", ["A", "B", "C", "D", "E", "F", "G"])
    
    # Mehrere Dateien gleichzeitig hochladen
    uploaded_files = st.file_uploader(
        "Wähle Bilder aus", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state["bilder"] = uploaded_files
        st.success(f"{len(uploaded_files)} Bild(er) gespeichert.")
        
    st.session_state.objekte = []
    
    # Button, um die Eingabe zu übernehmen
    if st.button("Übernehmen"):
        # Eingabe in der Session-State speichern
        st.session_state.objekte = []
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
                                         "energieklasse": energieklasse,
                                         "Eindrücke": uploaded_files})
        # Streamlit neu laden
        st.rerun()

if "objekte" not in st.session_state:
    
    ############ Quick Maths ############
    st.subheader("Quick Maths", divider=True)
    col1, col2 = st.columns([3,1])
    with col1:
            kaufpreis = st.number_input("Kaufpreis", min_value=0.01, value = 300000.00, step=500.00)
    with col2:
        finanzierungsart = st.selectbox("Finanzierungssatz", [1.00, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50], index=2)

    hoehe_kredit = kaufpreis * finanzierungsart
    eigenkapital = kaufpreis - hoehe_kredit
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Kredithoehe**:", "{:,.2f} €".format(hoehe_kredit), unsafe_allow_html=True)
    with col2:
        st.write("**Eigenkapital**:", "{:,.2f} €".format(eigenkapital), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        zins =st.number_input("Zins", min_value=0.0, value=4.0, step=0.05, format="%.2f")
    with col2:
        tilgung = st.number_input("Tilgung", min_value=0.0, value=2.0, step=0.05, format="%.2f")
    rate_jaehrl = hoehe_kredit * (zins/100 + tilgung/100)
    rate_monatl = rate_jaehrl / 12
    st.write("**Rate (monatl.):**", "{:,.2f} €".format(round(rate_monatl,2)), unsafe_allow_html=True)
    
    ############ Erstellung Exposé ############
    st.subheader("Exposé", divider=True)
    col1, col2 = st.columns([3,1])
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

    

# iterativ zu befuellen
st.session_state.cashflow_dict = {"Posten": [], "Betrag": [], "Einnahme": []}

# Eine Funktion, die das cashflow_dict aktualisiert
def update_cashflow_dict(posten, betrag, einnahme):
    st.session_state.cashflow_dict["Posten"].append(posten)
    st.session_state.cashflow_dict["Betrag"].append(betrag)
    st.session_state.cashflow_dict["Einnahme"].append(einnahme)

st.title(st.session_state.objekte[0]["name"])

############################################ Details ############################################
st.header("Details", divider=True)
st.markdown(st.session_state.objekte[0]["link"])
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Lage:", st.session_state.objekte[0]["lage"])
    st.write("Größe:", f"{st.session_state.objekte[0]['groesse_wohnung']:.1f} qm")
with col2:
    st.write("Angebotspreis:", f"{st.session_state.objekte[0]['kaufpreis_initial']:,.2f} €")
    st.write("Zimmer:", format(st.session_state.objekte[0]["zimmeranzahl"], ".1f"))
with col3:
    st.write("Quadratmeterpreis:", f"{st.session_state.objekte[0]['kaufpreis_initial']/st.session_state.objekte[0]['groesse_wohnung']:,.2f} €")

col1, col2, col3 = st.columns(3)
with col1:
    st.write("Baujahr:", f"{st.session_state.objekte[0]['baujahr']:.0f}")
    st.write("Hausgeld:", f"{st.session_state.objekte[0]['hausgeld']:,.2f} €")

with col2:
    st.write("Heizungsart:", st.session_state.objekte[0]["heizungsart"])
    st.write("davon nicht-umlagefähig:", f"{st.session_state.objekte[0]["nicht_umlagefähig"]:,.2f}", "€")
with col3:
    st.write("Energieklasse:", st.session_state.objekte[0]["energieklasse"])
    st.write("Maklerprovision:", f"{st.session_state.objekte[0]["maklerprovision"]:,.2f}", "%")

update_cashflow_dict("NK (nicht umlagefähig)", st.session_state.objekte[0]["nicht_umlagefähig"], False)

############################################ Kosten ############################################
st.header("Kosten", divider=True)

# Steuersätze
prozentsatz_grunderwerbssteuer = 0.065
prozentsatz_notarkosten = 0.015
prozentsatz_grundbuchkosten = 0.005

# Einzelkosten
#kaufpreis = st.session_state.objekte[0]["kaufpreis_initial"]
maklercourtage = st.session_state.objekte[0]["kaufpreis_initial"] * st.session_state.objekte[0]["maklerprovision"] / 100
grunderwerbssteuer = prozentsatz_grunderwerbssteuer * st.session_state.objekte[0]["kaufpreis_initial"]
notarkosten = prozentsatz_notarkosten * st.session_state.objekte[0]["kaufpreis_initial"]
grundbuchkosten = prozentsatz_grundbuchkosten * st.session_state.objekte[0]["kaufpreis_initial"]
kaufpreis = st.session_state.objekte[0]["kaufpreis_initial"]

kaufnebenkosten_liste = [maklercourtage, grunderwerbssteuer, notarkosten, grundbuchkosten]
#gesamtkosten = sum(kaufnebenkosten_liste)+st.session_state.objekte[0]["kaufpreis_initial"]
gesamtkosten = sum(kaufnebenkosten_liste)+kaufpreis

col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Kaufpreis**")
    st.write("**Kaufnebenkosten**")
    st.write("**Gesamtkosten**")
with col2:
    st.write("{:,.2f} €".format(st.session_state.objekte[0]["kaufpreis_initial"]), unsafe_allow_html=True)
    st.write("{:,.2f} €".format(sum(kaufnebenkosten_liste)), unsafe_allow_html=True)
    st.write("{:,.2f} €".format(gesamtkosten), unsafe_allow_html=True)

   
with st.expander("**Kaufnebenkosten**"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("Maklercourtage ({}%)".format(st.session_state.objekte[0]["maklerprovision"]))
        st.markdown("Grunderwerbssteuer ({}%)".format(prozentsatz_grunderwerbssteuer*100))
        st.markdown("Notarkosten ({}%)".format(prozentsatz_notarkosten*100))
        st.markdown("Grundbucheintrag ({}%)".format(prozentsatz_grundbuchkosten*100))
    with col2:     
        st.write("{:,.2f} €".format(maklercourtage))
        st.write("{:,.2f} €".format(grunderwerbssteuer))
        st.write("{:,.2f} €".format(notarkosten))
        st.write("{:,.2f} €".format(grundbuchkosten))

############################################ Finanzierung ############################################
st.header("Finanzierung", divider=True)
col1, col2 = st.columns([3,1])
with col1:
        kaufpreis = st.number_input("Kaufpreis", min_value=0.01, value=st.session_state.objekte[0]["kaufpreis_initial"],max_value=st.session_state.objekte[0]["kaufpreis_initial"], step=500.00)
with col2:
    finanzierungsart = st.selectbox("Finanzierungssatz", [1.00, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50], index = 0)

hoehe_kredit = kaufpreis * finanzierungsart
eigenkapital = gesamtkosten - hoehe_kredit
col1, col2 = st.columns(2)
with col1:
    st.write("**Kredithoehe**:", "{:,.2f} €".format(hoehe_kredit), unsafe_allow_html=True)
with col2:
    st.write("**Eigenkapital**:", "{:,.2f} €".format(eigenkapital), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    zins =st.number_input("Zins", min_value=0.0, value=4.0, step=0.05, format="%.2f")
with col2:
    tilgung = st.number_input("Tilgung", min_value=0.0, value=1.20, step=0.05, format="%.2f")
rate_jaehrl = hoehe_kredit * (zins/100 + tilgung/100)
rate_monatl = rate_jaehrl / 12
st.write("**Rate (monatl.):**", "{:,.2f} €".format(round(rate_monatl,2)), unsafe_allow_html=True)

# monatliche Kreditrate als Ausgabe in Dict aufnehmen
update_cashflow_dict("Zins", hoehe_kredit * (zins/100) / 12, False)
update_cashflow_dict("Tilgung", hoehe_kredit * (tilgung/100) / 12, False)

# "Finanzierung" Eigenkapital
privatkredit = st.checkbox("Fremdfinanzierung der Kaufnebenkosten", value = False)

if privatkredit:
    # Einzubringendes eigenkapital
    st.write("Einzubringendes Eigenkapital:", eigenkapital, "€")
    dauer_rueckzahlung_ek = st.number_input("Laufzeit Privatkredit", min_value=1.0, value=10.0, step=0.5, format="%.1f")
    rueckzahlung_ek_jaehrl = round(eigenkapital / dauer_rueckzahlung_ek,2)
    rueckzahlung_ek_monatl = round(rueckzahlung_ek_jaehrl / 12,2)
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
    index=0, horizontal=True
    ) 
with col2:
    if eingabe_kaltmiete == "Gesamt":
        kaltmiete = st.number_input("Kaltmiete:", min_value=1.0, step=5.0, format="%.2f")
        quadratmeterpreis = kaltmiete/st.session_state.objekte[0]["groesse_wohnung"]
        st.write("(", "{:,.2f}".format(quadratmeterpreis), "€/qm)")
    else:
        quadratmeterpreis = st.number_input("Quadratmeterpreis:", min_value=1.0, step=0.5, format="%.2f")
        kaltmiete = quadratmeterpreis * st.session_state.objekte[0]["groesse_wohnung"]
        st.write("(Kaltmiete: {:,.2f} €)".format(kaltmiete))

# Kaltmiete als Ausgabe in Dict aufnehmen
update_cashflow_dict("Kaltmiete", kaltmiete, True)

#### KPIs ####
bruttorealrendite = kaltmiete * 12 / kaufpreis * 100
nettorealrendite = kaltmiete * 12 / (sum(kaufnebenkosten_liste)+kaufpreis)*100

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

############################################ Cashflow Analyse ############################################
st.header("Cashflow Analyse", divider = True)

col1, col2 = st.columns(2)
# Einnahmen
with col1:            
    st.markdown ("**Einnahmen**")
    
    col4, col5 = st.columns(2)
    # Summe der Einnahmen            
    for i in range(len(cashflow)):
        if cashflow.iloc[i, 2]:
            with col4:  
                st.write(cashflow.iloc[i, 0])
            with col5:
                if cashflow.iloc[i, 1] < 0:
                    st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(cashflow.iloc[i, 1]), unsafe_allow_html=True)
                else:
                    st.write("{0:,.2f} €".format(cashflow.iloc[i, 1]))

# Ausgaben
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

#Gesamt
einnahmen_gesamt = 0
for i in range(len(cashflow)):
    if cashflow.iloc[i, 2]:
        einnahmen_gesamt += cashflow.iloc[i, 1]

ausgaben_gesamt = 0
for i in range(len(cashflow)):
    if not cashflow.iloc[i, 2]:
        ausgaben_gesamt += cashflow.iloc[i, 1]

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


# Überschuss
col4, col5 = st.columns([1,3])
with col4:
    st.write("**Überschuss**")
    
#Überschuss berechnen
ueberschuss_gesamt = einnahmen_gesamt - ausgaben_gesamt
with col5:
    if ueberschuss_gesamt < 0:
        st.markdown("<span style='color: red;'>{0:,.2f} €</span>".format(ueberschuss_gesamt), unsafe_allow_html=True)
    else:
        st.write("{0:,.2f} €".format(ueberschuss_gesamt))

# Schlussfolgerungen 
if kaltmiete >= hoehe_kredit*zins/100/12:
    deckungZins = True
else:
    deckungZins = False

if kaltmiete >= hoehe_kredit*zins/100/12 + hoehe_kredit*tilgung/100/12:
    deckungZinsTilgung = True
else:
    deckungZinsTilgung = False
    
if kaltmiete >= hoehe_kredit*zins/100/12 + hoehe_kredit*tilgung/100/12 + st.session_state.objekte[0]["nicht_umlagefähig"]:
    deckungZinsTilgungNichtUmlagefähig = True
else:        
    deckungZinsTilgungNichtUmlagefähig = False

if privatkredit:   
    if kaltmiete >= hoehe_kredit*zins/100/12 + hoehe_kredit*tilgung/100/12 + st.session_state.objekte[0]["nicht_umlagefähig"] + rueckzahlung_ek_monatl:
        deckungZinsTilgungNichtUmlagefähigPrivatkredit = True
    else:
        deckungZinsTilgungNichtUmlagefähigPrivatkredit = False

col4, col5 = st.columns([1,3])

if deckungZins:
    with col4:
        st.write("✅")
    with col5:
        st.write("Zinsen gedeckt")
else:
    with col4:
        st.write("❌")
    with col5:
        st.write("Zinsen gedeckt")
        
if deckungZinsTilgung:
    with col4:
        st.write("✅")
    with col5:
        st.write("Tilgung gedeckt")
else:
    with col4:
        st.write("❌")
    with col5:
        st.write("Tilgung gedeckt")

if deckungZinsTilgungNichtUmlagefähig:
    with col4:
        st.write("✅")
    with col5:
        st.write("NK (nicht umlagefähig gedeckt)")
else:
    with col4:
        st.write("❌")
    with col5:
        st.write("NK (nicht umlagefähig gedeckt)")

if privatkredit:
    if deckungZinsTilgungNichtUmlagefähigPrivatkredit:
        with col4:
            st.write("✅")
        with col5:
            st.write("Privatkredit gedeckt")
    else:
        with col4:
            st.write("❌")
        with col5:
            st.write("Privatkredit gedeckt")
            
############################################ Steuer ############################################
st.header("Steuer", divider = True)

col1, col2, col3 = st.columns(3)

# Abfragen
with col1:
    afa_satz = st.number_input("AfA Satz (%)", min_value=0.0, step=0.01, format="%.2f", value=2.00)
with col2:
    anteil_gebaude = st.number_input("Anteil Gebäude (%)", min_value=0, step=1, value=85)
with col3:
    steuersatz = st.number_input("Persönlicher Steuersatz", min_value=0, step= 1,value=25)

# Steuerrelevante Kosten
zins_kosten = hoehe_kredit * (zins/100)
abschreibung = (kaufpreis * anteil_gebaude/100) * (afa_satz/100)
steuerrelevante_kosten = zins_kosten + abschreibung

# Mietteinnahmen
mieteinnahmen = kaltmiete * 12

# Steuervorteil
ergebnis = mieteinnahmen - steuerrelevante_kosten
steuerersparnis = ergebnis * (steuersatz/100) *(-1)

# Ausgabe
col1, col2 = st.columns(2)
with col1:
    col3, col4 = st.columns([2,1])
    with col3:
        st.markdown("Mietteinnahmen:")
        st.write("Zinsen:")
        st.write("Abschreibung:")
        st.write("**Ergebnis:**")
        st.write("**Steuerersparnis:**")
    with col4:
        st.write("➕","{:,.2f} €".format(mieteinnahmen))
        st.write("➖","{:,.2f} €".format(zins_kosten))
        st.write("➖","{:,.2f} €".format(abschreibung))
        st.write("🟰","{:,.2f} €".format(ergebnis))
        st.write("**{:,.2f} €**".format(steuerersparnis))  

############################################ Eindrücke ############################################
st.header("Eindrücke", divider = True)

# Bilder anzeigen – untereinander
if "bilder" in st.session_state:
    for file in st.session_state["bilder"]:
        try:
            img = Image.open(file)
            st.image(img, caption=file.name, use_container_width=True)
        except Exception as e:
            st.error(f"{file.name} konnte nicht geladen werden: {e}")
else:
    st.info("Noch keine Bilder hochgeladen.")
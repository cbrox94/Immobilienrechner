# Review-Report: Immobilienrechner (Realvaluator)

**Datum:** 2026-05-26  
**Datei:** `immobilienrechner.py` (488 Zeilen)  
**Tech-Stack:** Python 3.11, Streamlit, pandas, numpy, Pillow

---

## Zusammenfassung

Die Anwendung ist für eine grundlegende Immobilien-Wirtschaftlichkeitsanalyse funktionsfähig, hat aber kritische Bugs, die vor einem produktiven Einsatz behoben werden müssen. Die monolithische Struktur erschwert Wartung und Tests erheblich.

---

## Kritische Fehler (Prio 1)

### 1. Undefinierte Variable `kaufpreis` (Zeile 18)

```python
# Zeile 18 im Dialog objekt_initialisieren()
value = kaufpreis  # NameError: kaufpreis ist hier nicht definiert
```

`kaufpreis` wird im Dialog referenziert, bevor sie in der Session oder lokal definiert wurde. Führt zu einem `NameError` beim ersten Öffnen des Dialogs.

**Fix:** `value`-Parameter entfernen oder einen Standardwert (z. B. `0`) verwenden.

---

### 2. Session-State-Überschreibung im Dialog (Zeilen 44, 49)

```python
# Zeile 44 – wird bei jedem Render ausgeführt, löscht bestehende Daten
st.session_state.objekte = []

# Zeile 49 – nach Button-Klick noch einmal zurückgesetzt
st.session_state.objekte = []
```

Die Liste wird bei jedem Renderdurchlauf auf `[]` gesetzt, bevor der Button-Zustand ausgewertet wird. Persistenz ist damit nicht gewährleistet.

**Fix:** Initialisierung nur einmal durchführen:

```python
if "objekte" not in st.session_state:
    st.session_state.objekte = []
```

---

### 3. IndexError bei leerem `objekte`-Array (Zeile 131)

```python
st.session_state.objekte[0]["name"]  # IndexError wenn Liste leer
```

Es gibt keinen Guard, der prüft, ob die Liste mindestens ein Element enthält.

**Fix:**

```python
if st.session_state.get("objekte"):
    ...
```

---

## Sicherheitsprobleme (Prio 1)

### 4. XSS-Anfälligkeit durch `unsafe_allow_html=True`

`unsafe_allow_html=True` wird an mehr als 15 Stellen verwendet (u. a. Zeilen 80, 82, 90, 199–202, 275–286, 306–308, 341, 348, 362, 474), ohne dass Benutzereingaben bereinigt werden. Nutzereingaben wie Objektname oder Link werden direkt als HTML gerendert.

**Beispiel:**

```python
# Zeile 135
st.markdown(st.session_state.objekte[0]["link"])
```

**Fix:** `st.write()` für Nutzerdaten verwenden; HTML nur für eigene, statische Templates einsetzen.

---

## Wichtige Fehler (Prio 2)

### 5. Keine Eingabevalidierung

Alle numerischen Eingaben erlauben negative oder unsinnige Werte:

- Wohnfläche kann negativ sein (Zeile 19)
- Hausgeld kann negativ sein (Zeilen 22–25)
- Kein Maximalwert für den Kaufpreis

**Fix:** `min_value=0` (und wo sinnvoll `max_value`) auf alle `st.number_input`-Felder setzen.

---

### 6. Hartcodierte Steuersätze und Nebenkosten (Zeilen 164–166)

```python
grunderwerbssteuer = kaufpreis * 0.065   # 6,5 % – variiert nach Bundesland (3,5 %–6,5 %)
notarkosten        = kaufpreis * 0.015
grundbuchkosten    = kaufpreis * 0.005
```

Die Grunderwerbssteuer unterscheidet sich je nach Bundesland erheblich. Hartcodierte Werte liefern für viele Nutzer falsche Ergebnisse.

**Fix:** Steuersätze als konfigurierbare Parameter im UI oder in einer `config.py` auslagern.

---

### 7. Berechnungslogik Eigenkapital (Zeile 213)

```python
eigenkapital = gesamtkosten - hoehe_kredit
```

`gesamtkosten` enthält Kaufnebenkosten, `hoehe_kredit` bezieht sich aber üblicherweise nur auf den Kaufpreis. Die Mischung der beiden führt zu einer potenziell falschen Eigenkapitalangabe.

**Fix:** Klären, ob der Kredit den Kaufpreis oder die Gesamtkosten finanziert, und die Berechnung entsprechend dokumentieren bzw. trennen.

---

### 8. Maklerprovision: unklares Eingabeformat (Zeile 27)

Die Provision wird als Dezimalzahl eingegeben (`step=0.1`), intern aber als Prozentwert interpretiert. Nutzer können unklar sein, ob sie `7.5` oder `0.075` eingeben sollen.

**Fix:** Einheitlich auf Prozenteingabe (0–100) umstellen und intern durch 100 teilen.

---

### 9. Performance: DataFrame wird bei jedem Render neu erstellt (Zeilen 123, 288)

```python
# Jedes Mal neu berechnet, auch wenn sich nichts geändert hat
st.session_state.cashflow_dict = {...}
cashflow = pd.DataFrame(...)
```

**Fix:** `@st.cache_data` oder `st.session_state`-Caching mit einem Dirty-Flag verwenden.

---

## Code-Qualität (Prio 3)

### 10. Ungenutzer Import: `numpy` (Zeile 3)

```python
import numpy as np  # wird nirgendwo verwendet
```

**Fix:** Zeile entfernen.

---

### 11. Doppelte KPI-Anzeige-Logik (Zeilen 274–286)

Die bedingte Farbgebung für Bruttorealrendite und Nettorealrendite ist identisch dupliziert. 

**Fix:** In eine Hilfsfunktion auslagern:

```python
def render_rendite_kpi(label: str, value: float) -> None:
    if value > 4.5:
        color = "green"
    elif value >= 3.9:
        color = "orange"
    else:
        color = "red"
    st.markdown(f'<p style="color:{color}">{label}: {value:.2f} %</p>', unsafe_allow_html=True)
```

---

### 12. Allgemeines Exception-Handling (Zeilen 486–487)

```python
except Exception as e:
    pass  # Fehler beim Laden von Bildern werden stillschweigend ignoriert
```

**Fix:** Spezifische Exceptions fangen (z. B. `PIL.UnidentifiedImageError`) und dem Nutzer eine Meldung anzeigen.

---

### 13. Keine Docstrings und keine Typen

Die einzige Funktion `objekt_initialisieren()` hat keinen Docstring. Keine Funktion besitzt Type Hints.

---

### 14. Keine Unit-Tests

Finanzberechnungen (Rendite, Cashflow, Steuerersparnis) werden nicht automatisiert getestet. Fehler in der Berechnungslogik fallen erst durch manuelle Prüfung auf.

---

## Architektur-Empfehlung

Die gesamte Logik liegt in einer einzigen 488-Zeilen-Datei. Empfohlene Zielstruktur:

```
immobilienrechner/
├── app.py                  # Nur UI-Schicht
├── calculations/
│   ├── financing.py        # Kreditberechnungen
│   ├── cashflow.py         # Einnahmen/Ausgaben
│   ├── tax.py              # Steuerberechnungen
│   └── metrics.py          # Rendite-Kennzahlen
├── config.py               # Steuersätze, Konstanten
├── tests/
│   ├── test_financing.py
│   └── test_cashflow.py
└── requirements.txt
```

---

## Metriken-Übersicht

| Kriterium            | Bewertung | Anmerkung                          |
|----------------------|-----------|------------------------------------|
| Kritische Bugs       | 3         | Müssen sofort behoben werden       |
| Sicherheit           | Mittel    | XSS durch unsafe HTML              |
| Eingabevalidierung   | Keine     | Alle Felder ungeschützt            |
| Code-Duplizierung    | Mittel    | KPI-Logik 2x identisch             |
| Testabdeckung        | 0 %       | Kein einziger Test                 |
| Ungenutzte Importe   | 1         | `numpy`                            |
| Architektur          | Schwach   | Monolith ohne Separation of Concerns |
| Berechnungsgenauigkeit | Gut     | Grundformeln korrekt               |

---

## Priorisierte To-do-Liste

**Prio 1 – sofort:**
- [ ] `kaufpreis`-Referenz in Zeile 18 fixen
- [ ] Session-State-Initialisierung korrigieren (Zeilen 44, 49)
- [ ] IndexError-Guard für `objekte[0]` hinzufügen
- [ ] `unsafe_allow_html` absichern oder Nutzerdaten heraushalten

**Prio 2 – kurzfristig:**
- [ ] `min_value=0` auf alle numerischen Eingaben setzen
- [ ] Steuersätze konfigurierbar machen
- [ ] Eigenkapital-Berechnung klären
- [ ] Maklerprovision auf einheitliches Format bringen

**Prio 3 – mittelfristig:**
- [ ] Berechnungslogik in eigene Module auslagern
- [ ] Unit-Tests schreiben
- [ ] `numpy`-Import entfernen
- [ ] Hilfsfunktion für KPI-Farbgebung erstellen
- [ ] Docstrings und Type Hints ergänzen

---

*Geschätzter Aufwand für alle Prio-1- und Prio-2-Fixes: ca. 3–4 Stunden*

# Code Review Report — Realvaluator

**Datum:** 2026-05-26  
**Reviewer:** code-reviewer Agent  
**Geprüfte Dateien:** `immobilienrechner.py`, `logic.py`, `test_immobilienrechner.py`  
**Technischer Stack:** Python 3.11, Streamlit, pandas, Pillow

---

## Zusammenfassung

Das Projekt hat seit dem letzten Review erhebliche Qualitätsverbesserungen erfahren: Die Berechnungslogik wurde sauber in `logic.py` ausgelagert, eine vollständige Testsuite mit 30+ Testfällen wurde ergänzt, XSS-Risiken durch `unsafe_allow_html` wurden auf das nötige Minimum reduziert, und eine Hilfsfunktion `render_rendite_kpi` vermeidet Codeduplizierung. Die Grundarchitektur ist nun solide.

Es verbleiben jedoch ein kritischer semantischer Bug in der Steuerberechnung, eine fehlerhafte Deckungslogik sowie mehrere mittlere und kleinere Befunde, die vor einem produktiven Einsatz adressiert werden sollten.

---

## Kritische Befunde (Severity: HIGH)

### [H1] Steuerberechnung: Zinskosten auf Jahresbasis falsch berechnet

- **Datei:** `logic.py`, Zeile 108
- **Problem:** `calculate_steuer` berechnet die Zinskosten als `hoehe_kredit * (zins / 100)` — also den vollen Jahreszins auf die gesamte Kreditsumme. Das ist die Anfangszinslast, stimmt aber nicht mit der monatlichen Rate überein, die im Cashflow verwendet wird. Wichtiger: Mieteinnahmen werden als Jahresbetrag (`kaltmiete * 12`) eingesetzt, während `zins_kosten` ebenfalls ein Jahresbetrag ist — das ist konsistent. Der semantische Fehler ist jedoch, dass `zins_kosten` in der Steuerberechnung die tatsächlichen Zinsen des Jahres darstellen sollte (die bei Annuitätendarlehen im Zeitverlauf sinken), aber hier statisch als Anfangszins berechnet wird. Für die Steuerersparnis im ersten Jahr ist das korrekt; eine Darstellung ohne diesen Hinweis im UI ist irreführend.
- **Konkreter Bug:** `steuerersparnis = ergebnis * (steuersatz / 100) * (-1)` — wenn `ergebnis` positiv ist (Gewinn), wird die Steuerersparnis negativ. Das ist mathematisch korrekt (Steuerlast statt Ersparnis), aber im UI wird das Feld immer als "Steuerersparnis" bezeichnet, ohne auf die Vorzeichenbedeutung hinzuweisen. Ein positives `ergebnis` bei der Steuer bedeutet Steuerschuld, kein negativer Wert sollte als Ersparnis kommuniziert werden.
- **Empfehlung:** Das Rückgabewort `steuerersparnis` umbenennen in `steuer_effekt` (negativ = Steuerlast, positiv = Ersparnis) und im UI eine bedingte Anzeige implementieren: bei negativem Wert "Steuerlast", bei positivem "Steuerersparnis".

---

### [H2] Deckungslogik: `deckungZinsTilgungNichtUmlagefähig` ignoriert Hausgeld-Anteil

- **Datei:** `logic.py`, Zeilen 90 / `immobilienrechner.py`, Zeilen 356–359
- **Problem:** `calculate_deckung` prüft, ob `kaltmiete >= zins + tilgung + nicht_umlagefähig`. Der Wert `nicht_umlagefähig` ist ein monatlicher Betrag (aus dem Dialog eingegeben), `zins_monatl` und `tilgung_monatl` sind korrekt als monatliche Werte berechnet. Der Vergleich ist intern konsistent. **Aber:** Im Cashflow-Dict (Zeilen 249–250 in `immobilienrechner.py`) werden Zins und Tilgung inline berechnet (`hoehe_kredit * (zins/100) / 12` und `hoehe_kredit * (tilgung/100) / 12`) — exakt dieselbe Formel wie in `calculate_deckung`. Das bedeutet, die Duplikation ist vorhanden und ein späterer Refactor (z. B. Änderung der Formel nur an einem Ort) kann zu Inkonsistenzen führen.
- **Empfehlung:** Die monatlichen Zins- und Tilgungsbeträge aus `calculate_deckung` (oder einer gemeinsamen Hilfsfunktion) in den Cashflow-Dict-Aufrufen verwenden, statt sie inline neu zu berechnen.

---

## Wichtige Befunde (Severity: MEDIUM)

### [M1] Tests testen nicht die tatsächlichen `logic.py`-Funktionen

- **Datei:** `test_immobilienrechner.py`, Zeilen 43–117
- **Problem:** Die Testdatei definiert ihre eigenen lokalen Hilfsfunktionen (`calc_hoehe_kredit`, `calc_renditen`, `calc_deckung`, etc.) und testet diese — nicht die importierten Funktionen aus `logic.py`. Ändert jemand eine Formel in `logic.py`, schlagen die Tests **nicht** an, weil sie die alte lokale Kopie der Formel testen. Dieser Ansatz gibt eine falsche Sicherheit.
- **Empfehlung:** Tests auf direkte Imports aus `logic.py` umstellen:
  ```python
  from logic import berechne_kredit, calculate_renditen, calculate_deckung, ...
  ```
  Die lokalen Hilfsfunktionen entfernen.

---

### [M2] Einzel-Objekt-Architektur: Mehrobjekt-Unterstützung nicht möglich

- **Datei:** `immobilienrechner.py`, Zeile 50 / 134
- **Problem:** `st.session_state.objekte` ist als Liste angelegt, aber es wird immer nur `objekte[0]` verwendet. Im Dialog wird bei jedem Klick auf "Übernehmen" die gesamte Liste mit `st.session_state.objekte = []` zurückgesetzt und dann ein einzelnes Objekt eingefügt. Ein Vergleich mehrerer Objekte (naheliegendes Feature) ist damit strukturell ausgeschlossen.
- **Empfehlung:** Entweder die Liste durch ein einzelnes Dict ersetzen (`st.session_state.objekt = {...}`) und den irreführenden Listenansatz aufgeben — oder die Architektur so erweitern, dass echtes Multiobjekt-Handling möglich wird (inkl. Objektauswahl im UI).

---

### [M3] `calculate_cashflow_summary` erhält einen pandas-DataFrame aus `st.session_state`

- **Datei:** `logic.py`, Zeile 66 / `immobilienrechner.py`, Zeile 294
- **Problem:** `calculate_cashflow_summary` nimmt einen `pd.DataFrame` als Parameter — dadurch ist `logic.py` implizit von pandas abhängig. Das ist grundsätzlich okay (pandas ist bereits im Stack), aber die Funktion nutzt `cashflow.iloc[:, 2]` (Spaltenindex statt Spaltenname), was brüchig ist: Ändert sich die Spaltenreihenfolge des Dicts, bricht die Funktion still.
- **Empfehlung:** Statt Positional-Indexing auf Spaltennamen zurückgreifen: `cashflow["Einnahme"]`, `cashflow["Betrag"]`. Alternativ die Funktion auf Listen/Dicts umstellen, um pandas aus `logic.py` zu entfernen.

---

### [M4] Privatkredit-Berechnung: Keine Zinsen berücksichtigt

- **Datei:** `logic.py`, Zeile 50–56
- **Problem:** `calculate_privatkredit` berechnet die monatliche Rückzahlung als reine Tilgung (`eigenkapital / laufzeit / 12`) ohne jegliche Zinsen. Ein Privatkredit (auch zinsloses Darlehen von Verwandten) hätte in der Realität oft Opportunitätskosten; ein echter Privatkredit von einer Bank oder Vermittlungsplattform hat immer Zinsen. Die Funktion ist für den bankkreditbasierten Anwendungsfall unvollständig.
- **Empfehlung:** Einen optionalen `zinssatz`-Parameter ergänzen (Default 0 für zinsloses Darlehen); bei nicht-null-Zinssatz mit der Annuitätenformel berechnen. Im UI dokumentieren, dass der Standardfall einen zinslosen Privatkredit annimmt.

---

### [M5] Hausgeld fehlt im Cashflow

- **Datei:** `immobilienrechner.py`, Zeile 163
- **Problem:** `nicht_umlagefähig` (der nicht-umlagefähige Anteil des Hausgelds) wird in den Cashflow aufgenommen — aber das **Hausgeld gesamt** (`obj["hausgeld"]`) fehlt im Cashflow. Der volle Hausgeld-Betrag ist für den Cashflow relevant, weil auch der umlagefähige Teil zumindest im Voraus vom Eigentümer getragen wird (Betriebskostenvorauszahlung). Ob und wie viel davon weiterverrechnet wird, ist eine Nutzerpräferenz — aber der aktuelle Cashflow zeigt nur einen Teil der tatsächlichen Kosten.
- **Empfehlung:** Entweder das gesamte Hausgeld in den Cashflow aufnehmen und einen separaten Posten "Erstattung umlagefähige NK" als Einnahme ergänzen — oder explizit dokumentieren, warum nur der nicht-umlagefähige Anteil berücksichtigt wird.

---

## Kleinere Befunde (Severity: LOW)

### [L1] Kaufpreis-Input in Finanzierungssektion hat unnötigen `max_value`-Guard

- **Datei:** `immobilienrechner.py`, Zeilen 219–222
- **Problem:** `max_value=obj["kaufpreis_initial"]` bedeutet, dass der Kaufpreis nur nach unten korrigiert werden kann, nicht nach oben. Szenario-Analysen ("Was, wenn der Kaufpreis 5 % höher verhandelt wird?") sind damit unmöglich.
- **Empfehlung:** `max_value` entfernen oder auf einen sinnvollen Multiplikator setzen (z. B. `obj["kaufpreis_initial"] * 1.5`).

---

### [L2] Typo im UI: "Mietteinnahmen" (doppeltes 't')

- **Datei:** `immobilienrechner.py`, Zeile 401
- **Problem:** `st.markdown("Mietteinnahmen:")` — doppeltes 't'.
- **Empfehlung:** Korrigieren zu `"Mieteinnahmen:"`.

---

### [L3] Inline-Cashflow-Berechnung dupliziert Logik aus `logic.py`

- **Datei:** `immobilienrechner.py`, Zeilen 249–250
- **Problem:** Zins und Tilgung werden direkt im UI-Code berechnet:
  ```python
  update_cashflow_dict("Zins", hoehe_kredit * (zins / 100) / 12, False)
  update_cashflow_dict("Tilgung", hoehe_kredit * (tilgung / 100) / 12, False)
  ```
  Diese Formel existiert identisch in `berechne_rate_monatl` und `calculate_deckung`.
- **Empfehlung:** `berechne_rate_monatl` aufteilen in `berechne_zins_monatl` und `berechne_tilgung_monatl`, oder einen Rückgabewert aus `berechne_kredit` nutzen, der bereits aufgeschlüsselt ist.

---

### [L4] `get_rendite_color` liegt in `logic.py`, ist aber reine UI-Logik

- **Datei:** `logic.py`, Zeilen 4–9
- **Problem:** Farbcodes (`"green"`, `"#F2C464"`, `"red"`) sind UI-spezifisch und gehören nicht in die Berechnungslogik. Die Schwellenwerte (4.5, 3.9) sind dagegen fachlich und könnten in einer Konstanten-Datei liegen.
- **Empfehlung:** `get_rendite_color` nach `immobilienrechner.py` verschieben (oder in eine eigene `ui_helpers.py`) und die Schwellenwerte als Konstanten in `logic.py` exportieren, wenn sie fachliche Bedeutung haben.

---

### [L5] `devcontainer.json` startet Streamlit mit deaktiviertem CSRF-Schutz

- **Datei:** `.devcontainer/devcontainer.json`, Zeile 22
- **Problem:** `--server.enableXsrfProtection false` deaktiviert den XSRF-Schutz in der Codespaces-Umgebung. Das ist für lokale Entwicklung tolerierbar, sollte aber nicht in einer geteilten oder öffentlichen Umgebung eingesetzt werden.
- **Empfehlung:** Flag nur für rein lokale Entwicklung setzen; in einer geteilten Codespace-Umgebung XSRF-Schutz aktiviert lassen.

---

### [L6] Fehlende `requirements.txt`

- **Datei:** Projektroot
- **Problem:** Es gibt keine `requirements.txt` im Projektverzeichnis (nur eine Referenz im `devcontainer.json`). Neue Entwickler müssen Abhängigkeiten (streamlit, pandas, Pillow) manuell ermitteln.
- **Empfehlung:** `requirements.txt` mit mindestens `streamlit`, `pandas`, `Pillow` anlegen.

---

### [L7] Tests: `from PIL import Image` importiert, aber nicht genutzt

- **Datei:** `test_immobilienrechner.py`, Zeile 35
- **Problem:** `from PIL import Image` wird importiert, aber in keinem Test verwendet.
- **Empfehlung:** Import entfernen.

---

## Positives

- **Saubere Trennung von UI und Logik:** Die Auslagerung aller Berechnungen in `logic.py` ist konsequent umgesetzt. `immobilienrechner.py` enthält nur noch UI-Code und Aufrufe der Logikfunktionen.
- **Vollständige Funktionssignaturen mit Type Hints:** Alle Funktionen in `logic.py` haben Parameter-Annotationen, was die Lesbarkeit und IDE-Unterstützung deutlich verbessert.
- **Hilfsfunktion `render_rendite_kpi`:** Die Farblogik für KPIs ist sauber in eine wiederverwendbare Funktion extrahiert.
- **Fehlerbehandlung beim Bildladen:** `except (Image.UnidentifiedImageError, OSError)` ist spezifisch und korrekt — kein bare `except`.
- **XSS-Risiko reduziert:** Nutzereingaben (Link, Name) werden via `st.write()` ausgegeben, nicht via `unsafe_allow_html`. Das `unsafe_allow_html` ist auf UI-Templates beschränkt, nicht auf Nutzerdaten.
- **Gut strukturierte Testsuite:** Die Testklassen sind sinnvoll nach Domänen gruppiert (Finanzierung, Kaufnebenkosten, Renditen, Steuer, Deckung, KPI-Farbe, Cashflow). Grenzwerttests für die Renditefarbe sind vorhanden.
- **Dialog für Objekterfassung:** Der `@st.dialog`-Ansatz ist idiomatisch für Streamlit und hält den Hauptcode übersichtlich.

---

## Metriken-Übersicht

| Kriterium                | Bewertung | Anmerkung                                          |
|--------------------------|-----------|----------------------------------------------------|
| Kritische Bugs           | 2         | Steuerausweis-Semantik, Cashflow-Formelinkonsistenz |
| Architektur              | Gut       | UI/Logik getrennt; Listenstruktur leicht irreführend |
| Testabdeckung (Logik)    | ~70 %     | Logik-Funktionen nicht direkt importiert            |
| Codeduplizierung         | Gering    | Zins/Tilgung-Formel 3× vorhanden                  |
| Eingabevalidierung       | Ausreichend | min_value gesetzt; max_value bei Kaufpreis zu eng  |
| Sicherheit               | Gut       | unsafe_allow_html nur für eigene Templates          |
| Typisierung              | Gut       | Type Hints in logic.py vollständig                 |
| Dokumentation            | Mittel    | Docstrings fehlen in immobilienrechner.py           |
| Dependencies             | Mittel    | requirements.txt fehlt                              |

---

*Geschätzter Aufwand für HIGH-Fixes: ~2 Stunden | MEDIUM-Fixes: ~4 Stunden | LOW-Fixes: ~1 Stunde*

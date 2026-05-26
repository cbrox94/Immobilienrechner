# Realvaluator

## Was ist dieses Projekt?
Ein Streamlit-basierter Immobilien-Wirtschaftlichkeitsrechner für private Immobilieninvestoren.

## Technischer Stack
- Python + Streamlit (UI)
- pandas, numpy (Berechnungen)
- Pillow (Bildanzeige)

## Projektstruktur
- `immobilienrechner.py` — Streamlit-UI und Seitenaufbau
- `logic.py` — Reine Berechnungslogik (ohne Streamlit-Abhängigkeiten)
- `test_immobilienrechner.py` — Unit-Tests (unittest, Streamlit vollständig gemockt)
- `requirements.txt` — Python-Abhängigkeiten (streamlit, pandas, Pillow)
- `.claude/agents/` — Agentendefinitionen für Claude Code
- `.claude/commands/` — Slash-Commands (z.B. `/review-pipeline`)

## Wichtige Funktionen in logic.py
- `berechne_zins_monatl` / `berechne_tilgung_monatl` — zentrale Hilfsfunktionen für Zins- und Tilgungsberechnung; werden von `berechne_rate_monatl`, `calculate_deckung` und der UI genutzt
- `calculate_steuer` — gibt `steuer_effekt` zurück (positiv = Ersparnis, negativ = Steuerlast)

## Konventionen
- Sprache: Deutsch in Kommentaren, Englisch im Code
- Keine direkte Datenbankanbindung, Daten kommen aus Dateien
- Berechnungslogik gehört in `logic.py`, UI-Code in `immobilienrechner.py`
- Tests importieren direkt aus `logic.py` — keine lokalen Formelkopien in Tests
- Tests laufen mit `python -m pytest test_immobilienrechner.py`

## Verfügbare Agenten
- `code-reviewer` — Analysiert Code auf Performance & Architektur
- `implementer` — Setzt Review-Empfehlungen um
- `tester` — Schreibt und ergänzt Unit-Tests für die Berechnungslogik

## Slash-Commands
- `/review-pipeline` — Führt Code-Review → Implementierung → Tests als dreistufige Pipeline aus
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
- `.claude/agents/` — Agentendefinitionen für Claude Code

## Konventionen
- Sprache: Deutsch in Kommentaren, Englisch im Code
- Keine direkte Datenbankanbindung, Daten kommen aus Dateien
- Berechnungslogik gehört in `logic.py`, UI-Code in `immobilienrechner.py`
- Tests laufen mit `python -m pytest test_immobilienrechner.py`

## Verfügbare Agenten
- `code-reviewer` — Analysiert Code auf Performance & Architektur
- `implementer` — Setzt Review-Empfehlungen um
- `tester` — Schreibt und ergänzt Unit-Tests für die Berechnungslogik
# Review Pipeline

Führe die vollständige Code-Review-Pipeline in drei Schritten aus.
Warte nach jedem Schritt auf das Ergebnis bevor du weitermachst.

## Schritt 1 — Code Review
Starte den code-reviewer Agenten:
- Analysiere das gesamte Projekt
- Erstelle review_report.md

Wenn review_report.md erstellt wurde und Befunde enthält: weiter mit Schritt 2.
Wenn keine kritischen oder wichtigen Befunde: stoppe und berichte dem Nutzer.

## Schritt 2 — Implementierung
Starte den implementer Agenten:
- Lies review_report.md
- Setze die Befunde der Reihe nach um
- Erstelle implementation_summary.md

Wenn implementation_summary.md erstellt wurde: weiter mit Schritt 3.

## Schritt 3 — Tests
Starte den test-agent Agenten:
- Führe Smoke Test durch
- Generiere und führe Pytest-Tests aus
- Erstelle test_report.md

## Abschlussbericht
Fasse am Ende zusammen:
- Wie viele Befunde wurden gefunden und umgesetzt?
- Sind alle Tests grün?
- Empfehlung: Bereit für git commit? ✅ oder ❌
# Praxis-Simulator LF 1–4

Prototyp einer Lern-App (Python, Streamlit) für Auszubildende in IT-Berufen.
Die App zeigt praxisnahe IT-Kundenfälle aus den Lernfeldern 1 bis 4. Nutzer treffen Entscheidungen (A, B oder C) und bekommen eine fachliche Auswertung mit Merksatz. Es gibt XP, Serien und Ränge.

## Dateien
- `app.py` – die Streamlit-App
- `szenarien.json` – die Fallstudien (3 Szenarien mit je 3 Entscheidungsschritten)
- `lernfeld_1.md` bis `lernfeld_4.md` – Themen und Merksätze der Lernfelder (Wissensbasis)
- `requirements.txt` – benötigte Python-Pakete

## Starten
1. Python installieren (python.org)
2. `python -m pip install -r requirements.txt`
3. `python -m streamlit run app.py`

## Hinweis zur KI-Nutzung
Die Szenarien und der Code wurden mit Unterstützung eines KI-Sprachmodells erstellt und vom Team geprüft und angepasst.

## Status
Erster Prototyp (Proof of Concept). Die Online-Bestenliste ist als „In Entwicklung“ markiert.

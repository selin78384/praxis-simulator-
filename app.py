"""Praxis-Simulator LF 1-4 (Prototyp, Spiel-Version)
Start mit:  python -m streamlit run app.py
Die Fallstudien stehen in der Datei szenarien.json (gleicher Ordner).
"""
import html
import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Praxis-Simulator LF 1–4", page_icon="🎮")

# ---------- Einstellungen (hier kannst du Farben und Ränge ändern) ----------
LF_FARBEN = {"LF 1": "#2563eb", "LF 2": "#16a34a", "LF 3": "#ea580c", "LF 4": "#9333ea"}
AVATARE = {1: "👩‍💼", 2: "🩺", 3: "🕵️"}  # Symbol pro Fall (id aus der JSON-Datei)
RAENGE = [(0, "🐣 Praktikant"), (300, "💻 Azubi"), (600, "🛠️ Techniker"), (1000, "🏆 IT-Profi")]
PUNKTE_RICHTIG = 100   # XP für eine richtige Entscheidung
PUNKTE_SERIE = 50      # Bonus-XP ab der 2. richtigen Antwort in Folge

CSS = """
<style>
.hero {background: linear-gradient(135deg, #4f46e5, #06b6d4); padding: 22px 26px;
       border-radius: 18px; margin-bottom: 18px;}
.hero h1 {color: white; margin: 0; font-size: 2rem;}
.hero p {color: #e0f2fe; margin: 4px 0 0 0;}
.card {background: linear-gradient(135deg, #ffffff, #eef2ff); border: 2px solid #c7d2fe;
       border-radius: 16px; padding: 16px 18px; margin-bottom: 6px; color: #1e293b;}
.card h3 {margin: 0 0 8px 0; color: #312e81; font-size: 1.25rem;}
.card p {margin: 10px 0 0 0;}
.avatar {font-size: 2rem; margin-right: 10px;}
.badge {display: inline-block; color: white; padding: 2px 10px; border-radius: 999px;
        font-size: 0.8rem; font-weight: 700; margin-right: 6px;}
.status {float: right; font-size: 0.85rem; font-weight: 700; color: #4338ca;}
.ticket {background: #fff7ed; border-left: 8px solid #f97316; border-radius: 12px;
         padding: 14px 18px; color: #431407; margin: 10px 0 16px 0;}
.ticket .kopf {font-weight: 800; color: #c2410c; margin-bottom: 6px;}
.richtig {background: linear-gradient(135deg, #22c55e, #15803d); color: white;
          padding: 14px 18px; border-radius: 14px; font-weight: 700; margin: 10px 0;}
.falsch {background: linear-gradient(135deg, #f87171, #b91c1c); color: white;
         padding: 14px 18px; border-radius: 14px; font-weight: 700; margin: 10px 0;}
.merksatz {background: #eff6ff; border: 2px dashed #3b82f6; color: #1e3a8a;
           padding: 12px 16px; border-radius: 12px; margin: 10px 0;}
.xpbox {background: linear-gradient(135deg, #fde68a, #f59e0b); color: #78350f;
        padding: 8px 14px; border-radius: 999px; font-weight: 800; display: inline-block;
        margin: 4px 6px 4px 0;}
div.stButton > button {width: 100%; border-radius: 14px; border: 2px solid #818cf8;
                       padding: 0.7rem 1rem; font-weight: 600; transition: all 0.15s;}
div.stButton > button:hover {border-color: #4f46e5; transform: translateY(-2px);
                             box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def lade_szenarien():
    """Liest die Szenarien aus der JSON-Datei (UTF-8)."""
    pfad = Path(__file__).parent / "szenarien.json"
    with open(pfad, "r", encoding="utf-8") as datei:
        return json.load(datei)["szenarien"]


szenarien = lade_szenarien()


def fall_by_id(fall_id):
    return next((s for s in szenarien if s["id"] == fall_id), None)


# ---------- Spielstand merken (bleibt bei jedem Klick erhalten) ----------
if "fall_id" not in st.session_state:
    st.session_state.fall_id = None    # welcher Fall läuft gerade
    st.session_state.schritt = 0       # welcher Entscheidungsschritt
    st.session_state.punkte = 0        # richtige Antworten im aktuellen Fall
    st.session_state.antwort = None    # gewählte Option (A/B/C)
    st.session_state.streak = 0        # richtige Antworten in Folge
    st.session_state.xp_fall = 0       # XP im aktuellen Durchlauf
    st.session_state.letzter_gewinn = 0
    st.session_state.best_xp = {}      # beste XP pro Fall
    st.session_state.perfekt = set()   # Fälle ohne Fehler gelöst


# ---------- Aktionen für die Buttons ----------
def starte_fall(fall_id):
    st.session_state.fall_id = fall_id
    st.session_state.schritt = 0
    st.session_state.punkte = 0
    st.session_state.antwort = None
    st.session_state.streak = 0
    st.session_state.xp_fall = 0
    st.session_state.letzter_gewinn = 0


def waehle(option_id, korrekt):
    st.session_state.antwort = option_id
    if korrekt:
        st.session_state.punkte += 1
        st.session_state.streak += 1
        gewinn = PUNKTE_RICHTIG
        if st.session_state.streak >= 2:
            gewinn += PUNKTE_SERIE
    else:
        st.session_state.streak = 0
        gewinn = 0
    st.session_state.letzter_gewinn = gewinn
    st.session_state.xp_fall += gewinn


def weiter():
    st.session_state.schritt += 1
    st.session_state.antwort = None
    fall = fall_by_id(st.session_state.fall_id)
    if st.session_state.schritt >= len(fall["schritte"]):
        # Fall beendet: Bestwert und Fehlerfrei-Abzeichen speichern
        fid = fall["id"]
        alt = st.session_state.best_xp.get(fid, 0)
        st.session_state.best_xp[fid] = max(alt, st.session_state.xp_fall)
        if st.session_state.punkte == len(fall["schritte"]):
            st.session_state.perfekt.add(fid)


def zurueck_zur_auswahl():
    st.session_state.fall_id = None


# ---------- Hilfsfunktionen für die Anzeige ----------
def lf_badges(lernfelder):
    return "".join(
        f'<span class="badge" style="background:{LF_FARBEN.get(lf, "#475569")}">{html.escape(lf)}</span>'
        for lf in lernfelder
    )


def status_text(fall_id):
    if fall_id in st.session_state.perfekt:
        return "🏅 Fehlerfrei"
    if fall_id in st.session_state.best_xp:
        return f"✅ Bestleistung: {st.session_state.best_xp[fall_id]} XP"
    return "🆕 Neu"


def rang_info(xp):
    aktuell, naechster = RAENGE[0], None
    for i, eintrag in enumerate(RAENGE):
        if xp >= eintrag[0]:
            aktuell = eintrag
            naechster = RAENGE[i + 1] if i + 1 < len(RAENGE) else None
    return aktuell, naechster


# ---------- Seitenleiste: Rang, XP, Menü ----------
gesamt_xp = sum(st.session_state.best_xp.values())
(rang_grenze, rang_name), naechster_rang = rang_info(gesamt_xp)

st.sidebar.title("🎮 Praxis-Simulator")
seite = st.sidebar.radio("Menü", ["🏠 Fallauswahl", "🏆 Meine Erfolge"])
st.sidebar.markdown(f"### {rang_name}")
st.sidebar.metric("⭐ Gesamt-XP", gesamt_xp)
if naechster_rang:
    anteil = (gesamt_xp - rang_grenze) / (naechster_rang[0] - rang_grenze)
    st.sidebar.progress(min(max(anteil, 0.0), 1.0),
                        text=f"Noch {naechster_rang[0] - gesamt_xp} XP bis {naechster_rang[1]}")
else:
    st.sidebar.success("Höchster Rang erreicht! 🎉")

# ---------- Seite: Meine Erfolge ----------
if seite == "🏆 Meine Erfolge":
    st.markdown('<div class="hero"><h1>🏆 Meine Erfolge</h1>'
                '<p>Deine Bestleistungen und Abzeichen</p></div>', unsafe_allow_html=True)
    for sz in szenarien:
        spalte1, spalte2 = st.columns([3, 1])
        spalte1.write(f"**{sz['titel']}**")
        spalte2.write(status_text(sz["id"]))
    st.divider()
    st.info("🚧 Online-Bestenliste: In Entwicklung")
    st.stop()

# ---------- Dashboard / Fallauswahl ----------
if st.session_state.fall_id is None:
    st.markdown('<div class="hero"><h1>🎮 Praxis-Simulator LF 1–4</h1>'
                '<p>Löse IT-Kundenfälle, sammle XP und steige im Rang auf!</p></div>',
                unsafe_allow_html=True)
    for sz in szenarien:
        avatar = AVATARE.get(sz["id"], "💻")
        st.markdown(
            f'<div class="card"><span class="status">{status_text(sz["id"])}</span>'
            f'<h3><span class="avatar">{avatar}</span>{html.escape(sz["titel"])}</h3>'
            f'{lf_badges(sz["lernfelder"])}'
            f'<p>{html.escape(sz["kundenfall"])}</p></div>',
            unsafe_allow_html=True,
        )
        st.button("🚀 Fall starten", key=f"start_{sz['id']}",
                  on_click=starte_fall, args=(sz["id"],))
        st.write("")
    st.stop()

# ---------- Interaktive Falllösung ----------
fall = fall_by_id(st.session_state.fall_id)
schritte = fall["schritte"]
i = st.session_state.schritt
anzahl = len(schritte)

# Ende des Falls: Ergebnis zeigen
if i >= anzahl:
    p = st.session_state.punkte
    st.markdown('<div class="hero"><h1>🏁 Fall abgeschlossen!</h1>'
                f'<p>{html.escape(fall["titel"])}</p></div>', unsafe_allow_html=True)
    st.markdown(f"## {'⭐' * p}{'☆' * (anzahl - p)}")
    st.markdown(f'<span class="xpbox">+{st.session_state.xp_fall} XP</span>'
                f'<span class="xpbox">{p} von {anzahl} richtig</span>', unsafe_allow_html=True)
    if p == anzahl:
        st.success("🎉 Perfekt! Fehlerfrei gelöst – du bist ein echter IT-Profi.")
        st.balloons()
    elif p >= anzahl / 2:
        st.info("👍 Gut gemacht! Mit etwas Übung klappt auch der Rest.")
    else:
        st.warning("💪 Übung macht den Meister – probier den Fall gleich noch einmal!")
    spalte1, spalte2 = st.columns(2)
    spalte1.button("🔁 Nochmal spielen", on_click=starte_fall, args=(fall["id"],))
    spalte2.button("🏠 Zur Fallauswahl", on_click=zurueck_zur_auswahl)
    st.stop()

st.markdown(f'<div class="hero"><h1>{AVATARE.get(fall["id"], "💻")} {html.escape(fall["titel"])}</h1>'
            f'<p>{lf_badges(fall["lernfelder"])}</p></div>', unsafe_allow_html=True)

# Kundenfall als Ticket
st.markdown(
    f'<div class="ticket"><div class="kopf">📨 Neue Kundenanfrage · Ticket #KD-{1000 + fall["id"]}</div>'
    f'{html.escape(fall["kundenfall"])}</div>',
    unsafe_allow_html=True,
)

# Fortschritt, XP und Serie
st.progress(i / anzahl, text=f"Schritt {i + 1} von {anzahl}")
st.markdown(f'<span class="xpbox">⭐ {st.session_state.xp_fall} XP</span>'
            f'<span class="xpbox">🔥 Serie: {st.session_state.streak}</span>',
            unsafe_allow_html=True)

schritt = schritte[i]
st.subheader(f"❓ {schritt['frage']}")

if st.session_state.antwort is None:
    # Noch nicht gewählt: Optionen als Buttons anzeigen
    for opt in schritt["optionen"]:
        st.button(
            f"{opt['id']}:  {opt['text']}",
            key=f"opt_{fall['id']}_{i}_{opt['id']}",
            on_click=waehle,
            args=(opt["id"], opt["korrekt"]),
        )
else:
    # Auswertung nach der Wahl
    gewaehlt = next(o for o in schritt["optionen"] if o["id"] == st.session_state.antwort)
    st.write(f"**Deine Wahl:** {gewaehlt['id']}: {gewaehlt['text']}")
    if gewaehlt["korrekt"]:
        text = f"✅ Richtig! +{st.session_state.letzter_gewinn} XP"
        if st.session_state.streak >= 2:
            text += f" · 🔥 Serien-Bonus ({st.session_state.streak} in Folge)"
        st.markdown(f'<div class="richtig">{html.escape(text)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="falsch">❌ Leider falsch – deine Serie ist unterbrochen.</div>',
                    unsafe_allow_html=True)
        richtige = next(o for o in schritt["optionen"] if o["korrekt"])
        st.write(f"**Richtig wäre gewesen:** {richtige['id']}: {richtige['text']}")
    st.write(f"**Konsequenz:** {gewaehlt['konsequenz']}")
    st.markdown(f'<div class="merksatz">📘 <b>Merksatz aus den Lernzetteln:</b><br>'
                f'{html.escape(gewaehlt["merksatz"])}</div>', unsafe_allow_html=True)
    letzter = (i + 1 >= anzahl)
    st.button("🏁 Zum Ergebnis" if letzter else "➡️ Weiter", on_click=weiter)

"""Site web — Radio Télé Source de Vie Goma (97.5 FM)."""
import json, os, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ───────── CONFIGURATION (modifiez ici ou via variables d'environnement) ─────────
STREAM_URL = os.getenv("STREAM_URL", "http://VOTRE-SERVEUR:8000/live")  # Icecast/Shoutcast alimenté par RadioBoss
NOWPLAYING_MODE = os.getenv("NOWPLAYING_MODE", "radioboss")  # "radioboss" | "icecast" | "none"
RADIOBOSS_API = os.getenv("RADIOBOSS_API", "http://127.0.0.1:9000")  # RadioBoss > Options > API
RADIOBOSS_PASS = os.getenv("RADIOBOSS_PASS", "motdepasse")
ICECAST_STATUS = os.getenv("ICECAST_STATUS", "http://VOTRE-SERVEUR:8000/status-json.xsl")

STATION = {
    "nom": "Radio Télé Source de Vie",
    "ville": "Goma, Nord-Kivu, RDC",
    "freq": "97.5 FM",
    "tel": "+243 000 000 000",
    "email": "contact@exemple.cd",
    "adresse": "Goma, Nord-Kivu, RD Congo",
}

# Exemple de grille : remplacez par vos vraies émissions (jour 0 = lundi … 6 = dimanche)
PROGRAMMES = [
    {"heure": "05:00", "titre": "Réveil en louange", "desc": "Chants et méditation pour bien commencer la journée.", "jours": [0, 1, 2, 3, 4, 5, 6]},
    {"heure": "08:00", "titre": "Goma Matin", "desc": "Actualités locales, météo et invités.", "jours": [0, 1, 2, 3, 4]},
    {"heure": "12:00", "titre": "Parole de vie", "desc": "Enseignement biblique et témoignages.", "jours": [0, 1, 2, 3, 4, 5]},
    {"heure": "16:00", "titre": "Jeunesse en action", "desc": "Musique, conseils et débats pour les jeunes.", "jours": [2, 5]},
    {"heure": "19:00", "titre": "Journal du soir", "desc": "Le point sur l'actualité de la région des Grands Lacs.", "jours": [0, 1, 2, 3, 4, 5, 6]},
    {"heure": "09:00", "titre": "Culte en direct", "desc": "Retransmission du culte dominical.", "jours": [6]},
]

_cache = {"t": 0, "data": {"artist": "", "title": "Radio Télé Source de Vie"}}


def fetch_now_playing():
    if time.time() - _cache["t"] < 8:
        return _cache["data"]
    try:
        if NOWPLAYING_MODE == "radioboss":
            url = f"{RADIOBOSS_API}/?pass={RADIOBOSS_PASS}&action=playbackinfo"
            root = ET.fromstring(urllib.request.urlopen(url, timeout=4).read())
            cur = root.find(".//CurrentTrack")
            data = {"artist": cur.get("ARTIST", ""), "title": cur.get("TITLE", "")}
        elif NOWPLAYING_MODE == "icecast":
            j = json.load(urllib.request.urlopen(ICECAST_STATUS, timeout=4))
            src = j["icestats"]["source"]
            src = src[0] if isinstance(src, list) else src
            raw = src.get("title", "")
            artist, _, title = raw.partition(" - ")
            data = {"artist": artist if title else "", "title": title or raw}
        else:
            return _cache["data"]
        if data["title"] or data["artist"]:
            _cache.update(t=time.time(), data=data)
    except Exception:
        pass  # on garde la dernière info connue
    return _cache["data"]


@app.route("/")
def index():
    return render_template("index.html", s=STATION, stream=STREAM_URL, programmes=PROGRAMMES,
                           today=datetime.now().weekday(), year=datetime.now().year)


@app.route("/api/now-playing")
def now_playing():
    return jsonify(fetch_now_playing())


@app.route("/contact", methods=["POST"])
def contact():
    f = request.form
    if not f.get("message", "").strip():
        return jsonify(ok=False, error="Le message est vide."), 400
    entry = {"date": datetime.now().isoformat(timespec="seconds"), "nom": f.get("nom", "")[:80],
             "contact": f.get("contact", "")[:120], "message": f["message"][:2000]}
    with open("messages.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

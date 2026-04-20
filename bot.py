import requests
import time
import threading
from flask import Flask
import os
from datetime import datetime

# ===== KONFIG =====
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 300  # 5 minut

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ===== TELEGRAM =====
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
        print("TELEGRAM:", r.status_code, r.text)
    except Exception as e:
        print("Błąd Telegram:", e)

# ===== API =====
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}"
    
    try:
        r = requests.get(url)
        print("API STATUS:", r.status_code)

        data = r.json()

        # ❌ jeśli API zwróciło błąd
        if isinstance(data, dict):
            return f"❌ API ERROR: {data}"

        # ❌ brak danych
        if not data:
            return "❌ Brak meczów"

        # ✅ pobierz pierwsze 5 meczów
        matches = []
        for m in data[:5]:
            home = m.get("home_team", "?")
            away = m.get("away_team", "?")
            matches.append(f"{home} vs {away}")

        msg = "🔥 MECZE 🔥\n\n" + "\n".join(matches)
        return msg

    except Exception as e:
        return f"❌ Błąd: {e}"

# ===== PĘTLA =====
def main_loop():
    print("🚀 Bot działa...")

    while True:
        print(f"\n⏱ {datetime.now().strftime('%H:%M:%S')}")
        result = get_matches()
        send(result)
        time.sleep(CHECK_INTERVAL)

# ===== START =====
threading.Thread(target=main_loop).start()

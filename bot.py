import requests
import time
import threading
from flask import Flask
import os
from datetime import datetime

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 300

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
        print("TELEGRAM:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)

# ===== API =====
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}"

    try:
        r = requests.get(url)

        print("API STATUS:", r.status_code)
        print("API RAW:", r.text[:200])  # 🔥 kluczowe

        if r.status_code != 200:
            return f"❌ API STATUS {r.status_code}"

        try:
            data = r.json()
        except:
            return f"❌ NIE JSON: {r.text[:100]}"

        # jeśli API zwróciło błąd
        if isinstance(data, dict):
            return f"❌ API ERROR: {data}"

        if not data:
            return "❌ Brak meczów"

        matches = []
        for m in data[:5]:
            home = m.get("home_team", "?")
            away = m.get("away_team", "?")
            matches.append(f"{home} vs {away}")

        return "🔥 MECZE 🔥\n\n" + "\n".join(matches)

    except Exception as e:
        return f"❌ Błąd: {e}"

# ===== LOOP =====
def main():
    print("🚀 Bot działa...")

    while True:
        print("⏱", datetime.now().strftime("%H:%M:%S"))
        result = get_matches()
        send(result)
        time.sleep(CHECK_INTERVAL)

threading.Thread(target=main).start()

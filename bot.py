import requests
import time
import threading
from flask import Flask
import os

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 60

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    print("TELEGRAM:", r.status_code, r.text)

def test_api():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}"
    r = requests.get(url)
    print("API STATUS:", r.status_code)
    print("API TEXT:", r.text[:500])  # skrócone

    try:
        data = r.json()
        if not data:
            return "❌ API zwróciło pustą listę"
        first = data[0]
        return f"OK: {first['home_team']} vs {first['away_team']}"
    except Exception as e:
        return f"Błąd parsowania: {e}"

print("🚀 START")

while True:
    send("🔄 TEST START")
    result = test_api()
    send(result)
    time.sleep(CHECK_INTERVAL)

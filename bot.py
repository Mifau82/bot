import requests
import json
import time
import threading
from datetime import datetime
from flask import Flask

# ===== KONFIG =====
API_KEY = "6a967fb17daf3c5e0d777ceceab644d8"
BOT_TOKEN = "8795419005:AAFwSkiSvFmSU8cgsxMywGC6UIv7m2yDxtM"
CHAT_ID = 8211336862

FILE = "results.json"
CHECK_INTERVAL = 300  # 5 minut

# ===== FLASK (żeby Render nie usypiał) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# ===== TELEGRAM =====
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}

    try:
        r = requests.post(url, data=data)
        print("Telegram:", r.status_code, r.text)
    except Exception as e:
        print("Błąd telegram:", e)

# ===== PLIK =====
def load_results():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_results(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# ===== TESTOWA FUNKCJA (na start żeby sprawdzić czy działa) =====
def check_new_matches():
    now = datetime.now().strftime("%H:%M:%S")
    msg = f"⏰ Bot działa: {now}"
    send_telegram(msg)

# ===== START =====
print("🚀 Bot działa...")

while True:
    check_new_matches()
    time.sleep(CHECK_INTERVAL)

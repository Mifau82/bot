import requests
import json
import time
import threading
from datetime import datetime
from flask import Flask
import os

# ===== KONFIG (z Render ENV!) =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FILE = "results.json"
CHECK_INTERVAL = 300  # 5 minut

# ===== FLASK (utrzymuje serwer przy życiu) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

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

# ===== TEST =====
def check():
    now = datetime.now().strftime("%H:%M:%S")
    msg = f"⏰ Bot działa: {now}"
    send_telegram(msg)

# ===== START =====
print("🚀 Bot działa...")

while True:
    check()
    time.sleep(CHECK_INTERVAL)

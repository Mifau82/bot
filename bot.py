import requests
import json
import time
import threading
from datetime import datetime
from flask import Flask

# ===== KONFIG =====
API_KEY = "TU_WSTAW_API"
BOT_TOKEN = "TU_WSTAW_TOKEN"
CHAT_ID = "8211336862"

FILE = "results.json"
CHECK_INTERVAL = 300

# ===== FLASK =====
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
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        res = requests.post(url, data=data)
        print("STATUS:", res.status_code)
        print("ODPOWIEDŹ:", res.text)
    except Exception as e:
        print("❌ Błąd Telegram:", e)

# ===== TEST NA START =====
send_telegram("🚀 Bot wystartował!")

# ===== PĘTLA =====
print("🚀 Bot działa...")

while True:
    print("⏱️", datetime.now().strftime("%H:%M:%S"))

    # TU NA RAZIE TEST
    send_telegram("Test działania")

    time.sleep(CHECK_INTERVAL)

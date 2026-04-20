import requests
import time
import threading
from datetime import datetime
from flask import Flask

# ===== KONFIG =====
BOT_TOKEN = "TU_WSTAW_TOKEN"
CHAT_ID = "8211336862"
CHECK_INTERVAL = 300

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ===== TELEGRAM =====
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}

    try:
        res = requests.post(url, data=data)
        print("STATUS:", res.status_code)
        print("ODPOWIEDŹ:", res.text)
    except Exception as e:
        print("❌ Błąd:", e)

# ===== BOT =====
def run_bot():
    print("🚀 Bot działa...")
    send_telegram("🔥 Bot wystartował!")

    while True:
        print("⏱️", datetime.now().strftime("%H:%M:%S"))
        send_telegram("Test działania")
        time.sleep(CHECK_INTERVAL)

# ===== START =====
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    threading.Thread(target=run_bot).start()

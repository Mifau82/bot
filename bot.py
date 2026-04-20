import os
import time
import threading
import requests
from flask import Flask

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ===== FLASK (utrzymanie online) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# ===== TELEGRAM =====
last_update_id = None

def send_message(text, chat_id):
    requests.post(URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def get_updates():
    global last_update_id

    params = {"timeout": 100}
    if last_update_id:
        params["offset"] = last_update_id + 1

    try:
        res = requests.get(URL + "getUpdates", params=params)
        data = res.json()

        for update in data["result"]:
            last_update_id = update["update_id"]

            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                print(f"Nowa wiadomość: {text}")

                # ===== /start =====
                if text == "/start":
                    send_message("👋 Bot działa!", chat_id)

                # ===== test =====
                elif text.lower() == "test":
                    send_message("✅ Wszystko działa", chat_id)

    except Exception as e:
        print("Błąd:", e)

# ===== START =====
print("🚀 Bot wystartował")

while True:
    get_updates()
    time.sleep(2)

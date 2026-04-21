import requests
import time
import threading
from flask import Flask
import os
import json
from datetime import datetime, timezone, timedelta

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FILE_SENT = "sent.json"
FILE_ODDS = "odds.json"
FILE_ALERT = "alerts.json"

MIN_ODD = 1.60
MAX_ODD = 1.99
MAX_CHANGE = 0.10

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
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ===== PLIKI =====
def load(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ===== INTERWAŁ (limit API) =====
def get_interval():
    hour = datetime.now().hour

    if 8 <= hour <= 23:
        return 5400   # 1.5h
    else:
        return 14400  # 4h

# ===== API =====
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?regions=eu&markets=h2h,totals&apiKey={API_KEY}"

    try:
        r = requests.get(url)
        data = r.json()

        if isinstance(data, dict):
            print("API ERROR:", data)
            return []

        matches = []

        for m in data:
            try:
                commence = datetime.fromisoformat(m["commence_time"].replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)

                if commence.date() != now.date():
                    continue

                match_id = m["id"]
                home = m["home_team"]
                away = m["away_team"]

                bookmakers = m.get("bookmakers", [])
                if not bookmakers:
                    continue

                markets = bookmakers[0]["markets"]

                home_odds = None
                over15_odds = None

                for market in markets:
                    if market["key"] == "h2h":
                        for o in market["outcomes"]:
                            if o["name"] == home:
                                home_odds = o["price"]

                    if market["key"] == "totals":
                        for o in market["outcomes"]:
                            if o["name"] == "Over" and o.get("point") == 1.5:
                                over15_odds = o["price"]

                if home_odds:
                    matches.append({
                        "id": match_id,
                        "home": home,
                        "away": away,
                        "odds": home_odds,
                        "over15": over15_odds,
                        "time": commence.isoformat()
                    })

            except:
                continue

        return matches

    except Exception as e:
        print("API ERROR:", e)
        return []

# ===== LOOP =====
def main():
    print("🚀 Bot działa...")

    sent = load(FILE_SENT)
    odds_mem = load(FILE_ODDS)
    alerts = load(FILE_ALERT)

    while True:
        now = datetime.now(timezone.utc)
        matches = get_matches()
        new_msgs = []

        for m in matches:
            mid = m["id"]
            odds = m["odds"]
            over = m.get("over15", "brak")
            match_time = datetime.fromisoformat(m["time"])

            # zakres kursu
            if not (MIN_ODD <= odds <= MAX_ODD):
                continue

            # filtr stabilności
            if mid in odds_mem:
                if abs(odds - odds_mem[mid]) > MAX_CHANGE:
                    odds_mem[mid] = odds
                    continue

            odds_mem[mid] = odds

            # nowe mecze
            if mid not in sent:
                sent[mid] = True
                new_msgs.append(
                    f"{m['home']} vs {m['away']}\n"
                    f"🏠 1: {odds}\n"
                    f"⚽ +1.5: {over}"
                )

            # przypomnienie 10 min przed
            alert_time = match_time - timedelta(minutes=10)

            if mid not in alerts and alert_time <= now < match_time:
                send(f"⏰ ZA 10 MIN: {m['home']} vs {m['away']}")
                alerts[mid] = True

        if new_msgs:
            msg = "🔥 STABILNE MECZE (1.60–1.99) 🔥\n\n" + "\n\n".join(new_msgs)
            send(msg)

        save(FILE_SENT, sent)
        save(FILE_ODDS, odds_mem)
        save(FILE_ALERT, alerts)

        sleep_time = get_interval()
        print(f"⏳ Następne sprawdzenie za {sleep_time/60:.0f} min")
        time.sleep(sleep_time)

threading.Thread(target=main).start()

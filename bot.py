import requests
import json
import time
from datetime import datetime
import os
from flask import Flask
import threading

# ====== KONFIG ======
API_KEY = "TU_WKLEJ_API_KEY"
BOT_TOKEN = "TU_WKLEJ_TOKEN_TELEGRAM"
CHAT_ID = "TU_WKLEJ_CHAT_ID"

FILE = "results.json"
CHECK_INTERVAL = 300  # 5 min

# ====== FLASK (żeby Render nie usypiał) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa ✅"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# ====== PLIK ======
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump([], f)

# ====== TELEGRAM ======
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}

    try:
        requests.post(url, data=data)
        print("📲 Telegram wysłany")
    except Exception as e:
        print("Błąd Telegram:", e)

# ====== DANE ======
def load_results():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_results(results):
    with open(FILE, "w") as f:
        json.dump(results, f)

# ====== API ======
def fetch_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        data = requests.get(url, params=params).json()
    except Exception as e:
        print("Błąd API:", e)
        return []

    today = datetime.now().date()
    matches = []

    for match in data:
        home = match.get("home_team")
        away = match.get("away_team")
        league = match.get("sport_title", "Unknown")
        match_id = match.get("id")
        commence_time = match.get("commence_time")

        if not commence_time:
            continue

        try:
            match_date = datetime.fromisoformat(commence_time.replace("Z", "")).date()
        except:
            continue

        if match_date != today:
            continue

        best_odds = None

        for bookmaker in match.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    if outcome.get("name") != home:
                        continue

                    odds = outcome.get("price")
                    if odds and (best_odds is None or odds > best_odds):
                        best_odds = odds

        if best_odds and 1.60 <= best_odds <= 1.99:
            matches.append({
                "id": match_id,
                "home": home,
                "away": away,
                "league": league,
                "odds": round(best_odds, 2),
                "result": None
            })

    return matches

# ====== LOGIKA ======
def check_new_matches():
    results = load_results()
    new_matches = []
    matches = fetch_matches()

    for match in matches:
        if not any(m["id"] == match["id"] for m in results):
            results.append(match)
            new_matches.append(match)

    if new_matches:
        msg = "🔥 NOWE MECZE 🔥\n\n"
        for m in new_matches:
            msg += f"{m['home']} vs {m['away']}\n{m['league']} @ {m['odds']}\n\n"
        send_telegram(msg)
    else:
        print("Brak nowych meczów")

    save_results(results)

def show_stats():
    results = load_results()
    wins = sum(1 for m in results if m["result"] == "W")
    losses = sum(1 for m in results if m["result"] == "L")
    total = wins + losses
    acc = round((wins / total) * 100, 2) if total else 0

    print(f"📊 W:{wins} L:{losses} Skuteczność:{acc}%")

# ====== START ======
print("🚀 Bot działa...")

while True:
    print(f"\n⏱ {datetime.now().strftime('%H:%M:%S')}")
    check_new_matches()
    show_stats()
    time.sleep(CHECK_INTERVAL)

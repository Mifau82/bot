bot.py
import requests
import json
import shutil
import time
from datetime import datetime

API_KEY = "6a967fb17daf3c5e0d777ceceab644d8"
FILE = "results.json"

BOT_TOKEN = "8640276334:AAEPq4HOdXrk3K_EUod3R8Z1i_Oasdx4jnE"
CHAT_ID = "8211336862"

CHECK_INTERVAL = 300  # 5 min

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
        print("📲 Telegram wysłany")
    except:
        print("Błąd Telegram")

def load_results():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_results(results):
    with open(FILE, "w") as f:
        json.dump(results, f)

def fetch_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    data = requests.get(url, params=params).json()
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

        match_date = datetime.fromisoformat(commence_time.replace("Z", "")).date()
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
    acc = round((wins/total)*100,2) if total else 0
    print(f"📊 W:{wins} L:{losses} Skuteczność:{acc}%")

def input_results():
    results = load_results()
    print("\nWpisz wyniki (np: 0W 1L) lub ENTER żeby pominąć")
    user_input = input(">> ").strip().upper()

    if user_input:
        try:
            for entry in user_input.split():
                idx = int(entry[:-1])
                res = entry[-1]
                if res in ["W","L"]:
                    results[idx]["result"] = res
            save_results(results)
            print("Zapisano ✅")
        except:
            print("Błąd wpisu ❌")

print("🚀 System działa...")

while True:
    print(f"\n⏱ {datetime.now().strftime('%H:%M:%S')}")
    check_new_matches()
    show_stats()
    input_results()
    time.sleep(CHECK_INTERVAL)

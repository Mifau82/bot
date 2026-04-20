import time
import requests
import os
from datetime import datetime, timedelta

# ====== ENV ======
API_URL = os.getenv("API_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL_IDLE = 10800   # 3 godziny
CHECK_INTERVAL_ACTIVE = 600   # 10 minut

# zapamiętane mecze (żeby nie spamować)
sent_matches = set()


# ====== TELEGRAM ======
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


# ====== API ======
def get_matches():
    response = requests.get(API_URL)
    data = response.json()

    matches = []

    for m in data:
        match_time = datetime.fromisoformat(m["date"])

        matches.append({
            "time": match_time,
            "home": m["home"],
            "away": m["away"]
        })

    return matches


# ====== LOGIKA ======
def matches_soon(matches):
    now = datetime.utcnow()
    soon = now + timedelta(hours=3)

    return any(now <= m["time"] <= soon for m in matches)


def process_matches(matches):
    today = datetime.utcnow().date()

    for m in matches:
        match_id = f"{m['home']}_{m['away']}_{m['time']}"

        if m["time"].date() == today and match_id not in sent_matches:
            msg = f"⚽ {m['home']} vs {m['away']} | {m['time'].strftime('%H:%M')}"
            print("📤", msg)
            send_telegram(msg)

            sent_matches.add(match_id)


# ====== GŁÓWNA PĘTLA ======
while True:
    try:
        print("🔄 Sprawdzam mecze...")

        matches = get_matches()
        process_matches(matches)

        if matches_soon(matches):
            sleep_time = CHECK_INTERVAL_ACTIVE
            print("⚽ Tryb AKTYWNY (co 10 min)")
        else:
            sleep_time = CHECK_INTERVAL_IDLE
            print("😴 Tryb OSZCZĘDNY (co 3h)")

    except Exception as e:
        print("❌ Błąd:", e)
        sleep_time = CHECK_INTERVAL_IDLE

    print(f"⏳ Następne sprawdzenie za {sleep_time/60:.0f} min")
    time.sleep(sleep_time)

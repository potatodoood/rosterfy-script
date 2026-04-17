from datetime import datetime, timedelta
import random
import requests
import time
import json
import os
import pytz

URL = os.getenv("ROSTERFY_URL")
HEADERS = json.loads(os.getenv("ROSTERFY_HEADERS", "{}"))

EVENTS_WEBHOOK_URL = os.getenv("EVENTS_WEBHOOK_URL")
STATUS_WEBHOOK_URL = os.getenv("STATUS_WEBHOOK_URL")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

SEEN_IDS_FILE = "seen_ids.json"

WORK_START = 8
WORK_END = 21

# Time
tz = pytz.timezone("Australia/Melbourne")
now = datetime.now(tz)

def now_str():
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# Notifications
def notify_discord(message, status=False, ping=False):
    url = STATUS_WEBHOOK_URL if status else EVENTS_WEBHOOK_URL
    if ping:
        message = f"@everyone {message}"
    try:
        requests.post(url, json={"content": message}, timeout=5)
    except Exception as e:
        print(f"Discord failed: {e}")


def notify_phone(message, title="Rosterfy Alert", priority="default", tags=None):
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags" : tags,
    }
    try:
        requests.post(
            f"{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=5
        )
    except Exception as e:
        print(f"ntfy failed: {e}")

# Randomisation
if not (WORK_START <= now.hour < WORK_END):
    print("⏰ Outside work hours. Exiting.")
    exit()

# Seen IDS
try:
    with open(SEEN_IDS_FILE, "r") as f:
        seen_ids = set(json.load(f))
except FileNotFoundError:
    seen_ids = set()

# Checking events logic (API)
def get_events():
    events = []
    for page in range(1,4):
        params= {
            "page": page,
            "perPage" : 12
        }
        r = requests.get(URL, params=params, headers=HEADERS)
        if r.status_code == 401:
            notify_discord("❌ Token expired — update authorization header", status=True)
            notify_phone(
                "Token expired — update header",
                title="Rosterfy Error",
                priority="high",
                tags="error,alert"
            )
            exit()
        data = r.json()
        
        for item in data.get("data", []):
            obj = item.get("object", {})
            events.append({
                "id": obj.get("id"),
                "name": obj.get("name"),
                "start": obj.get("start_timestamp"),
                "location": obj.get("address", {}).get("city", "Unknown")
            })
    return events

# Main logic
def check_events_once():
    global seen_ids
    events = get_events()
    current_ids = {e["id"] for e in events}

    # Find new events
    new_ids = current_ids - seen_ids

    for event in events:
        if event["id"] in new_ids:
            message = (
                f"🚨 NEW SHIFT FOUND\n"
                f"{event['name']}\n"
                f"📍 {event['location']}\n"
                f"🕒 {event['start']}"
            )
            print(message)
            notify_discord(message, status=False, ping=True)
            notify_phone(message, tags="rotating_light")
    # Update seen events
    seen_ids.update(new_ids)
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(sorted(seen_ids), f)


# Running
try:
    # Random skips
    if random.random() < 0.2:
        print("Skipping this run")
        notify_discord("Skipping this run!", status=True)
        notify_phone("SKipping", tags="rotating_light")
        exit()
    notify_discord(f"🚀 Script started at {now_str()}", status=True)
    # delay = random.randint(0, 3*60)
    delay = 0
    waketime = datetime.now(tz) + timedelta(seconds=delay)
    notify_discord(f"⏳ Sleeping for {delay//60} minutes (until {waketime.strftime('%H:%M')})", status=True, ping=False)
    time.sleep(delay)
    check_events_once()
    notify_discord(f"⏹ Script finished at {now_str()}", status=True)
except Exception as e:
    notify_discord(f"❌ Script crashed:\n{e}", status=True)
    notify_phone(
        f"Script crashed: {e}",
        title="Rosterfy Error",
        priority="high",
        tags="error,alert"
    )
    raise

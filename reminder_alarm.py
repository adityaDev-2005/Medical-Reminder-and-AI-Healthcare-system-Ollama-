

import requests
from datetime import datetime
import time
import winsound
import pyttsx3

BASE_URL = "http://127.0.0.1:8000"

print("Reminder Service Started")

engine = pyttsx3.init("sapi5")
engine.setProperty("rate", 170)

seen_ids = set()

try:
    response = requests.get(f"{BASE_URL}/reminders")
    if response.status_code == 200:
        reminders = response.json()
        now = datetime.now()
        for rem in reminders:
            remind_time = datetime.fromisoformat(rem["remind_time"])
            if remind_time < now:
                seen_ids.add(rem["id"])
except:
    pass

while True:
    try:
        response = requests.get(f"{BASE_URL}/reminders")

        if response.status_code != 200:
            time.sleep(5)
            continue

        reminders = response.json()
        now = datetime.now()

        for rem in reminders:
            rid = rem["id"]

            if rid in seen_ids:
                continue

            remind_time = datetime.fromisoformat(rem["remind_time"])

            if now >= remind_time:
                seen_ids.add(rid)

                winsound.Beep(1000, 700)
                time.sleep(0.2)
                winsound.Beep(1000, 700)

                engine.say(f"Reminder. {rem['task']}")
                engine.runAndWait()

        time.sleep(1)

    except:
        time.sleep(5)
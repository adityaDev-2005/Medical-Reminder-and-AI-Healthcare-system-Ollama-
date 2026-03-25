# import pyttsx3

# engine = pyttsx3.init('sapi5')
# engine.say("This is a test reminder")
# engine.runAndWait()

# import winsound
# import time

# print("Beep test starting...")

# winsound.Beep(1000, 500)
# time.sleep(0.2)
# winsound.Beep(1000, 500)

# print("Beep test finished.")

import time
from datetime import datetime, timedelta
import winsound

print("Simple Reminder Test")
print("Reminder will ring in 1 minute...")

# Set reminder 1 minute ahead
remind_time = datetime.now() + timedelta(minutes=1)
remind_time = remind_time.replace(second=0, microsecond=0)

print("Reminder set for:", remind_time.strftime("%Y-%m-%d %H:%M"))

while True:
    now = datetime.now().replace(second=0, microsecond=0)

    if now == remind_time:
        print("🔔 Reminder Triggered!")

        winsound.Beep(1000, 700)
        time.sleep(0.2)
        winsound.Beep(1000, 700)

        break

    time.sleep(1)
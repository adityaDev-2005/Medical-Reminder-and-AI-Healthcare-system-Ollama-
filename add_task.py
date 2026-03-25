import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"


def format_time(dt_string):
    dt = datetime.fromisoformat(dt_string)
    return dt.strftime("%d %b %Y  %I:%M %p")


def add_reminder():
    print("\n--- Add Reminder ---")

    task = input("Enter task: ").strip()
    date = input("Enter date (YYYY-MM-DD): ").strip()
    time_in = input("Enter time (HH:MM 24hr): ").strip()

    try:
        dt = datetime.strptime(f"{date} {time_in}", "%Y-%m-%d %H:%M")
        remind_time = dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date/time format")
        return

    r = requests.post(
        f"{BASE_URL}/reminder",
        params={"task": task, "remind_time": remind_time},
    )

    if r.status_code == 200:
        print("Reminder added")
    else:
        print("Failed:", r.text)


def view_reminders(return_data=False):
    print("\n--- Your Reminders ---")

    r = requests.get(f"{BASE_URL}/reminders")

    if r.status_code != 200:
        print("Could not fetch reminders")
        return []

    data = r.json()

    if not data:
        print("No reminders found")
        return []

    for i, rem in enumerate(data, start=1):
        nice_time = format_time(rem["remind_time"])
        print(f"{i}. {rem['task']}  |  {nice_time}")

    if return_data:
        return data


def delete_reminder(user_input):
    text = user_input.lower()

    if "all" in text or "everything" in text or "clear" in text:
        confirm = input("Delete ALL reminders? (yes/no): ").lower()
        if confirm != "yes":
            print("Cancelled")
            return

        r = requests.delete(f"{BASE_URL}/reminders/all")
        if r.status_code == 200:
            print("All reminders deleted")
        else:
            print("Failed:", r.text)
        return

    reminders = view_reminders(return_data=True)
    if not reminders:
        return

    number = None
    for w in text.split():
        if w.isdigit():
            number = int(w)
            break

    if number is None:
        number = int(input("Enter reminder number to delete: "))

    if number < 1 or number > len(reminders):
        print("Invalid selection")
        return

    rid = reminders[number - 1]["id"]

    r = requests.delete(f"{BASE_URL}/reminder/{rid}")

    if r.status_code == 200:
        print("Reminder deleted")
    else:
        print("Failed to delete")


ADD_WORDS = ["add", "remind", "create", "set"]
SHOW_WORDS = ["show", "list", "view", "display", "tasks"]
DELETE_WORDS = ["delete", "remove", "cancel", "clear"]
EXIT_WORDS = ["exit", "quit", "bye"]


print("\nAssistant ready. Type naturally: add, show, delete, exit\n")

while True:
    user_input = input("You: ").lower().strip()

    if any(word in user_input for word in ADD_WORDS):
        add_reminder()

    elif any(word in user_input for word in SHOW_WORDS):
        view_reminders()

    elif any(word in user_input for word in DELETE_WORDS):
        delete_reminder(user_input)

    elif any(word in user_input for word in EXIT_WORDS):
        print("Goodbye!")
        break

    else:
        print("I didn't understand.")
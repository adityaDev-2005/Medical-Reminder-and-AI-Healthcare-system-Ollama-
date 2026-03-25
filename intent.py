import subprocess
import sys
import os
import psutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "new_llm+api.py")
TASK_PATH = os.path.join(BASE_DIR, "backend", "add_task.py")
REMINDER_PATH = os.path.join(BASE_DIR, "backend", "reminder_alarm.py")
creationflags=subprocess.CREATE_NO_WINDOW

def is_reminder_running():
    for process in psutil.process_iter(['cmdline']):
        try:
            if process.info['cmdline'] and "reminder_alarm.py" in " ".join(process.info['cmdline']):
                return True
        except:
            pass
    return False

def start_reminder_service():
    if is_reminder_running():
        print("Reminder service already running.")
        return

    subprocess.Popen(
        [sys.executable, REMINDER_PATH],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    print("Reminder service started silently.")

print("\n===== Medical AI Healthcare System =====\n")

while True:

    print("\nSelect an option:")
    print("1 → Manage Medical Reminders")
    print("2 → AI Healthcare Assistant")
    print("3 → Exit System")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        print("\nOpening Reminder Manager...\n")

        # Start reminder service only here
        start_reminder_service()

        subprocess.run([sys.executable, TASK_PATH])

    elif choice == "2":
        print("\nOpening AI Healthcare Assistant...\n")
        subprocess.run([sys.executable, MODEL_PATH])

    elif choice == "3":
        print("\nExiting system. Goodbye!\n")
        break

    else:
        print("Invalid choice. Please try again.")
import ollama
import pyttsx3
import requests
import subprocess
import time
import sys
from datetime import datetime
from geopy.geocoders import Nominatim
import speech_recognition as sr

MODEL_NAME = "phi3"
OLLAMA_URL = "http://localhost:11434"

# ------------------- Speech Engine -------------------

engine = pyttsx3.init("sapi5")
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

def speak(text):
    print("AI:", text)
    try:
        engine.stop()

        lines = text.split("\n")

        for line in lines:
            clean_line = line.strip()
            if clean_line:
                engine.say(clean_line)
                engine.runAndWait()

    except Exception as e:
        print("Speech engine error:", e)

# ------------------- Ollama Control -------------------

def is_ollama_running():
    try:
        requests.get(OLLAMA_URL)
        return True
    except:
        return False

def start_ollama():
    print("Checking Ollama server...")

    if is_ollama_running():
        print("Ollama already running.")
        return

    print("Starting Ollama server...")
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(10):
        time.sleep(1)
        if is_ollama_running():
            print("Ollama started successfully.")
            return

    print("Failed to start Ollama.")
    sys.exit()

def check_model():
    try:
        ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "hello"}]
        )
    except:
        print(f"Model '{MODEL_NAME}' not found. Pulling model...")
        subprocess.run(["ollama", "pull", MODEL_NAME])

# ------------------- Auto Start -------------------

start_ollama()
check_model()

# ------------------- Weather Setup -------------------

geolocator = Nominatim(user_agent="ai_healthcare")

def get_coordinates(place):
    try:
        loc = geolocator.geocode(place)
        if loc:
            return loc.latitude, loc.longitude
    except:
        pass
    return None, None

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    return requests.get(url, params=params).json()

def weather_speech(place, weather):
    c = weather["current_weather"]
    return (
        f"The temperature in {place} is {c['temperature']} degrees Celsius. "
        f"Wind speed is {c['windspeed']} kilometers per hour."
    )

# ------------------- Voice Setup -------------------

recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source, 0.5)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
    try:
        text = recognizer.recognize_google(audio)
        print("User:", text)
        return text
    except:
        return ""

# ------------------- Interface -------------------

print("\n===== AI Healthcare Assistant =====\n")
print("Select Input Mode:")
print("1 → Text")
print("2 → Voice")

mode = input("Enter: ").strip()
use_voice = mode == "2"

print("\nAI Ready. Type 'exit' to return.\n")

# ------------------- Main Loop -------------------

while True:

    user_input = listen() if use_voice else input("User: ").strip()

    if not user_input:
        continue

    text = user_input.lower()
    thank_words = ["thanks", "thank you", "okay thanks", "ok thanks"]

    if any(word in text for word in thank_words):
        speak("You're welcome. Take care. Goodbye.")
        print("Returning to main menu...\n")
        break

    now = datetime.now()

    if text in ["exit", "quit", "bye"]:
        print("Returning to main menu...\n")
        break

    if "time" in text:
        speak(now.strftime("The time is %I:%M %p."))
        continue

    if "date" in text:
        speak(now.strftime("Today's date is %d %B %Y."))
        continue

    if "weather" in text:
        place = user_input.replace("weather", "").strip()
        lat, lon = get_coordinates(place)

        if not lat:
            speak("Location not found.")
            continue

        weather = get_weather(lat, lon)
        speak(weather_speech(place, weather))
        continue

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                "role": "system",
                "content": "You are a friendly healthcare assistant. Start with one short understanding sentence like 'Here are some suggestions.' Then give 3 to 5 short bullet points. Keep it concise and practical."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        reply = response["message"]["content"]
        speak(reply)

    except:
        print("Connection error with Ollama.")
        break
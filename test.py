import ollama
import pyttsx3
import speech_recognition as sr
import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

def speak(text):
    engine = pyttsx3.init(driverName='sapi5')
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("User:", text)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Speech service is unavailable.")
        return ""

input_model = "phi4"

geolocator = Nominatim(user_agent="ai_assistant_weather")

def get_coordinates(place):
    try:
        location = geolocator.geocode(place)
        if location:
            return location.latitude, location.longitude
        return None, None
    except:
        return None, None

def get_weather_by_coords(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    r = requests.get(url, params=params)
    return r.json()

def extract_place_with_llm(user_input):
    prompt = f"""
    Extract the place name from this sentence.
    Return ONLY the place name, nothing else.

    Sentence: "{user_input}"
    """
    response = ollama.chat(
        model=input_model,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.message.content.strip()

def explain_weather_with_llm(weather_data):
    prompt = f"""
    You are a weather assistant.
    Here is the real-time weather data:
    {weather_data}

    Explain it naturally for speech output.
    """
    response = ollama.chat(
        model=input_model,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.message.content

concluding_phrases = ['thanks', 'thank you', 'bye', 'exit']
time_keywords = ['time']
date_keywords = ['date']
weather_keywords = ['weather', 'temperature', 'forecast', 'climate']

speak("Hello. Choose input mode. Type one for text, two for voice.")
print("1 → Text Input\n2 → Voice Input")

mode = ""
while mode not in ["1", "2"]:
    mode = input("Enter choice (1/2): ").strip()

use_voice_input = (mode == "2")
speak("Voice input mode selected." if use_voice_input else "Text input mode selected.")

while True:

    if use_voice_input:
        user_input = listen().strip()
        if not user_input:
            continue
    else:
        user_input = input("User: ").strip()

    user_input_clean = user_input.lower()
    now = datetime.now()

    if any(p in user_input_clean for p in concluding_phrases):
        speak("It was nice talking to you. Goodbye.")
        break

    if any(w in user_input_clean for w in time_keywords):
        speak(now.strftime("The current time is %I:%M %p."))
        continue

    if any(w in user_input_clean for w in date_keywords):
        speak(now.strftime("Today's date is %d %B %Y."))
        continue

    if 'day' in user_input_clean:
        if 'tomorrow' in user_input_clean:
            speak(f"Tomorrow will be {(now + timedelta(days=1)).strftime('%A')}.")
        elif 'yesterday' in user_input_clean:
            speak(f"Yesterday was {(now - timedelta(days=1)).strftime('%A')}.")
        else:
            speak(f"Today is {now.strftime('%A')}.")
        continue

    if any(w in user_input_clean for w in weather_keywords):

        place = extract_place_with_llm(user_input)
        print("DEBUG place:", place)

        if not place:
            speak("I could not detect the place name.")
            continue

        lat, lon = get_coordinates(place)

        if lat is None or lon is None:
            speak("I could not find that location.")
            continue

        weather_data = get_weather_by_coords(lat, lon)

        if "current_weather" not in weather_data:
            speak("I could not fetch weather information.")
            continue

        bot_reply = explain_weather_with_llm(weather_data)
        print("Bot🤖:", bot_reply)
        speak(bot_reply)
        continue

    response = ollama.chat(
        model=input_model,
        messages=[{'role': 'user', 'content': user_input}]
    )

    bot_reply = response.message.content
    print("Bot🤖:", bot_reply)
    speak(bot_reply)

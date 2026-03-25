import ollama
import pyttsx3
import speech_recognition as sr
import requests
from datetime import datetime, timedelta
import string
import geopy
import requests
# -------- TEXT TO SPEECH --------
def speak(text):
    engine = pyttsx3.init(driverName='sapi5')
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# -------- SPEECH TO TEXT --------
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

# -------- OLLAMA --------
input_model = "phi4"

# -------- WEATHER API --------
OPENWEATHER_API_KEY = "REPLACE_WITH_NEW_KEY"

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, 
              "appid": OPENWEATHER_API_KEY, 
              "units": "metric"}
    return requests.get(url, params=params).json()

# -------- KEYWORDS --------
concluding_phrases = ['thanks', 'thank you', 'bye', 'exit']
time_keywords = ['time']
date_keywords = ['date']
weather_keywords = ['weather', 'temperature', 'forecast', 'climate']

# words that may appear before city
user_weather_phrases = ["about", "in", "of", "like"]

# -------- INPUT MODE --------
speak("Hello. Choose input mode. Type one for text, two for voice.")
print("1 → Text Input\n2 → Voice Input")

mode = ""
while mode not in ["1", "2"]:
    mode = input("Enter choice (1/2): ").strip()

use_voice_input = (mode == "2")
speak("Voice input mode selected." if use_voice_input else "Text input mode selected.")

# -------- MAIN LOOP --------
while True:

    # input
    if use_voice_input:
        user_input = listen().strip()
        if not user_input:
            continue
    else:
        user_input = input("User: ").strip()

    user_input_clean = user_input.lower()
    now = datetime.now()

    # exit
    if any(p in user_input_clean for p in concluding_phrases):
        speak("It was nice talking to you. Goodbye.")
        break

    # time
    if any(w in user_input_clean for w in time_keywords):
        speak(now.strftime("The current time is %I:%M %p."))
        continue

    # date
    if any(w in user_input_clean for w in date_keywords):
        speak(now.strftime("Today's date is %d %B %Y."))
        continue

    # day
    if 'day' in user_input_clean:
        if 'tomorrow' in user_input_clean:
            speak(f"Tomorrow will be {(now + timedelta(days=1)).strftime('%A')}.")
        elif 'yesterday' in user_input_clean:
            speak(f"Yesterday was {(now - timedelta(days=1)).strftime('%A')}.")
        else:
            speak(f"Today is {now.strftime('%A')}.")
        continue

    # -------- WEATHER --------
    if any(w in user_input_clean for w in weather_keywords):

    # 1️⃣ Extract city using LLM (robust method)
        extract_prompt = f"""
    Extract only the city name from this sentence.
    Return ONLY the city name, nothing else.

    Sentence: "{user_input}"
    """

    extract_response = ollama.chat(
        model=input_model,
        messages=[{'role': 'user', 'content': extract_prompt}]
    )

    city = extract_response.message.content.strip()
    print("DEBUG city (from LLM):", city)

    if not city:
        speak("I could not detect the city name. Please try again.")
        continue

    # 2️⃣ Call weather API using extracted city
    weather_data = get_weather(city)

    if weather_data.get("cod") != 200:
        speak("I could not find weather information for that city.")
        continue

    # 3️⃣ Ask LLM to explain the weather data
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

    bot_reply = response.message.content
    print("Bot🤖:", bot_reply)
    speak(bot_reply)
    continue

# -------- NORMAL CHAT --------
response = ollama.chat(
    model=input_model,
    messages=[{'role': 'user', 'content': user_input}]
)
bot_reply = response.message.content
print("Bot🤖:", bot_reply)
speak(bot_reply)

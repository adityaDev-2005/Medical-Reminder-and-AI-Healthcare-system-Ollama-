import ollama
import pyttsx3
import speech_recognition as sr
import time
from datetime import datetime, timedelta

# text to speech and re-intialising everytime coz did not work when initialised once
def speak(text):
    engine = pyttsx3.init(driverName='sapi5')
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1.0)
    engine.say(text)    
    engine.runAndWait()
    engine.stop()

# speech to text
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

# defining the ollama model
input_model = "phi4"

concluding_phrases = [
    'thanks', 'thank you', 'thanks a lot',
    'fine', 'see ya', 'see you', 'bye', 'exit'
]

# lists for date time and day
time_keywords = ['time', 'current time', 'what time']
date_keywords = ['date', 'today date', 'current date']
day_keywords  = ['day', 'today', 'which day']

# choosing input mode
speak("Hello. Choose input mode. Type one for text, two for voice.")

print("Choose input mode:")
print("1 → Text Input")
print("2 → Voice Input")

mode = ""
while mode not in ["1", "2"]:
    mode = input("Enter choice (1/2): ").strip()

use_voice_input = (mode == "2")

if use_voice_input:
    speak("Voice input mode selected. You can start speaking.")
else:
    speak("Text input mode selected. You can start typing.")

# main loop
while True:

    if use_voice_input:
        user_input = listen().strip()
        if not user_input:
            continue
    else:
        user_input = input("User: ").strip()

    user_input_clean = user_input.lower()

    now = datetime.now()

    # part for date time and day
    if any(word in user_input_clean for word in time_keywords):
        response_text = now.strftime("The current time is %I:%M %p.")
        print("Bot🤖:", response_text)
        speak(response_text)
        continue

    if any(word in user_input_clean for word in date_keywords):
        response_text = now.strftime("Today's date is %d %B %Y.")
        print("Bot🤖:", response_text)
        speak(response_text)
        continue

    # ---------- DAY INTENT (CONTEXT AWARE) ----------
    if 'day' in user_input_clean:

        if 'tomorrow' in user_input_clean:
            target_date = datetime.now() + timedelta(days=1)
            response_text = f"Tomorrow will be {target_date.strftime('%A')}."

        elif 'yesterday' in user_input_clean:
            target_date = datetime.now() - timedelta(days=1)
            response_text = f"Yesterday was {target_date.strftime('%A')}."

        else:
            target_date = datetime.now()
            response_text = f"Today is {target_date.strftime('%A')}."

        print("Bot🤖:", response_text)
        speak(response_text)
        continue


    # ollama part
    messages = [
        {'role': 'user', 'content': user_input}
    ]

    response = ollama.chat(model=input_model, messages=messages)
    bot_reply = response.message.content

    print("Bot🤖:", bot_reply)
    speak(bot_reply)

    if any(phrase in user_input_clean for phrase in concluding_phrases):
        speak("It was nice talking to you. Goodbye.")
        break

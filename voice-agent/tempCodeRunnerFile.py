import os
import io
import wave
import json
import re
import numpy as np
import sounddevice as sd
import pyttsx3
import dateparser
import requests
from dotenv import load_dotenv
import groq

# Load environment variables and Groq API key
load_dotenv()
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

# Backend API endpoint + default city for weather lookup
BACKEND_URL = "http://localhost:5000/api/bookings"
DEFAULT_CITY = "Delhi,IN"

# Initialize text-to-speech engine
tts = pyttsx3.init()


# -------------------------------------------------------------
# TEXT-TO-SPEECH FUNCTION
# -------------------------------------------------------------
def speak(text):
    print("Assistant:", text)
    engine = pyttsx3.init()        
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()



# -------------------------------------------------------------
# SPEECH-TO-TEXT FUNCTION (WHISPER API)
# -------------------------------------------------------------
def listen():
    """
    Records 4 seconds of audio using sounddevice,
    converts it to WAV, sends to Groq Whisper model,
    and returns the transcribed text.
    """
    print("Listening...")
    duration = 4
    sample_rate = 16000

    # Capture microphone audio
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    # Convert raw audio to WAV format in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    wav_bytes = wav_buffer.getvalue()

    # Send audio to Whisper model for transcription
    response = client.audio.transcriptions.create(
        file=("audio.wav", wav_bytes),
        model="whisper-large-v3-turbo",
        response_format="json"
    )

    # Extract the text output
    text = response.text.strip().lower()
    print("User:", text)
    return text


# -------------------------------------------------------------
# BOOKING DATA STORE (in-memory conversation memory)
# -------------------------------------------------------------
booking = {
    "name": None,
    "guests": None,
    "date": None,
    "time": None,
    "cuisine": None,
    "special": None
}

# Tracks what question to expect next
last_question = None


# -------------------------------------------------------------
# CHECK IF BOOKING IS COMPLETE
# -------------------------------------------------------------
def booking_complete():
    """Returns True only when all booking fields are filled."""
    return all(booking.values())


# -------------------------------------------------------------
# DECIDE NEXT QUESTION BASED ON PROGRESS
# -------------------------------------------------------------
def next_question():
    """Returns the next question the assistant should ask."""
    if not booking["name"]:
        return "May I know your name?"
    if not booking["guests"]:
        return "How many guests should I book the table for?"
    if not booking["date"]:
        return "On what date would you like the booking?"
    if not booking["time"]:
        return "What time should I book the table?"
    if not booking["cuisine"]:
        return "What cuisine would you prefer? Italian, Chinese, Indian, or something else?"
    if not booking["special"]:
        return "Any special requests such as birthday, anniversary, or dietary needs?"
    return None


# -------------------------------------------------------------
# FIELD EXTRACTION FUNCTIONS
# These help extract structured info from user speech
# -------------------------------------------------------------

def extract_name(text):
    """Extracts user's name based on simple patterns."""
    if "my name is" in text:
        return text.split("my name is")[-1].strip()
    if "i am" in text:
        return text.split("i am")[-1].strip()
    if len(text.split()) == 1:
        return text.strip()
    return None


def extract_guests(text):
    """Extracts number of guests using fuzzy word mapping."""
    mapping = {
        "one": 1, "1": 1,
        "two": 2, "to": 2, "too": 2, "tu": 2,
        "three": 3, "tree": 3, "free": 3, "3": 3,
        "four": 4, "for": 4, "4": 4,
        "five": 5, "5": 5,
        "six": 6, "sex": 6, "6": 6,
        "seven": 7, "7": 7,
        "eight": 8, "ate": 8, "8": 8,
        "nine": 9, "9": 9,
        "ten": 10, "10": 10
    }
    for w in text.split():
        if w in mapping:
            return mapping[w]
    return None


def extract_cuisine(text):
    """Detects cuisine based on keywords."""
    text = text.lower()
    cuisines = {
        "italian": ["italian", "pasta", "pizza"],
        "chinese": ["chinese", "noodles"],
        "indian": ["indian", "curry"],
        "mexican": ["mexican", "taco"],
        "thai": ["thai"],
        "japanese": ["japanese", "sushi"]
    }
    for key, words in cuisines.items():
        for w in words:
            if w in text:
                return key
    return None


def extract_date(text):
    """Uses dateparser to interpret natural-language dates."""
    text = text.lower().strip()

    if "tomorrow" in text:
        dt = dateparser.parse("tomorrow")
        return dt.date().isoformat()

    dt = dateparser.parse(text)
    if dt:
        return dt.date().isoformat()
    return None


def extract_time(text):
    """
    Extracts time using robust regex:
    - 6 pm / 6 p.m
    - 8pm
    - midnight / noon
    - 6:30
    """
    text = text.lower().replace(".", "").strip()

    if "midnight" in text:
        return "12:00 AM"
    if "noon" in text:
        return "12:00 PM"

    match = re.search(r"(\d{1,2})\s*p\s*m|\b(\d{1,2})pm\b|\b(\d{1,2})\s*pm\b", text)
    if match:
        hr = match.group(1) or match.group(2) or match.group(3)
        return f"{hr}:00 PM"

    match = re.search(r"(\d{1,2})\s*a\s*m|\b(\d{1,2})am\b|\b(\d{1,2})\s*am\b", text)
    if match:
        hr = match.group(1) or match.group(2) or match.group(3)
        return f"{hr}:00 AM"

    match = re.search(r"(\d{1,2}):(\d{2})", text)
    if match:
        return f"{match.group(1)}:{match.group(2)}"

    match = re.search(r"\b(\d{1,2})\b", text)
    if match:
        hr = int(match.group(1))
        if 1 <= hr <= 11: return f"{hr}:00 AM"
        if hr == 12: return "12:00 PM"
        if 13 <= hr <= 23: return f"{hr-12}:00 PM"

    return None


def extract_special(text):
    """Extracts special requests like birthday / anniversary."""
    text = text.lower().strip()

    if text in ["no", "none", "nothing", "nope"]:
        return "none"

    for w in ["birthday", "anniversary", "diet", "allergy"]:
        if w in text:
            return w

    if len(text.split()) >= 2:
        return text

    return None


# -------------------------------------------------------------
# YES / NO HELPER FUNCTIONS
# -------------------------------------------------------------
def is_yes(text):
    return any(w in text for w in ["yes", "yeah", "yup", "ok", "okay", "haan", "sure"])

def is_no(text):
    return any(w in text for w in ["no", "nah", "nope", "cancel"])


# -------------------------------------------------------------
# SEND BOOKING TO BACKEND API
# -------------------------------------------------------------
def save_booking_to_backend(booking):
    """
    Sends final booking details to backend via POST request.
    Backend handles:
    - saving to MongoDB
    - fetching weather
    - seating recommendation
    """
    payload = {
        "customerName": booking["name"],
        "numberOfGuests": booking["guests"],
        "bookingDate": booking["date"],
        "bookingTime": booking["time"],
        "cuisinePreference": booking["cuisine"],
        "specialRequests": booking["special"],
        "city": DEFAULT_CITY
    }

    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        print("Error sending to backend:", e)
        return None


# -------------------------------------------------------------
# LLM FALLBACK EXTRACTION
# -------------------------------------------------------------
def extract_details_llm(text):
    """
    Sends user text to Groq Llama model,
    asking for structured booking extraction.
    Used when local rule-based extraction fails.
    """
    prompt = f"""
Extract booking details from: "{text}"

Return JSON:

{{
 "name": string or null,
 "guests": number or null,
 "date": string or null,
 "time": string or null,
 "cuisine": string or null,
 "special": string or null
}}
"""
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return json.loads(r.choices[0].message.content)
    except:
        return {}


# -------------------------------------------------------------
# MAIN CONVERSATION LOOP
# -------------------------------------------------------------
speak("Hello, welcome to the restaurant booking assistant. How may I help you today?")


while True:
    user_text = listen()

    # LOCAL FIELD EXTRACTION BASED ON CONTEXT
    if last_question == "name" and not booking["name"]:
        nm = extract_name(user_text)
        if nm: booking["name"] = nm

    if last_question == "guests" and not booking["guests"]:
        g = extract_guests(user_text)
        if g: booking["guests"] = g

    if last_question == "date" and not booking["date"]:
        d = extract_date(user_text)
        if d: booking["date"] = d

    if last_question == "time" and not booking["time"]:
        t = extract_time(user_text)
        if t: booking["time"] = t

    if last_question == "cuisine" and not booking["cuisine"]:
        c = extract_cuisine(user_text)
        if c: booking["cuisine"] = c

    if last_question == "special" and not booking["special"]:
        sp = extract_special(user_text)
        if sp: booking["special"] = sp

    # LLM FALLBACK (fills missing fields)
    details = extract_details_llm(user_text)
    for k in booking:
        if booking[k] is None and details.get(k):
            booking[k] = details[k]

    # ---------------------------------------------------------
    # IF BOOKING COMPLETE → CONFIRMATION STAGE
    # ---------------------------------------------------------
    if booking_complete():

        summary = f"""
Here is your booking summary:

Name: {booking['name']}
Guests: {booking['guests']}
Date: {booking['date']}
Time: {booking['time']}
Cuisine: {booking['cuisine']}
Special Request: {booking['special']}

Would you like to confirm this booking?
Say yes or no.
"""
        speak(summary)

        confirm = listen()

        # Handle negative or unclear confirmation
        if is_no(confirm):
            speak("Booking cancelled. You can start again.")
            booking = {k: None for k in booking}
            last_question = None
            continue

        if not is_yes(confirm):
            speak("I didn't understand. Booking cancelled.")
            booking = {k: None for k in booking}
            last_question = None
            continue

        # -----------------------------------------------------
        # SAVE BOOKING TO BACKEND + GET WEATHER + SEATING
        # -----------------------------------------------------
        result = save_booking_to_backend(booking)

        if not result:
            speak("Error saving booking.")
        else:
            weather = result.get("weatherInfo", {})
            seating = result.get("seatingPreference", "indoor")

            msg = "Your booking is confirmed."

            if weather:
                description = weather.get("description", "unavailable")
                temp = weather.get("temp")

                if temp is not None:
                    msg += f" The weather on that day is expected to be '{description}' with a temperature of {temp}°C."
                else:
                    msg += f" The weather condition is '{description}', but temperature data is unavailable."

# Seating recommendation
            if seating == "outdoor":
                msg += " Based on the weather, outdoor seating is recommended."
            else:
                msg += " Based on the weather, indoor seating is recommended."


            speak(msg)

        # Reset for next booking
        booking = {k: None for k in booking}
        last_question = None
        continue

    # ---------------------------------------------------------
    # ASK NEXT QUESTION IN THE FLOW
    # ---------------------------------------------------------
    q = next_question()

    # Set conversation context for next listen()
    if "name" in q.lower(): last_question = "name"
    elif "guest" in q.lower(): last_question = "guests"
    elif "date" in q.lower(): last_question = "date"
    elif "time" in q.lower(): last_question = "time"
    elif "cuisine" in q.lower(): last_question = "cuisine"
    elif "special" in q.lower(): last_question = "special"

    speak(q)

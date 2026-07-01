import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3

API_URL = "http://127.0.0.1:8000/api/v1/chat"

st.set_page_config(page_title="RAVAND OS", layout="centered")
st.title("🧠 RAVAND OS - AI System")

# session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# TTS engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Voice input function
def voice_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        return text
    except:
        return "Sorry, could not understand audio"

# نمایش history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# UI buttons
col1, col2 = st.columns(2)

voice_input = None

with col1:
    if st.button("🎤 Speak"):
        voice_input = voice_to_text()

with col2:
    st.write("")

# chat input
user_input = st.chat_input("Type or use voice...")

if voice_input:
    user_input = voice_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    payload = {
        "message": user_input,
        "session_id": st.session_state.session_id
    }

    try:
        res = requests.post(API_URL, json=payload, timeout=120)
        data = res.json()

        st.session_state.session_id = data.get("session_id")
        reply = data.get("content", "")

    except Exception as e:
        reply = str(e)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)

    speak(reply)
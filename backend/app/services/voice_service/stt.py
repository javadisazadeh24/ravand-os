import speech_recognition as sr

def transcribe_audio(file_path: str) -> str:
    r = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    text = r.recognize_google(audio)
    return text
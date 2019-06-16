import speech_recognition as sr


def audio_to_text(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = r.record(source)
    command = r.recognize_google(audio)
    return command

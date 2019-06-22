import speech_recognition as sr


class AudioConverter:
    """ Contains method to convert audio to text"""

    @staticmethod
    def audio_to_text(path):
        r = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio = r.record(source)
        command = r.recognize_google(audio)
        return command

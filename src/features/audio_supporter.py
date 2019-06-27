import subprocess
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

    @staticmethod
    def convert_format(path, dest):
        process = subprocess.run(['ffmpeg', '-i', path, dest])
        if process.returncode != 0:
            raise Exception("Something went wrong")

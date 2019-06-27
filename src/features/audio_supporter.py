import subprocess
import speech_recognition as sr


class AudioConverter:
    """ Contains method to convert audio to text"""

    @staticmethod
    def audio_to_text(path):
        """
        Converts audio in formats .wav, .flac into text
        :param path: input file path
        :return: string
        """
        r = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio = r.record(source)
        command = r.recognize_google(audio)
        return command

    @staticmethod
    def convert_format(path, dest):
        """
        Converts audio file in a format specified in @path into format specified in @dest
        :param path: input file path
        :param dest: destination file path
        """
        process = subprocess.run(['ffmpeg', '-i', path, dest])
        if process.returncode != 0:
            raise Exception("Something went wrong")

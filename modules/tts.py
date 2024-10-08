import os
import vosk
import pyttsx3
import wave
import json
import subprocess

# Obtener el directorio del script
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class AudioProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def convert_audio(self):
        """Convierte el archivo de audio a mono, 16 bits y 16 kHz."""
        command = [
            "ffmpeg",
            "-i",
            self.input_file,
            "-ac",
            "1",  # Canal mono
            "-ar",
            "16000",  # Frecuencia de muestreo 16 kHz
            "-sample_fmt",
            "s16",  # 16 bits
            self.output_file,
        ]

        try:
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
            print(f"Audio convertido exitosamente: {self.output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error en la conversión de audio: {e.stderr.decode()}")

    def is_valid_audio(self):
        """Verifica que el archivo de audio tenga el formato correcto."""
        with wave.open(self.output_file, "rb") as wf:
            if (
                wf.getnchannels() != 1
                or wf.getsampwidth() != 2
                or wf.getframerate() != 16000
            ):
                print("El archivo de audio debe estar en mono, 16 bits, 16kHz.")
                return False
        return True


class SpeechRecognizer:
    def __init__(self, model_path):
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

    def recognize_speech(self, audio_file):
        """Reconoce el texto en el archivo de audio proporcionado."""
        recognized_text = []
        with wave.open(audio_file, "rb") as wf:
            if not self.is_valid_audio(wf):
                return None

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    result_json = json.loads(result)
                    recognized_text.append(result_json["text"])

            final_result = self.recognizer.FinalResult()
            result_json = json.loads(final_result)
            recognized_text.append(result_json["text"])

        return recognized_text

    def is_valid_audio(self, wf):
        """Verifica que el archivo de audio tenga el formato correcto."""
        return (
            wf.getnchannels() == 1
            and wf.getsampwidth() == 2
            and wf.getframerate() == 16000
        )


def speak(text):
    """Utiliza pyttsx3 para convertir texto a voz."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def main():
    input_audio = os.path.join(BASE_PATH, "../temp/audios/ytaudio_241008271974.wav")
    converted_audio = os.path.join(BASE_PATH, "../temp/audios/converted_audio.wav")

    print("Probando reconocimiento de voz y síntesis de voz...")

    # Procesar el audio
    audio_processor = AudioProcessor(input_audio, converted_audio)
    audio_processor.convert_audio()

    # Reconocer el habla
    recognizer = SpeechRecognizer(
        os.path.join(BASE_PATH, "../models/speech-models/vosk-model-small-es-0.42")
    )
    recognized_lines = recognizer.recognize_speech(converted_audio)

    if recognized_lines:
        print("Texto reconocido:")
        for line in recognized_lines:
            if line.strip():  # Solo imprimir líneas no vacías
                print(f"- {line.strip()}")

        full_transcription = " ".join(
            recognized_lines
        )  # Unir todas las líneas en una sola
        speak(f"Has dicho: {full_transcription}")


if __name__ == "__main__":
    main()

import os
from pytubefix import YouTube
from pydub import AudioSegment
from datetime import datetime

# Obtener el directorio del script
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

VIDEOS_PATH = "../temp/videos"
AUDIOS_PATH = "../temp/audios"


def create_directories(BASE_PATH):
    # Crea las carpetas de videos y audios si no existen
    os.makedirs(os.path.join(BASE_PATH, VIDEOS_PATH), exist_ok=True)
    os.makedirs(os.path.join(BASE_PATH, AUDIOS_PATH), exist_ok=True)


def get_unique_filename(base_name, extension):
    # Genera un nombre único basado en la fecha y hora actual
    timestamp = datetime.now().strftime("%y%m%d%f")
    return f"{base_name}_{timestamp}.{extension}"


def download_video(url, format_choice):
    create_directories(BASE_PATH)  # Asegúrate de que las carpetas existen

    try:
        yt = YouTube(url)
        print(f"Title: {yt.title}")

        if format_choice == "video":
            # Descarga el video en la mejor calidad
            stream = yt.streams.get_highest_resolution()
            try:
                video_file_path = stream.download(
                    output_path=os.path.join(BASE_PATH, VIDEOS_PATH),
                    filename=get_unique_filename("ytvideo", "mp4"),
                )
                print("Video descargado exitosamente.")
            except Exception as e:
                print(f"Hubo un error al descargar el video del URL proporcionado: {e}")

        elif format_choice == "audio":
            # Descarga solo el audio
            audio_stream = yt.streams.filter(adaptive=True, only_audio=True).first()
            audio_file_path = audio_stream.download(
                output_path=os.path.join(BASE_PATH, AUDIOS_PATH)
            )
            print("Audio descargado exitosamente.")

            # Convierte a formato deseado
            audio_format = (
                input("Elige el formato de audio (mp3, wav, ogg): ").strip().lower()
            )
            if audio_format not in ["mp3", "wav", "ogg"]:
                print("Formato no soportado, se usará mp3 por defecto.")
                audio_format = "mp3"

            # Cargar el audio y convertirlo
            audio = AudioSegment.from_file(audio_file_path)
            new_file_path = os.path.join(
                BASE_PATH, AUDIOS_PATH, get_unique_filename("ytaudio", audio_format)
            )
            audio.export(new_file_path, format=audio_format)
            os.remove(audio_file_path)  # Elimina el archivo original
            print(f"Audio convertido a {audio_format} y guardado como {new_file_path}.")

        else:
            print("Opción no válida. Elige 'video' o 'audio'.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    video_url = input("Ingresa la URL del video de YouTube: ")
    format_choice = (
        input("Elige el formato de descarga (video/audio): ").strip().lower()
    )
    download_video(video_url, format_choice)

import requests
import time
import os
import re
from http.client import IncompleteRead
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
import speech_recognition as sr

def transcribe_audio_sphinx(audio_path):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    
    try:
        transcription = recognizer.recognize_sphinx(audio_data)
        return transcription
    except sr.UnknownValueError:
        print("Sphinx could not understand the audio.")
    except sr.RequestError:
        print("Sphinx error; check if you've installed the CMU Sphinx dependencies.")


def extract_youtube_id(youtube_url):
    """Extract the YouTube video ID from a URL."""
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_url)
    return match.group(1) if match else None


def get_most_replayed_section(youtube_id):
    url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={youtube_id}"
    response = requests.get(url)
    data = response.json()

    # Check for items in the API response
# Check for mostReplayed in the first item
    if not data['items'][0].get('mostReplayed'):
        print("The video doesn't have sufficient 'mostReplayed' data. This could be due to insufficient views or it being a new video.")
        return None, None


    # Check for mostReplayed in the first item
    if not data['items'][0].get('mostReplayed'):
        raise ValueError("API response does not contain 'mostReplayed' in the first item")

    # Check for heatMarkers in the mostReplayed
    if not data['items'][0]['mostReplayed'].get('heatMarkers'):
        raise ValueError("API response does not contain 'heatMarkers'")

    # If all checks pass, extract the most replayed section
    heat_markers = data['items'][0]['mostReplayed']['heatMarkers']
    most_replayed = max(heat_markers, key=lambda x: x['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized'])
    
    start_time_millis = most_replayed['heatMarkerRenderer']['timeRangeStartMillis']
    end_time_millis = start_time_millis + most_replayed['heatMarkerRenderer']['markerDurationMillis']

    return start_time_millis / 1000, end_time_millis / 1000  # Convert to seconds


def download_video_section(youtube_id, start_time, end_time, output_filename, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={youtube_id}")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            download_path = stream.download(filename="temp_video")
            ffmpeg_extract_subclip(download_path, start_time, end_time, targetname=output_filename)
            os.remove("temp_video")
            return
        except IncompleteRead:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("Failed to download after multiple attempts.")

def extract_audio_from_video(video_path, output_audio_path="temp_audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio_path, codec='pcm_s16le')  # PCM 16-bit format is compatible

video_path = output_filename
audio_path = "temp_audio.wav"

def main():
    youtube_url = input("Enter the entire YouTube video URL: ")
    youtube_id = extract_youtube_id(youtube_url)
    if not youtube_id:
        print("Invalid YouTube URL provided.")
        return
    print(f"Extracted YouTube ID: {youtube_id}")
    output_filename = input("Enter the desired output filename (e.g. output_clip.mp4): ")
    
    try:
        start_time, end_time = get_most_replayed_section(youtube_id)
        download_video_section(youtube_id, start_time, end_time, output_filename)
        extract_audio_from_video(video_path, audio_path)

        transcription = transcribe_audio_sphinx(audio_path)

        # Write the transcription to a text file
        with open(youtube_id + "-highlight-transcription.txt", "w") as f:
            f.write(transcription)
    except ValueError as e:
        if str(e) == "API response does not contain 'items'":
            print("The video might not be available or indexed by the API, or the YouTube ID extracted is invalid.")
        else:
            print(e)


if __name__ == "__main__":
    main()

import requests
import time
import os
import re
from http.client import IncompleteRead
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
import speech_recognition as sr


# Utilizes the CMU Sphinx toolkit for speech recognition 
def transcribe_audio_sphinx(output_audio_path):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(output_audio_path) as source:
        audio_data = recognizer.record(source)
    
    try:
        transcription = recognizer.recognize_sphinx(audio_data)
        return transcription
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError:
        print("Sphinx error; check if you've installed the CMU Sphinx dependencies.")

# Extract the video ID from a URL
def extract_youtube_id(youtube_url):
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_url)
    return match.group(1) if match else None


def get_most_replayed_section(youtube_id, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            print("Fetching the significant moment of the video...")
            url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={youtube_id}"
            response = requests.get(url)
            data = response.json()
            print(data)

            # Check for JSON items in the API response
            if data['items'] and data['items'][0].get('mostReplayed'):
                heat_markers = data['items'][0]['mostReplayed']['heatMarkers']
                most_replayed = max(heat_markers, key=lambda x: x['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized'])
                
                start_time_millis = most_replayed['heatMarkerRenderer']['timeRangeStartMillis']
                end_time_millis = start_time_millis + most_replayed['heatMarkerRenderer']['markerDurationMillis']

                return start_time_millis / 1000, end_time_millis / 1000  # Convert to seconds

        except:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("The video doesn't have sufficient 'mostReplayed' data. This could be due to insufficient views or it being a new video.")
    return None, None



def download_video_section(youtube_id, start_time, end_time, output_mp4, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            print("Downloading video, please wait...")
            yt = YouTube(f"https://www.youtube.com/watch?v={youtube_id}")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            download_path = stream.download(filename="temp_video.mp4")
            ffmpeg_extract_subclip(download_path, start_time, end_time, targetname=output_mp4)
            #os.remove("temp_video")
            return
        except IncompleteRead:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("Failed to download after multiple attempts.")

def extract_audio_from_video(output_mp4, output_audio_path="temp_audio.wav"):
    clip = VideoFileClip(output_mp4)
    clip.audio.write_audiofile(output_audio_path, codec='pcm_s16le')  # PCM 16-bit format is compatible

    #video_path = output_mp4
    #output_audio_path = "temp_audio.wav"

def main():
    youtube_url = input("Enter the entire YouTube video URL: ")
    output_mp4 = input("Enter the desired output filename (e.g. output_clip.mp4): ")
    output_audio_path = "temp_audio.wav"
    youtube_id = extract_youtube_id(youtube_url)
    if not youtube_id:
        print("Invalid YouTube URL provided.")
        return
    print(f"YouTube ID: " + youtube_id)
    
    
    start_time, end_time = get_most_replayed_section(youtube_id)

    if start_time is None or end_time is None:
        print("Unable to retrieve the most replayed section for this video.")
        return

    try:
        download_video_section(youtube_id, start_time, end_time, output_mp4)
        extract_audio_from_video(output_mp4, output_audio_path)

        transcription = transcribe_audio_sphinx(output_audio_path)
        print(transcription)
        if transcription is None:
            print("No transcription available. Exiting...")
            return
        # Write the transcription to a text file
        with open(youtube_id + "-highlight-transcription.txt", "w") as f:
        #with open("test-highlight-transcription.txt", "w") as f:

            f.write(transcription)
    except ValueError as e:
        if str(e) == "API response does not contain 'items'":
            print("The video might not be available or indexed by the API, or the YouTube ID extracted is invalid.")
        else:
            print(e)
        # Clean up temp files
        print("Cleaning up...")
        os.remove("temp_video.mp4")
        os.remove("temp_audio.wav")


if __name__ == "__main__":
    main()

import requests
import time
import os
import re
import shutil
from http.client import IncompleteRead
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
import speech_recognition as sr
import tkinter as tk

# (Your imports remain unchanged)
# ...
# Uses the CMU Sphinx toolkit for speech recognition 
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

# Queries the API and parses the JSON to find the video segment
def get_most_replayed_section(youtube_id, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            print("Fetching the significant moment of the video...")
            url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={youtube_id}"
            response = requests.get(url)
            data = response.json()
            #print(data)

            # Check for JSON items in the API response
            if data['items'] and data['items'][0].get('mostReplayed'):
                heat_markers = data['items'][0]['mostReplayed']['heatMarkers']
                most_replayed = max(heat_markers, key=lambda x: x['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized'])
                
                start_time_ms = most_replayed['heatMarkerRenderer']['timeRangeStartMillis']
                end_time_ms = start_time_ms + most_replayed['heatMarkerRenderer']['markerDurationMillis']

                # Converts 
                return start_time_ms / 1000, end_time_ms / 1000  # Convert to seconds

        except:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("The video doesn't have sufficient 'mostReplayed' data. This could be due to insufficient views or it being a new video.")
    return None, None

def download_video_section(youtube_id, start_time, end_time, output_mp4, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            print("Downloading video, please wait...")
            yt = YouTube(f"https://www.youtube.com/watch?v={youtube_id}")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            download_path = stream.download(filename=f"{youtube_id}/full_video.mp4")
            ffmpeg_extract_subclip(download_path, start_time, end_time, targetname=f"{youtube_id}/{output_mp4}")
            #os.remove("temp_video")
            return
        except IncompleteRead:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("Failed to download after multiple attempts.")

def extract_audio_from_video(youtube_id, output_mp4, output_audio_path):
    clip = VideoFileClip(youtube_id + "/" + output_mp4)
    clip.audio.write_audiofile(output_audio_path, codec='pcm_s16le')

    #video_path = output_mp4
    output_audio_path = f"{youtube_id}/temp_audio.wav"

def check_dir(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

def zip_directory(directory_path, output_filename):
    shutil.make_archive(output_filename, 'zip', directory_path)

# Function to handle button click event
def submit_url():
    youtube_url = url_entry.get()
    output_mp4 = name_entry.get()
    print("Entered URL:", youtube_url)

    # Proceed with the main functionality
    process_video(youtube_url, output_mp4)

    # display the entered URL
    url_label.config(text="Processed URL: " + youtube_url)

def process_video(youtube_url, output_mp4):
    # (This is essentially the main functionality you provided earlier but now within a function)

    youtube_id = extract_youtube_id(youtube_url)

    if not youtube_id:
        print("Invalid YouTube URL provided.")
        return
    print(f"YouTube ID: " + youtube_id)

    check_dir(youtube_id)
    
    start_time, end_time = get_most_replayed_section(youtube_id)

    if start_time is None or end_time is None:
        print("Unable to retrieve the most replayed section for this video.")
        return

    try:
        output_audio_path = f"{youtube_id}/highlight_audio.wav"
        download_video_section(youtube_id, start_time, end_time, output_mp4)
        extract_audio_from_video(youtube_id, output_mp4, output_audio_path)

        transcription = transcribe_audio_sphinx(output_audio_path)
        if transcription is None:
            print("No transcription available. Exiting...")
            return

        # Write the transcription to a text file
        with open(f"{youtube_id}/{youtube_id}-highlight-transcription.txt", "w") as f:
            f.write(transcription + "\r\n")
            print(f"Transcription saved to "+ youtube_id + "/" + youtube_id + "-highlight-transcription.txt")

        zip_choice = input("Do you want to zip the folder? (y/n): ").lower()
        if zip_choice == 'y':
            zip_directory(youtube_id, youtube_id)
            print(f"Directory {youtube_id} zipped as {youtube_id}.zip")

    except ValueError as e:
        if str(e) == "API response does not contain 'items'":
            print("The video might not be available or indexed by the API, or the YouTube ID extracted is invalid.")
        else:
            print(e)

# Your GUI script integrated here:

root = tk.Tk()
root.title("URL Entry App")
root.minsize(width=250, height=400)

label = tk.Label(root, text="Extract the most popular part of a Youtube Video", font=("Arial", 16))
label.pack(pady=20)

label = tk.Label(root, text="Warning: This applies only to videos that have 'most replayed' activated", font=("Arial", 10), fg="red")
label.pack(pady=5)

label = tk.Label(root, text="Enter the entire YouTube video URL: ", font=("Arial", 10))
label.pack(pady=10)
url_entry = tk.Entry(root, width=70)
url_entry.pack(pady=10)

label = tk.Label(root, text="Enter the desired name for the new video: ", font=("Arial", 10))
label.pack(pady=10)
name_entry = tk.Entry(root, width=70)  # Changed variable name to avoid reuse
name_entry.pack(pady=10)

submit_button = tk.Button(root, text="Submit", command=submit_url)
submit_button.pack(pady=20)

youtube_url = ""
output_mp4 = ""

url_label = tk.Label(root, text="", font=("Arial", 12))
url_label.pack(pady=20)

root.mainloop()


import requests
import time
import os
import re
from http.client import IncompleteRead
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def extract_youtube_id(youtube_url):
    """regex to extract the YouTube video ID from a URL."""
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_url)
    return match.group(1) if match else None

def get_most_replayed_section(youtube_id):
    url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={youtube_id}"
    response = requests.get(url)
    data = response.json()

    # Check for items in the API response
    if not data.get('items'):
        raise ValueError("API response does not contain 'items'")

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

# Downloads the video into a temp file, extracts the highlighted time range, and deletes the temp video
def download_video_section(youtube_url, start_time, end_time, output_filename, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            yt = YouTube(f"{youtube_url}")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            download_path = stream.download(filename="temp_video")
            ffmpeg_extract_subclip(download_path, start_time, end_time, targetname=output_filename)
            # removes temp file when done
            os.remove("temp_video")
            return
        except IncompleteRead:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("Failed to download after multiple attempts.")

def main():
    # Reads user input for a YouTube URL
    youtube_url = input("Enter the entire YouTube video URL: ")
    youtube_id = extract_youtube_id(youtube_url)
    if not youtube_id:
        print("Invalid YouTube URL provided.")
        return
    #print(youtube_id)
    # Reads user input for mp4 file output
    output_filename = input("Enter the desired output filename (e.g. output_clip.mp4): ")
    start_time, end_time = get_most_replayed_section(youtube_url)

    download_video_section(youtube_id, start_time, end_time, output_filename)

if __name__ == "__main__":
    main()

import requests
import time
from http.client import IncompleteRead
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

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


def download_video_section(youtube_id, start_time, end_time, output_filename="output_clip.mp4", max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={youtube_id}")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            download_path = stream.download(filename="temp_video")
            ffmpeg_extract_subclip(download_path, start_time, end_time, targetname=output_filename)
            return
        except IncompleteRead:
            retries += 1
            print(f"Attempt {retries} failed. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("Failed to download after multiple attempts.")

def main():
    youtube_id = "KdpeV2KBPBQ"  # Replace with your YouTube Video ID
    start_time, end_time = get_most_replayed_section(youtube_id)
    download_video_section(youtube_id, start_time, end_time)

if __name__ == "__main__":
    main()

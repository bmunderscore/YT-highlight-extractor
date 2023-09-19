# YT-highlight-extractor
My team's submission for Shellhacks 2023

## Install dependencies

Python 3.X:

pip3 install -r requirements.txt

or

python3 -m pip install -r requirements.txt

## Usage:
`$ python3 yt-highlight-extractor-cli.py`

`Enter the entire YouTube video URL: https://www.youtube.com/watch?v=oD2OrBjqVtY`

`Enter the desired output filename (e.g. highlight_clip.mp4): highlight_clip.mp4`

```
YouTube ID: oD2OrBjqVtY
Fetching the significant moment of the video...
Fetching the significant moment of the video...
Downloading video, please wait...
Moviepy - Running:
>>> "+ " ".join(cmd)
Moviepy - Command successful
MoviePy - Writing audio in oD2OrBjqVtY/highlight_audio.wav
MoviePy - Done.
Transcription saved to oD2OrBjqVtY/oD2OrBjqVtY-highlight-transcription.txt
Do you want to zip the folder? (y/n): y
Directory oD2OrBjqVtY zipped as oD2OrBjqVtY.zip
```

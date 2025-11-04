import time

import os

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

DOWNLOADS_DIR = "downloads"


def download_video_and_audio(video_url=None, downloads_dir=DOWNLOADS_DIR):
    print(f"Starting download for video {video_url}...")
    # Create a YouTube object
    yt = YouTube(video_url)
    # Get the highest resolution video stream (stream with progressive=True)
    video_stream = yt.streams.filter(adaptive=True).order_by("resolution").last()
    # Get the highest quality audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()
    # Download the video and audio streams
    video_filename = f"{yt.video_id}_video.mp4"
    audio_filename = f"{yt.video_id}_audio.mp3"
    video_path = os.path.join(downloads_dir, video_filename)
    audio_path = os.path.join(downloads_dir, audio_filename)
    video_stream.download(output_path=downloads_dir, filename=video_filename)
    audio_stream.download(output_path=downloads_dir, filename=audio_filename)
    print("Video and audio downloaded successfully.")
    return yt, audio_path, video_path


def merge_audio_and_video(audio_path, video_path, result_name=None, from_timestamp=None, to_timestamp=None, downloads_dir=DOWNLOADS_DIR):
    # Merge video and audio into a single file
    print(f"Merging audio and video({from_timestamp}:{to_timestamp}) to result file {result_name}.mp4")
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    if to_timestamp and from_timestamp:
        video = video.subclip(from_timestamp, to_timestamp)
        audio = audio.subclip(from_timestamp, to_timestamp)
    final_output = video.set_audio(audio)
    final_path = os.path.join(downloads_dir, f"{result_name}.mp4")
    final_output.write_videofile(final_path, codec="libx264")
    time.sleep(3)
    # Clean up downloaded video and audio files
    try:
        os.remove(video_path)
        os.remove(audio_path)
    except:
        pass
    print("Video with merged audio downloaded successfully.")
    return final_path


def download_video_transcript(video_id=None, downloads_dir=DOWNLOADS_DIR):
    # Get the video transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    # Save the transcript to a file
    transcript_path = os.path.join(downloads_dir, f"{video_id}_transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        for entry in transcript:
            f.write(f"[{entry['start']} - {entry['start'] + entry['duration']}] {entry['text']}\n")
    print("Transcript downloaded successfully.")
    return transcript_path


if __name__ == "__main__":
    video_meta, audio_path, video_path = download_video_and_audio("https://www.youtube.com/watch?v=J4_d7nENMFM")
    transcript_path = download_video_transcript(video_meta.video_id)

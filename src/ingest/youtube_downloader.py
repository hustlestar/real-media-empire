from pytube import YouTube, Playlist


def download_video(link: str):
    """Download a YouTube video."""
    youtube = YouTube(link)
    print("Downloading video: ", youtube.title)
    youtube.streams.get_highest_resolution().download()
    print("Video downloaded successfully")


def download_playlist(playlist_link: str):
    """Download all videos in a YouTube playlist."""
    playlist = Playlist(playlist_link)
    print("Number of videos in playlist:", len(playlist.video_urls))
    for video_url in playlist.video_urls:
        download_video(video_url)


# Usage
# Replace the links with the actual YouTube video or playlist URL
# download_video("https://www.youtube.com/watch?v=rh6Cj0CW4Bo")
# download_playlist("https://www.youtube.com/watch?v=sQrYoFVCiQM&list=PLotrUJhmcK7RJawRXoib4MLGBk4fTI8Uo")
# download_playlist("https://www.youtube.com/watch?v=_SZuUDKjnCg&list=PLMMiIzbQ5LUzVCwsoLlsCFvZh9UENgbPH")
# download_playlist("https://www.youtube.com/watch?v=YnjPDKPaeIc&list=PL5hws9jJULo2kfftxkBeyQCz2mPbJ2yjy")

import requests
import os

PEXELS_API_KEY = 'YOUR_API_KEY_HERE'

def search_videos(query, orientation=None, size=None, page=1):
    """
    Search for videos on Pexels.com.

    Parameters:
    - query: str
        The search query to use.
    - orientation: str, optional
        The orientation of the video (either 'landscape', 'portrait', or None).
    - size: str, optional
        The size of the video (either 'small', 'medium', 'large', or None).
    - page: int, optional
        The page number to return (default is 1).

    Returns:
    - A list of dictionaries representing the search results. Each dictionary
      contains the following keys:
      - id: str
      - width: int
      - height: int
      - url: str
      - duration: float
      - user: dict
    """
    params = {'query': query, 'per_page': 15, 'page': page}
    if orientation is not None:
        params['orientation'] = orientation
    if size is not None:
        params['size'] = size

    headers = {'Authorization': PEXELS_API_KEY}
    response = requests.get('https://api.pexels.com/videos/search', params=params, headers=headers)
    response.raise_for_status()

    return response.json()['videos']


def download_video(video_url, download_folder):
    """
    Download a video from the specified URL and save it to the specified folder.

    Parameters:
    - video_url: str
        The URL of the video to download.
    - download_folder: str
        The folder to save the downloaded video to.
    """
    response = requests.get(video_url, stream=True)
    response.raise_for_status()

    os.makedirs(download_folder, exist_ok=True)

    filename = os.path.join(download_folder, os.path.basename(video_url))
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


if __name__ == '__main__':
    query = input('Enter a search query: ')
    orientation = input('Enter an orientation (landscape, portrait, or leave blank): ')
    size = input('Enter a size (small, medium, large, or leave blank): ')

    videos = search_videos(query, orientation=orientation, size=size)

    for i, video in enumerate(videos):
        print(f"Downloading video {i + 1} of {len(videos)}...")
        download_video(video['video_files'][0]['link'], 'videos')

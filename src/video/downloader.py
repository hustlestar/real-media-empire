import requests
import os

from config import CONFIG

PEXELS_API_KEY = CONFIG.get("PEXEL_API_KEY")


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
    # looks like 80 perp_page is max
    params = {'query': query, 'per_page': 80, 'page': page}
    if orientation is not None:
        params['orientation'] = orientation
    if size is not None:
        params['size'] = size

    videos, next_page_url, total_results = read_page(params)
    return videos, next_page_url, total_results


def read_page(params=None, page_url='https://api.pexels.com/videos/search'):
    headers = {'Authorization': PEXELS_API_KEY}
    response = requests.get(page_url, params=params, headers=headers, verify=False)
    response.raise_for_status()
    response_json = response.json()
    videos, next_page_url, total_results = response_json['videos'], response_json.get('next_page'), response_json['total_results']
    return videos, next_page_url, total_results


def process_next_page(page_url):
    videos, next_page_url, total_results = read_page(page_url)
    return videos, next_page_url


def download_video(video_url, result_filename, download_folder):
    """
    Download a video from the specified URL and save it to the specified folder.

    Parameters:
    - video_url: str
        The URL of the video to download.
    - download_folder: str
        The folder to save the downloaded video to.
    """
    response = requests.get(video_url, stream=True, verify=False)
    try:
        response.raise_for_status()
    except:
        return None

    os.makedirs(download_folder, exist_ok=True)

    filename = os.path.join(download_folder, f"{result_filename}.mp4")
    if os.path.exists(filename):
        return False
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename


class PexelsDownloadTask:
    def __init__(self, query, download_dir=None, orientation='landscape', size='small', number_of_downloads=3, height=1080, width=1920):
        self.query = query
        self.download_dir = download_dir
        self.orientation = orientation
        self.size = size
        self.number_of_downloads = number_of_downloads
        self.completed_downloads = 0
        self.height = height
        self.width = width
        self.processed_videos = 0
        self.current_page_number = 0
        self.downloaded_files = []

    def run(self):
        print(f"Starting download task for query {self.query}, number of downloads is set to {self.number_of_downloads}")
        videos, next_page, total_results_number = search_videos(self.query, self.orientation, self.size)

        if self.number_of_downloads and videos:
            while True:
                try:
                    video = videos.pop()
                    self.processed_videos = self.processed_videos + 1
                except:
                    video = None
                    print(f"Processed all videos on page {self.current_page_number}, going to next page {next_page}")
                    self.current_page_number = self.current_page_number + 1
                if self.completed_downloads >= self.number_of_downloads:
                    print("Successfully finished running of download task")
                    break
                if video:
                    video_files = list(filter(lambda x: x.get('height') == self.height and x.get('width') == self.width, video['video_files']))
                    if video_files:
                        video_url = video_files[0]['link']
                        file_type = video_files[0]['file_type']
                        result_filename = video_files[0]['id']
                        if 'mp4' in file_type:
                            print(f"Downloading video with id {result_filename}")
                            downloaded_file = download_video(video_url, result_filename, self.download_dir)
                            if downloaded_file:
                                self.completed_downloads = self.completed_downloads + 1
                                self.downloaded_files.append(downloaded_file)
                        else:
                            print(f"Video {result_filename} is not mp4")
                    else:
                        print(f"Required resolution is not found for video")
                elif self.processed_videos < total_results_number and next_page:
                    videos, next_page = process_next_page(next_page)
                else:
                    break

        else:
            print(f"Found {total_results_number} results matching your query: "
                  f"{self.query}, {self.orientation}, {self.size} and desired amount of downloads {self.number_of_downloads}")
        return self


if __name__ == '__main__':
    # 'Enter an orientation (landscape, portrait, or leave blank): '
    orientation = 'landscape'
    # 'Enter a size (small, medium, large, or leave blank): '
    size = 'small'

    PexelsDownloadTask(query="mountain range", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="city skyline", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="stormy sky", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="vibrant sunset", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="winding road", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="long flight of stairs", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="wild river", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    PexelsDownloadTask(query="steep cliff", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()

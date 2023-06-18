import random

from typing import List, Tuple

import logging
import math
import os

import requests

from config import CONFIG
from text.helpers import pick_random_from_list
import urllib3

from video.utils import read_video_clip

PEXELS_API_KEY = CONFIG.get("PEXEL_API_KEY")

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def search_photos(query, orientation=None, size=None, color=None, page=1):
    """
    Downloads photos from Pexels.com based on the given query and API key.
    Saves the photos in a subdirectory with the same name as the query.

    Parameters:
        query (str): The search query for the photos.
        api_key (str): The API key to use for the Pexels API.
        num_photos (int): The number of photos to download.

    Returns:
        None
    """
    # Set up the API request URL
    params = {'query': query, 'per_page': 80, 'page': page}
    if orientation is not None:
        params['orientation'] = orientation
    if size is not None:
        params['size'] = size
    if size is not None:
        params['color'] = color
    return read_page(page_url=f"https://api.pexels.com/v1/search", params=params)


def round_down_up(num):
    rounded_down = math.floor(num * 10) / 10
    rounded_up = math.ceil(num * 10) / 10
    return rounded_down, rounded_up


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

    videos, next_page_url, total_results = read_page(page_url='https://api.pexels.com/videos/search', params=params)
    return videos, next_page_url, total_results


def read_page(page_url='https://api.pexels.com/videos/search', params=None):
    headers = {'Authorization': PEXELS_API_KEY}
    logger.info(f"Reading page {page_url} with params {params}")
    response = requests.get(page_url, params=params, headers=headers, verify=False)
    response.raise_for_status()
    response_json = response.json()
    return response_json['videos'] if 'videos' in page_url else response_json['photos'], response_json.get('next_page'), response_json['total_results']


def download(url, result_filename, download_folder, file_format='.mp4', on_exists_filename=False):
    """
    Download a video from the specified URL and save it to the specified folder.

    Parameters:
    - video_url: str
        The URL of the video to download.
    - download_folder: str
        The folder to save the downloaded video to.
    """
    response = requests.get(url, stream=True, verify=False)
    try:
        response.raise_for_status()
    except:
        return None

    os.makedirs(download_folder, exist_ok=True)

    filename = os.path.join(download_folder, f"{result_filename}{file_format}")
    if os.path.exists(filename):
        return False if not on_exists_filename else filename
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename


class PexelsDownloadTask:
    def __init__(
            self,
            query,
            download_dir=CONFIG.get('DOWNLOAD_DIR'),
            orientation='landscape',
            size=None,
            number_of_downloads=3,
            height=1080,
            width=1920,
            is_video_download=True,
            width_to_height_ratio=16 / 9,
            photo_size='original',  # 'original', 'large2x', 'large', 'medium', 'small', 'tiny'
    ):
        self.query = query
        self.is_video_download = is_video_download
        if self.is_video_download:
            self.download_dir = os.path.join(download_dir, 'VIDEO', orientation, f"{width}_{height}")
        else:
            self.download_dir = os.path.join(download_dir, 'PHOTO', orientation, photo_size)
        self.orientation = orientation
        self.size = size
        self.number_of_downloads = number_of_downloads
        self.completed_downloads = 0
        self.height = height
        self.width = width
        self.processed_downloads = 0
        self.current_page_number = 0
        self.downloaded_files = []
        self.width_to_height_ratio_lower, self.width_to_height_ratio_higher = round_down_up(width_to_height_ratio)
        self.photo_size = photo_size
        self.appropriate_videos = []

    def run(self):
        logger.info(f"Starting download task for query {self.query}, number of downloads is set to {self.number_of_downloads}")
        self.download_video()
        self.download_photo()
        return self

    def download_photo(self):
        if not self.is_video_download:
            photos, next_page, total_results_number = search_photos(self.query, self.orientation, self.size)
            logger.info(f"Starting download task, found {total_results_number} results")
            if self.number_of_downloads and photos:
                while True:
                    try:
                        photo = photos.pop()
                        self.processed_downloads = self.processed_downloads + 1
                    except:
                        photo = None
                        logger.info(f"Processed all photos on page {self.current_page_number}, going to next page {next_page}")
                        self.current_page_number = self.current_page_number + 1
                    if self.completed_downloads >= self.number_of_downloads:
                        logger.info("Successfully finished running of download task")
                        break
                    if photo:
                        if photo.get('height') >= self.height and photo.get('width') >= self.width:
                            photo_files = photo.get('src', None)
                            ratio = photo.get('width') / photo.get('height')
                            if photo_files and ratio >= self.width_to_height_ratio_lower and ratio <= self.width_to_height_ratio_higher:
                                photo_url = photo_files.get(self.photo_size)
                                result_filename = photo.get('id')
                                logger.info(f"Downloading photo with id {result_filename}")
                                downloaded_file = download(photo_url, result_filename, self.download_dir, file_format='.jpg')
                                if downloaded_file:
                                    self.completed_downloads = self.completed_downloads + 1
                                    self.downloaded_files.append(downloaded_file)
                        else:
                            logger.info(f"Required width to height is not found for photo")
                    elif self.processed_downloads < total_results_number and next_page:
                        photos, next_page, _ = read_page(next_page)
                    else:
                        logger.info("Finished")
                        break

            else:
                logger.info(f"Found {total_results_number} results matching your query: "
                            f"{self.query}, {self.orientation}, {self.size} and desired amount of downloads {self.number_of_downloads}")

    def download_video(self):
        if self.is_video_download:
            videos, next_page, total_results_number = search_videos(self.query, self.orientation, self.size)
            logger.info(f"Starting download task, found {total_results_number} results")
            if self.number_of_downloads and videos:
                while True:
                    try:
                        video = videos.pop()
                        self.processed_downloads = self.processed_downloads + 1
                    except:
                        video = None
                        logger.info(f"Processed all videos on page {self.current_page_number}, going to next page {next_page}")
                        self.current_page_number = self.current_page_number + 1
                    if self.completed_downloads >= self.number_of_downloads:
                        logger.info("Successfully finished running of download task")
                        break
                    if video:
                        video_files = list(filter(lambda x: x.get('height') == self.height and x.get('width') == self.width, video['video_files']))
                        if video_files:
                            video_url = video_files[0]['link']
                            file_type = video_files[0]['file_type']
                            result_filename = video_files[0]['id']
                            if 'mp4' in file_type:
                                logger.info(f"Downloading video with id {result_filename}")
                                downloaded_file = download(video_url, result_filename, self.download_dir)
                                if downloaded_file:
                                    self.completed_downloads = self.completed_downloads + 1
                                    self.downloaded_files.append(downloaded_file)
                            else:
                                logger.info(f"Video {result_filename} is not mp4")
                        else:
                            logger.info(f"Required resolution is not found for video")
                    elif self.processed_downloads < total_results_number and next_page:
                        videos, next_page, _ = read_page(next_page)
                    else:
                        break

            else:
                logger.info(f"Found {total_results_number} results matching your query: "
                            f"{self.query}, {self.orientation}, {self.size} and desired amount of downloads {self.number_of_downloads}")

    def find_all_matching_videos(self):
        videos, next_page, total_results_number = search_videos(self.query, self.orientation, self.size)
        logger.info(f"Found {total_results_number} results matching your query: {self.query}, {self.orientation}, {self.size}")
        while next_page:
            new_videos, next_page, _ = read_page(next_page)
            videos.extend(new_videos)

        for f in videos:
            video_files = list(filter(lambda x: x.get('height') == self.height and x.get('width') == self.width, f['video_files']))
            if video_files:
                video_url = video_files[0]['link']
                file_type = video_files[0]['file_type']
                result_filename = video_files[0]['id']
                if 'mp4' in file_type:
                    self.appropriate_videos.append((video_url, result_filename))
        logger.info(f"Found {len(self.appropriate_videos)} videos with required resolution and orientation")
        return self.appropriate_videos

    def download_generator(self, download_queue: List[Tuple[str, str, str]]):
        """
        A generator that yields the results of the download_queue.
        """
        while True:
            next_index = random.randint(0, len(download_queue) - 1)
            try:
                next_download = download_queue.pop(next_index)
            except:
                raise StopIteration("No more items in the download queue")
            download_result = download(next_download[0], next_download[1], self.download_dir, on_exists_filename=True)
            if download_result:
                logger.info(f"Downloaded {download_result} successfully")
                yield download_result


def download_matching_video(thematic_download_generator, required_duration):
    filename = next(thematic_download_generator)
    logger.info(f"Downloaded cli: {filename}")
    clip = read_video_clip(filename)
    if clip.duration >= required_duration:
        return clip
    else:
        logger.warning(f"Clip duration is too short, trying to download another one")
        return download_matching_video(thematic_download_generator, required_duration)


if __name__ == '__main__':
    # 'Enter an orientation (landscape, portrait, or leave blank): '
    orientation = 'portrait'
    # 'Enter a size (small, medium, large, or leave blank): '
    size = 'small'
    task = PexelsDownloadTask(query="thunder storm", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=5000)
    videos = task.find_all_matching_videos()
    logger.info(next(task.download_generator(videos)))
    # PexelsDownloadTask(
    #     query="mountain range",
    #     orientation='landscape', height=1920, width=1080,
    #     download_dir=CONFIG.get('DOWNLOAD_DIR'),
    #     number_of_downloads=500,
    #     is_video_download=False,
    #     photo_size='large2x'
    # ).run()
    # PexelsDownloadTask(
    #     query="city skyline",
    #     orientation='landscape', height=1920, width=1080,
    #     download_dir=CONFIG.get('DOWNLOAD_DIR'),
    #     number_of_downloads=500,
    #     is_video_download=False,
    #     photo_size='large2x'
    # ).run()
    # PexelsDownloadTask(
    #     query="flower",
    #     orientation='landscape', height=1920, width=1080,
    #     download_dir=CONFIG.get('DOWNLOAD_DIR'),
    #     number_of_downloads=5000,
    #     is_video_download=False,
    #     photo_size='large2x'
    # ).run()
    # PexelsDownloadTask(query="model", download_dir=CONFIG.get('DOWNLOAD_DIR'),
    #                    size='medium',
    #                    height=1920,
    #                    width=1080,
    #                    orientation='portrait',
    #                    number_of_downloads=10000).run()
    # PexelsDownloadTask(query="waterfall",
    #                    download_dir=CONFIG.get('DOWNLOAD_DIR'),
    #                    size='medium',
    #                    height=1920,
    #                    width=1080,
    #                    orientation='portrait',
    #                    number_of_downloads=5000).run()
    # PexelsDownloadTask(query="waterfall", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=5000).run()
    # PexelsDownloadTask(query="vibrant sunset", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    # PexelsDownloadTask(query="winding road", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    # PexelsDownloadTask(query="long flight of stairs", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    # PexelsDownloadTask(query="wild river", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()
    # PexelsDownloadTask(query="steep cliff", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=200).run()

import logging
import os
import random
from moviepy.video.io.VideoFileClip import VideoFileClip
from typing import List, Any

from common.exception import WrongMediaException
from config import CONFIG
from image.colors import get_image_main_colors
from image.image_tagging import get_image_classes
from image.video_to_image import extract_frames
from pipelines.tasks import DEFAULT_ORIENTATION, DEFAULT_WIDTH, DEFAULT_HEIGHT
from text.helpers import pick_random_from_list

DIR_CACHE = {}

logger = logging.getLogger(__name__)


def find_matching_video(channel, required_duration=None):
    bg_video = None
    while bg_video is None:
        clip = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                               "VIDEO",
                                               channel.config.video_orientation,
                                               f"{channel.config.video_width}_{channel.config.video_height}"), 1)[0]
        try:
            is_video_matching(clip,
                              topics=channel.video_manager.topics,
                              colors=channel.video_manager.colors,
                              colors_to_avoid=channel.video_manager.colors_to_avoid,
                              topics_to_avoid=channel.video_manager.topics_to_avoid)
            if required_duration and clip.duration < required_duration:
                raise WrongMediaException(f"Video duration is too short {clip.duration}")
            bg_video = clip
        except WrongMediaException as x:
            logger.info(x)
            continue
    return bg_video


def is_video_matching(clip, colors, colors_to_avoid, topics, topics_to_avoid):
    if topics or colors or colors_to_avoid:
        all_colors, all_topics = extract_video_colors_and_topics(clip, colors, topics)
        if colors and not any(color in colors for color in all_colors):
            raise WrongMediaException(f"Video colors are not in required {colors}")
        if colors_to_avoid and any(color in colors_to_avoid for color in all_colors):
            raise WrongMediaException(f"Video colors are in forbidden {colors_to_avoid}")
        if topics and not any(topic in topics for topic in all_topics):
            raise WrongMediaException(f"Video topics are not in required {topics}")
        if topics_to_avoid and any(topic in topics_to_avoid for topic in all_topics):
            raise WrongMediaException(f"Video topics are in forbidden {topics_to_avoid}")


def extract_video_colors_and_topics(clip, colors, topics):
    images = extract_frames(clip.filename, num_frames=5)
    all_topics = set()
    all_colors = set()
    if topics:
        for i in images:
            image_classes = get_image_classes(image_ndarray=i, number_of_classes=6)
            all_topics.update(image_classes)
        logger.info(f"All TOPICS from video {all_topics}")

    if colors:
        for i in images:
            image_colors = get_image_main_colors(image_ndarray=i, number_of_colors=6)
            all_colors.update(image_colors)
        logger.info(f"All COLORS from video: {all_colors}")
    return all_colors, all_topics


def build_video_dir_path(orientation=DEFAULT_ORIENTATION, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    return os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                        "VIDEO",
                        orientation,
                        f"{width}_{height}")


def prepare_clip(video_dir, is_should_download, topics, orientation, width, height):
    from video.downloader import PexelsDownloadTask

    if is_should_download and topics:
        res = PexelsDownloadTask(query=topics[random.randint(0, len(topics))], number_of_downloads=1, orientation=orientation, height=height, width=width).run()
        clip = read_video_clip(res.downloaded_files[0])
    else:
        clip = read_n_video_clips(video_dir, 1)[0]
    return clip


def download_new_videos(topic, number, channel) -> List[Any]:
    from video.downloader import PexelsDownloadTask
    task = PexelsDownloadTask(query=topic, number_of_downloads=number, orientation=channel.config.video_orientation, height=channel.config.video_height,
                              width=channel.config.video_width, )
    res = task.find_all_matching_videos()
    task.download_generator(res)
    return None


def read_all_video_clips(path_to_dir, video_format='mp4'):
    return [VideoFileClip(os.path.join(path_to_dir, f)).setout_audio() for f in os.listdir(path_to_dir) if f.endswith(video_format)]


def read_n_video_clips(path_to_dir, number, video_format='mp4') -> List[VideoFileClip]:
    dir_files = DIR_CACHE.get(path_to_dir)
    if not dir_files:
        dir_files = os.listdir(path_to_dir)
        DIR_CACHE[path_to_dir] = dir_files
    dir_files = [f for f in dir_files if f.endswith(video_format)]
    number_of_files_in_dir = len(dir_files)
    result = []
    for n in range(number):
        f = dir_files[random.randint(0, number_of_files_in_dir - 1)]
        logger.info(f"Randomly selected file: {f} from dir: {path_to_dir}")
        result.append(VideoFileClip(os.path.join(path_to_dir, f)).without_audio())
    return result


def read_video_clip(path_to_clip):
    return VideoFileClip(path_to_clip).without_audio()


def pick_audio_background_file(channel):
    return os.path.join(channel.config.audio_background_dir_path, pick_random_from_list(os.listdir(channel.config.audio_background_dir_path)))

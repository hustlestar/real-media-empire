import json
import logging
import os.path
import random
from typing import Tuple

from audio.audio_processor import read_audio_clip
from common.config import read_config, ChannelConfig
from config import CONFIG
from pipelines.tasks.audio_tasks import AudioTasks
from pipelines.tasks.image_tasks import ImageTasks
from pipelines.tasks.social_tasks import SocialTasks
from pipelines.tasks.text_tasks import TextTasks
from pipelines.tasks.video_tasks import VideoTasks
from social.you_tube import VALID_PRIVACY_STATUSES
from text.helpers import build_prompt
from util.time import get_now

logger = logging.getLogger(__name__)


class YouTubeChannel:
    def __init__(self, channel_config_path, execution_date=None, is_recover=False) -> None:
        config: ChannelConfig = read_config(channel_config_path)
        logger.debug(f"Starting with following config:\n{json.dumps(config, indent=4)}")
        self.config = config
        neat_chanel_name = str(config.youtube_channel_name).lower().strip().replace(" ", "_")
        self.channel_root_dir = os.path.join(
            CONFIG.get("MEDIA_GALLERY_DIR"),
            "RESULTS",
            neat_chanel_name
        )
        self.youtube_privacy_status = config.youtube_privacy_status
        self.this_run_result_dir = os.path.join(
            self.channel_root_dir,
            get_now() if not execution_date else execution_date
        )
        if not is_recover:
            os.makedirs(self.this_run_result_dir, exist_ok=True)
        self.text_manager = TextTasks(
            title_suffix=config.youtube_title_suffix,
            results_dir=self.this_run_result_dir
        )
        self.audio_manager = AudioTasks(
            audio_background_dir_path=config.audio_background_dir_path,
            audio_background_api=config.audio_background_api,
            audio_background_api_key_or_path=config.audio_background_api_key_or_path,
            tts_api=config.tts_api,
            tts_type=config.tts_type,
            tts_voice_name=config.tts_voice_name,
            tts_api_key_or_path=config.tts_api_key_or_path,
            start_end_delay=config.video_start_end_delay,
            results_dir=self.this_run_result_dir,
            voice_over_speed=config.voice_over_speed
        )
        video_preset = config.video_background_presets[random.randint(0, len(config.video_background_presets) - 1)]
        logger.info(f"Randomly selected following video preset {video_preset.name}")
        self.video_manager = VideoTasks(
            topics=video_preset.topics,
            colors=video_preset.colors,
            colors_to_avoid=video_preset.colors_to_avoid,
            start_end_delay=config.video_start_end_delay,
            orientation=config.video_orientation,
            height=config.video_height,
            width=config.video_width,
            single_video_duration=config.video_single_video_duration,
            is_allow_duplicate_clips=False,
            results_dir=self.this_run_result_dir
        )
        self.image_manager = ImageTasks(
            thumbnail_background_colors=config.thumbnail_background_colors,
            thumbnail_fonts_dir=config.thumbnail_fonts_dir,
            results_dir=self.this_run_result_dir
        )
        self.socials_manager = SocialTasks(
            youtube_api_key_path=config.youtube_client_secrets_file,
            youtube_channel_name=neat_chanel_name,
            youtube_channel_id=config.youtube_channel_id,
            youtube_tags=config.youtube_tags,
            youtube_category=config.youtube_category
        )

    @property
    def result_dir(self):
        return self.this_run_result_dir

    def create_text_script(self, prompt) -> Tuple[str, bool]:
        return self.text_manager.create_text(prompt)

    def create_video(self, duration=None):
        return self.video_manager.create_video_background(duration=duration)

    def create_audio_voice_over(self, text_script, is_ssml, result_file=f"2_voiceover.mp3"):
        voice_over_filename = self.audio_manager.create_audio_voice_over(text_script, is_ssml, result_file=result_file)
        return read_audio_clip(voice_over_filename)

    def create_audio_background(self):
        audio_background_filename = self.audio_manager.create_audio_background()
        return read_audio_clip(audio_background_filename)

    def create_final_audio(self, voice_over_audio_clip, background_audio_clip):
        final_audio, final_duration = self.audio_manager.create_final_audio(voice_over_audio_clip, background_audio_clip)
        return final_audio, final_duration

    def create_final_video(self, video, final_audio) -> str:
        final_video = self.video_manager.save_final_video(video, final_audio)
        return final_video

    def create_thumbnail(self, title):
        return self.image_manager.create_thumbnail(title)

    def create_title_description_thumbnail_title(self, text, prompt=None) -> Tuple[str, str, str, str]:
        return self.text_manager.create_title_description_thumbnail_title(text, prompt=prompt)

    def create_basic_youtube_video(self, text_script, is_ssml) -> str:
        voice_over_audio_clip = self.create_audio_voice_over(text_script, is_ssml)
        background_audio_clip = self.create_audio_background()
        final_audio, final_duration = self.create_final_audio(voice_over_audio_clip, background_audio_clip)
        video = self.create_video(duration=final_duration)
        final_video = self.create_final_video(video, final_audio)
        return final_video

    def upload_to_youtube(self, final_video, text_script):
        title, description, thumbnail_title, comment = self.create_title_description_thumbnail_title(text_script)
        thumbnail_image_path = self.create_thumbnail(thumbnail_title)
        logger.info(f"Before YouTube upload\n{title}\n{description}\n{thumbnail_title}")
        video_id = self.socials_manager.upload_video_to_youtube(final_video, title, description, privacy_status=VALID_PRIVACY_STATUSES[1])
        thumbnail_url = self.socials_manager.upload_thumbnail_for_youtube(thumbnail_image_path, video_id)
        return video_id, thumbnail_url


if __name__ == '__main__':
    channel = YouTubeChannel("D:\\Projects\\media-empire\\jack\\daily_mindset.yaml")
    prompt = build_prompt(channel.config.main_prompt_template,
                          channel.config.main_prompt_topics_file,
                          narrative_types=channel.config.main_prompt_narrative_types,
                          engagement_techniques=channel.config.main_prompt_engagement_techniques,
                          )
    channel.socials_manager.youtube_uploader.authenticate()
    text_script, is_ssml = channel.create_text_script(prompt)
    final_video = channel.create_basic_youtube_video(text_script, is_ssml)
    logger.info(f"Video {final_video} \ntext{text_script}")
    video_id, thumbnail_url = channel.upload_to_youtube(final_video, text_script)
    logger.info(f"Video id {video_id} thumbnail url {thumbnail_url}")

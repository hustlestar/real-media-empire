from typing import List, Any, Dict, Union

import yaml
from munch import Munch


class VideoBackgroundPreset:
    def __init__(self):
        self.name: str = None
        self.colors: List[str] = None
        self.colors_to_avoid: List[str] = None
        self.topics: List[str] = None
        self.topics_to_avoid: List[str] = None


class ChannelConfigTemplate:
    def __init__(self):
        self.youtube_channel_name: str = None
        self.youtube_channel_id: str = None
        self.youtube_client_secrets_file: str = None
        self.youtube_category: str = None
        self.youtube_tags: List[str] = None
        self.youtube_title_suffix: str = None
        self.youtube_privacy_status: str = None

        self.all_extras: Dict[str, Any] = None

        self.video_download_new:  bool = False
        self.video_orientation: str = 'landscape'  # portrait
        self.video_width: int = 1920
        self.video_height: int = 1080
        self.video_transition: str = None
        self.video_transition_duration: int = None
        self.video_start_end_delay: int = None
        self.video_single_video_duration: int = None
        self.video_background_presets: List[VideoBackgroundPreset] = None
        self.video_fonts_list: List[str] = None
        self.video_text_color_list: List[str] = None

        self.audio_background_dir_path: str = None
        self.audio_background_api: str = None
        self.audio_background_api_key_or_path: str = None

        self.main_text_type: str = 'text'  # ssml
        self.main_prompt_topics_file = None
        self.main_prompt_narrative_types: List[str] = None
        self.main_prompt_number_of_engagement_techniques: int = None
        self.main_prompt_engagement_techniques: List[str] = None
        self.main_prompt_template = None
        self.main_prompt_number_of_words: int = None
        self.main_ttt_api: str = None
        self.main_ttt_model_name: str = None
        self.main_ttt_tokens_number: int = None

        self.description_ttt_api: str = None
        self.description_ttt_model_name: str = None

        self.title_ttt_api: str = None
        self.title_ttt_model_name: str = None

        self.thumbnail_ttt_api: str = None
        self.thumbnail_model_name: str = None
        self.thumbnail_background_colors: List[str] = None
        self.thumbnail_fonts_dir: str = None

        self.tts_api: str = None
        self.tts_type: str = None
        self.tts_voice_name: Union[str, int] = None
        self.tts_secondary_voice_name: Union[str, int] = None
        self.tts_api_key_or_path: str = None
        self.voice_over_speed: float = None


class ChannelConfig(Munch, ChannelConfigTemplate):
    pass


def read_config(config_path) -> ChannelConfig:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return Munch.fromDict(ChannelConfig(config))


if __name__ == '__main__':
    config = read_config("D:\\Projects\\media-empire\\jack\\daily_mindset.yaml")
    print(config)

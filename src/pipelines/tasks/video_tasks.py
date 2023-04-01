import os.path
from typing import List

from pipelines.tasks import DEFAULT_START_END_DELAY, DEFAULT_ORIENTATION, DEFAULT_HEIGHT, DEFAULT_WIDTH
from pipelines.tasks.common_tasks import CommonTasks, build_video_dir_path


class VideoTasks:
    def __init__(
            self,
            topics: List[str] = None,
            colors: List[str] = None,
            colors_to_avoid: List[str] = None,
            start_end_delay: int = DEFAULT_START_END_DELAY,
            orientation=DEFAULT_ORIENTATION,
            height=DEFAULT_HEIGHT,
            width=DEFAULT_WIDTH,
            single_video_duration=10,
            is_allow_duplicate_clips=False,
            results_dir=None):
        self.topics = topics
        self.colors = colors
        self.colors_to_avoid = colors_to_avoid
        self.start_end_delay = start_end_delay
        self.orientation = orientation
        self.height = height
        self.width = width
        self.video_task = CommonTasks(
            single_video_duration=single_video_duration,
            is_allow_duplicate_clips=is_allow_duplicate_clips
        )
        self.results_dir = results_dir

        self.video = None
        self.used_video_clips = None

    def create_video_background(self, duration=None):
        print(f"Final video duration would be: {duration}")
        self.video, self.used_video_clips = self.video_task.prepare_video(
            final_duration=duration,
            topics=self.topics,
            colors=self.colors,
            colors_to_avoid=self.colors_to_avoid,
            video_dir=build_video_dir_path(self.orientation, self.width, self.height),
            orientation=self.orientation,
            width=self.width,
            height=self.height
        )
        print(self.video)
        print(self.used_video_clips)
        return self.video

    def save_final_video(self, video, final_audio) -> str:
        final_video_path = os.path.join(self.results_dir, '0_result_video.mp4')
        self.video_task.prepare_and_save_final_video(video, final_audio, final_audio.duration, final_video_path)
        return final_video_path


if __name__ == '__main__':
    VideoTasks(
        topics=[1],
        colors=['green', 'olive', 'mint', 'turquoise', 'teal'],
        colors_to_avoid=['magenta', 'pink', 'coral', 'red']
    ).create_video_background()

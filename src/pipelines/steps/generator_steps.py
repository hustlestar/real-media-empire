import os.path

import logging
import time

from common.log import me_init_logger
from pipelines.steps.gpt_steps import rate_text
from pipelines.you_tube_channel import YouTubeChannel
from text.extract_keywords import extract_key_sentences, extract_keywords_with_timestamps, preprocess_transcript
from text.text_summary import provide_text_summary
from video.download.youtube_downloader import download_video_and_audio, download_video_transcript, merge_audio_and_video, DOWNLOADS_DIR

me_init_logger()
logger = logging.getLogger(__name__)


def prepare_shorts_snippets_video_with_transcript(video_url, prompt_template, downloads_dir, rating_sum=15):
    video_meta, audio_path, video_path = download_video_and_audio(video_url, downloads_dir=downloads_dir)

    transcript_path = download_video_transcript(video_meta.video_id, downloads_dir=downloads_dir)

    with open(transcript_path, "r") as f:
        initial_transcript = f.read().lower()

    key_sentences = extract_key_sentences(initial_transcript, num_sentences=round(video_meta.length / 60 / 6) + 1)

    final_summary = provide_text_short_summary(initial_transcript, video_meta, downloads_dir=downloads_dir)

    # Iterate through the key_sentences of the keyword transcript
    initial_transcript_lines = initial_transcript.split("\n")
    last_line_index = 0
    for i, sentence in enumerate(key_sentences):
        logger.info(f"Processing video {i} with sentence:\n{sentence}")
        keyword_matches, last_line_index = extract_keywords_with_timestamps(initial_transcript_lines[last_line_index:], sentence)
        # logger.info the keyword matches
        if keyword_matches:
            ratings = rate_text(sentence, final_summary, prompt_template)
            if sum(ratings.values()) >= rating_sum:
                from_timestamp = keyword_matches[0]["timestamp_range"][0]
                to_timestamp = keyword_matches[-1]["timestamp_range"][1]
                try:
                    if to_timestamp < from_timestamp:
                        raise ValueError("Timestamp Range is not valid: start is before end")
                    result_name = f"{video_meta.video_id}_{i}"
                    final_path = merge_audio_and_video(
                        audio_path,
                        video_path,
                        result_name=result_name,
                        downloads_dir=downloads_dir,
                        from_timestamp=from_timestamp - 3 if from_timestamp > 3 else from_timestamp,
                        to_timestamp=to_timestamp + 4,
                    )
                    with open(os.path.join(downloads_dir, f"{result_name}.txt"), "w") as f:
                        f.write(sentence)
                    logger.info(f"Video {i} result path: {final_path}")
                except Exception as x:
                    logger.info(f"Error processing video {i}: {x}")
            else:
                logger.info(f"Video {i} has poor rating")


def provide_text_short_summary(initial_transcript, video_meta, downloads_dir=DOWNLOADS_DIR):
    text = preprocess_transcript(initial_transcript)
    start_time = time.time()
    long_summary = provide_text_summary(text)
    final_summary = long_summary
    if len(long_summary) > 1024:
        logger.info("--- %s seconds ---" % (time.time() - start_time))
        final_summary = provide_text_summary(long_summary)
        logger.info("--- %s seconds ---" % (time.time() - start_time))
    with open(os.path.join(downloads_dir, f"{video_meta.video_id}_summary.txt"), "w") as f:
        f.write(f"Initial Title: {video_meta.title}\n")
        f.write(f"Initial Author: {video_meta.author}\n")
        f.write(final_summary)
    return final_summary


def test_prepare_shorts_snippets_video_with_transcript():
    with open("G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\downloads\\z-mJEZbHFLs_transcript.txt", "r") as f:
        initial_transcript = f.read()

    key_sentences = extract_key_sentences(initial_transcript.lower(), num_sentences=round(20))

    # Iterate through the key_sentences of the keyword transcript
    initial_transcript_lines = initial_transcript.lower().split("\n")
    last_line_index = 0
    for i, sentence in enumerate(key_sentences):
        logger.info(f"Processing video {i} with sentence: {sentence}")
        keyword_matches, last_line_index = extract_keywords_with_timestamps(initial_transcript_lines[last_line_index:], sentence)


if __name__ == "__main__":
    channel = YouTubeChannel(channel_config_path="G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\daily_mindset_shorts.yaml")
    prepare_shorts_snippets_video_with_transcript(
        "https://www.youtube.com/watch?v=i4EhddvJS2A&t=236s", channel.config.main_prompt_template, channel.config.manual_downloads_dir, rating_sum=7
    )
    # test_prepare_shorts_snippets_video_with_transcript()

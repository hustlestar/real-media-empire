import re

from typing import Optional, Tuple

import json

import os

import logging

from common.constants import QUOTE_TXT, EXTRA_LABEL_COLORS, VIDEO_BACKGROUND_THEMES
from config import CONFIG
from data.dao import add_channel, get_db, is_author_used_in_channel
from pipelines.params.params_for_pipeline import PipelineParams
from pipelines.you_tube_channel import YouTubeChannel
from text import helpers
from text.helpers import pick_random_from_list, finish_line, TemplateArg, DEFAULT_TEMPLATE
from video.movie import ExtraLabel, video_with_text_full_sentence_many_clips, LineToMp3File, create_thematic_download_generator, BG_CLIP_STRATEGIES, video_with_text
from video.utils import read_n_video_clips, pick_audio_background_file

logger = logging.getLogger(__name__)


def predefined_quote_by_author(params):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    single_author = get_single_author(params)
    quote = pick_random_from_list(single_author.get('quotes'))
    logger.info(f"Result quote is\n{quote}")
    quote_lines = [finish_line(s) for s in quote.split(".") if s]
    result = quote_lines if not params.is_split_quote else helpers.prepare_short_lines(quote_lines)
    result.append(finish_line(single_author.get("author")))
    with open(os.path.join(channel.result_dir, f"{QUOTE_TXT}"), "w") as k:
        k.write(f"{quote} {single_author.get('author')}")
    for l in result:
        logger.info(l)
    return result


def get_single_author(params: PipelineParams):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    if not params.author:
        logger.info(f"No selected author, picking one randomly.")
        quote_file = pick_random_from_list(channel.config.all_extras.get("quote_sources"))
        with open(quote_file) as f:
            all_authors = json.loads(f.read())
        return pick_random_from_list(all_authors)
    else:
        return find_selected_author(params)


def find_selected_author(params: PipelineParams):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Selected author {params.author}")
    for quote_file in channel.config.all_extras.get("quote_sources"):
        with open(quote_file) as f:
            all_authors = json.loads(f.read())
            for a in all_authors:
                if a.get('author') == params.author:
                    return a


def find_unused_author(params: PipelineParams):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    if not params.author:
        add_channel(next(get_db()), name=channel.config.youtube_channel_id)
        logger.info(f"No selected author, picking unused one.")
        for quote_file in channel.config.all_extras.get("quote_sources"):
            with open(quote_file) as f:
                all_authors = json.loads(f.read())
                for a in all_authors:
                    if not is_author_used_in_channel(next(get_db()), channel_name=channel.config.youtube_channel_id, author_name=a.get('author')):
                        return a
    else:
        return find_selected_author(params)


def prepare_author_title(title: str):
    if title and 'unknown' not in title.lower():
        title = title.replace(", was a ", ", ").replace(", was an ", ", ")
        logger.info(f"Prepared following author title: {title}")
        return title
    else:
        return None


def prepare_extra_label(author_funny_facts, author_interesting_facts, author_inspiring_facts, used_facts) -> Optional[Tuple[str, ExtraLabel]]:
    def pop_lists(list1, list2, list3):
        while list1 or list2 or list3:
            if list1 and len(list1) >= len(list2) and len(list1) >= len(list3):
                yield "Funny Fact", list1.pop()
            elif list2 and len(list2) >= len(list3):
                yield "Interesting Fact", list2.pop()
            elif list3:
                yield "Inspiring Fact", list3.pop()
            else:
                yield None

    res = pop_lists(author_funny_facts, author_interesting_facts, author_inspiring_facts)
    fact = None
    try:
        fact = next(res)
    except:
        pass
    if fact and fact not in used_facts:
        used_facts.add(fact)
        return fact[1], ExtraLabel(fact[0], color=pick_random_from_list(EXTRA_LABEL_COLORS))


def prepare_quote_intro_questions(quote, author):
    prompt_params = {
        "main_idea": f"For the video with following quote by {author}:\n{''.join(quote)}",
    }
    json_field_name = 'quote_intro_questions'
    args = [
        TemplateArg(
            text_definition="json array of 6 to 10 strings containing question about quote and author, that will spark viewers"
                            "curiosity and engage them."
                            " Question must not contain word quote. "
                            " Use you instead of the word one. "
                            "Each question should be up to 6 words and it should end with ...",
            json_field_name=json_field_name,
            value='[]'
        ),
    ]
    quote_intro_questions_dict = helpers.create_result_dict_from_prompt_template(
        DEFAULT_TEMPLATE,
        args,
        prompt_params,
        tokens_number=1000
    )
    return quote_intro_questions_dict[json_field_name]


def is_bad_intro_question(intro_question):
    skip_question = False
    for b in [
        'what was the context',
        'what other famous quotes ',
        'what other inspiring quotes ',
        'what other ',
        'who wrote ',
        'what does the quote suggest ',
        'what are some examples ',
        'what is the context of',
        'what is the famous quote ',
        'who said ',
    ]:
        if b in intro_question.lower():
            skip_question = True
    return skip_question


def prepare_intro_video(channel, final_video_sequence, voice_over_index, generator=None, intro_question=None):
    logger.info(f"Starting generation of INTRO video {intro_question}")
    voice_over_file = single_voice_over(intro_question, channel, index=voice_over_index, is_secondary=True)
    intro_video = video_with_text_full_sentence_many_clips(
        channel,
        [LineToMp3File(intro_question, voice_over_file)],
        text_colors=['yellow'],
        fonts_list=channel.config.video_fonts_list,
        is_download_new_video=channel.config.video_download_new,
        is_save_result=False,
        thematic_download_generator=generator,
        single_clip_duration=4
    )
    final_video_sequence.append(intro_video)
    return intro_video, intro_question, voice_over_index + 1


def prepare_thematic_download_generator(channel, quote):
    background_themes_dict = ask_for_background_themes(channel, quote)
    thematic_download_generator = create_thematic_download_generator(channel, True, background_themes_dict)
    return thematic_download_generator


def read_video_for_channel(channel):
    return read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                           "VIDEO",
                                           channel.config.video_orientation,
                                           f"{channel.config.video_width}_{channel.config.video_height}"), 1)[0]


def voice_overs(params, text_lines):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    return [single_voice_over(line, channel, i)
            for i, line in enumerate(text_lines)]


def single_voice_over(line, channel, index, is_secondary=False):
    return channel.audio_manager.create_audio_voice_over(
        line,
        is_ssml=False,
        result_file=f"{index}_voiceover.mp3",
        speaking_rate=channel.config.voice_over_speed,
        is_secondary=is_secondary
    )


def shorts_with_voice(params, text_lines, voice_over_files, is_swamp=False):
    from video.utils import find_matching_video
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    background_themes_list = ask_for_background_themes(channel, text_lines)
    for i in range(len(BG_CLIP_STRATEGIES)):
        try:
            clean_text = re.sub(r"[^a-zA-Z]+", " ", " ".join(text_lines))
            clean_text = re.sub(r"\\s+", "_", clean_text).lower()

            result_video_filename = build_file_name(clean_text, channel, i, is_swamp, params)

            lines = [LineToMp3File(k, v) for k, v in zip(text_lines, voice_over_files)]
            bg_audio_filename = pick_audio_background_file(channel)
            if params.is_split_quote:
                bg_video = find_matching_video(channel)
                logger.warning(f"Split quote is used for text preparation.")
                video_with_text(bg_video,
                                lines,
                                result_file=result_video_filename,
                                fonts_list=channel.config.video_fonts_list,
                                bg_audio_filename=bg_audio_filename,
                                text_colors=channel.config.video_text_color_list
                                )
            else:
                for s in BG_CLIP_STRATEGIES:
                    is_download_new_video = pick_random_from_list([True, False])
                    video_with_text_full_sentence_many_clips(
                        channel,
                        lines,
                        result_file=build_file_name(clean_text, channel, i, is_swamp, params, bg_clip_strategy=s, background_type='new' if is_download_new_video else 'reuse'),
                        fonts_list=channel.config.video_fonts_list,
                        bg_audio_filename=bg_audio_filename,
                        text_colors=channel.config.video_text_color_list,
                        bg_clip_strategy=s,
                        single_clip_duration=2,
                        is_download_new_video=is_download_new_video
                    )
        except Exception as x:
            logger.error(f"Error while creating video {i}", x)
            continue
    return result_video_filename


def ask_for_background_themes(channel, text_lines):
    background_themes = None
    if channel.config.video_download_new:
        prompt_params = {
            "main_idea": f"For the video with following text script:\n{''.join(text_lines)}",
        }
        json_field_name = 'video_background_picture'
        args = [
            TemplateArg(
                text_definition="json array of strings containing matching picture for video background. Each picture topic should be up to 3 words",
                json_field_name=json_field_name,
                value='[]'
            ),
        ]
        background_themes_dict = helpers.create_result_dict_from_prompt_template(
            DEFAULT_TEMPLATE,
            args,
            prompt_params,
            tokens_number=1000
        )
        background_themes = background_themes_dict[json_field_name]
    return background_themes


def build_file_name(clean_text, channel, i, is_swamp, params, bg_clip_strategy="", background_type=''):
    return os.path.join(
        channel.swamp_dir if is_swamp else channel.result_dir,
        f"{params.execution_date}_{clean_text}_{bg_clip_strategy}_{i}_{background_type}.mp4"
    )

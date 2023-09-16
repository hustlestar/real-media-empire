import os

import json

from typing import List, Dict

import logging
from zenml.steps import step, Output

from common.constants import QUOTE_TXT
from pipelines.params.params_for_pipeline import PipelineParams
from pipelines.steps.utils import predefined_quote_by_author
from pipelines.you_tube_channel import YouTubeChannel
from text import helpers
from text.helpers import pick_random_from_list, TemplateArg, finish_line

INT_VALUE = 'integer 1 to 10'

logger = logging.getLogger(__name__)


@step
def build_prompt(params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    prompt = helpers.build_prompt(
        channel.config.main_prompt_template,
        channel.config.main_prompt_topics_file,
        narrative_types=channel.config.main_prompt_narrative_types,
        engagement_techniques=channel.config.main_prompt_engagement_techniques,
        number_of_words=channel.config.main_prompt_number_of_words
    )
    return prompt


@step
def create_quote_by_author(params: PipelineParams) -> List[str]:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    author = pick_random_from_list(json.loads(open(channel.config.main_prompt_topics_file).read())['authors'])
    topic = pick_random_from_list(channel.config.main_prompt_narrative_types)
    prompt_params = {
        "topic": topic,
        "author": author,
        "main_idea": ""
    }
    args = [
        TemplateArg(
            text_definition="field named quote having [[topic]] by [[author]] as string. It shouldn't be well known or popular, it should be random",
            json_field_name='quote',
            value='\"\"'
        ),
        TemplateArg(
            text_definition="field named author having author of quote",
            json_field_name='author',
            value='\"\"'
        ),
    ]
    quote_dict = helpers.create_result_dict_from_prompt_template(
        channel.config.main_prompt_template,
        args,
        prompt_params,
    )
    quote = quote_dict.get("quote")
    logger.info(f"Result quote is\n{quote}")
    quote_lines = [finish_line(s) for s in quote.split(".") if s]
    result = helpers.prepare_short_lines(quote_lines)

    with open(os.path.join(channel.result_dir, f"{QUOTE_TXT}"), "w") as k:
        k.write(f"{quote} {finish_line(author)}")

    result.append(quote_dict.get("author"))
    for l in result:
        logger.info(l)
    return result


def rate_text(text, context, prompt_template) -> Dict[str, str]:
    prompt_params = {
        "main_idea": "I'll provide you with text snipper and with short summary of the original full text. "
                     "You'll rate this text snippet by several criteria in the grade of 1 to 10, where 1 is least matching criteria and 10 is most.\n"
                     "Here's text snippet: " + text.replace("\n", " ") + "\nHere's short summary: " + context.replace("\n", " ") + "\n",
    }
    args = [
        TemplateArg(
            text_definition="is text snippet clear without full context",
            json_field_name='clearness',
            value=INT_VALUE
        ),
        TemplateArg(
            text_definition="is text snippet engaging enough",
            json_field_name='engaging',
            value=INT_VALUE
        ),
        TemplateArg(
            text_definition="is text snippet worth publishing as youtube shorts",
            json_field_name='publishable',
            value=INT_VALUE
        ),
    ]
    result_dict = helpers.create_result_dict_from_prompt_template(
        prompt_template,
        args,
        prompt_params,
    )
    return result_dict


@step
def use_predefined_quote_by_author(params: PipelineParams) -> List[str]:
    return predefined_quote_by_author(params)


@step
def create_text_script(prompt: str, params: PipelineParams) -> Output(text_script=str, is_ssml=bool):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    text_script, is_ssml = channel.create_text_script(prompt)
    return text_script, is_ssml


if __name__ == '__main__':
    channel = YouTubeChannel(channel_config_path="G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\daily_mindset_shorts.yaml")
    for i in range(21):
        print(f"Iteration {i}")
        text = open(f"G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\downloads\\z-mJEZbHFLs_{i}.txt", "r").read()
        context = open("G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\downloads\\z-mJEZbHFLs_summary.txt", "r").read()
        print(rate_text(text, context, channel.config.main_prompt_template))
        print(sum(rate_text(text, context, channel.config.main_prompt_template).values()))
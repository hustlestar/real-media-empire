import json

import logging
import os
from zenml.steps import step

from pipelines.params.mgmt_params import MgmtParams
from pipelines.steps.library import single_voice_over
from pipelines.you_tube_channel import YouTubeChannel

logger = logging.getLogger(__name__)


@step
def batch_create_voiceover(params: MgmtParams) -> None:
    logger.info(f"Starting empty dir cleanup in: {params.starting_dir}")
    channel = YouTubeChannel(channel_config_path=params.channel_config_path)
    if not os.path.exists(params.voiceover_json):
        raise Exception(f"Starting dir {params.voiceover_json} does not exist")
    raw_quotes = json.loads(open(params.voiceover_json).read())
    for a, quotes in raw_quotes.items():
        if len(quotes) < 15:
            continue
        voice_over_id = 0
        try:
            logger.info(f"Creating voiceover for {a}")
            voice_over_results_dir = os.path.join(params.results_dir, a)
            os.makedirs(voice_over_results_dir, exist_ok=True)
            channel.set_audio_results_dir(voice_over_results_dir)
            for q in set(quotes):
                try:
                    voice_over_file = single_voice_over(q, channel, index=voice_over_id, is_secondary=False)
                    voice_over_id = voice_over_id + 1
                except Exception as e:
                    logger.error(f"Error creating voiceover for {e}")
            result_text_script = "".join(quotes)
            with open(os.path.join(voice_over_results_dir, f"0_text_script.txt"), "w") as f:
                f.write(result_text_script)
        except Exception as e:
            logger.error(f"Error creating voiceover for {a}: {e}")
    logger.info("Finished shorts generation")

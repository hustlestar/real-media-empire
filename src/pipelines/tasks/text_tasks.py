import json
import os
import re
from typing import Tuple

from pipelines.tasks.common_tasks import CommonTasks
from text.chat_gpt import ChatGPTTask
from text.util import extract_json_as_dict


class TextTasks:
    def __init__(self, main_ttt_api=None, main_ttt_model_name=None, description_ttt_api=None, description_ttt_model_name=None, title_ttt_api=None, title_ttt_model_name=None,
                 thumbnail_ttt_api=None, thumbnail_model_name=None, title_suffix=None, results_dir=None):
        self.main_ttt_api: str = main_ttt_api
        self.main_ttt_model_name: str = main_ttt_model_name

        self.description_ttt_api: str = description_ttt_api
        self.description_ttt_model_name: str = description_ttt_model_name

        self.title_ttt_api: str = title_ttt_api
        self.title_ttt_model_name: str = title_ttt_model_name

        self.thumbnail_ttt_api: str = thumbnail_ttt_api
        self.thumbnail_model_name: str = thumbnail_model_name

        self.title_suffix = title_suffix
        self.results_dir = results_dir

        self.text_for_voiceover = None
        self.cleaned_text = None
        self.is_ssml = None

        self.title, self.description, self.thumbnail_title = None, None, None

    def create_text(self, prompt, text_type='text') -> Tuple[str, bool]:
        helper = CommonTasks(prompt=prompt)
        self.text_for_voiceover, self.is_ssml = helper.prepare_text_for_voiceover()
        with open(os.path.join(self.results_dir, '1_text_script.txt'), 'w') as f:
            f.write(self.text_for_voiceover)
        return self.text_for_voiceover, self.is_ssml

    def create_description(self, text, prompt=None):
        pass

    def create_title(self, text, prompt=None, suffix=None):
        pass

    def create_thumbnail_title(self, text, prompt=None):
        pass

    def create_title_description_thumbnail_title(self, text, prompt=None) -> Tuple[str, str, str]:
        self.cleaned_text = re.sub(r'<.*?>', '', text) if '<speak>' in text else text
        if not prompt:
            prompt = """
            please fill this json
            {
                "title": "",
                "description_from_2_to_5_sentences": "",
                "thumbnail_from_2_to_4_words_clickbait_phrase": ""
            }
            with:
            title,
            2 to 5 sentences description, 
            2 to 4 words thumbnail clickbait phrase
            for the following video script:\n""" + self.cleaned_text
            retry_counter = 0
            while retry_counter < 5:
                result_text = ChatGPTTask(prompt=prompt, tokens_number=500).run().text
                print(f"CHAT GPT response \n{result_text}")
                if '{' in result_text and '}' in result_text:
                    result_dict = extract_json_as_dict(result_text)
                    if ("title" in result_dict.keys()
                            and "description_from_2_to_5_sentences" in result_dict.keys()
                            and "thumbnail_from_2_to_4_words_clickbait_phrase" in result_dict.keys()
                    ):
                        self.title, self.description, self.thumbnail_title = (
                            result_dict["title"],
                            result_dict["description_from_2_to_5_sentences"],
                            result_dict["thumbnail_from_2_to_4_words_clickbait_phrase"]
                        )
                        self.title = (str(self.title).upper().strip() + f" {self.title_suffix}").strip()
                        self.thumbnail_title = str(self.thumbnail_title).upper()
                        with open(os.path.join(self.results_dir, '4_youtube_meta.json'), 'w') as f:
                            f.write(json.dumps(
                                {
                                    "title": self.title,
                                    "description": self.description,
                                    "thumbnail_title": self.thumbnail_title
                                }, indent=4)
                            )
                        return self.title, self.description, self.thumbnail_title
                print(f"Invalid ChatGPT response in try {retry_counter}, going on retry")
                retry_counter = retry_counter + 1
            else:
                raise Exception("ChatGPT response did not include json in right format")
        else:
            raise NotImplementedError("Please provide logic")


if __name__ == '__main__':
    text_tasks = TextTasks()
    with open("D:\\Projects\\media-empire\\tmp\\test_text.xml", 'r') as f:
        text = f.read()

    print(text)
    print(text_tasks.create_title_description_thumbnail_title(text))
    print(text_tasks.cleaned_text)

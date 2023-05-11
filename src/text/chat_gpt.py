import logging
import os

import openai

from config import CONFIG
from util.time import get_now

openai.api_key = CONFIG.get("OPEN_AI_API_KEY")

logger = logging.getLogger(__name__)

class ChatGPTTask:
    def __init__(self, prompt, model_name="text-davinci-003", tokens_number=3700):
        self.prompt = prompt
        self.model_name = model_name
        self.text = None
        self.filename = None
        self.task_time = None
        self.tokens_number = tokens_number

    def run(self):
        self.text, self.filename, self.task_time = process_chatgpt_results(self.prompt, model_name=self.model_name, tokens_number=self.tokens_number)
        logger.info(f"Chat GPT response text: {self.text}")
        return self


def ask_chatgpt(prompt, model_name="text-davinci-003", tokens_number=3700):
    model_engine = model_name
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=tokens_number,
        n=1,
        stop=None,
        temperature=0.7,
    )
    message = response.choices[0].text.strip()
    return message


def chat_completion(prompt, model_name="gpt-3.5-turbo", tokens_number=3700):
    messages = [
        {"role": "system", "content": "You are an REST API that responds with JSON to user"},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=messages,
        max_tokens=tokens_number,
        n=1,
        stop=None,
        temperature=0.7,
    )
    message = response.choices[0]['message']['content'].strip()
    return message


def save_results(prompt, text):
    prompt_dir = os.path.join(CONFIG.get("MEDIA_GALLERY_DIR"), 'TEXT')
    prompt_index_file = os.path.join(prompt_dir, '.chatGPT_prompt_index.txt')
    now = get_now()
    filename = os.path.join(prompt_dir, f"{now}_prompt.txt".lower())

    with open(prompt_index_file, 'a' if os.path.exists(prompt_index_file) else 'w') as f:
        cleaned_prompt = prompt.replace('\n', ' ')
        f.write(f"{filename}={cleaned_prompt}\n")

    print(f"Saving prompt result to {filename}")

    with open(filename, "w") as f:
        f.write(text)
    return filename, now


def process_chatgpt_results(prompt, model_name=None, tokens_number=3700):
    res = generate_text(prompt, model_name, tokens_number=tokens_number)
    filename, now = save_results(prompt, res)
    return res, filename, now


def print_models():
    print(openai.Model.list())


def generate_text(prompt, model_name, tokens_number):
    if model_name and model_name.startswith('gpt-3.5-turbo') or model_name.startswith('gpt-4'):
        result_text = chat_completion(prompt, model_name=model_name, tokens_number=tokens_number)
    else:
        result_text = ask_chatgpt(prompt, model_name=model_name, tokens_number=tokens_number)
    return result_text


if __name__ == '__main__':
    print_models()
    # prompt = "Provide me with 1000 words motivational story about Achieving Goals in the style of Tony Robbins. " \
    #          "Represent your answer as ssml for google text to speech api." \
    #          "Use 5 seconds breaks between different parts, emphasize important parts by increasing or decreasing pitch." \
    #          "Prosody rate should be slow." \
    #          "Your answer should contain only xml"
    # print(process_chatgpt_results(prompt))

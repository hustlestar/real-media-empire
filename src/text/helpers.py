import json
import logging
import os
import random
import re
from collections import namedtuple
from typing import List, Tuple, Dict

from text.chat_gpt import ChatGPTTask, chat_completion

logger = logging.getLogger(__name__)


def extract_json_as_dict(text_with_json):
    first_value = text_with_json.index("{")
    last_value = len(text_with_json) - text_with_json[::-1].index("}")
    json_string = text_with_json[first_value:last_value]
    result_dict = json.loads(json_string)
    return result_dict


def build_prompt(prompt_template: str,
                 topics_json_filepath: str,
                 narrative_types: List[str] = None,
                 engagement_techniques: List[str] = None,
                 is_authored=None,
                 author=None,
                 number_of_ideas=3,
                 number_of_words=2500
                 ):
    with open(topics_json_filepath) as f:
        topics_list = json.load(f)
    if author and any(author == f['author'] for f in topics_list):
        author_collection = filter(lambda x: x['author'] == author, topics_list)[0]
    else:
        author_collection = topics_list[random.randint(0, len(topics_list) - 1)]
        author = author_collection['author']

    is_book = False
    if is_authored is not None:
        if is_authored:
            is_book = True
            theme = pick_book_theme(author_collection)
        else:
            theme = pick_topic_theme(author_collection)
    else:
        is_books = random.randint(0, 1)
        if is_books:
            is_authored = True
            is_book = True
            theme = pick_book_theme(author_collection)
        else:
            theme = pick_topic_theme(author_collection)

    mention_author = "Don't mention author {author}.".replace("{author}", author) if not is_authored else ""
    theme = theme if not is_book else f"{number_of_ideas} main ideas from the book '{theme}'"
    narrative_type = "speech" if not narrative_types else pick_random_from_list(narrative_types)
    number_of_techniques_to_use = random.randint(0, len(engagement_techniques) - 1) if engagement_techniques else 0

    if number_of_techniques_to_use and engagement_techniques:
        to_use = set()
        while len(to_use) < number_of_techniques_to_use:
            to_use.add(pick_random_from_list(engagement_techniques))
        techniques = "\n".join(to_use)
    else:
        techniques = ""

    prompt = (prompt_template
              .replace("{number_of_words}", str(number_of_words))
              .replace("{theme}", theme)
              .replace("{author}", author)
              .replace("{mention_author}", mention_author)
              .replace("{narrative_type}", narrative_type)
              .replace("{engagement_techniques}", techniques)
              )
    logger.info("-" * 100)
    logger.info(f"Built following prompt:\n{prompt}")
    logger.info("-" * 100)
    return prompt


def pick_topic_theme(author_collection):
    topics = author_collection['topics']
    return pick_random_from_list(topics)


def pick_random_from_list(any_list):
    return any_list[random.randint(0, len(any_list) - 1)]


def pick_book_theme(author_collection):
    books = author_collection['books']
    return pick_random_from_list(books)


def create_thoughts_list(topic="from Michael Hyatt's Your Best Year Ever book", what=None):
    thoughts = "thoughts" if not what else what
    prompt = f'Main {thoughts} {topic} as json with key "{thoughts}" with array of strings'
    result_text = ChatGPTTask(prompt=prompt, tokens_number=3700).run().text

    retry_counter = 0
    while retry_counter < 5:
        if has_json(result_text):
            result_dict = extract_json_as_dict(result_text)
            if thoughts in result_dict:
                return result_dict[thoughts]
        print(f"Invalid ChatGPT response in try {retry_counter}, going on retry")
        retry_counter = retry_counter + 1
    raise Exception("Failed to create required json using ChatGPT")


def chatgpt_answer_as_a_dict(template, arguments: dict):
    pass


def create_quote_and_author(author_file, topic_list, model_name='gpt-3.5-turbo', results_dir=None) -> Dict[str, str]:
    author = pick_random_from_list(json.loads(open(author_file).read())['authors'])
    topic = pick_random_from_list(topic_list)
    params = {
        "topic": topic,
        "author": author,
        "main_idea": ""
    }
    args = [
        TemplateArg(
            text_definition="[[topic]] by [[author]]",
            json_field_name='quote',
            value='\"\"'
        ),
        TemplateArg(
            text_definition="author of quote",
            json_field_name='author',
            value='\"\"'
        ),
    ]
    prompt = create_prompt_from_template(args, params, quote_template)
    retry_counter = 0
    while retry_counter < 5:
        result_text = chat_completion(prompt, model_name=model_name, tokens_number=500)
        print(f"CHAT GPT response \n{result_text}")
        if has_json(result_text):
            result_dict = extract_json_as_dict(result_text)
            for arg in args:
                if arg.json_field_name not in result_dict.keys():
                    # quote, author = (
                    #     result_dict["quote"],
                    #     result_dict["author"],
                    # )
                    # with open(os.path.join(results_dir, '1_quotes.json'), 'w') as f:
                    #     f.write(json.dumps(
                    #         {
                    #             "title": quote,
                    #             "description": author,
                    #         }, indent=4)
                    #     )
                    raise Exception(f"ChatGPT response did not include {arg.json_field_name} field in json")
                return result_dict
        print(f"Invalid ChatGPT response in try {retry_counter}, going on retry")
        retry_counter = retry_counter + 1
    else:
        raise Exception("ChatGPT response did not include json in right format")


def has_json(result_text):
    return '{' in result_text and '}' in result_text


quote_template = f"""[[main_idea]]
Provide json having ${{n}} fields:
${{arg1}} 
in the following format:
{{
    "${{arg2}}": ${{arg3}}
}}
Your response should contain only json.
"""
TemplateArg = namedtuple('QuoteArg', ['text_definition', 'json_field_name', 'value'])


def create_prompt_from_template(args: List[TemplateArg], params: Dict[str, str], template_string: str = quote_template):
    res = template_string
    number_of_fields = str(len(args))
    for i, a in enumerate(args):
        arg1 = f"\t{i + 1}. {a.text_definition}" + ("" if i == len(args) - 1 else """,\n${arg1}""")
        arg2 = a.json_field_name
        arg3 = f'{a.value}' + ("" if i == len(args) - 1 else f""",\n\t"${{arg2}}": ${{arg3}}""")
        res = (res.replace("""${arg1}""", arg1)
               .replace("""${arg2}""", arg2)
               .replace("""${arg3}""", arg3)
               .replace("""${n}""", number_of_fields)
               )
    for k, v in params.items():
        res = res.replace(f"[[{k}]]", v)
    print(res)
    return res


def find_split_index(line):
    split_at = -1
    but_index = line.find('but') if 'but' in line.lower() else -1
    print(f"but index {but_index}")
    and_index = line.find('and') if 'and' in line.lower() else -1
    print(f"and index {and_index}")
    comma_index = line.find(',') if ',' in line else -1
    print(f"comma index {comma_index}")
    space_index = line.find(" ", 25)
    print(f"space index {space_index}")
    return


def method_name():
    for l in quote_lines:
        if len(l) < 25:
            result.append(l)
            continue
        print(f"line length {len(l)}")
        split_idnex = find_split_index(l)


if __name__ == '__main__':
    # topic = 'motivational quote'
    # author = 'author'
    # params = {
    #     "topic": "motivational quote",
    #     "author": "Les Brown",
    #     "main_idea": ""
    # }
    # args = [
    #     TemplateArg(
    #         text_definition="[[topic]] by [[author]] where each logical quote part is a different string in array about 30 characters long",
    #         json_field_name='quote',
    #         value='["","","","",""]'
    #     ),
    #     TemplateArg(
    #         text_definition="author of quote",
    #         json_field_name='author',
    #         value='\"\"'
    #     ),
    # ]
    #
    # res = create_prompt_from_template(args, params, quote_template)
    # print(res)

    # res_dict = create_quote_and_author(topic_list=['motivational quote'],
    #                                    author_file='/Users/yauhenim/JACK/media-empire/jack/topic_list.json',
    #                                    model_name='gpt-3.5-turbo', )
    # print(res_dict)
    quote_dict = {
        "quote": "Beliefs have the power to create and the power to destroy. Human beings have the awesome ability to take any experience of their lives and create a meaning that disempowers them or one that can literally save their lives.",
        "author": "Tony Robbins"
    }

    quote = quote_dict.get("quote")
    print(quote)
    quote_lines = [s for s in quote.split(".") if s]
    result = []
    method_name()

    print(f"final result {result}")

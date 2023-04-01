import json
import logging
import random
from typing import List

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


if __name__ == '__main__':
    build_prompt()
import json
import logging
import os
import random
from collections import namedtuple
from typing import List, Dict, Any

from text.chat_gpt import ChatGPTTask, generate_text

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = f"""[[main_idea]]
Provide json having ${{n}} fields:
${{arg1}} 
in the following format:
{{
    "${{arg2}}": ${{arg3}}
}}
Your response should contain only json. Json must be valid.
"""


def extract_json_as_dict(text_with_json):
    first_value = text_with_json.index("{")
    last_value = len(text_with_json) - text_with_json[::-1].index("}")
    json_string = text_with_json[first_value:last_value]
    result_dict = json.loads(json_string)
    return result_dict


def build_prompt(
    prompt_template: str,
    topics_json_filepath: str,
    narrative_types: List[str] = None,
    engagement_techniques: List[str] = None,
    is_authored=None,
    author=None,
    number_of_ideas=3,
    number_of_words=2500,
):
    with open(topics_json_filepath) as f:
        topics_list = json.load(f)
    if author and any(author == f["author"] for f in topics_list):
        author_collection = filter(lambda x: x["author"] == author, topics_list)[0]
    else:
        author_collection = topics_list[random.randint(0, len(topics_list) - 1)]
        author = author_collection["author"]

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

    prompt = (
        prompt_template.replace("{number_of_words}", str(number_of_words))
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
    topics = author_collection["topics"]
    return pick_random_from_list(topics)


def pick_random_from_list(any_list):
    return any_list[random.randint(0, len(any_list) - 1)]


def pick_book_theme(author_collection):
    books = author_collection["books"]
    return f"{pick_random_from_list(books)}"


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


def create_result_dict_from_prompt_template(
    prompt_template: str, args, params, model_name="gpt-3.5-turbo", results_dir=None, tokens_number=700
) -> Dict[str, Any]:
    prompt = create_prompt_from_template(args, params, prompt_template)
    retry_counter = 0
    while retry_counter < 5:
        result_text = generate_text(prompt, model_name, tokens_number)
        print(f"CHAT GPT {model_name} response \n{result_text}")
        if has_json(result_text):
            result_dict = extract_json_as_dict(result_text)
            for arg in args:
                if arg.json_field_name not in result_dict.keys():
                    raise Exception(f"ChatGPT response did not include {arg.json_field_name} field in json")
                return result_dict
        print(f"Invalid ChatGPT response in try {retry_counter}, going on retry")
        retry_counter = retry_counter + 1
    else:
        raise Exception("ChatGPT response did not include json in right format")


def has_json(result_text):
    return "{" in result_text and "}" in result_text


TemplateArg = namedtuple("TemplateArg", ["text_definition", "json_field_name", "value"])


def create_prompt_from_template(args: List[TemplateArg], params: Dict[str, str], template_string: str = DEFAULT_TEMPLATE):
    res = template_string
    number_of_fields = str(len(args))
    for i, a in enumerate(args):
        arg1 = f"\t{i + 1}. {a.text_definition}" + ("" if i == len(args) - 1 else """,\n${arg1}""")
        arg2 = a.json_field_name
        arg3 = f"{a.value}" + ("" if i == len(args) - 1 else f""",\n\t"${{arg2}}": ${{arg3}}""")
        res = res.replace("""${arg1}""", arg1).replace("""${arg2}""", arg2).replace("""${arg3}""", arg3).replace("""${n}""", number_of_fields)
    for k, v in params.items():
        res = res.replace(f"[[{k}]]", v)
    print(res)
    return res


def find_split_index(line, max_line_length):
    index = line.find("but") if "but" in line.lower() else -1
    if 11 < index < 25:
        print(f"but index {index}")
        return index
    index = line.find("and") if "and" in line.lower() else -1
    if 11 < index < 25:
        print(f"and index {index}")
        return index
    index = line.find(",") if "," in line else -1
    if 11 < index < 25:
        print(f"comma index {index}")
        return index
    index = line.find(";") if ";" in line else -1
    if 11 < index < 25:
        print(f"semicolom index {index}")
        return index
    index = line.find(" is ") if " is " in line else -1
    if 11 < index < 25:
        print(f"is index {index}")
        return index
    index = line.find(" are ") if " are " in line else -1
    if 11 < index < 25:
        print(f"are index {index}")
        return index
    space_index = line.find(" ", max_line_length)
    print(f"space index {space_index}")
    return space_index if space_index > 0 and space_index + 9 < len(line) else len(line)


def prepare_short_lines(quote_lines, max_line_length=22):
    result = []
    for line in quote_lines:
        if len(line) < max_line_length:
            result.append(line)
            continue
        print(f"line length {len(line)}")
        split_index = find_split_index(line, max_line_length)
        print(f"split index is {split_index} for {line}")
        if split_index < 0:
            result.append(line)
        else:
            result.append(line[:split_index].strip())
            remaining = line[split_index:]
            while len(remaining) > max_line_length:
                split_index = find_split_index(remaining, max_line_length)
                print(f"split index is {split_index} for {remaining}")
                line_part = remaining[:split_index].strip()
                remaining = remaining[split_index:]
                if not remaining:
                    result.append(f"{line_part}")
                else:
                    result.append(line_part)
            else:
                result.append(remaining.strip())
    return [l for l in result if l]


def finish_line(s: str):
    s = s.strip()
    if s.endswith("..") and not s.endswith("..."):
        return f"{s}."
    if s.endswith(".") or s.endswith("!") or s.endswith(";") or s.endswith(":") or s.endswith(",") or s.endswith("?"):
        return s
    else:
        return f"{s}."


def prepare_all_quotes():
    categories = [
        # "philosophers",
        # "historical figures",
        # "poets", #skipped
        # "novelists and writers", #skipped
        # "journalists", #skipped
        "businessman",  # failed
        "psychologists",
        "business coaches",
        "leaders",
        # "scientists", #skipped
        "speakers",
        # "engineers" #skipped
    ]
    # with open("G:\OLD_DISK_D_LOL\Projects\media-empire\jack\speakers_list.json") as f:
    #     authors = json.loads(f.read())['authors']
    all_authors_and_quotes = {}
    for c in categories:
        category_args = [
            TemplateArg(text_definition=f"100 {c} names as strings in array field called authors", json_field_name="authors", value="[]"),
        ]
        category_params = {"main_idea": ""}
        authors_dict = create_result_dict_from_prompt_template(
            DEFAULT_TEMPLATE, category_args, category_params, model_name="text-davinci-003", tokens_number=3500
        )
        print(authors_dict)
        all_quotes_in_category = []
        for a in authors_dict.get("authors"):
            params = {"topic": "quotes", "author": a, "main_idea": ""}
            args = [
                TemplateArg(text_definition="100 [[topic]] by [[author]] in array field called quotes", json_field_name="quotes", value="[]"),
                TemplateArg(text_definition="author of quote", json_field_name="author", value='""'),
            ]
            try:
                if a in all_authors_and_quotes.keys():
                    print("-" * 100)
                    print(f"Cache hit for author {a}")
                    print("-" * 100)
                    all_quotes_in_category.append({"author": a, "quotes": all_authors_and_quotes[a]})
                else:
                    quotes_by_author = create_result_dict_from_prompt_template(
                        DEFAULT_TEMPLATE, args, params, model_name="text-davinci-003", tokens_number=3500
                    )
                    quotes_by_author["quotes"] = list(set(quotes_by_author["quotes"]))
                    all_authors_and_quotes[quotes_by_author["author"]] = quotes_by_author["quotes"]
                    all_quotes_in_category.append(quotes_by_author)
            except:
                print(f"Failed to get quotes by {a}")

        with open(f"G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes\\{c.lower().replace(' ', '_')}.json", "w") as r:
            r.write(json.dumps(all_quotes_in_category))


def prepare_all_authors():
    categories = [
        # "philosophers",
        # "historical figures",
        # "poets", #skipped
        # "novelists and writers", #skipped
        # "journalists", #skipped
        "businessman",  # failed
        "psychologists",
        "business coaches",
        "leaders",
        # "scientists", #skipped
        "speakers",
        # "engineers" #skipped
    ]
    # with open("G:\OLD_DISK_D_LOL\Projects\media-empire\jack\speakers_list.json") as f:
    #     authors = json.loads(f.read())['authors']
    all_authors_and_quotes = {}
    for c in categories:
        category_args = [
            TemplateArg(text_definition=f"100 {c} names as strings in array field called authors", json_field_name="authors", value="[]"),
        ]
        category_params = {"main_idea": ""}
        authors_dict = create_result_dict_from_prompt_template(
            DEFAULT_TEMPLATE, category_args, category_params, model_name="text-davinci-003", tokens_number=3500
        )
        print(authors_dict)
        all_quotes_in_category = []
        for a in authors_dict.get("authors"):
            params = {"topic": "quotes", "author": a, "main_idea": ""}
            args = [
                TemplateArg(text_definition="100 [[topic]] by [[author]] in array field called quotes", json_field_name="quotes", value="[]"),
                TemplateArg(text_definition="author of quote", json_field_name="author", value='""'),
            ]
            try:
                if a in all_authors_and_quotes.keys():
                    print("-" * 100)
                    print(f"Cache hit for author {a}")
                    print("-" * 100)
                    all_quotes_in_category.append({"author": a, "quotes": all_authors_and_quotes[a]})
                else:
                    quotes_by_author = create_result_dict_from_prompt_template(
                        DEFAULT_TEMPLATE, args, params, model_name="text-davinci-003", tokens_number=3500
                    )
                    quotes_by_author["quotes"] = list(set(quotes_by_author["quotes"]))
                    all_authors_and_quotes[quotes_by_author["author"]] = quotes_by_author["quotes"]
                    all_quotes_in_category.append(quotes_by_author)
            except:
                print(f"Failed to get quotes by {a}")

        with open(f"G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes\\{c.lower().replace(' ', '_')}.json", "w") as r:
            r.write(json.dumps(all_quotes_in_category))


def cleaned_quotes():
    jack_quotes = "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes"
    quote_template = f"""
Provide json having ${{n}} fields:
${{arg1}} 
in the following format:
{{
    "${{arg2}}": ${{arg3}}
}}
Your response should contain only json. Json must be valid. Don't include row number in any of the array strings.
"""
    params = {}
    args = [
        TemplateArg(text_definition="author of quote with value [[author]]", json_field_name="author", value='"[[author]]"'),
        TemplateArg(
            text_definition="2-5 words description about author, if dead with years of living",
            json_field_name="author_description",
            value='"years from - years to if dead, description"',
        ),
        TemplateArg(text_definition="array with 1-3 funny facts about author", json_field_name="author_funny_facts", value="[]"),
        TemplateArg(text_definition="array with 1-3 interesting facts about author", json_field_name="author_interesting_facts", value="[]"),
        TemplateArg(text_definition="array with 1-3 inspiring facts about author", json_field_name="author_inspiring_facts", value="[]"),
    ]
    for q in os.listdir(jack_quotes):
        with open(os.path.join(jack_quotes, q)) as f:
            quotes = json.loads(f.read())
        new_quotes = []
        for k in quotes:
            params["author"] = k.get("author")
            quotes_by_author = None
            while quotes_by_author is None:
                try:
                    quotes_by_author = create_result_dict_from_prompt_template(
                        quote_template, args, params, model_name="gpt-3.5-turbo", tokens_number=1500
                    )
                except Exception as x:
                    print(x)
            new_quotes.append({"quotes": list(set(k.get("quotes"))), **quotes_by_author, "author": k.get("author")})
        with open(os.path.join(jack_quotes, f"clean_{q}"), "w") as o:
            o.write(json.dumps(new_quotes))


def more_than_n_quotes(number_of_quotes=30):
    jack_quotes = "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes"
    for q in os.listdir(jack_quotes):
        if os.path.isdir(os.path.join(jack_quotes, q)):
            continue
        with open(os.path.join(jack_quotes, q)) as f:
            quotes = json.loads(f.read())
        new_quotes = []
        for k in quotes:
            if len(k.get("quotes")) > number_of_quotes:
                new_quotes.append({**k})
        print(f"Writing {len(new_quotes)} quotes to file more_than_{number_of_quotes}_quotes_{q}, initially there were {len(quotes)}")
        with open(os.path.join(jack_quotes, f"more_than_20_quotes_{q}"), "w") as o:
            o.write(json.dumps(new_quotes))


if __name__ == "__main__":
    # prepare_all_quotes()

    # quote_lines = [f"{s}." for s in quote.split(".") if s]
    #
    # result = prepare_short_lines(quote_lines)
    #
    # print(f"final result {result}")

    more_than_n_quotes()

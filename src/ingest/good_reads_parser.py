import os.path

import json

import requests
import time
from bs4 import BeautifulSoup
from typing import Dict, Set
from langdetect import detect

ALL_QUOTES_BY_AUTHOR: Dict[str, Set[str]] = {}
ALL_QUOTES_BY_TAG: Dict[str, Set[str]] = {}


def remove_after_comma(s):
    return s.split(',', 1)[0]


def is_english(s):
    try:
        lang = detect(s)
    except:
        return False

    if lang == 'en':
        return True
    else:
        return False


def read_100_pages(by_tag):
    print(f"starting reading 100 pages of quotes from goodreads by  tag {by_tag}...")
    for i in range(100):
        try:
            url = f"https://www.goodreads.com/quotes/{by_tag if by_tag else ''}{'?page=' + str(i + 1) if i > 0 else ''}"
            print("-" * 100)
            print(f"reading page {i + 1} of quotes from goodreads by tag {by_tag} {url}...")
            response = requests.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            quote_divs = soup.find_all('div', {'class': 'quoteText'})

            for quote_div in quote_divs:
                # Extract the text of the quote
                quote = quote_div.contents[0].strip().strip('“').strip('”')

                # Extract the author
                author = remove_after_comma(quote_div.find('span', {'class': 'authorOrTitle'}).text.strip().strip(','))
                if is_english(quote):
                    print(f'Quote: {quote}\nAuthor: {author}')
                    if author in ALL_QUOTES_BY_TAG:
                        ALL_QUOTES_BY_TAG[author].add(quote)
                    if author in ALL_QUOTES_BY_AUTHOR:
                        ALL_QUOTES_BY_AUTHOR[author].add(quote)
                    else:
                        ALL_QUOTES_BY_AUTHOR[author] = {quote}
                        ALL_QUOTES_BY_TAG[author] = {quote}
        except Exception as x:
            print(f"error reading page {i + 1} of quotes from goodreads by tag {by_tag}...")
        time.sleep(2)


if __name__ == '__main__':
    # Test it
    print(is_english("Hello, World!"))  # Should print True
    print(is_english("Bonjour, Monde!"))  # Should print False
    semi_tags = {
            "love",
            "life",
            "inspirational",
            "humor",
            "philosophy",
            "god",
            "inspirational-quotes",
            "truth",
            "wisdom",
            "romance",
            "poetry",
            "death",
            "happiness",
            "hope",
            "faith",
            "life-lessons",
            "inspiration",
            "quotes",
            "writing",
            "motivational",
            "religion",
            "spirituality",
            "relationships",
            "success",
            "life-quotes",
            "love-quotes",
            "time",
            "science",
            "knowledge",
            "motivation"
    }
    for i, semi_tag in enumerate(semi_tags):
        read_100_pages(f"/tag/{semi_tag}")
        print(f"done reading 100 pages of quotes from goodreads by tag {semi_tag}...")
        with open(os.path.join("G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes\\NEWEST", f"{i + 1:02d}_quotes_by_tag_{semi_tag}.json"), 'w') as f:
            print(ALL_QUOTES_BY_TAG)
            # Convert the sets to lists
            dict_of_lists = {key: list(value) for key, value in ALL_QUOTES_BY_TAG.items()}
            json.dump(dict_of_lists, f, sort_keys=True, indent=2)
        ALL_QUOTES_BY_TAG = {}

    print("done reading ALL pages of quotes from goodreads...")
    with open(os.path.join("G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes\\NEWEST", f"00_quotes_by_author.json"), 'w') as f:
        dict_of_lists = {key: list(value) for key, value in ALL_QUOTES_BY_AUTHOR.items()}
        json.dump(dict_of_lists, f, sort_keys=True, indent=2)


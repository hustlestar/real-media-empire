import json
import pandas

quotes = json.loads(open("G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\quotes\\NEWEST\\00_quotes_by_author.json").read())

counter = 0
for author, quotes_by_author in quotes.items():
    if len(quotes_by_author) > 20:
        counter += 1
        print(author)

print(counter)

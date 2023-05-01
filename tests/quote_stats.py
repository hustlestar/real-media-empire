import json
import os
import pandas as pd
if __name__ == '__main__':
    quotes_dir = "G:\\OLD DISK D - LOL\\Projects\\media-empire\\jack\\quotes"
    files = os.listdir(quotes_dir)
    quotes_total = 0
    quotes_max_length = 0
    quotes_sum_length = 0
    quote_lengths = []
    for file in files:
        quotes_file = os.path.join(quotes_dir, file)
        print(f"Reading {quotes_file}...")
        with open(quotes_file) as f:
            quote_list = json.loads(f.read())
            for quote_obj in quote_list:
                for quote in quote_obj["quotes"]:
                    quotes_total += 1
                    quote_len = len(quote)
                    quote_lengths.append(quote_len)
                    quotes_sum_length += quote_len
                    if quote_len > quotes_max_length:
                        quotes_max_length = quote_len

    df = pd.DataFrame(quote_lengths)
    print(df.describe())
    print(df.quantile(0.9))
    print(df.quantile(0.95))
    quotes_avg_length = quotes_sum_length / quotes_total
    print(f"Total Quotes: {quotes_total},  Average Quote Length: {quotes_avg_length}, Max Quote Length: {quotes_max_length}")

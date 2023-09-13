from collections import Counter

import heapq
import spacy
from transformers import pipeline

from text.extract_keywords import preprocess_transcript

import time

_nlp = None


def text_summary(text, max_length=130, min_length=30):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    values = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    print(values)


def provide_text_summary(text):
    from transformers import BartTokenizer, BartForConditionalGeneration
    import torch

    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

    # tokenize without truncation
    inputs_no_trunc = tokenizer(text, max_length=None, return_tensors='pt', truncation=False)

    # get batches of tokens corresponding to the exact model_max_length
    chunk_start = 0
    chunk_end = tokenizer.model_max_length  # == 1024 for Bart
    inputs_batch_lst = []
    while chunk_start <= len(inputs_no_trunc['input_ids'][0]):
        inputs_batch = inputs_no_trunc['input_ids'][0][chunk_start:chunk_end]  # get batch of n tokens
        inputs_batch = torch.unsqueeze(inputs_batch, 0)
        inputs_batch_lst.append(inputs_batch)
        chunk_start += tokenizer.model_max_length  # == 1024 for Bart
        chunk_end += tokenizer.model_max_length  # == 1024 for Bart

    # generate a summary on each batch
    summary_ids_lst = [model.generate(inputs, num_beams=3, max_length=80, early_stopping=True) for inputs in inputs_batch_lst]

    # decode the output and join into one string with one paragraph per summary batch
    summary_batch_lst = []
    for summary_id in summary_ids_lst:
        summary_batch = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_id]
        summary_batch_lst.append(summary_batch[0])
    summary_all = '\n'.join(summary_batch_lst)

    print(summary_all)
    return summary_all


def load_nlp():
    global _nlp
    if not _nlp:
        _nlp = spacy.load("en_core_web_lg")
    return _nlp


def preprocess_text(text):
    nlp = load_nlp()
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)


def summarize_text(text, num_sentences=3):
    # Preprocess the text
    preprocessed_text = preprocess_text(text)

    # Tokenize the preprocessed text into sentences
    nlp = load_nlp()
    sentences = [sent.text for sent in nlp(preprocessed_text).sents]

    # Calculate word frequency using TF-IDF
    word_freq = Counter(preprocessed_text.split())

    # Calculate sentence scores based on word frequency
    sentence_scores = {}
    for sentence in sentences:
        for word in sentence.split():
            if word in word_freq:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_freq[word]
                else:
                    sentence_scores[sentence] += word_freq[word]

    # Select top sentences based on scores
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)

    # Generate the summary
    summary = "|".join(summary_sentences)
    return summary


if __name__ == '__main__':
    text = open("G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\steps\\downloads\\z-mJEZbHFLs_transcript.txt", "r").read()
    text = preprocess_transcript(text)
    start_time = time.time()
    x = provide_text_summary(text)
    print("--- %s seconds ---" % (time.time() - start_time))
    x2 = provide_text_summary(x)
    print("--- %s seconds ---" % (time.time() - start_time))

    # summary = text_summary(text)
    # print(summary)
    # Example text
    # Summarize the text
    summary = summarize_text(text)
    print(summary)
    x3 = provide_text_summary(summary)
    print("--- %s seconds ---" % (time.time() - start_time))
    print(x3)

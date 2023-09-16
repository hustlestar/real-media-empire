import logging

import re

from transformers import BertTokenizer, BertForMaskedLM
import torch
import spacy

nlp = spacy.load("en_core_web_lg")
logger = logging.getLogger(__name__)


def extract_keywords_from_transcript(transcript_text, num_keywords=10):
    # Load a pre-trained BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertForMaskedLM.from_pretrained("bert-base-uncased")

    # Tokenize the transcript text
    tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(transcript_text)))

    # Convert tokens to tensor
    input_ids = torch.tensor(tokenizer.convert_tokens_to_ids(tokens)).unsqueeze(0)

    # Predict token probabilities
    with torch.no_grad():
        outputs = model(input_ids)
        predictions = outputs[0]

    # Get token probabilities
    token_probs = torch.softmax(predictions[0], dim=1)

    # Find the top N tokens as keywords
    top_keyword_indices = token_probs[0].argsort(descending=True)[:num_keywords]

    # Get the keywords
    keywords = [tokens[idx] for idx in top_keyword_indices]

    return keywords


def extract_key_phrases_from_transcript(transcript_text):
    # Load the spaCy model
    # Process the transcript text
    doc = nlp(transcript_text)

    # Extract noun phrases
    key_phrases = [chunk.text for chunk in doc.noun_chunks]

    return key_phrases


def extract_key_sentences(transcript, num_sentences=5):
    # Preprocess the transcript (tokenization and cleanup)
    transcript = preprocess_transcript(transcript)

    # Parse the transcript with spaCy
    doc = nlp(transcript)

    # Calculate scores for each sentence (e.g., using word vectors)
    sentence_scores = calculate_sentence_scores(doc)

    # Select the top N sentences as key sentences
    key_sentences = select_top_sentences(doc, sentence_scores, num_sentences)

    return key_sentences


def preprocess_transcript(transcript):
    # Remove timestamps and [Music]
    cleaned_transcript = re.sub(r'\[\d+\.\d+\s*-\s*\d+\.\d+\]\s*|\[Music\]\s*', '', transcript)
    return cleaned_transcript


def calculate_sentence_scores(doc):
    # Implement your sentence scoring logic here
    # For example, calculate word vector similarity
    sentence_scores = [s.similarity(doc) for s in doc.sents]
    return sentence_scores


def select_top_sentences(doc, scores, num_sentences):
    # Select the top N sentences based on scores
    sorted_sentences = [sent.text for _, sent in sorted(zip(scores, doc.sents), reverse=True)]
    result_sentences = sorted_sentences[:num_sentences] if len(sorted_sentences) > num_sentences else sorted_sentences
    return [s.text for s in doc.sents if s.text in result_sentences]


def extract_keywords_with_timestamps(initial_transcript_lines, key_idea, last_line_index=0):
    # Split the cleaned transcript into key_sentences
    key_sentences = [s for s in key_idea.lower().split('\n') if s]

    # Initialize a list to store keyword matches
    keyword_matches = []
    for i, initial_line in enumerate(initial_transcript_lines[last_line_index:]):
        # Extract the timestamp range from the keyword initial_line
        if not key_sentences:
            last_line_index = last_line_index + i - 1
            break
        timestamp_match = re.search(r'\[(\d+\.\d+)\s*-\s*(\d+\.\d+)\]', initial_line)
        if timestamp_match:
            start_time = float(timestamp_match.group(1))
            end_time = float(timestamp_match.group(2))

            # Search for the corresponding text in the initial transcript
            if key_sentences[0] in initial_line:
                keyword_text = key_sentences[0]
                key_sentences.remove(keyword_text)
                # Append the keyword and its corresponding text to the list
                keyword_matches.append({
                    'timestamp_range': (start_time, end_time),
                    'keyword_text': keyword_text.strip()
                })
    if key_sentences:
        print(f"Didn't find match for key_sentences:\n{key_sentences}")
    return keyword_matches, last_line_index


if __name__ == '__main__':
    # Example usage:
    initial_transcript = open("G:\\OLD_DISK_D_LOL\\Projects\media-empire\\src\\video\\download\\downloads\\oBXFBTHSqas_transcript.txt", "r").read()
    # keywords = extract_keywords_from_transcript(transcript)
    # print("Top Keywords:", keywords)
    # Example usage:
    # key_phrases = extract_key_phrases_from_transcript(transcript)
    # print("Key Phrases:", key_phrases)
    key_sentences = extract_key_sentences(initial_transcript, num_sentences=3)
    for i, sentence in enumerate(key_sentences, start=1):
        print(f"Key Sentence {i}:\n{sentence}")
    keyword_matches, _ = extract_keywords_with_timestamps(initial_transcript, key_sentences[0])

    # Print the keyword matches
    for match in keyword_matches:
        print(f"Timestamp Range: {match['timestamp_range']}")
        print(f"Keyword Text: {match['keyword_text']}\n")

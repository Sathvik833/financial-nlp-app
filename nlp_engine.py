import os

import requests
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline

load_dotenv()


_finbert = None


def nlp_engine(get_sentences):
    global _finbert

    if _finbert is None:
        _finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")

    predictions = []
    for sentence in get_sentences:
        predictions.append(_finbert(sentence)[0]["label"].lower())

    return predictions


def _ensure_nltk_tokenizer_resources():
    nltk_data_dir = os.getenv("NLTK_DATA")
    if nltk_data_dir and nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)

    try:
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError as exc:
        raise RuntimeError(
            "NLTK tokenizer data is missing. Ensure 'punkt' and 'punkt_tab' are downloaded and NLTK_DATA is configured."
        ) from exc


def split_sentences(text):
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")

    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Text cannot be empty.")

    _ensure_nltk_tokenizer_resources()
    return sent_tokenize(cleaned_text)


def finalPrediction(all_predictions):
    dict_labels = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
    }

    for prediction in all_predictions:
        label = prediction.lower()
        if label not in dict_labels:
            raise ValueError(f"Unknown prediction label: {prediction}")
        dict_labels[label] += 1

    return dict_labels


def insertDB(sentences, labels):
    airtable_token = os.getenv("AIRTABLE_API_TOKEN")
    if not airtable_token:
        return False

    url = "https://api.airtable.com/v0/appW5EZ5UOmtghvxE/Sentence%20Predictions"
    headers = {
        "Authorization": f"Bearer {airtable_token}",
        "Content-Type": "application/json",
    }
    records = [
        {
            "fields": {
                "sentence": sentence,
                "model_prediction": label,
            }
        }
        for sentence, label in zip(sentences, labels)
    ]

    try:
        for record_batch in _chunk_records(records, 10):
            response = requests.post(
                url,
                headers=headers,
                json={"records": record_batch},
                timeout=15,
            )
            response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def _chunk_records(records, batch_size):
    for index in range(0, len(records), batch_size):
        yield records[index:index + batch_size]

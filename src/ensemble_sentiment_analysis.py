# ensemble_sentiment_analysis.py
#
# Classifies financial text as positive ("UP"), negative ("DOWN"), or neutral ("NEUTRAL").
#
# Implements a voting ensemble including a TF-IDF + Logistic Regression Classifer, VADER, and finBERT.
#
# In the case that all models yield a different result, VADER breaks the tie
# because it has demonstrated higher accuracy so far.

import torch
import numpy as np
import pickle
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL = os.path.join(BASE_DIR, "tfidf_lr_model.pkl")

labels = ["UP", "DOWN", "NEUTRAL"]

"""
VADER Sentiment
"""
def analyze_sentiment_vader(text):
    vader_analyzer = SentimentIntensityAnalyzer()
    scores = vader_analyzer.polarity_scores(text)
    polarity = scores["compound"]

    if polarity > 0.05:
        return "UP"
    elif polarity < -0.05:
        return "DOWN"
    else:
        return "NEUTRAL"

"""
FinBERT Sentiment
"""
def analyze_sentiment_finbert(text):
    finbert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    finbert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")

    if not text.strip():
        return 0.0, "NEUTRAL"

    inputs = finbert_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = finbert_model(**inputs)

    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1).numpy()[0]
    max_index = np.argmax(probabilities)
    sentiment = labels[max_index]

    return sentiment

"""
Base Model Sentiment
"""
def analyze_sentiment_base(text):
    with open(BASE_MODEL, "rb") as f:
        saved = pickle.load(f)
    vectorizer = saved["vectorizer"]
    model = saved["model"]

    X_tfidf = vectorizer.transform([text])
    pred = model.predict(X_tfidf)[0]

    return pred

"""
Voting Ensemble
"""
def analyze_sentiment(text):
    base_vote = analyze_sentiment_base(text)
    vader_vote = analyze_sentiment_vader(text)
    finbert_vote = analyze_sentiment_finbert(text)

    votes = [base_vote, vader_vote, finbert_vote]
    votes = [vader_vote, finbert_vote]
    vote_counts = {label: votes.count(label) for label in labels}

    # Find max votes
    max_votes = max(vote_counts.values())
    candidates = [label for label, count in vote_counts.items() if count == max_votes]

    # VADER breaks tie
    if len(candidates) > 1:
        final_label = vader_vote
    else:
        final_label = candidates[0]

    return final_label

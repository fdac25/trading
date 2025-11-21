# tfidf_lr_model.py
#
# Implements a primitve base model.
#
# Checks to see if closing price is greater than the previous closing price.
#
# Matches daily stock data from 2011-2025 with NVDA forbes articles.
#
# Does NOT classify anything as 'neutral'.

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_CSV = os.path.join(BASE_DIR, "../data/forbes_articles_738.csv")
STOCK_DATA_CSV = os.path.join(BASE_DIR, "../data/NVDA_yahoo_finance_data_2011_2025.csv")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "tfidf_lr_model.pkl")

"""
Prepare Data
"""
articles = pd.read_csv(ARTICLES_CSV)
stock_data = pd.read_csv(STOCK_DATA_CSV)

# Parse Dates
articles["Time_clean"] = articles["Time"].str.rsplit(" ", n=1).str[0]
articles["Time_clean"] = pd.to_datetime(
    articles["Time_clean"], format="%b %d, %Y, %I:%M%p"
)
articles["Date"] = pd.to_datetime(articles["Time_clean"].dt.date)
articles = articles.sort_values("Date")

stock_data["StockDate"] = pd.to_datetime(stock_data["Date"], format="%d-%b-%y")
stock_data = stock_data.sort_values("StockDate")

# Compute UP/DOWN labels
stock_data["PrevClose"] = stock_data["Close"].shift(1)
stock_data["Label"] = stock_data.apply(
    lambda row: "UP" if row["Close"] > row["PrevClose"] else "DOWN", axis=1
)
stock_data = stock_data.drop(columns="PrevClose")

"""
Merge articles with stock data
"""
merged = pd.merge_asof(
    articles,
    stock_data[["StockDate", "Label"]],
    left_on="Date",
    right_on="StockDate",
    direction="forward"
)
merged = merged.dropna(subset=["Label"])

# Combine title + body into one text column
merged["text"] = merged["Title"].fillna("") + " " + merged["Body"].fillna("")

X = merged["text"].astype(str)
y = merged["Label"].astype(str)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
X_tfidf = vectorizer.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=42, stratify=y
)

# Train Model
model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)

y_pred =  model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save model
with open(MODEL_SAVE_PATH, "wb") as f:
    pickle.dump({
        "vectorizer": vectorizer,
        "model": model
    }, f)

print("\nTF-IDF + Logistic Regression model saved to:", MODEL_SAVE_PATH)

#!/usr/bin/env python
# coding: utf-8
# ============================================================
# preprocessing.py — NLP Text Cleaning
# Uses NLTK SnowballStemmer + bundled English stopwords
# (Bundled to avoid network dependency for NLTK data download)
# ============================================================

import re
import string
import nltk

# Attempt NLTK download (works if network allows; silent otherwise)
nltk.download("stopwords", quiet=True)
nltk.download("punkt",     quiet=True)

from nltk.stem import SnowballStemmer

STEMMER = SnowballStemmer("english")

# Full NLTK English stopword list — bundled for offline reliability
_NLTK_STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll",
    "m","o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn",
    "weren","won","wouldn"
}

try:
    from nltk.corpus import stopwords as _nltk_sw
    STOPWORDS = set(_nltk_sw.words("english"))
except Exception:
    STOPWORDS = _NLTK_STOPWORDS


def clean_text(text: str) -> str:
    """
    Full preprocessing pipeline:
      1. Lowercase
      2. Remove URLs
      3. Remove HTML tags
      4. Remove punctuation
      5. Remove newlines
      6. Remove tokens containing digits
      7. Remove stopwords
      8. Stem remaining words
    Returns a single cleaned, stemmed string.
    """
    text = str(text).lower()
    text = re.sub(r"\[.*?\]",           "", text)   # bracketed text
    text = re.sub(r"https?://\S+|www\.\S+", "", text)  # URLs
    text = re.sub(r"<.*?>+",            "", text)   # HTML tags
    text = re.sub(r"[%s]" % re.escape(string.punctuation), "", text)  # punctuation
    text = re.sub(r"\n",                "", text)   # newlines
    text = re.sub(r"\w*\d\w*",          "", text)   # tokens with digits

    # Stopword removal
    words = [w for w in text.split() if w not in STOPWORDS and w.strip()]
    # Stemming
    words = [STEMMER.stem(w) for w in words]

    return " ".join(words)

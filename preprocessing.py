"""
preprocessing.py
-----------------
This module contains all the text preprocessing logic used by the FAQ chatbot.

The SAME preprocessing pipeline is applied to:
    1. The FAQ questions loaded from faq.csv (done once, when the app starts)
    2. Every new question typed by the user (done every time they ask something)

Using the exact same pipeline for both sides is critical - if we preprocessed
them differently, the TF-IDF vectors would not be comparable and cosine
similarity would give meaningless results.

Preprocessing steps performed here:
    1. Lowercasing        -> "What IS Python?" becomes "what is python?"
    2. Punctuation removal -> "what is python?" becomes "what is python"
    3. Tokenization        -> "what is python" becomes ["what", "is", "python"]
    4. Stopword removal    -> ["what", "is", "python"] becomes ["python"]
    5. Lemmatization       -> reduces words to their dictionary base form
                              e.g. "running" -> "run", "libraries" -> "library"
"""

import string
import nltk

# ---------------------------------------------------------------------------
# NLTK RESOURCE DOWNLOADS
# ---------------------------------------------------------------------------
# NLTK needs a few pre-built resources before it can tokenize, remove
# stopwords, or lemmatize text. These are downloaded once and then cached
# locally, so this block only actually downloads files the first time the
# program runs on a machine.
#
# We wrap each download in a try/except so that if a resource is already
# present, NLTK does not raise an error and the program keeps running.
# ---------------------------------------------------------------------------

REQUIRED_NLTK_RESOURCES = [
    ("tokenizers/punkt", "punkt"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
    ("corpora/omw-1.4", "omw-1.4"),
]


def download_nltk_resources():
    """
    Ensure that every NLTK resource required by this module is available
    locally. If a resource is missing, it is downloaded automatically.
    """
    for resource_path, resource_name in REQUIRED_NLTK_RESOURCES:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(resource_name, quiet=True)


# Run the resource check as soon as this module is imported, so that by the
# time preprocess_text() is called, everything it needs is ready to use.
download_nltk_resources()

# ---------------------------------------------------------------------------
# IMPORTS THAT DEPEND ON THE DOWNLOADED RESOURCES
# ---------------------------------------------------------------------------
# These imports are placed after the download step above because they rely
# on the corpora/tokenizers that were just verified/downloaded.
from nltk.corpus import stopwords          # noqa: E402  (list of common words)
from nltk.stem import WordNetLemmatizer    # noqa: E402  (reduces words to base form)
from nltk.tokenize import word_tokenize    # noqa: E402  (splits text into words)

# Load the English stopword list once as a set (sets give fast lookup speed).
ENGLISH_STOPWORDS = set(stopwords.words("english"))

# Create a single lemmatizer instance to be reused for every word.
lemmatizer = WordNetLemmatizer()

# A ready-made translation table that maps every punctuation character to
# None, which str.translate() uses to strip punctuation efficiently.
PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)


def preprocess_text(raw_text: str) -> str:
    """
    Run the full preprocessing pipeline on a single piece of text and
    return a cleaned string ready to be fed into the TF-IDF vectorizer.

    Parameters
    ----------
    raw_text : str
        The original, unprocessed text (an FAQ question or a user question).

    Returns
    -------
    str
        The cleaned text: lowercase, punctuation-free, stopword-free,
        and lemmatized, with tokens joined back together by single spaces.
    """

    # Guard clause: if the input is empty, not a string, or just whitespace,
    # return an empty string instead of crashing.
    if not isinstance(raw_text, str) or raw_text.strip() == "":
        return ""

    # STEP 1: Convert everything to lowercase so that "Python" and "python"
    # are treated as the exact same word.
    text = raw_text.lower()

    # STEP 2: Remove punctuation (commas, question marks, periods, etc.)
    # using the translation table created above.
    text = text.translate(PUNCTUATION_TABLE)

    # STEP 3: Tokenize the cleaned text into a list of individual words.
    tokens = word_tokenize(text)

    # STEP 4: Remove stopwords AND any leftover non-alphabetic tokens
    # (like stray numbers or single characters left over from punctuation).
    meaningful_tokens = [
        token for token in tokens
        if token not in ENGLISH_STOPWORDS and token.isalpha()
    ]

    # STEP 5: Lemmatize each remaining token to reduce it to its base
    # dictionary form (e.g. "libraries" -> "library", "running" -> "run").
    lemmatized_tokens = [
        lemmatizer.lemmatize(token) for token in meaningful_tokens
    ]

    # Finally, join the cleaned tokens back into a single space-separated
    # string, since scikit-learn's TfidfVectorizer expects plain strings.
    cleaned_text = " ".join(lemmatized_tokens)

    return cleaned_text


# ---------------------------------------------------------------------------
# QUICK MANUAL TEST
# ---------------------------------------------------------------------------
# Running this file directly (python preprocessing.py) lets you quickly see
# the preprocessing pipeline in action without starting the whole chatbot.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_questions = [
        "What is Artificial Intelligence?",
        "How do I install Python libraries using PIP?",
        "What's the difference between AI and Machine Learning?",
    ]

    for question in sample_questions:
        print(f"Original : {question}")
        print(f"Cleaned  : {preprocess_text(question)}")
        print("-" * 50)

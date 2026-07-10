"""
chatbot.py
-----------
This module contains the "brain" of the FAQ chatbot.

It is responsible for:
    1. Loading the FAQ dataset from faq.csv.
    2. Preprocessing every FAQ question using preprocessing.py.
    3. Converting the cleaned FAQ questions into TF-IDF vectors.
    4. Given a new user question, preprocessing it the same way,
       converting it into a TF-IDF vector, and comparing it against
       every FAQ question using cosine similarity.
    5. Returning the best-matching answer, or a fallback message if
       nothing is similar enough.

This file has NO Flask code in it at all - it is a plain Python class that
could just as easily be used from a command-line script, a Jupyter
notebook, or a different web framework. Keeping the "chatbot logic" and
the "web server" separate is good software design (separation of concerns).
"""

import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing import preprocess_text

# ---------------------------------------------------------------------------
# CONFIGURATION CONSTANTS
# ---------------------------------------------------------------------------
# Keeping "magic numbers" and file paths as named constants at the top of
# the file makes the code easier to read and easier to tweak later.
# ---------------------------------------------------------------------------

# If the cosine similarity between the user question and the BEST matching
# FAQ question is below this threshold, we consider it "not a good match"
# and tell the user we couldn't find a relevant answer.
SIMILARITY_THRESHOLD = 0.35

# Default path to the FAQ dataset, relative to this file's location.
DEFAULT_FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq.csv")

# The exact message returned when no FAQ is similar enough to the question.
FALLBACK_ANSWER = "Sorry, I couldn't find a relevant answer."


class FAQChatbot:
    """
    A simple retrieval-based FAQ chatbot.

    "Retrieval-based" means the chatbot does not generate new text - it
    always retrieves and returns one of the existing answers from the
    FAQ dataset, choosing whichever one best matches the user's question.
    """

    def __init__(self, faq_csv_path: str = DEFAULT_FAQ_PATH):
        """
        Load the FAQ dataset and prepare the TF-IDF vectorizer as soon as
        the chatbot object is created. Doing this heavy lifting once (at
        startup) instead of on every single request keeps the chatbot fast.

        Parameters
        ----------
        faq_csv_path : str
            Path to the CSV file containing 'question' and 'answer' columns.
        """
        self.faq_csv_path = faq_csv_path

        # Load the raw FAQ data (questions + answers) from disk into memory.
        self.faq_dataframe = self._load_faq_data(faq_csv_path)

        # Preprocess every FAQ question ONCE and store the cleaned versions
        # in a new column. This avoids repeating the cleaning work for
        # every single user question later on.
        self.faq_dataframe["cleaned_question"] = (
            self.faq_dataframe["question"].apply(preprocess_text)
        )

        # Create the TF-IDF vectorizer. This object learns the vocabulary
        # of the FAQ dataset and knows how to convert text into numeric
        # vectors based on word importance.
        self.vectorizer = TfidfVectorizer()

        # Fit the vectorizer on the cleaned FAQ questions AND transform
        # them into a TF-IDF matrix in one step. Each row of this matrix
        # is the numeric "fingerprint" of one FAQ question.
        self.faq_tfidf_matrix = self.vectorizer.fit_transform(
            self.faq_dataframe["cleaned_question"]
        )

    @staticmethod
    def _load_faq_data(faq_csv_path: str) -> pd.DataFrame:
        """
        Load the FAQ CSV file and validate that it has the expected
        'question' and 'answer' columns.

        Raises
        ------
        FileNotFoundError
            If the CSV file does not exist at the given path.
        ValueError
            If the CSV file is missing the required columns.
        """
        if not os.path.exists(faq_csv_path):
            raise FileNotFoundError(
                f"FAQ dataset not found at '{faq_csv_path}'. "
                "Make sure faq.csv exists in the project folder."
            )

        dataframe = pd.read_csv(faq_csv_path)

        required_columns = {"question", "answer"}
        if not required_columns.issubset(set(dataframe.columns)):
            raise ValueError(
                f"faq.csv must contain the columns {required_columns}, "
                f"but found {set(dataframe.columns)} instead."
            )

        # Drop any rows where the question or answer is missing, since
        # they cannot be matched against or returned to the user.
        dataframe = dataframe.dropna(subset=["question", "answer"])
        dataframe = dataframe.reset_index(drop=True)

        return dataframe

    def get_response(self, user_question: str) -> dict:
        """
        Given a raw question typed by the user, find the most similar FAQ
        question and return its answer.

        Parameters
        ----------
        user_question : str
            The raw, unprocessed question typed by the user.

        Returns
        -------
        dict
            A dictionary with the following keys:
                'answer'            -> the matched FAQ answer, or the
                                        fallback message
                'similarity_score'  -> similarity percentage (0-100), rounded
                                        to 1 decimal place
                'matched_question'  -> the FAQ question that was matched
                                        (None if no good match was found)
        """

        # Guard clause: handle empty or whitespace-only input gracefully
        # instead of letting it flow into the vectorizer and error out.
        if not user_question or not user_question.strip():
            return {
                "answer": "Please type a question so I can help you.",
                "similarity_score": 0.0,
                "matched_question": None,
            }

        # STEP 1: Clean the user's question using the EXACT same
        # preprocessing pipeline used on the FAQ questions.
        cleaned_user_question = preprocess_text(user_question)

        # If nothing meaningful is left after cleaning (e.g. the user typed
        # only stopwords or punctuation), we cannot match anything.
        if cleaned_user_question == "":
            return {
                "answer": FALLBACK_ANSWER,
                "similarity_score": 0.0,
                "matched_question": None,
            }

        # STEP 2: Convert the cleaned user question into a TF-IDF vector
        # using the SAME vectorizer that was fitted on the FAQ questions.
        # We must use .transform() here (NOT .fit_transform()) so that the
        # vector uses the same vocabulary and IDF weights as the FAQ data.
        user_tfidf_vector = self.vectorizer.transform([cleaned_user_question])

        # STEP 3: Compute cosine similarity between the user's question
        # vector and every FAQ question vector. This returns a 2D array
        # with shape (1, number_of_faq_questions).
        similarity_scores = cosine_similarity(
            user_tfidf_vector, self.faq_tfidf_matrix
        )

        # Flatten the 2D array into a simple 1D array of scores, one score
        # per FAQ question, so it's easier to work with.
        similarity_scores = similarity_scores.flatten()

        # STEP 4: Find the index of the FAQ question with the HIGHEST
        # similarity score.
        best_match_index = similarity_scores.argmax()
        best_match_score = similarity_scores[best_match_index]

        # Convert the raw similarity (0.0 - 1.0) into a percentage
        # (0.0 - 100.0) rounded to 1 decimal place, for a nicer display.
        similarity_percentage = round(float(best_match_score) * 100, 1)

        # STEP 5: Compare the best score against our threshold.
        if best_match_score < SIMILARITY_THRESHOLD:
            return {
                "answer": FALLBACK_ANSWER,
                "similarity_score": similarity_percentage,
                "matched_question": None,
            }

        # If we get here, we found a good enough match! Retrieve the
        # corresponding answer and original question text from the dataframe.
        matched_answer = self.faq_dataframe.loc[best_match_index, "answer"]
        matched_question = self.faq_dataframe.loc[best_match_index, "question"]

        return {
            "answer": matched_answer,
            "similarity_score": similarity_percentage,
            "matched_question": matched_question,
        }


# ---------------------------------------------------------------------------
# QUICK MANUAL TEST
# ---------------------------------------------------------------------------
# Running this file directly (python chatbot.py) lets you chat with the bot
# straight from the terminal, without needing to start the Flask server.
# Type 'quit' or 'exit' to stop.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Loading FAQ Chatbot... please wait.")
    bot = FAQChatbot()
    print("FAQ Chatbot is ready! Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break

        result = bot.get_response(user_input)
        print(f"Bot: {result['answer']}")
        print(f"     (Similarity: {result['similarity_score']}%)\n")

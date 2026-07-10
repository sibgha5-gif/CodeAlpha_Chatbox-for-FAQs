# 🤖 FAQ Chatbot — NLP-Based Question Answering System

A beginner-friendly, fully working **retrieval-based FAQ chatbot** built with
Python, NLTK, scikit-learn, and Flask. The chatbot reads a set of
Frequently Asked Questions from a CSV file, learns their meaning using
**TF-IDF vectorization**, and answers new user questions by finding the most
similar FAQ using **cosine similarity** — no paid APIs, no external LLMs,
100% classic NLP.

---

## 📌 Project Overview

This project was built to fulfill an internship task requiring an
NLP-based chatbot that:

1. Reads FAQs (question/answer pairs) from a CSV file.
2. Preprocesses text with NLTK (lowercasing, punctuation removal,
   tokenization, stopword removal, lemmatization).
3. Converts FAQ questions into TF-IDF vectors.
4. Accepts a live user question through a web interface.
5. Preprocesses the user's question with the **exact same** pipeline.
6. Computes cosine similarity between the user question and every FAQ.
7. Returns the best-matching answer — or a polite fallback message if
   nothing is similar enough (similarity < 0.35).

The result is wrapped in a clean, modern, mobile-responsive Flask web app.

---

## ✨ Features

- 🧠 Classic NLP pipeline (NLTK) — lowercase → remove punctuation →
  tokenize → remove stopwords → lemmatize
- 📊 TF-IDF vectorization + cosine similarity matching (scikit-learn)
- 💬 Chat-style web interface with bubbles (user right, bot left)
- 📈 **Similarity percentage** shown under every bot reply
- ⏳ **"Searching..." animation** while the bot is "thinking"
- 🕒 **Timestamp** on every message
- 🧹 **Clear Chat** button
- 🌙 **Dark Mode** toggle
- 🗂️ In-session **chat history** (kept while the tab is open)
- ⌨️ Press **Enter** to send a message
- 📱 Fully **mobile-responsive** design
- 🛡️ Graceful **error handling** on both frontend and backend
- 🎨 Smooth CSS animations (fade-in messages, bouncing typing dots, pulsing
  online indicator)

---

## 📁 Folder Structure

```
FAQ_Chatbot/
│
├── app.py                # Flask server - routes & API endpoint
├── chatbot.py             # Chatbot "brain": TF-IDF + cosine similarity logic
├── preprocessing.py       # NLTK text preprocessing pipeline
├── faq.csv                 # FAQ dataset (58 question/answer pairs)
├── requirements.txt        # Python dependencies
├── README.md                # You are here
│
├── static/
│   ├── style.css            # Chat UI styling (light + dark mode)
│   └── script.js             # Frontend chat logic (fetch, DOM, dark mode)
│
└── templates/
    └── index.html             # Chat web page (Flask Jinja2 template)
```

---

## ⚙️ Installation

### 1. Clone or download the project folder
Make sure all files above are inside a folder named `FAQ_Chatbot`.

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open the chatbot in your browser
Go to:
```
http://127.0.0.1:5000/
```

> 💡 The first time you run the app, NLTK will automatically download the
> small resource files it needs (`punkt`, `stopwords`, `wordnet`). This
> requires an internet connection but only happens once.

---

## 📚 Libraries Used

| Library        | Purpose                                                        |
|----------------|-----------------------------------------------------------------|
| **Flask**      | Web server, routing, and rendering the HTML interface            |
| **pandas**     | Reading and handling the FAQ dataset (`faq.csv`)                 |
| **nltk**       | Tokenization, stopword removal, and lemmatization                |
| **scikit-learn** | TF-IDF vectorization and cosine similarity computation          |

---

## 🧠 How It Works

1. **Loading the data** — `chatbot.py` reads `faq.csv` into a pandas
   DataFrame containing `question` and `answer` columns.

2. **Preprocessing** — Every FAQ question is cleaned once at startup using
   `preprocessing.py`'s `preprocess_text()` function:
   - Lowercase the text
   - Strip out punctuation
   - Tokenize into individual words
   - Remove English stopwords (the, is, a, ...)
   - Lemmatize each remaining word to its dictionary base form

3. **Vectorization** — The cleaned FAQ questions are converted into TF-IDF
   vectors using scikit-learn's `TfidfVectorizer`. This turns each question
   into a numeric representation where rarer, more meaningful words carry
   more weight than common ones.

4. **User interaction** — When a user types a question in the chat UI,
   the frontend (`script.js`) sends it to the Flask backend via a POST
   request to `/get_response`.

5. **Matching** — The backend cleans the user's question with the exact
   same preprocessing pipeline, converts it into a TF-IDF vector using the
   **already-fitted** vectorizer, and computes **cosine similarity** against
   every FAQ vector.

6. **Response** — The FAQ with the highest similarity score is selected.
   - If the best score is **≥ 0.35**, its answer is returned along with the
     similarity percentage.
   - If the best score is **below 0.35**, the chatbot replies:
     _"Sorry, I couldn't find a relevant answer."_

7. **Display** — The frontend renders the response as a chat bubble with a
   timestamp and a similarity badge (e.g. `91.7% match`).

---

## 🖼️ Screenshots

> _Add screenshots of your running chatbot here before submitting._

- Light mode chat view: `screenshots/light-mode.png`
- Dark mode chat view: `screenshots/dark-mode.png`
- Mobile responsive view: `screenshots/mobile-view.png`

---

## 🚀 Future Improvements

- Add support for multi-turn conversations (remembering context across
  messages).
- Expand the FAQ dataset and allow admins to add new FAQs through a UI.
- Add spelling correction before preprocessing to handle typos.
- Use word embeddings (e.g. Word2Vec/GloVe) instead of TF-IDF for better
  semantic matching of paraphrased questions.
- Persist chat history in a database instead of only in-session memory.
- Add voice input/output support.
- Deploy the app to a cloud platform (Render, Railway, PythonAnywhere).

---

## 👩‍💻 Author

**Sibgha Shahid**

Biomedical Engineering Undergraduate

Internship Project: NLP-Based FAQ Chatbot

Technologies:
- Python
- Flask
- NLTK
- Scikit-learn
- HTML
- CSS
- JavaScript

## 📄 License

This project is developed for educational and internship purposes.

## 🎯 Demo

Run the application locally:

python app.py

Then open:

http://127.0.0.1:5000



"""
app.py
-------
This file is the entry point of the web application. It creates a Flask
web server that:
    1. Serves the chatbot's HTML/CSS/JS interface to the browser.
    2. Exposes a '/get_response' API endpoint that the front-end JavaScript
       calls whenever the user sends a message.

This file intentionally contains NO NLP or machine learning code - all of
that logic lives in chatbot.py and preprocessing.py. app.py's only job is
to connect the chatbot "brain" to the web.
"""

from flask import Flask, render_template, request, jsonify

from chatbot import FAQChatbot

# ---------------------------------------------------------------------------
# APPLICATION SETUP
# ---------------------------------------------------------------------------

# Create the Flask application instance. __name__ tells Flask where to look
# for templates/ and static/ folders relative to this file.
app = Flask(__name__)

# Create ONE chatbot instance when the server starts up. Loading the FAQ
# dataset and building the TF-IDF matrix only happens once here, instead of
# on every single request, which keeps response times fast.
faq_chatbot = FAQChatbot()


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """
    Serve the main chatbot web page (templates/index.html) when a user
    visits the root URL of the site, e.g. http://127.0.0.1:5000/
    """
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    """
    API endpoint used by the front-end JavaScript (static/script.js) to
    send the user's question to the chatbot and receive an answer back.

    Expects a JSON body like:
        { "message": "What is Python?" }

    Returns a JSON response like:
        {
            "answer": "Python is a high-level ...",
            "similarity_score": 91.7,
            "matched_question": "What is Python?"
        }
    """
    try:
        # Parse the incoming JSON request body sent by the browser.
        request_data = request.get_json(silent=True) or {}
        user_message = request_data.get("message", "")

        # Ask the chatbot to find the best matching FAQ answer.
        chatbot_result = faq_chatbot.get_response(user_message)

        # Send the result back to the browser as JSON.
        return jsonify(chatbot_result), 200

    except Exception as error:
        # If anything unexpected goes wrong (bad input, internal error,
        # etc.), we catch it here so the server never crashes and the
        # user always gets a sensible JSON response instead of a blank
        # error page.
        return jsonify({
            "answer": "Something went wrong while processing your question. "
                      "Please try again.",
            "similarity_score": 0.0,
            "matched_question": None,
            "error": str(error),
        }), 500


# ---------------------------------------------------------------------------
# RUN THE APPLICATION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # debug=True enables auto-reloading and detailed error pages while
    # developing. This should be set to False in a real production setting.
    app.run(debug=True)

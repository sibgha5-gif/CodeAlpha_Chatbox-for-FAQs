/* ===========================================================================
   script.js
   ---------
   Handles all the interactive behaviour of the chatbot page:
     - Sending user messages to the Flask backend ('/get_response')
     - Rendering bot and user chat bubbles with timestamps
     - Showing the "Searching..." typing indicator while waiting for a reply
     - Auto-scrolling the chat to the latest message
     - Dark mode toggle
     - Clear chat button
     - Basic error handling if the server request fails
   =========================================================================== */

// ---------------------------------------------------------------------------
// GRAB REFERENCES TO THE HTML ELEMENTS WE NEED TO WORK WITH
// ---------------------------------------------------------------------------
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");
const darkModeToggle = document.getElementById("darkModeToggle");
const clearChatBtn = document.getElementById("clearChatBtn");

// This array stores the chat history for the CURRENT browser session only.
// (Per the project requirements, history does not need to persist after
// the page is refreshed or closed.)
let chatHistory = [];

// ---------------------------------------------------------------------------
// HELPER: Get a nicely formatted current time string, e.g. "10:42 AM"
// ---------------------------------------------------------------------------
function getCurrentTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// ---------------------------------------------------------------------------
// HELPER: Scroll the chat box all the way down so the newest message
// is always visible to the user.
// ---------------------------------------------------------------------------
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ---------------------------------------------------------------------------
// Render a single chat bubble (either from the "user" or the "bot") into
// the chat box, along with a timestamp and (for bot messages) an optional
// similarity score badge.
// ---------------------------------------------------------------------------
function appendMessage(sender, text, similarityScore = null) {
    // Create the outer wrapper for this message (controls left/right align)
    const messageRow = document.createElement("div");
    messageRow.classList.add("message-row", sender);

    // Create the speech-bubble element itself and insert the message text.
    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.textContent = text;

    // Create the metadata row (timestamp + similarity badge if applicable).
    const meta = document.createElement("div");
    meta.classList.add("message-meta");

    const timeSpan = document.createElement("span");
    timeSpan.textContent = getCurrentTimestamp();
    meta.appendChild(timeSpan);

    // Only bot messages that found a real match display a similarity score.
    if (sender === "bot" && similarityScore !== null) {
        const scoreBadge = document.createElement("span");
        scoreBadge.classList.add("similarity-badge");
        scoreBadge.textContent = `${similarityScore}% match`;
        meta.appendChild(scoreBadge);
    }

    messageRow.appendChild(bubble);
    messageRow.appendChild(meta);
    chatBox.appendChild(messageRow);

    // Save this message into our in-memory session history.
    chatHistory.push({ sender, text, similarityScore, time: getCurrentTimestamp() });

    scrollToBottom();
}

// ---------------------------------------------------------------------------
// Show or hide the "Searching..." typing indicator while we wait for the
// Flask backend to respond.
// ---------------------------------------------------------------------------
function setTypingIndicator(isVisible) {
    if (isVisible) {
        typingIndicator.classList.remove("hidden");
        scrollToBottom();
    } else {
        typingIndicator.classList.add("hidden");
    }
}

// ---------------------------------------------------------------------------
// MAIN FUNCTION: Send the user's typed message to the Flask backend and
// display the chatbot's response once it arrives.
// ---------------------------------------------------------------------------
async function sendMessage() {
    const messageText = userInput.value.trim();

    // Don't send empty messages.
    if (messageText === "") {
        return;
    }

    // Immediately display the user's own message in the chat.
    appendMessage("user", messageText);

    // Clear the input box and disable the send button while we wait,
    // to prevent the user from spamming multiple requests at once.
    userInput.value = "";
    sendBtn.disabled = true;
    setTypingIndicator(true);

    try {
        // Send a POST request to our Flask '/get_response' endpoint with
        // the user's message packed as JSON.
        const response = await fetch("/get_response", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: messageText }),
        });

        // If the server responded with an error status code, treat it
        // as a failure so we fall into the catch block below.
        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();

        // Display the bot's answer along with its similarity score.
        appendMessage("bot", data.answer, data.similarity_score);

    } catch (error) {
        // Network failure, server crash, or unexpected error - show the
        // user a friendly message instead of leaving them with no response.
        console.error("Error contacting chatbot backend:", error);
        appendMessage(
            "bot",
            "Oops! I'm having trouble connecting to the server. Please try again."
        );
    } finally {
        // Whether it succeeded or failed, always hide the typing indicator
        // and re-enable the send button so the user can try again.
        setTypingIndicator(false);
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// ---------------------------------------------------------------------------
// EVENT LISTENERS
// ---------------------------------------------------------------------------

// Send the message when the send button is clicked.
sendBtn.addEventListener("click", sendMessage);

// Send the message when the user presses Enter inside the text box.
userInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

// ---------------------------------------------------------------------------
// DARK MODE TOGGLE
// ---------------------------------------------------------------------------
darkModeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");

    // Update the button icon depending on the current mode, purely for a
    // nice visual touch (sun icon in dark mode, moon icon in light mode).
    const isDarkMode = document.body.classList.contains("dark-mode");
    darkModeToggle.textContent = isDarkMode ? "☀️" : "🌙";
});

// ---------------------------------------------------------------------------
// CLEAR CHAT BUTTON
// ---------------------------------------------------------------------------
clearChatBtn.addEventListener("click", () => {
    // Remove every message currently shown in the chat box.
    chatBox.innerHTML = "";

    // Reset the in-memory session history.
    chatHistory = [];

    // Show the welcome message again after clearing.
    showWelcomeMessage();
});

// ---------------------------------------------------------------------------
// WELCOME MESSAGE
// ---------------------------------------------------------------------------
// Shown once when the page first loads (and again after clearing the chat)
// so the user immediately understands what the chatbot can do.
// ---------------------------------------------------------------------------
function showWelcomeMessage() {
    const welcomeDiv = document.createElement("div");
    welcomeDiv.classList.add("welcome-message");
    welcomeDiv.textContent = "👋 Ask me anything about Python, AI, Machine Learning, Data Science, NLP, or Flask!";
    chatBox.appendChild(welcomeDiv);

    // Also send a friendly greeting as an actual bot message bubble.
    appendMessage("bot", "Hi there! I'm your FAQ Assistant. What would you like to know?");
}

// Run once the page finishes loading.
window.addEventListener("DOMContentLoaded", () => {
    showWelcomeMessage();
    userInput.focus();
});

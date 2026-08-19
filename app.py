"""
Waste Management Chatbot
-------------------------
A session-based memory chatbot built with Flask + SQLite + Ollama (llama3.2:latest).

Structure:
    session2/
        app.py
        data.json          -> waste management knowledge base
        db.sqlite           -> stores chat history per session (created automatically)
        templates/
            index.html       -> Bootstrap-only frontend with floating chat widget

Run:
    1. Make sure Ollama is installed and running:  https://ollama.com
    2. Pull the model:  ollama pull llama3.2:latest
    3. pip install flask requests
    4. python app.py
    5. Open http://127.0.0.1:5000
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime

import requests
from flask import Flask, request, jsonify, render_template, session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite")
DATA_PATH = os.path.join(BASE_DIR, "data.json")

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:latest"

app = Flask(__name__)
app.secret_key = "waste-management-chatbot-secret-key"  # change in production


# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #
def init_db():
    """Create the chat_history table if it does not already exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,          -- 'user' or 'assistant'
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_message(session_id, role, message):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (session_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, message, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(session_id, limit=20):
    """Return the last `limit` messages for a session, oldest first."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT role, message FROM chat_history
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": r, "content": m} for r, m in rows]


def clear_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- #
# Knowledge base helpers
# --------------------------------------------------------------------------- #
def load_knowledge_base():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt():
    """Turn data.json into a compact system prompt the model can reference."""
    kb = load_knowledge_base()
    lines = [
        "You are 'EcoBot', a friendly waste management assistant. "
        "You help users understand waste categories, how to recycle them, "
        "and give recommendations and suggestions for responsible disposal. "
        "Use the reference knowledge base below whenever relevant, but you may "
        "also answer general waste-management questions using your own knowledge. "
        "Keep answers concise, practical, and encouraging. Remember the ongoing "
        "conversation and refer back to earlier messages when useful.",
        "",
        "REFERENCE KNOWLEDGE BASE (waste categories):",
    ]
    for item in kb.get("waste_categories", []):
        lines.append(f"- Type: {item['type']}")
        lines.append(f"  Description: {item['description']}")
        lines.append(f"  Recycle Details: {item['recycle_details']}")
        lines.append(f"  Recommendation: {item['recommendation']}")
        lines.append(f"  Suggestions: {', '.join(item['suggestions'])}")
    return "\n".join(lines)


SYSTEM_PROMPT = build_system_prompt()


# --------------------------------------------------------------------------- #
# Ollama call
# --------------------------------------------------------------------------- #
def ask_ollama(messages):
    """
    messages: list of {"role": "user"/"assistant", "content": "..."} (chat history)
    Prepends the system prompt and calls the local Ollama server.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": False,
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "Sorry, I couldn't generate a response.")
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ I can't reach the Ollama server. Please make sure Ollama is running "
            "(`ollama serve`) and that the model 'llama3.2:latest' is pulled "
            "(`ollama pull llama3.2:latest`)."
        )
    except Exception as e:
        return f"⚠️ Something went wrong talking to the model: {e}"


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/api/history", methods=["GET"])
def api_history():
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"history": []})
    return jsonify({"history": get_history(session_id)})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    session_id = session["session_id"]

    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Save user's message
    save_message(session_id, "user", user_message)

    # Build conversation memory (previous turns + this one)
    history = get_history(session_id, limit=20)

    # Ask the model
    reply = ask_ollama(history)

    # Save assistant's reply
    save_message(session_id, "assistant", reply)

    return jsonify({"reply": reply})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    session_id = session.get("session_id")
    if session_id:
        clear_history(session_id)
    return jsonify({"status": "cleared"})


@app.route("/api/categories", methods=["GET"])
def api_categories():
    """Expose the waste knowledge base to the frontend (e.g. quick-suggestion chips)."""
    return jsonify(load_knowledge_base())


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
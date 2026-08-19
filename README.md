♻️ EcoWaste Manager — Waste Management Chatbot

A session-based, memory-enabled chatbot that helps users understand waste categories, recycling details, and disposal recommendations. Built with Flask, SQLite, Bootstrap, and Ollama (llama3.2:latest).

📁 Project Structure
session2/
├── app.py                 # Flask backend (routes, DB, Ollama integration)
├── data.json               # Waste management knowledge base
├── db.sqlite                # SQLite database (chat history per session)
├── requirements.txt        # Python dependencies
└── templates/
    └── index.html           # Bootstrap-only frontend + floating chat widget
✨ Features
Floating chat icon at the bottom-right of the page — click to open/close the chatbot window (Bootstrap components only, no custom CSS/JS).
Conversational memory — each browser session gets a unique session_id; previous messages are stored in db.sqlite and replayed to the model so EcoBot remembers the ongoing conversation.
Waste knowledge base (data.json) covering:
Plastic Waste
Organic / Wet Waste
E-Waste
Paper & Cardboard
Glass Waste
Hazardous Waste
Metal Waste
Each entry includes description, type, recycle details, recommendation, and suggestions.
Quick-suggestion chips inside the chat window for one-click questions.
Reset button to clear the current session's chat history.
Powered by Ollama's llama3.2:latest model running locally.
🧰 Tech Stack
Layer	Technology
Backend	Flask (Python)
Database	SQLite
Frontend	Bootstrap 5 + Bootstrap Icons (CDN)
LLM	Ollama — llama3.2:latest
⚙️ Prerequisites
Python 3.9+
Ollama installed locally
The llama3.2:latest model pulled:
bash
  ollama pull llama3.2:latest
🚀 Setup & Run (Local)
Clone / download the project
bash
   cd session2
Install dependencies
bash
   pip install -r requirements.txt
Start Ollama (in a separate terminal, if not already running)
bash
   ollama serve
Run the Flask app
bash
   python app.py
Open the app Visit http://127.0.0.1:5000 in your browser.
Chat with EcoBot Click the round chat icon in the bottom-right corner and start asking questions like:
"How do I recycle plastic bottles?"
"What should I do with old batteries?"
"Tell me about hazardous waste."
🔌 API Endpoints
Method	Endpoint	Description
GET	/	Renders the main page
GET	/api/history	Returns the current session's chat history
POST	/api/chat	Sends a user message, returns EcoBot's reply
POST	/api/reset	Clears the current session's chat history
GET	/api/categories	Returns the full waste knowledge base (JSON)
🌐 Deploying on Render
Push this project to a GitHub repository.
Create a new Web Service on Render and connect the repo.
Configure:
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Deploy.

⚠️ Important: Render's standard web services cannot run a local Ollama server. To use the chatbot in production, point OLLAMA_URL in app.py to a remotely hosted Ollama instance (or another LLM API), and consider replacing SQLite with a persistent database (e.g. Render PostgreSQL), since the local filesystem is reset on every redeploy.

📝 Notes
Chat memory is scoped per browser session using Flask's session cookie.
If Ollama is not running or unreachable, EcoBot responds with a friendly error message instead of crashing.
The knowledge base (data.json) is injected into the model's system prompt, so the bot's answers stay grounded in the defined waste categories while still being able to answer general waste-management questions.
📄 License

This project is provided for educational/demo purposes. Feel free to modify and extend it.

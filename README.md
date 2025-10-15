# 🤖 AI-Powered Chatbot (Beginner Friendly)

🚀 Gemini-only FastAPI chatbot with streaming to the browser, optional lightweight web search context, light/dark theme toggle, and a simple demo login.

## ✨ Features
- 🗣️ Gemini-only streaming responses (google-generativeai)
- 🔎 Optional “Use web search” context via DuckDuckGo Instant Answer (demo-only)
- 🎨 Clean UI with avatars, chat bubbles, typing indicator, and feature bar:
	- 🔍 Web Search toggle, 📋 Copy Transcript, 🧹 Clear, ℹ️ About, 🌓 Theme toggle
- 🌗 Light/Dark theme (persistent)
- 🔐 Demo login (cookie-based display name; not production auth)
- ❤️‍🩹 Health endpoints and a Gemini connectivity check
- 🖼️ Favicon (SVG) that looks sharp on high-DPI displays

## 🧰 Requirements
- 🪟 Windows, 🐍 Python 3.9+

## 🛠️ Setup

1) 🧩 Create and activate a virtual environment, then install dependencies.

```cmd
REM From Windows cmd
cd /d "D:\Vs Code\PROJECT\AI_Powered_Chatbot_New"
python -m venv .venv
".venv\Scripts\python" -m pip install --upgrade pip
".venv\Scripts\python" -m pip install -r requirements.txt
```

2) 🔑 Configure your Gemini API key.

```cmd
REM Copy the example and edit your key
copy .env.example .env
REM Open .env and set GEMINI_API_KEY=your_key_here
```

The app will default to `GEMINI_MODEL=gemini-2.0-flash`. If you have issues, try `gemini-1.5-flash`.

3) ▶️ Run the app (pick a port that works on your machine; 8020 is used below).

```cmd
".venv\Scripts\python" -m uvicorn app.main:app --reload --port 8020
```

🔁 Open http://127.0.0.1:8020 and press Ctrl+F5 to hard refresh (ensures latest CSS/JS).

### 🐚 Git Bash (alternative)
```bash
cd "/d/Vs Code/PROJECT/AI_Powered_Chatbot_New"
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --port 8020
```

## 💬 Using the UI
- ⌨️ Type a message and press Enter (or click Send). Responses stream in real-time.
- 🌐 Toggle Web Search to add a brief live context from DuckDuckGo IA (demo).
- 📄 Copy Transcript copies visible bubbles to your clipboard.
- 🧽 Clear only clears the current view (no server history).
- ℹ️ About opens a brief info modal.
- 🌓 Theme toggles light/dark and remembers your choice.
- 🔓 Login lets you set a display name stored in a cookie (demo only). Logout clears it.

## 🚪 Endpoints
- 🏠 `GET /` – Chat UI
- ✅ `GET /health` – Health check: `{status: "ok", gemini_key_present: true|false}`
- 🔬 `GET /health/gemini` – Quick Gemini test (model + short sample or error)
- 📨 `POST /api/chat` – Streaming chat endpoint
	- Request body (example):

```json
{
	"messages": [
		{ "role": "system", "content": "You are a helpful assistant." },
		{ "role": "user", "content": "Hello!" }
	],
	"use_web_search": false
}
```

## 📁 Project structure
- 🧭 `app/main.py` – FastAPI app, endpoints (`/`, `/health`, `/health/gemini`, `/api/chat`, `/login`, `/logout`)
- 🖥️ `app/templates/index.html` – Chat UI
- 🔑 `app/templates/login.html` – Simple name-only login form (demo)
- 🎨 `app/static/style.css` – Styles (supports light/dark)
- ⚙️ `app/static/main.js` – Client logic (streaming, UI controls)
- 🏷️ `app/static/favicon.svg` – Favicon
- 📄 `.env.example` – Example env vars (copy to `.env`)
- 📦 `requirements.txt` – Dependencies
- 🧾 `pyproject.toml` – Project metadata

## 🩺 Troubleshooting
- 🚫 Port permissions (WinError 10013): choose another port (e.g., 8021, 8023).
- 🧭 PowerShell curl alias issues: prefer `curl.exe` when testing endpoints.
	- 🔎 Example: `curl.exe http://127.0.0.1:8020/health`
	- 📨 JSON post example:

```cmd
curl.exe -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}],\"use_web_search\":false}" http://127.0.0.1:8020/api/chat
```

- If UI looks unchanged: hard refresh (Ctrl+F5). Assets are versioned (e.g., `?v=20251014-4`).
- If responses don’t stream: check `/health` and `/health/gemini`. Ensure `GEMINI_API_KEY` is set in the same terminal used to start uvicorn.
- Light mode text contrast: ensure latest CSS loaded (hard refresh). The bubbles use `color: var(--fg)`.

## 🧾 Notes
- The login is for demo purposes only (cookie-based display name, no auth).
- The web search is a minimal demo via DuckDuckGo IA. For production, use a robust retrieval pipeline (e.g., Tavily/Bing + proper citations).

## ▶️ VS Code
- You can use the task “Run FastAPI app” to start the server.

---

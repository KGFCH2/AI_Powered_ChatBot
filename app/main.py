import os
from typing import AsyncGenerator, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from fastapi import Form

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

app = FastAPI(title="AI Chatbot")

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    use_web_search: Optional[bool] = False


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    username = request.cookies.get("username")
    return templates.TemplateResponse("index.html", {"request": request, "username": username})


@app.get("/health")
async def health():
    return {"status": "ok", "gemini_key_present": bool(GEMINI_API_KEY)}





async def stream_gemini_response(messages: List[ChatMessage]) -> AsyncGenerator[bytes, None]:
    """Stream a Gemini response and yield plain text bytes.

    This function is defensive: it yields short error messages instead of raising,
    so the client doesn't hang if something goes wrong mid-stream.
    """
    try:
        import google.genai as genai
    except Exception as e:  # Library missing or import failure
        yield f"[setup error] google-genai not available: {e}".encode("utf-8")
        return

    if not GEMINI_API_KEY:
        yield b"[config error] GEMINI_API_KEY is not set on the server"
        return

    # Convert messages to Gemini "contents" format
    contents = []
    for m in messages:
        if m.role == "user":
            role = "user"
            text = m.content
        elif m.role == "assistant":
            role = "model"
            text = m.content
        else:  # e.g., "system" -> convert to user instruction for compatibility
            role = "user"
            text = f"Instruction: {m.content}"
        contents.append({
            "role": role,
            "parts": [{"text": text}],
        })

    try:
        # Initialize client with API key
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Stream response from Gemini
        stream = client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=contents,
            config={
                "temperature": 0.7,
                "max_output_tokens": 512,
            },
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text.encode("utf-8")
    except Exception as e:
        # Surface model/config/runtime errors to the client as a final line
        yield f"\n[model error] {str(e)}".encode("utf-8")


@app.post("/api/chat")
async def chat(req: ChatRequest):
    last = req.messages[-1].content if req.messages else ""
    messages = req.messages  # Gemini-only

    # If web search is enabled, fetch context and prepend to system prompt
    if req.use_web_search and last:
        try:
            context = await fetch_web_context(query=last)
            system_prefix = (
                "You can use the following recent web context to answer. If it's irrelevant, ignore it.\n\n"
                + context
                + "\n\nAnswer clearly and cite sources with their URLs if used."
            )
            messages = [ChatMessage(role="system", content=system_prefix)] + messages
        except Exception as e:
            # On failure, proceed without web context
            pass

    if not GEMINI_API_KEY:
        return JSONResponse(status_code=400, content={"error": "GEMINI_API_KEY is not set. Add it to your .env or environment variables."})
    try:
        return StreamingResponse(stream_gemini_response(messages), media_type="text/plain")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


async def fetch_web_context(query: str) -> str:
    # Minimal web search with DuckDuckGo Instant Answer API (no key), then fetch top result page title/summary.
    # Note: This is a simple demo and not guaranteed for production. Replace with Tavily/Bing/Web APIs as needed.
    ddg_url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(ddg_url, params=params)
        r.raise_for_status()
        data = r.json()
        abstract = data.get("AbstractText") or ""
        heading = data.get("Heading") or ""
        url = data.get("AbstractURL") or ""
        related = data.get("RelatedTopics") or []
        extra = []
        for t in related[:3]:
            if isinstance(t, dict):
                text = t.get("Text")
                first_url = t.get("FirstURL")
                if text and first_url:
                    extra.append(f"- {text} ({first_url})")
        parts = []
        if heading: parts.append(f"Heading: {heading}")
        if abstract: parts.append(f"Summary: {abstract}")
        if url: parts.append(f"Source: {url}")
        if extra: parts.append("Related:\n" + "\n".join(extra))
        return "\n".join(parts)


@app.get("/health/gemini")
async def health_gemini():
    """Quickly verify Gemini configuration and connectivity without streaming."""
    if not GEMINI_API_KEY:
        return JSONResponse(status_code=400, content={"ok": False, "error": "GEMINI_API_KEY is missing"})
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        res = model.generate_content("ping")
        sample = getattr(res, "text", "")
        return {"ok": True, "model": GEMINI_MODEL, "sample": (sample or "").strip()[:60]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "model": GEMINI_MODEL, "error": str(e)})


# --- simple demo login/logout (cookie-based, not production-ready) ---
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def do_login(username: str = Form(...)):
    username = (username or "").strip()
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    resp = RedirectResponse(url="/", status_code=303)
    # Cookie for demo only; consider secure flags in production
    resp.set_cookie(key="username", value=username, httponly=False, samesite="Lax")
    return resp


@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("username")
    return resp

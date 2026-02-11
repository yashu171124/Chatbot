import subprocess
import os
import sqlite3
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

try:
    from langchain_ollama import ChatOllama
except Exception:
    ChatOllama = None

try:
    from langchain_community.tools import DuckDuckGoSearchRun
except Exception:
    DuckDuckGoSearchRun = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str

def init_db():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS profile (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)')
    cursor.execute("INSERT OR IGNORE INTO profile (key, value) VALUES ('name', 'Yash')")
    cursor.execute("INSERT OR IGNORE INTO profile (key, value) VALUES ('role', 'Lead Developer @ Jaffer Agentic')")
    cursor.execute("INSERT OR IGNORE INTO profile (key, value) VALUES ('tech', 'C++, React, FastAPI, Ollama')")
    conn.commit()
    conn.close()

init_db()

# Fallback classes
class _DummyResponse:
    def __init__(self, content: str):
        self.content = content

class _DummyLLM:
    async def ainvoke(self, messages):
        return _DummyResponse("Ollama unavailable — using fallback response.")

if ChatOllama is not None:
    try:
        llm = ChatOllama(model="llama3.1:8b")
    except Exception as e:
        logging.warning(f"Failed to initialize ChatOllama: {e}")
        llm = _DummyLLM()
else:
    llm = _DummyLLM()

search_tool = None
if DuckDuckGoSearchRun is not None:
    try:
        search_tool = DuckDuckGoSearchRun()
    except Exception as e:
        logging.warning(f"Failed to initialize DuckDuckGoSearchRun: {e}")

def get_cpp_intelligence(query_key: str):
    try:
        exe_path = os.path.join("data_engine", "search.exe")
        result = subprocess.run([exe_path, query_key], capture_output=True, text=True, encoding='utf-8', timeout=5)
        return result.stdout.strip()
    except Exception:
        return "No data found. | User mood is NEUTRAL."

@app.get("/profile")
async def get_profile():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM profile")
    data = dict(cursor.fetchall())
    conn.close()
    return data

@app.post("/chat")
async def chat(input_data: ChatInput):
    user_message = input_data.message
    
    cpp_output = get_cpp_intelligence(user_message)
    parts = cpp_output.split(" | ")
    local_fact = parts[0] if len(parts) > 0 else "No data found."
    user_mood = parts[1] if len(parts) > 1 else "NEUTRAL"
    
    live_web_data = ""
    if "No data found" in local_fact and search_tool:
        try:
            live_web_data = search_tool.run(f"{user_message} today February 10 2026")
        except Exception as e:
            logging.warning(f"Search failed: {e}")
            
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM profile WHERE key='name'")
    result = cursor.fetchone()
    user_name = result[0] if result else "User"

    system_prompt = f"""
    ROLE: You are Jaffer, a live-data agent. 
    DATE: Tuesday, February 10, 2026.
    
    DATA_FEED:
    - LOCAL: {local_fact.strip()}
    - WEB: {live_web_data.strip()}
    
    MANDATORY RULES:
    1. If the WEB feed is empty, say "I'm currently unable to fetch live numbers." 
    2. NEVER invent a price (like 51,500). If the data says ₹15,791, use that.
    3. You are prohibited from saying "I don't have real-time access." 
    4. Be savvy and concise.
    """
    
    try:
        response = await llm.ainvoke([("system", system_prompt), ("user", user_message)])
        cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", ("user", user_message))
        cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", ("bot", response.content))
        conn.commit()
        conn.close()
        return {"reply": str(response.content)}
    except Exception:
        conn.close()
        raise HTTPException(status_code=500, detail="Core Inference Failure")
    
@app.get("/history")
async def get_history():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM history WHERE role='user' ORDER BY id DESC LIMIT 10")
    chats = cursor.fetchall()
    conn.close()
    return {"history": [chat[0][:25] + "..." for chat in chats]}

@app.post("/clear")
async def clear_history():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    return {"status": "cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)

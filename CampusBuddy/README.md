# CampusBuddy AI — Multi-provider student assistant

CampusBuddy is a student-focused chatbot built with Python and Streamlit. It connects to AI providers that support the OpenAI-compatible Chat Completions API.

## Features
- Explains academic concepts in student-friendly language
- Helps create study plans and interview preparation schedules
- Provides project guidance and technical explanations
- Drafts professional emails to faculty
- Supports xAI (Grok), OpenAI, Groq, OpenRouter, Together AI, and custom compatible endpoints
- Maintains conversation context during the active Streamlit session

## Requirements
- Python 3.10 or newer
- An API key and supported model from one compatible provider

## Run locally (Windows / VS Code)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Configure
1. Open the app at `http://localhost:8501`.
2. Select a provider in the sidebar.
3. Enter that provider's API key and exact model ID.
4. For the custom option, also enter its OpenAI-compatible base URL.

The API key can be entered in the sidebar at runtime. Do not commit real API keys or `.env` files. The `.env.example` file contains placeholders only.

## Architecture
Student → Streamlit UI → Python application → OpenAI-compatible Chat Completions API → response

## Limitations
Provider compatibility depends on support for the OpenAI-compatible Chat Completions endpoint. The app does not currently retrieve private college records or persist conversation history to a database; chat history lasts for the active Streamlit session.

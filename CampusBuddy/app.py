import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="CampusBuddy AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp {background:linear-gradient(135deg,#081426 0%,#102b46 55%,#102033 100%);color:#f4f7fb;}
.block-container {max-width:1050px;padding-top:2rem;}
.hero {padding:1.5rem 1.8rem;border:1px solid #294b68;border-radius:22px;
background:linear-gradient(120deg,#143d5b,#142742);margin-bottom:1.2rem;}
.hero h1 {margin:0;color:#fff;font-size:2.25rem;}
.hero p {color:#d5e5f5;margin:.45rem 0 0;}
.pill {display:inline-block;padding:5px 11px;border-radius:20px;background:#164d60;
color:#b8f4e6;font-size:.8rem;margin:4px 5px 0 0;}
[data-testid="stSidebar"] {background:#f4f6fa;}
[data-testid="stSidebar"] * {color:#172b42;}
[data-testid="stChatMessage"] {background:rgba(21,43,65,.85);border:1px solid #29445d;border-radius:16px;}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li {color:#fff !important;}
[data-testid="stChatInput"] textarea {color:#172b42 !important;background:#fff !important;-webkit-text-fill-color:#172b42 !important;}
[data-testid="stChatInput"] textarea::placeholder {color:#64748b !important;-webkit-text-fill-color:#64748b !important;opacity:1 !important;}
.stButton>button {background:#fff !important;color:#17324d !important;border:1px solid #9bbbd3 !important;border-radius:10px !important;font-weight:600 !important;}
.stButton>button p,.stButton>button span {color:#17324d !important;}
[data-testid="stAlert"],[data-testid="stAlert"] * {color:#172b42 !important;-webkit-text-fill-color:#172b42 !important;}
[data-testid="stAlert"] pre,[data-testid="stAlert"] code {background:#e8eef5 !important;color:#172b42 !important;}
</style>
""", unsafe_allow_html=True)

PROVIDERS = {
    "xAI (Grok)": "https://api.x.ai/v1",
    "OpenAI": "https://api.openai.com/v1",
    "Groq": "https://api.groq.com/openai/v1",
    "OpenRouter": "https://openrouter.ai/api/v1",
    "Together AI": "https://api.together.xyz/v1",
    "Custom OpenAI-compatible API": ""
}

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("## 🎓 CampusBuddy")
    st.caption("Your student-life co-pilot")
    st.markdown("---")
    st.markdown("### AI provider settings")
    provider = st.selectbox("Choose API provider", list(PROVIDERS.keys()), index=0)
    default_base = PROVIDERS[provider]
    base_url = st.text_input("API Base URL", value=default_base,
                             placeholder="https://your-provider.com/v1",
                             help="For Custom, enter the provider's OpenAI-compatible API endpoint.")
    env_key = os.getenv("AI_API_KEY") or os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    api_key = st.text_input("API key", value=env_key, type="password",
                            placeholder="Paste your provider API key")
    default_model = os.getenv("AI_MODEL", "grok-4.7" if provider == "xAI (Grok)" else "")
    model = st.text_input("Model name", value=default_model,
                          placeholder="Enter the exact model ID from your provider")
    st.caption("Your key is used for this session and is not written into app.py.")
    st.markdown("---")
    st.markdown("**What CampusBuddy can do**")
    st.markdown("- Explain academic concepts\n- Draft emails to faculty\n- Plan study schedules\n- Guide projects and placement preparation\n- Answer general campus questions")
    st.markdown("---")
    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("""
<div class="hero">
  <h1>🎓 CampusBuddy AI</h1>
  <p>A smart campus assistant that turns confusing student questions into clear, actionable next steps.</p>
  <span class="pill">Multi-provider AI</span><span class="pill">Context-aware chat</span><span class="pill">Student-focused</span>
</div>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """You are CampusBuddy, a friendly, reliable AI assistant for college students.
Help with academics, campus life, projects, internships, placements and communication.
Explain in simple student-friendly language, using examples and numbered steps when useful.
For study plans, make realistic schedules with breaks and measurable tasks.
Never invent college-specific rules, deadlines, fees, contacts, events or policies; say when information must be verified.
For technical help, provide working code and explain how to run it.
Be encouraging, clear and concise. Distinguish confirmed facts from suggestions.
"""

if not api_key.strip():
    st.info("Choose an AI provider in the sidebar and paste its API key to start chatting.")
elif not base_url.strip():
    st.info("Enter the API Base URL for the selected provider.")
elif not model.strip():
    st.info("Enter the exact model name supported by your selected provider.")
else:
    client = OpenAI(api_key=api_key.strip(), base_url=base_url.strip().rstrip("/") + "/")

    if not st.session_state.messages:
        st.markdown("### Try asking")
        prompts = [
            "Make me a 7-day Python interview preparation plan.",
            "Explain generative AI like I'm presenting it to my lecturer.",
            "Suggest a unique final-year AI project with modules.",
            "Write a polite email asking my professor for project feedback."
        ]
        cols = st.columns(2)
        for i, prompt in enumerate(prompts):
            if cols[i % 2].button(prompt, key=f"prompt_{i}", use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🎓"):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask CampusBuddy anything about college, learning or your career…")
    if not user_prompt and st.session_state.get("pending_prompt"):
        user_prompt = st.session_state.pop("pending_prompt")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar="🎓"):
            placeholder = st.empty()
            try:
                completion = client.chat.completions.create(
                    model=model.strip(),
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                    temperature=0.7,
                    max_tokens=1600,
                )
                answer = completion.choices[0].message.content or "The provider returned an empty response. Please try again."
                placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                placeholder.error("The selected AI provider could not complete the request.")
                st.error(f"Error details: {exc}")
                st.info("Check the API key, base URL, model ID, account credits and whether the provider supports the OpenAI-compatible Chat Completions endpoint.")
                # Remove failed user turn so it is not resent as part of the next request.
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()

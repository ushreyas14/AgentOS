"""
streamlit_app.py
────────────────
A Streamlit web interface for the Multi-Agent Productivity System.

Run:
    streamlit run streamlit_app.py
"""

import asyncio
from typing import AsyncGenerator
import os
from uuid import uuid4

import streamlit as st

# --- Dependency Check ---
def _check_dependencies() -> None:
    """Checks for required packages and displays an error if any are missing."""
    missing = []
    # Assuming google-adk is installed via `pip install google-adk`
    # which might not register a top-level `google.adk` module directly
    # in a way `__import__` can easily find without the rest of google-cloud.
    # A more robust check might be needed if issues persist.
    for pkg in ["google.generativeai", "google.adk", "streamlit"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    if missing:
        st.error(
            f"Missing packages: {', '.join(missing)}. "
            "Please run: pip install -r requirements.txt"
        )
        st.stop()

_check_dependencies()

# --- ADK Imports ---
from config import GEMINI_MODEL
from coordinator import coordinator
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.generativeai import types as genai_types


# --- Async Helper ---
async def stream_message(
    runner: Runner, session_id: str, user_id: str, message: str
) -> AsyncGenerator[str, None]:
    """Sends a message to the coordinator and streams the reply text."""
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=message)])

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.author == "model" and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    yield part.text


# --- App ---
st.set_page_config(page_title="Multi-Agent System", page_icon="🤖")
st.title("🤖 Multi-Agent Productivity System")

# --- API Key Check ---
google_api_key = st.secrets.get("GOOGLE_API_KEY")
if not google_api_key:
    st.error("🚨 GOOGLE_API_KEY not found in Streamlit secrets!")
    st.info(
        "Please add the GOOGLE_API_KEY to your Streamlit secrets to run this app. "
        "You can get a key from the Google AI Studio."
    )
    st.code("GOOGLE_API_KEY='your-api-key-here'", language="toml")
    st.stop()
# Set the environment variable for ADK/GenAI library if it expects it from os.environ
os.environ["GOOGLE_API_KEY"] = google_api_key
st.caption(f"Powered by Google ADK + {GEMINI_MODEL}")

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    if st.button("New Chat"):
        # Re-initialize the session for a fresh start
        with st.spinner("Initializing new chat..."):
            runner, session_id, user_id = asyncio.run(initialize_session())
            st.session_state.runner = runner
            st.session_state.session_id = session_id
            st.session_state.user_id = user_id
            st.session_state.messages = []
        st.rerun()

# --- Session State Initialization ---
async def initialize_session():
    """Initializes the ADK runner and session for the Streamlit app."""
    session_service = InMemorySessionService()
    app_name = "productivity_assistant_streamlit"
    user_id = "user_" + str(uuid4())
    session_id = "session_" + str(uuid4())

    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    return Runner(agent=coordinator, app_name=app_name, session_service=session_service), session_id, user_id

if "runner" not in st.session_state:
    with st.spinner("Initializing agents..."):
        runner, session_id, user_id = asyncio.run(initialize_session())
        st.session_state.runner = runner
        st.session_state.session_id = session_id
        st.session_state.user_id = user_id
        st.session_state.messages = []

# --- Chat UI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_generator = stream_message(st.session_state.runner, st.session_state.session_id, st.session_state.user_id, prompt)
        response = st.write_stream(response_generator)

    st.session_state.messages.append({"role": "assistant", "content": response})
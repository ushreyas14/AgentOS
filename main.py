"""
main.py
───────
Entry point for the Multi-Agent Productivity System.

Run:
    python main.py

The script demonstrates three scenarios:
  1. Single-agent call  — add a task via the coordinator
  2. Multi-step workflow — add task + set reminder + save note (all in one message)
  3. Interactive mode    — user types their own requests
"""

import os
import sys
import asyncio

# ── Dependency guard ──────────────────────────────────────────────────────────
def _check_dependencies() -> None:
    missing = []
    for pkg in ["google.adk", "google.generativeai"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    if missing:
        print("[ERROR] Missing packages:", ", ".join(missing))
        print("        Run:  pip install -r requirements.txt")
        sys.exit(1)

_check_dependencies()

# ── ADK imports ───────────────────────────────────────────────────────────────
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.generativeai import types as genai_types

from coordinator import coordinator
from config import GEMINI_MODEL


# ═══════════════════════════════════════════════════════════════════════════════
# Core helper — send one message to the coordinator and return its reply
# ═══════════════════════════════════════════════════════════════════════════════

async def send_message(
    runner: Runner,
    session_id: str,
    user_id: str,
    message: str,
) -> str:
    """
    Send a message to the coordinator and collect the full reply text.

    Args:
        runner:     ADK Runner bound to the coordinator agent.
        session_id: Unique session identifier (keeps conversation context).
        user_id:    Unique user identifier.
        message:    The user's natural-language request.

    Returns:
        The coordinator's reply as a plain string.
    """
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )
    reply_parts: list[str] = []

    # run_async streams events; we collect every text part from the agent
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        # ADK emits different event types; we only care about agent text output
        if event.is_final_response():
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    reply_parts.append(part.text)

    return "\n".join(reply_parts) or "(no reply)"


# ═══════════════════════════════════════════════════════════════════════════════
# Demo scenarios
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_single_step(runner: Runner, session_id: str, user_id: str) -> None:
    """Demo 1 — simple single-agent task."""
    print("\n" + "─" * 60)
    print("  DEMO 1 — Single-step: Add a task")
    print("─" * 60)
    msg = "Add a high-priority task: 'Prepare project presentation'"
    print(f"\n  👤 You: {msg}\n")
    reply = await send_message(runner, session_id, user_id, msg)
    print(f"  🤖 Agent: {reply}\n")


async def demo_multi_step(runner: Runner, session_id: str, user_id: str) -> None:
    """Demo 2 — multi-step workflow spanning all three sub-agents."""
    print("\n" + "─" * 60)
    print("  DEMO 2 — Multi-step workflow (Task + Calendar + Notes)")
    print("─" * 60)
    msg = (
        "Please do three things for me: "
        "1) Add a task 'Review Q3 report' with high priority. "
        "2) Set a reminder 'Q3 Review Meeting' for 2025-09-01 at 10:00. "
        "3) Save a note titled 'Q3 Key Findings' with content "
        "'Revenue up 12%, costs down 5%, new markets in APAC' and tag it 'work'."
    )
    print(f"\n  👤 You: {msg}\n")
    reply = await send_message(runner, session_id, user_id, msg)
    print(f"  🤖 Agent: {reply}\n")


async def demo_retrieval(runner: Runner, session_id: str, user_id: str) -> None:
    """Demo 3 — retrieve data previously stored by sub-agents."""
    print("\n" + "─" * 60)
    print("  DEMO 3 — Retrieval: list tasks, reminders, and notes")
    print("─" * 60)
    msg = "Show me all my tasks, upcoming reminders, and work-tagged notes."
    print(f"\n  👤 You: {msg}\n")
    reply = await send_message(runner, session_id, user_id, msg)
    print(f"  🤖 Agent: {reply}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Interactive REPL
# ═══════════════════════════════════════════════════════════════════════════════

async def interactive_mode(runner: Runner, session_id: str, user_id: str) -> None:
    """Let the user type their own requests in a simple REPL."""
    print("\n" + "═" * 60)
    print("  INTERACTIVE MODE  (type 'quit' or 'exit' to stop)")
    print("═" * 60)
    while True:
        try:
            user_input = input("\n  👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Goodbye! 👋")
            break
        if user_input.lower() in {"quit", "exit", "q"}:
            print("\n  Goodbye! 👋")
            break
        if not user_input:
            continue
        reply = await send_message(runner, session_id, user_id, user_input)
        print(f"\n  🤖 Agent: {reply}")


# ═══════════════════════════════════════════════════════════════════════════════
# Bootstrap
# ═══════════════════════════════════════════════════════════════════════════════

async def main() -> None:
    # ── API key check ─────────────────────────────────────────────────────────
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("\n[ERROR] GOOGLE_API_KEY is not set.")
        print("        Run test_api.py first to diagnose your setup.")
        sys.exit(1)

    # ── ADK session + runner setup ────────────────────────────────────────────
    # InMemorySessionService keeps conversation history within this process.
    session_service = InMemorySessionService()
    APP_NAME   = "productivity_assistant"
    USER_ID    = "user_001"
    SESSION_ID = "session_001"

    # Create the session (one session = one conversation thread)
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # Runner ties the coordinator agent to the session service
    runner = Runner(
        agent=coordinator,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ── Banner ────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  MULTI-AGENT PRODUCTIVITY SYSTEM")
    print(f"  Powered by Google ADK + {GEMINI_MODEL}")
    print("═" * 60)
    print("  Agents: coordinator → task | calendar | notes")

    # ── Run pre-built demos ───────────────────────────────────────────────────
    # Add a delay between demos to avoid hitting potential rate limits with
    # burst requests.
    await demo_single_step(runner, SESSION_ID, USER_ID)
    await asyncio.sleep(2)
    await demo_multi_step(runner, SESSION_ID, USER_ID)
    await asyncio.sleep(2)
    await demo_retrieval(runner, SESSION_ID, USER_ID)

    # ── Drop into interactive mode ────────────────────────────────────────────
    await interactive_mode(runner, SESSION_ID, USER_ID)


if __name__ == "__main__":
    asyncio.run(main())
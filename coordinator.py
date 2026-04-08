"""
coordinator.py
──────────────
Makes exactly ONE Gemini API call per user message.
Returns a structured JSON action plan for the executor.
"""

import os
import json
import google.api_core.exceptions as api_exceptions
import google.genai as genai

from config import GEMINI_MODEL

_SYSTEM_PROMPT = """You are a coordinator for a productivity assistant with three agents:

1. task_agent    — manages tasks
   Tools: add_task(title, priority), list_tasks(), mark_task_done(task_id), delete_task(task_id)

2. calendar_agent — manages reminders
   Tools: set_reminder(title, date, time), list_reminders(), delete_reminder(event_id)

3. notes_agent   — manages notes
   Tools: save_note(title, content, tag), list_notes(tag), search_notes(keyword), delete_note(note_id)

Given the user's message, return ONLY a valid JSON array of actions to execute.
Each action: {"agent": "agent_name", "tool": "tool_name", "args": {...}}

Examples:
User: "Add a task buy groceries"
[{"agent":"task_agent","tool":"add_task","args":{"title":"Buy groceries","priority":"medium"}}]

User: "show all tasks and reminders"
[{"agent":"task_agent","tool":"list_tasks","args":{}},{"agent":"calendar_agent","tool":"list_reminders","args":{}}]

User: "Add high priority task finish report, set reminder for 2025-08-01 at 10:00, save note Meeting prep with content prepare slides tagged work"
[
  {"agent":"task_agent","tool":"add_task","args":{"title":"Finish report","priority":"high"}},
  {"agent":"calendar_agent","tool":"set_reminder","args":{"title":"Finish report deadline","date":"2025-08-01","time":"10:00"}},
  {"agent":"notes_agent","tool":"save_note","args":{"title":"Meeting prep","content":"Prepare slides","tag":"work"}}
]

Return ONLY the JSON array. No markdown, no explanation, no extra text."""


def plan(user_message: str, api_key: str) -> list[dict]:
    """
    Single Gemini API call — returns action plan as list of dicts.
    """
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config={"system_instruction": _SYSTEM_PROMPT},
        )
        raw = response.text.strip()

        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            actions = json.loads(raw)
            return actions if isinstance(actions, list) else []
        except json.JSONDecodeError:
            # Log the raw response that caused the JSON error for debugging
            print(f"Warning: Gemini API returned non-JSON response: {raw}")
            return []
    except api_exceptions.NotFound as e:
        print(f"Error: Gemini model '{GEMINI_MODEL}' not found or is inaccessible.")
        print("Please verify the model name in 'config.py' and ensure it's available for your API key and region.")
        print(f"Original error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during Gemini API call: {e}")
        return []
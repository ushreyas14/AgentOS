"""
agents/calendar_agent.py
────────────────────────
Calendar Agent — manages reminders and scheduled events.
Each function simulates an MCP tool call to a calendar backend.
"""

from google.adk.agents import Agent


# ── Simulated MCP Tool Store ──────────────────────────────────────────────────
_event_store: list[dict] = []


# ── Tool Functions ────────────────────────────────────────────────────────────

def set_reminder(title: str, date: str, time: str = "09:00") -> dict:
    """
    MCP-style tool: Create a reminder/event.

    Args:
        title: What the reminder is about.
        date:  Date string, e.g. '2025-08-15'.
        time:  24-hour time string, e.g. '14:30'  (default: 09:00)

    Returns:
        Dict with status and the created event object.
    """
    event = {
        "id": len(_event_store) + 1,
        "title": title,
        "date": date,
        "time": time,
        "reminded": False,
    }
    _event_store.append(event)
    return {"status": "created", "event": event}


def list_reminders() -> dict:
    """
    MCP-style tool: List all scheduled reminders.

    Returns:
        Dict with the event list and total count.
    """
    return {"events": _event_store, "total": len(_event_store)}


def delete_reminder(event_id: int) -> dict:
    """
    MCP-style tool: Remove a reminder by ID.

    Args:
        event_id: Integer ID of the event to delete.

    Returns:
        Confirmation dict or an error message.
    """
    global _event_store
    before = len(_event_store)
    _event_store = [e for e in _event_store if e["id"] != event_id]
    if len(_event_store) < before:
        return {"status": "deleted", "event_id": event_id}
    return {"status": "error", "message": f"Event {event_id} not found"}


# ── Agent Definition ──────────────────────────────────────────────────────────

calendar_agent = Agent(
    name="calendar_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Manages the user's calendar and reminders. "
        "Can set reminders, list upcoming events, and delete reminders."
    ),
    instruction=(
        "You are a helpful calendar assistant. "
        "When asked to set or add a reminder, call set_reminder with the title, date, and time. "
        "When asked to show upcoming events or reminders, call list_reminders. "
        "When asked to remove or delete a reminder, call delete_reminder with the event ID. "
        "If the user doesn't give a time, default to 09:00. "
        "Always confirm every action with the event details."
    ),
    tools=[set_reminder, list_reminders, delete_reminder],
)
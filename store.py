"""
store.py
────────
Shared in-memory stores for all agents.
All reads/writes are pure Python — zero API calls.
Uses Streamlit session_state so data persists across reruns.
"""

import streamlit as st


def _init():
    """Initialize stores in session state if not already present."""
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "events" not in st.session_state:
        st.session_state.events = []
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "api_call_count" not in st.session_state:
        st.session_state.api_call_count = 0


# ── Task tools ────────────────────────────────────────────────────────────────

def add_task(title: str, priority: str = "medium") -> dict:
    _init()
    task = {
        "id": len(st.session_state.tasks) + 1,
        "title": title,
        "priority": priority,
        "done": False,
    }
    st.session_state.tasks.append(task)
    return {"status": "created", "task": task}


def list_tasks() -> dict:
    _init()
    return {"tasks": st.session_state.tasks, "total": len(st.session_state.tasks)}


def mark_task_done(task_id: int) -> dict:
    _init()
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["done"] = True
            return {"status": "updated", "task": t}
    return {"status": "error", "message": f"Task {task_id} not found"}


def delete_task(task_id: int) -> dict:
    _init()
    before = len(st.session_state.tasks)
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    if len(st.session_state.tasks) < before:
        return {"status": "deleted", "task_id": task_id}
    return {"status": "error", "message": f"Task {task_id} not found"}


# ── Calendar tools ────────────────────────────────────────────────────────────

def set_reminder(title: str, date: str, time: str = "09:00") -> dict:
    _init()
    event = {
        "id": len(st.session_state.events) + 1,
        "title": title,
        "date": date,
        "time": time,
    }
    st.session_state.events.append(event)
    return {"status": "created", "event": event}


def list_reminders() -> dict:
    _init()
    return {"events": st.session_state.events, "total": len(st.session_state.events)}


def delete_reminder(event_id: int) -> dict:
    _init()
    before = len(st.session_state.events)
    st.session_state.events = [e for e in st.session_state.events if e["id"] != event_id]
    if len(st.session_state.events) < before:
        return {"status": "deleted", "event_id": event_id}
    return {"status": "error", "message": f"Event {event_id} not found"}


# ── Notes tools ───────────────────────────────────────────────────────────────

def save_note(title: str, content: str, tag: str = "general") -> dict:
    _init()
    note = {
        "id": len(st.session_state.notes) + 1,
        "title": title,
        "content": content,
        "tag": tag,
    }
    st.session_state.notes.append(note)
    return {"status": "saved", "note": note}


def list_notes(tag: str = "") -> dict:
    _init()
    notes = (
        [n for n in st.session_state.notes if n["tag"] == tag]
        if tag
        else st.session_state.notes
    )
    return {"notes": notes, "total": len(notes)}


def search_notes(keyword: str) -> dict:
    _init()
    kw = keyword.lower()
    matches = [
        n for n in st.session_state.notes
        if kw in n["title"].lower() or kw in n["content"].lower()
    ]
    return {"matches": matches, "total": len(matches)}


def delete_note(note_id: int) -> dict:
    _init()
    before = len(st.session_state.notes)
    st.session_state.notes = [n for n in st.session_state.notes if n["id"] != note_id]
    if len(st.session_state.notes) < before:
        return {"status": "deleted", "note_id": note_id}
    return {"status": "error", "message": f"Note {note_id} not found"}
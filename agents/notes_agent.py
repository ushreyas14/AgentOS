"""
agents/notes_agent.py
─────────────────────
Notes Agent — saves, lists, searches, and deletes quick notes.
Each function simulates an MCP tool call to a notes backend.
"""

from google.adk.agents import Agent


# ── Simulated MCP Tool Store ──────────────────────────────────────────────────
_notes_store: list[dict] = []


# ── Tool Functions ────────────────────────────────────────────────────────────

def save_note(title: str, content: str, tag: str = "general") -> dict:
    """
    MCP-style tool: Save a new note.

    Args:
        title:   Short title for the note.
        content: Full note body / content.
        tag:     Category tag, e.g. 'work', 'idea', 'meeting' (default: general)

    Returns:
        Dict with status and the saved note object.
    """
    note = {
        "id": len(_notes_store) + 1,
        "title": title,
        "content": content,
        "tag": tag,
    }
    _notes_store.append(note)
    return {"status": "saved", "note": note}


def list_notes(tag: str = "") -> dict:
    """
    MCP-style tool: List all notes, optionally filtered by tag.

    Args:
        tag: If provided, only return notes with this tag.

    Returns:
        Dict with the note list and total count.
    """
    notes = (
        [n for n in _notes_store if n["tag"] == tag]
        if tag
        else _notes_store
    )
    return {"notes": notes, "total": len(notes)}


def search_notes(keyword: str) -> dict:
    """
    MCP-style tool: Search notes by keyword in title or content.

    Args:
        keyword: Word or phrase to search for.

    Returns:
        Dict with matching notes.
    """
    kw = keyword.lower()
    matches = [
        n for n in _notes_store
        if kw in n["title"].lower() or kw in n["content"].lower()
    ]
    return {"matches": matches, "total": len(matches)}


def delete_note(note_id: int) -> dict:
    """
    MCP-style tool: Delete a note by ID.

    Args:
        note_id: Integer ID of the note to delete.

    Returns:
        Confirmation dict or an error message.
    """
    global _notes_store
    before = len(_notes_store)
    _notes_store = [n for n in _notes_store if n["id"] != note_id]
    if len(_notes_store) < before:
        return {"status": "deleted", "note_id": note_id}
    return {"status": "error", "message": f"Note {note_id} not found"}


# ── Agent Definition ──────────────────────────────────────────────────────────

notes_agent = Agent(
    name="notes_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Manages the user's notes. "
        "Can save notes with tags, list notes, search by keyword, and delete notes."
    ),
    instruction=(
        "You are a smart notes assistant. "
        "When asked to save or create a note, call save_note with title, content, and an appropriate tag. "
        "When asked to show or list notes, call list_notes (optionally filter by tag). "
        "When asked to search notes, call search_notes with the keyword. "
        "When asked to delete a note, call delete_note with the note ID. "
        "Always summarise the note content in your confirmation reply."
    ),
    tools=[save_note, list_notes, search_notes, delete_note],
)
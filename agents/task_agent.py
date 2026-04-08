"""
agents/task_agent.py
────────────────────
Task Agent — manages a simple in-memory to-do list.
Each function below simulates an MCP tool call (like calling a real server).
"""

from google.adk.agents import Agent
from config import GEMINI_MODEL


# ── Simulated MCP Tool Store ──────────────────────────────────────────────────
# In a real system this would be a database or actual MCP server.
_task_store: list[dict] = []


# ── Tool Functions ────────────────────────────────────────────────────────────

def add_task(title: str, priority: str = "medium") -> dict:
    """
    MCP-style tool: Add a new task.

    Args:
        title:    Short description of the task.
        priority: 'low' | 'medium' | 'high'  (default: medium)

    Returns:
        Dict with status and the created task object.
    """
    task = {
        "id": len(_task_store) + 1,
        "title": title,
        "priority": priority,
        "done": False,
    }
    _task_store.append(task)
    return {"status": "created", "task": task}


def list_tasks() -> dict:
    """
    MCP-style tool: Return every task in the store.

    Returns:
        Dict with the task list and total count.
    """
    return {"tasks": _task_store, "total": len(_task_store)}


def mark_task_done(task_id: int) -> dict:
    """
    MCP-style tool: Mark a task as completed by ID.

    Args:
        task_id: Integer ID of the task.

    Returns:
        Updated task dict or an error message.
    """
    for task in _task_store:
        if task["id"] == task_id:
            task["done"] = True
            return {"status": "updated", "task": task}
    return {"status": "error", "message": f"Task {task_id} not found"}


# ── Agent Definition ──────────────────────────────────────────────────────────

task_agent = Agent(
    name="task_agent",
    model=GEMINI_MODEL,
    description=(
        "Manages the user's task list. "
        "Can add tasks, list all tasks, and mark tasks as done."
    ),
    instruction=(
        "You are a friendly task manager. "
        "When asked to add a task, call add_task with title and priority. "
        "When asked to list tasks, call list_tasks. "
        "When asked to complete a task, call mark_task_done with the task ID. "
        "Always confirm every action clearly and concisely."
    ),
    tools=[add_task, list_tasks, mark_task_done],
)
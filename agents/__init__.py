"""agents package — exposes all sub-agents for the coordinator."""

from agents.task_agent import task_agent
from agents.calendar_agent import calendar_agent
from agents.notes_agent import notes_agent

__all__ = ["task_agent", "calendar_agent", "notes_agent"]
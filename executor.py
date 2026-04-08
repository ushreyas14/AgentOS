"""
executor.py
───────────
Executes the coordinator's action plan in pure Python.
Zero API calls.
"""

import store

TOOL_REGISTRY = {
    ("task_agent",     "add_task"):        store.add_task,
    ("task_agent",     "list_tasks"):      store.list_tasks,
    ("task_agent",     "mark_task_done"):  store.mark_task_done,
    ("task_agent",     "delete_task"):     store.delete_task,
    ("calendar_agent", "set_reminder"):    store.set_reminder,
    ("calendar_agent", "list_reminders"):  store.list_reminders,
    ("calendar_agent", "delete_reminder"): store.delete_reminder,
    ("notes_agent",    "save_note"):       store.save_note,
    ("notes_agent",    "list_notes"):      store.list_notes,
    ("notes_agent",    "search_notes"):    store.search_notes,
    ("notes_agent",    "delete_note"):     store.delete_note,
}


def execute(actions: list[dict]) -> list[dict]:
    """Run each action from the plan. Returns list of result dicts."""
    results = []
    for action in actions:
        agent = action.get("agent", "")
        tool  = action.get("tool", "")
        args  = action.get("args", {})
        fn    = TOOL_REGISTRY.get((agent, tool))

        if fn is None:
            results.append({
                "agent": agent, "tool": tool,
                "result": {"status": "error", "message": f"Unknown: {agent}.{tool}"},
            })
            continue

        try:
            result = fn(**args)
        except TypeError as e:
            result = {"status": "error", "message": f"Bad args for {tool}: {e}"}
        except Exception as e:
            result = {"status": "error", "message": str(e)}

        results.append({"agent": agent, "tool": tool, "result": result})
    return results


def format_results(results: list[dict]) -> str:
    """Format execution results into human-readable text."""
    if not results:
        return "No actions were taken."

    lines = []
    for r in results:
        agent  = r["agent"].replace("_", " ").title()
        tool   = r["tool"]
        result = r["result"]
        status = result.get("status", "ok")

        if tool == "add_task" and status == "created":
            t = result["task"]
            lines.append(f"✅ **[{agent}]** Task #{t['id']} added: *{t['title']}* ({t['priority']} priority)")

        elif tool == "list_tasks":
            tasks = result.get("tasks", [])
            if not tasks:
                lines.append(f"📋 **[{agent}]** No tasks yet.")
            else:
                lines.append(f"📋 **[{agent}]** {result['total']} task(s):")
                for t in tasks:
                    done = "~~" if t["done"] else ""
                    end  = "~~" if t["done"] else ""
                    lines.append(f"  - {'✓' if t['done'] else '○'} #{t['id']} [{t['priority']}] {done}{t['title']}{end}")

        elif tool == "mark_task_done" and status == "updated":
            t = result["task"]
            lines.append(f"✅ **[{agent}]** Task #{t['id']} *{t['title']}* marked done.")

        elif tool == "delete_task" and status == "deleted":
            lines.append(f"🗑️ **[{agent}]** Task #{result['task_id']} deleted.")

        elif tool == "set_reminder" and status == "created":
            e = result["event"]
            lines.append(f"📅 **[{agent}]** Reminder #{e['id']} set: *{e['title']}* — {e['date']} at {e['time']}")

        elif tool == "list_reminders":
            events = result.get("events", [])
            if not events:
                lines.append(f"📅 **[{agent}]** No reminders yet.")
            else:
                lines.append(f"📅 **[{agent}]** {result['total']} reminder(s):")
                for e in events:
                    lines.append(f"  - #{e['id']} *{e['title']}* — {e['date']} {e['time']}")

        elif tool == "delete_reminder" and status == "deleted":
            lines.append(f"🗑️ **[{agent}]** Reminder #{result['event_id']} deleted.")

        elif tool == "save_note" and status == "saved":
            n = result["note"]
            lines.append(f"📝 **[{agent}]** Note #{n['id']} saved: *{n['title']}* [#{n['tag']}]")

        elif tool == "list_notes":
            notes = result.get("notes", [])
            if not notes:
                lines.append(f"📝 **[{agent}]** No notes yet.")
            else:
                lines.append(f"📝 **[{agent}]** {result['total']} note(s):")
                for n in notes:
                    lines.append(f"  - #{n['id']} [#{n['tag']}] *{n['title']}*: {n['content'][:80]}")

        elif tool == "search_notes":
            matches = result.get("matches", [])
            if not matches:
                lines.append(f"🔍 **[{agent}]** No notes found.")
            else:
                lines.append(f"🔍 **[{agent}]** {result['total']} match(es):")
                for n in matches:
                    lines.append(f"  - #{n['id']} *{n['title']}*: {n['content'][:80]}")

        elif tool == "delete_note" and status == "deleted":
            lines.append(f"🗑️ **[{agent}]** Note #{result['note_id']} deleted.")

        elif status == "error":
            lines.append(f"❌ **[{agent}]** Error in `{tool}`: {result.get('message', 'unknown')}")

        else:
            lines.append(f"ℹ️ **[{agent}]** `{tool}` completed.")

    return "\n".join(lines)
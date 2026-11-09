"""
Matin — Personal Assistant MCP Server for Muse AI
Developed by firoze vafadari
"""
import os

# Support both mcp v1 (mcp.server.fastmcp) and v2 (fastmcp package)
FastMCP = None
_last_error = None
for _import_path in ("mcp.server.fastmcp", "fastmcp"):
    try:
        if _import_path == "mcp.server.fastmcp":
            from mcp.server.fastmcp import FastMCP as _F
        else:
            from fastmcp import FastMCP as _F
        FastMCP = _F
        break
    except ImportError as e:
        _last_error = e

if FastMCP is None:
    raise SystemExit(f"Missing dependency. Run: pip install -r requirements.txt (import error: {_last_error})")

PORT = int(os.environ.get("PORT", "8000"))

try:
    mcp = FastMCP("Matin", host="0.0.0.0", port=PORT)
except TypeError:
    mcp = FastMCP("Matin")


def _parse_tasks(text: str) -> list[str]:
    if not text:
        return []
    parts = []
    for chunk in text.replace(";", "\n").split("\n"):
        for piece in chunk.split(","):
            piece = piece.strip(" -•\t")
            if piece:
                parts.append(piece)
    return parts


@mcp.tool()
def make_todo_list(tasks: str, focus: str = "programming") -> str:
    """
    Make a prioritized to-do list from the user's tasks.
    Use this when the user asks for a to-do list, e.g.
    'Make my programming job to-do list for today'.
    Args:
        tasks: Tasks separated by commas or new lines.
        focus: Main focus area, e.g. 'programming', 'work', 'personal'.
    """
    items = _parse_tasks(tasks)
    if not items:
        return "No tasks provided. Please list the tasks you want in your to-do list."
    lines = [f"Your {focus} to-do list for today:", ""]
    for i, task in enumerate(items, 1):
        lines.append(f"{i}. {task}  — start with the smallest first step")
    lines += ["", "Tip: Do the hardest task first, then check items off one by one."]
    return "\n".join(lines)


@mcp.tool()
def plan_day(goals: str, available_hours: float = 8) -> str:
    """
    Plan the user's day from their goals.
    Use this when the user asks 'Plan my day' or 'What should I do today?'.
    Args:
        goals: Goals separated by commas or new lines.
        available_hours: Hours available today (default 8).
    """
    items = _parse_tasks(goals)
    if not items:
        return "No goals provided. Tell me what you want to achieve today."
    block = max(0.5, round(available_hours / max(len(items), 1), 1))
    lines = [f"Your plan for today ({available_hours}h available):", ""]
    for i, goal in enumerate(items, 1):
        lines.append(f"Block {i} (~{block}h): {goal}")
    lines += ["", "Tip: Add a 10-minute break between blocks and review at the end of the day."]
    return "\n".join(lines)


@mcp.tool()
def prioritize_tasks(tasks: str) -> str:
    """
    Prioritize tasks by urgency and importance keywords.
    Use this when the user asks to prioritize or rank their tasks.
    Args:
        tasks: Tasks separated by commas or new lines.
    """
    items = _parse_tasks(tasks)
    if not items:
        return "No tasks provided. Please list the tasks you want prioritized."

    def score(task: str) -> int:
        t = task.lower()
        s = 0
        if any(w in t for w in ("urgent", "asap", "deadline", "today", "فوری")):
            s += 3
        if any(w in t for w in ("important", "must", "مهم")):
            s += 2
        if any(w in t for w in ("bug", "fix", "error", "fail")):
            s += 1
        return s

    ranked = sorted(items, key=score, reverse=True)
    lines = ["Your tasks, prioritized:", ""]
    for i, task in enumerate(ranked, 1):
        tag = " 🔴 high" if score(task) >= 3 else (" 🟡 medium" if score(task) >= 1 else " 🟢 normal")
        lines.append(f"{i}. {task}{tag}")
    return "\n".join(lines)


@mcp.tool()
def daily_checkin(completed: str, tomorrow_goals: str = "") -> str:
    """
    Summarize what the user completed and suggest tomorrow's focus.
    Use this for an end-of-day review.
    Args:
        completed: What the user finished today.
        tomorrow_goals: Goals for tomorrow (optional).
    """
    done = _parse_tasks(completed)
    lines = ["Daily check-in:", ""]
    if done:
        lines.append("✅ Completed today:")
        lines += [f"  - {d}" for d in done]
    else:
        lines.append("No completed tasks listed yet — that's okay, note one win!")
    nxt = _parse_tasks(tomorrow_goals)
    if nxt:
        lines += ["", "🎯 Tomorrow's focus:"]
        lines += [f"  {i}. {g}" for i, g in enumerate(nxt, 1)]
    lines += ["", "Great job showing up. Rest well and start fresh tomorrow!"]
    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Matin MCP server...", flush=True)
    try:
        mcp.run(transport="streamable-http")
    except Exception:
        # fastmcp v2 uses "http" instead of "streamable-http"
        mcp.run(transport="http")

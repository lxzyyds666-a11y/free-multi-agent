import json
from pathlib import Path

from llm import ask_json
from prompts import PLANNER_PROMPT

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_planner():
    mission = (STATE / "mission.md").read_text(encoding="utf-8")
    backlog = load_json(STATE / "backlog.json", {"tasks": [], "next_task_id": 1})
    done = load_json(STATE / "done.json", {"items": []})

    open_tasks = [t for t in backlog["tasks"] if t["status"] in ("todo", "revise")]
    if open_tasks:
        return {"skipped": True, "reason": "Open tasks already exist"}

    user_prompt = f"""
mission:
{mission}

backlog:
{json.dumps(backlog, ensure_ascii=False)}

done:
{json.dumps(done, ensure_ascii=False)}

请生成最多 3 个新的最小任务。
"""

    result = ask_json(PLANNER_PROMPT, user_prompt)
    new_tasks = result.get("new_tasks", [])

    for task in new_tasks:
        task["id"] = backlog["next_task_id"]
        backlog["next_task_id"] += 1
        task["status"] = "todo"

    backlog["tasks"].extend(new_tasks)
    save_json(STATE / "backlog.json", backlog)

    return {"skipped": False, "created": len(new_tasks), "note": result.get("planning_note", "")}

import json
from pathlib import Path

from llm import ask_json
from prompts import WORKER_PROMPT

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_task(backlog):
    for task in backlog["tasks"]:
        if task["status"] in ("todo", "revise"):
            return task
    return None


def run_worker():
    mission = (STATE / "mission.md").read_text(encoding="utf-8")
    backlog = load_json(STATE / "backlog.json", {"tasks": [], "next_task_id": 1})
    done = load_json(STATE / "done.json", {"items": []})

    task = pick_task(backlog)
    if not task:
        return {"skipped": True, "reason": "No task to work on"}

    user_prompt = f"""
mission:
{mission}

task:
{json.dumps(task, ensure_ascii=False)}

existing_done:
{json.dumps(done, ensure_ascii=False)}

请执行这个任务，并输出结构化 JSON。
"""

    result = ask_json(WORKER_PROMPT, user_prompt)

    task["status"] = "done_pending_review"
    task["worker_output"] = result

    save_json(STATE / "backlog.json", backlog)
    return {"skipped": False, "task_id": task["id"], "summary": result.get("summary", "")}

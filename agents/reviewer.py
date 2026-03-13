import json
from pathlib import Path

from llm import ask_json
from prompts import REVIEWER_PROMPT

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def find_review_target(backlog):
    for task in backlog["tasks"]:
        if task["status"] == "done_pending_review":
            return task
    return None


def run_reviewer():
    backlog = load_json(STATE / "backlog.json", {"tasks": [], "next_task_id": 1})
    done = load_json(STATE / "done.json", {"items": []})
    review_log = load_json(STATE / "review_log.json", {"items": []})

    task = find_review_target(backlog)
    if not task:
        return {"skipped": True, "reason": "No completed task awaiting review"}

    user_prompt = f"""
task:
{json.dumps(task, ensure_ascii=False)}

请审查 worker_output，并输出 JSON。
"""

    review = ask_json(REVIEWER_PROMPT, user_prompt)
    decision = review.get("decision", "defer")

    review_entry = {
        "task_id": task["id"],
        "decision": decision,
        "review": review,
    }
    review_log["items"].append(review_entry)

    if decision == "approve":
        task["status"] = "approved"
        done["items"].append({
            "task_id": task["id"],
            "title": task["title"],
            "worker_output": task.get("worker_output", {}),
            "review": review,
        })
    elif decision == "revise":
        task["status"] = "revise"
        task["review_feedback"] = review.get("fixes", [])
    else:
        task["status"] = "deferred"
        task["review_feedback"] = review.get("fixes", [])

    save_json(STATE / "backlog.json", backlog)
    save_json(STATE / "done.json", done)
    save_json(STATE / "review_log.json", review_log)

    return {"skipped": False, "task_id": task["id"], "decision": decision}

import json
from datetime import datetime, timezone
from pathlib import Path

from planner import run_planner
from worker import run_worker
from reviewer import run_reviewer

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"
LOGS = ROOT / "logs"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    LOGS.mkdir(exist_ok=True)

    planner_result = run_planner()
    worker_result = run_worker()
    reviewer_result = run_reviewer()

    now = datetime.now(timezone.utc).isoformat()

    heartbeat = load_json(STATE / "heartbeat.json", {
        "runs": 0,
        "last_run_utc": None,
        "status": "idle",
    })
    heartbeat["runs"] += 1
    heartbeat["last_run_utc"] = now
    heartbeat["status"] = "ok"

    cycle_log = {
        "time_utc": now,
        "planner": planner_result,
        "worker": worker_result,
        "reviewer": reviewer_result,
    }

    save_json(STATE / "heartbeat.json", heartbeat)
    save_json(LOGS / f"{now.replace(':', '-')}.json", cycle_log)

    print(json.dumps(cycle_log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

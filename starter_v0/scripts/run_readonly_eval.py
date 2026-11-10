"""Run the normal eval with real research tools but Telegram publishing disabled.

Accepts the same CLI arguments as run_eval.py. Timing metadata is added without
changing cases, tool decisions, grading, or the original summary.
"""
from pathlib import Path
import argparse
import json
import os
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run_eval


def main():
    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    os.environ.pop("TELEGRAM_CHAT_ID", None)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    config, _ = parser.parse_known_args()
    runs_dir = config.runs_dir
    before = set(runs_dir.glob("*.json"))
    started = monotonic()
    evaluate = run_eval.evaluate_phase_b

    def evaluate_with_progress(case, calls, text):
        result = evaluate(case, calls, text)
        verdict = "PASS" if result["passed"] else "FAIL"
        details = "; ".join(result["failures"])
        print(f"  {case['id']}: {verdict} {details}", flush=True)
        return result

    run_eval.evaluate_phase_b = evaluate_with_progress
    try:
        run_eval.main()
    finally:
        run_eval.evaluate_phase_b = evaluate
    created = set(runs_dir.glob("*.json")) - before
    if len(created) == 1:
        path = created.pop()
        data = json.loads(path.read_text(encoding="utf-8"))
        data["execution_metadata"] = {
            "duration_seconds": round(monotonic() - started, 2),
            "telegram_publishing": "disabled_for_eval",
            "research_tools": "live",
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Elapsed: {data['execution_metadata']['duration_seconds']}s", flush=True)


if __name__ == "__main__":
    main()

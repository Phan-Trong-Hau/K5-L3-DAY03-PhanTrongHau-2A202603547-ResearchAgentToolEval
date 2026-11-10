"""Export cloud/local comparison tables directly from saved eval JSONs."""
import csv
import json
from collections import Counter
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    runs = []
    for path in sorted((ROOT / "runs").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["version"].startswith("v3-local-") or data["version"] in ("v4-local", "v5-local", "v5-local-cloud") or (data["version"] == "v3" and data["provider"] == "openrouter" and data["suite"] == "base"):
            runs.append((path, data))
    output = ROOT / "analysis"
    output.mkdir(exist_ok=True)
    fields = ["version", "provider", "model", "cases", "measured", "passed", "case_accuracy", "tool_routing_accuracy",
              "argument_accuracy", "multiturn_accuracy", "provider_errors", "invalid_json_cases", "missing_tool_cases",
              "extra_tool_cases", "no_call_cases", "unknown_tool_calls", "duplicate_tool_cases", "wrong_tool_cases", "tool_errors", "duration_seconds", "prompt_hash", "tools_hash", "run_file"]
    with (output / "local_eval_comparison.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fields, lineterminator="\n")
        writer.writeheader()
        for path, run in runs:
            summary = run["summary"]
            results = run["results"]
            invalid = sum(any("_invalid_json_arguments" in c.get("args", {}) for c in r["result"]["actual_tool_calls"]) for r in results)
            failures = [r["result"].get("failures", []) for r in results]
            artifact_path = ROOT / run["tools"]
            if not artifact_path.exists():
                # Historical cloud evidence records its author's Windows path.
                artifact_path = ROOT / "artifacts/versions/v3/tools.yaml"
            declared = {t["name"] for t in yaml.safe_load(artifact_path.read_text())["tools"]}
            calls = [r["result"]["actual_tool_calls"] for r in results]
            errors = [e for r in results for e in r.get("tool_results", []) if e.get("result", e).get("error")]
            writer.writerow({"version": run["version"], "provider": run["provider"], "model": run["model"],
                "cases": summary["total_cases"], "measured": summary["measured_cases"], "passed": summary["passed_cases"],
                **{k: summary[k] for k in ("case_accuracy", "tool_routing_accuracy", "argument_accuracy", "multiturn_accuracy")},
                "provider_errors": summary["provider_error_cases"], "invalid_json_cases": invalid,
                "missing_tool_cases": sum(any("missing tool call" in s for s in row) for row in failures),
                "extra_tool_cases": sum(any("extra tool call" in s or "expected no tool" in s for s in row) for row in failures),
                "no_call_cases": sum(bool(r["expect"].get("tool_calls")) and not r["result"]["actual_tool_calls"] for r in results),
                "unknown_tool_calls": sum(c["name"] not in declared for row in calls for c in row),
                "duplicate_tool_cases": sum(any(count > 1 for count in Counter(c["name"] for c in row).values()) for row in calls),
                "wrong_tool_cases": sum(r["result"].get("failure_type") == "wrong_tool" for r in results),
                "tool_errors": len(errors), "duration_seconds": run.get("execution_metadata", {}).get("duration_seconds", ""),
                "prompt_hash": run["prompt_hash"], "tools_hash": run["tools_hash"], "run_file": str(path.relative_to(ROOT))})
    with (output / "local_eval_failures.csv").open("w", newline="", encoding="utf-8") as file:
        fields = ["version", "model", "case_id", "passed", "observed_mismatch", "calls", "failures"]
        writer = csv.DictWriter(file, fields, lineterminator="\n")
        writer.writeheader()
        for _, run in runs:
            for result in run["results"]:
                row = result["result"]
                writer.writerow({"version": run["version"], "model": run["model"], "case_id": result["id"],
                    "passed": row["passed"], "observed_mismatch": row.get("observed_mismatch"),
                    "calls": json.dumps(row["actual_tool_calls"], ensure_ascii=False),
                    "failures": "; ".join(row["failures"])})
    for path, run in runs:
        print(f"{run['version']} | {run['provider']}/{run['model']} | {run['summary']['passed_cases']}/{run['summary']['total_cases']} | {path.name}")


if __name__ == "__main__":
    main()

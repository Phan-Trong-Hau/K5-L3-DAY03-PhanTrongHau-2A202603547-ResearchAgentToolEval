"""Versioned prompt/tool artifacts and their recorded eval evidence."""
import json
from pathlib import Path

from versioning import build_artifact_version

ROOT = Path(__file__).resolve().parent


def load_versions(root: Path = ROOT) -> dict:
    versions = {}
    for metadata_path in sorted((root / "artifacts/versions").glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        folder = metadata_path.parent
        prompt_path, tools_path = folder / "system_prompt.md", folder / "tools.yaml"
        artifact = build_artifact_version(metadata["version"], prompt_path, tools_path)
        if artifact.prompt_hash != metadata["prompt_hash"] or artifact.tools_hash != metadata["tools_hash"]:
            raise ValueError(f"Snapshot {metadata['version']} không khớp hash đã lưu.")
        versions[metadata["version"]] = {**metadata, "prompt_path": prompt_path, "tools_path": tools_path}
    return versions


def load_run(version: dict, root: Path = ROOT, suite: str = "base") -> dict:
    if suite not in ("base", "group"):
        raise ValueError("Unknown eval suite")
    run_file = version.get("group_run_file") if suite == "group" else version["run_file"]
    if not run_file:
        raise ValueError(f"{version['version']} chưa có run {suite}.")
    run = json.loads((root / run_file).read_text(encoding="utf-8"))
    if run["version"] != version.get("run_version", version["version"]):
        raise ValueError("Run version không khớp snapshot")
    if run["suite"] != suite or run.get("dataset_role") != suite:
        raise ValueError("Run evidence dùng sai dataset/suite")
    for key in ("prompt_hash", "tools_hash"):
        if run[key] != version[key]:
            raise ValueError(f"Run evidence không khớp snapshot: {key}")
    return run


def compare_cases(before: dict, after: dict, before_label: str | None = None, after_label: str | None = None) -> list[dict]:
    before_rows = {row["id"]: row for row in before["results"]}
    after_rows = {row["id"]: row for row in after["results"]}
    if set(before_rows) != set(after_rows):
        raise ValueError("Hai run cần dùng cùng bộ case để so sánh.")
    for field in ("provider", "model", "dataset_id"):
        if before.get(field) != after.get(field):
            raise ValueError(f"Hai run cần cùng {field} để so sánh.")
    before_label = before_label or before.get("version", "Trước")
    after_label = after_label or after.get("version", "Sau")
    if before_label == after_label:
        raise ValueError("Chọn hai phiên bản khác nhau.")
    rows = []
    for case_id, old in before_rows.items():
        new = after_rows[case_id]
        if old["expect"] != new["expect"]:
            raise ValueError(f"Expected của case {case_id} đã thay đổi.")
        passed_before, passed_after = old["result"]["passed"], new["result"]["passed"]
        change = "Đã sửa" if not passed_before and passed_after else "Regression" if passed_before and not passed_after else "Giữ nguyên pass" if passed_after else "Còn lỗi"
        rows.append({"Case": case_id, "Loại": "Multi-turn" if old["is_multiturn"] else "Single-turn",
                     before_label: "PASS" if passed_before else "FAIL", after_label: "PASS" if passed_after else "FAIL", "Thay đổi": change})
    return rows

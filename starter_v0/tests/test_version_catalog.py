import shutil

import pytest

from tools import load_tool_declarations
from version_catalog import ROOT, compare_cases, load_run, load_versions


def test_snapshots_match_their_recorded_runs():
    versions = load_versions()
    assert set(versions) == {"v0", "v1", "v2", "v3"}
    for name, version in versions.items():
        assert load_run(version)["version"] == version.get("run_version", name)
    before = {tool["name"] for tool in load_tool_declarations(versions["v0"]["tools_path"])}
    after = {tool["name"] for tool in load_tool_declarations(versions["v1"]["tools_path"])}
    assert after - before == {"github_repos"}


def test_comparison_retains_improvements_and_regression():
    versions = load_versions()
    rows = compare_cases(load_run(versions["v0"]), load_run(versions["v1"]))
    assert len(rows) == 20
    assert sum(row["Thay đổi"] == "Đã sửa" for row in rows) == 5
    assert sum(row["Thay đổi"] == "Regression" for row in rows) == 1
    assert next(row for row in rows if row["Case"] == "M06_switch_tool")["v1"] == "FAIL"


def test_modified_snapshot_is_rejected(tmp_path):
    shutil.copytree(ROOT / "artifacts/versions", tmp_path / "artifacts/versions")
    (tmp_path / "artifacts/versions/v0/system_prompt.md").write_text("changed")
    with pytest.raises(ValueError, match="không khớp hash"):
        load_versions(tmp_path)


def test_different_case_sets_are_not_compared():
    with pytest.raises(ValueError, match="cùng bộ case"):
        compare_cases({"results": []}, {"results": [{"id": "other"}]})


def test_v2_v3_group_uses_member_runs_and_retains_remaining_failure():
    versions = load_versions()
    before = load_run(versions["v2"], suite="group")
    after = load_run(versions["v3"], suite="group")
    assert before["version"] == "v2-openrouter-vietduc"
    assert before["summary"]["passed_cases"] == 8
    assert after["summary"]["passed_cases"] == 9
    rows = compare_cases(before, after, "v2", "v3")
    assert len(rows) == 10
    assert sum(row["Thay đổi"] == "Đã sửa" for row in rows) == 1
    assert next(row for row in rows if row["Case"] == "G08_multiturn_switch_to_github")["v3"] == "FAIL"


def test_missing_group_evidence_does_not_fall_back_to_base():
    with pytest.raises(ValueError, match="chưa có run group"):
        load_run(load_versions()["v0"], suite="group")


def test_comparison_rejects_different_models():
    versions = load_versions()
    before, after = load_run(versions["v2"]), load_run(versions["v3"])
    after["model"] = "different-model"
    with pytest.raises(ValueError, match="cùng model"):
        compare_cases(before, after, "v2", "v3")


def test_comparison_rejects_changed_expectations():
    versions = load_versions()
    before, after = load_run(versions["v2"]), load_run(versions["v3"])
    after["results"][0]["expect"] = {"no_tool": True}
    with pytest.raises(ValueError, match="Expected"):
        compare_cases(before, after, "v2", "v3")

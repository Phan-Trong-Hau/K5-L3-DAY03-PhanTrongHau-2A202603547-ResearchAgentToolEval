import shutil

import pytest

from tools import load_tool_declarations
from version_catalog import ROOT, compare_cases, load_run, load_versions


def test_snapshots_match_their_recorded_runs():
    versions = load_versions()
    assert set(versions) == {"v0", "v1"}
    for name, version in versions.items():
        assert load_run(version)["version"] == name
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

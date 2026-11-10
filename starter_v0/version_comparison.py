"""Read-only comparison of member-provided eval runs and artifact snapshots."""
import difflib
import json

import streamlit as st

from version_catalog import compare_cases, load_run

METRICS = [("Case accuracy", "case_accuracy"), ("Tool routing", "tool_routing_accuracy"),
           ("Arguments", "argument_accuracy"), ("Multi-turn", "multiturn_accuracy")]


def render_comparison(versions):
    st.title("So sánh các phiên bản")
    base_runs = {name: load_run(version) for name, version in versions.items()}
    reference = next(iter(base_runs.values()))
    st.caption(f"Kết quả eval đã lưu của nhóm · {reference['provider']} · {reference['model']}. Điểm này không đại diện cho các model khác.")
    overview = []
    columns = st.columns(len(versions))
    for column, (name, run) in zip(columns, base_runs.items()):
        summary = run["summary"]
        column.metric(name, f"{summary['case_accuracy']:.0%}", help=f"{summary['passed_cases']}/{summary['measured_cases']} case base")
        group_run = load_run(versions[name], suite="group") if versions[name].get("group_run_file") else None
        overview.append({"Version": name, "Base đúng": f"{summary['passed_cases']}/{summary['measured_cases']}",
                         **{label: f"{summary[key]:.2%}" for label, key in METRICS},
                         "Group đúng": f"{group_run['summary']['passed_cases']}/{group_run['summary']['measured_cases']}" if group_run else "Chưa đo"})
    st.dataframe(overview, hide_index=True)
    st.caption("Base dùng cùng 20 case. Group v2/v3 dùng cùng 10 case; v0/v1 chưa có run group trong catalog.")

    st.subheader("Đối chiếu hai phiên bản")
    names = list(versions)
    left, right = st.columns(2)
    with left:
        before_name = st.selectbox("Phiên bản trước", names, index=max(0, len(names)-2), key="compare_before")
    after_names = [name for name in names if name != before_name]
    with right:
        after_name = st.selectbox("Phiên bản sau", after_names, index=len(after_names)-1, key="compare_after")
    suites = ["base"]
    if all(versions[name].get("group_run_file") for name in (before_name, after_name)):
        suites.append("group")
    suite = st.radio("Bộ eval", suites, format_func=lambda value: "Base · 20 case" if value == "base" else "Group · 10 case", horizontal=True, key="compare_suite")
    before, after = [load_run(versions[name], suite=suite) for name in (before_name, after_name)]
    try:
        rows = compare_cases(before, after, before_name, after_name)
    except ValueError as exc:
        st.error(str(exc))
        return
    old, new = before["summary"], after["summary"]
    st.dataframe([{"Metric": label, before_name: f"{old[key]:.2%}", after_name: f"{new[key]:.2%}",
                   "Chênh lệch (điểm %)": round((new[key]-old[key])*100, 2)} for label, key in METRICS], hide_index=True)
    fixed = sum(row["Thay đổi"] == "Đã sửa" for row in rows)
    regressed = sum(row["Thay đổi"] == "Regression" for row in rows)
    remaining = sum(row["Thay đổi"] == "Còn lỗi" for row in rows)
    st.caption(f"{fixed} case được sửa · {regressed} regression · {remaining} case còn lỗi")

    st.subheader("Kết quả từng case")
    only_changes = st.checkbox("Chỉ hiện case đã sửa, regression hoặc còn lỗi", value=True)
    filtered = [row for row in rows if not only_changes or row["Thay đổi"] != "Giữ nguyên pass"]
    if filtered:
        st.dataframe(filtered, hide_index=True)
    else:
        st.success("Các case đều giữ nguyên PASS.")
    ids = [row["Case"] for row in rows]
    default_case = filtered[0]["Case"] if filtered else ids[0]
    selected = st.selectbox("Xem chi tiết case", ids, index=ids.index(default_case), key=f"detail_{before_name}_{after_name}_{suite}")
    columns = st.columns(2)
    for column, name, run in zip(columns, (before_name, after_name), (before, after)):
        row = next(row for row in run["results"] if row["id"] == selected)
        with column:
            st.markdown(f"**{name} · {'PASS' if row['result']['passed'] else 'FAIL'}**")
            st.write(row.get("input", ""))
            st.json({"expected": row["expect"], "actual_tool_calls": row["result"]["actual_tool_calls"],
                     "failures": row["result"]["failures"], "answer": row["result"].get("actual_text")}, expanded=True)

    with st.expander("Thay đổi prompt và khai báo tool"):
        prompt_tab, tool_tab = st.tabs(["System prompt", "Tool declaration"])
        for tab, path_key in [(prompt_tab, "prompt_path"), (tool_tab, "tools_path")]:
            first, second = [versions[name][path_key].read_text(encoding="utf-8") for name in (before_name, after_name)]
            diff = "\n".join(difflib.unified_diff(first.splitlines(), second.splitlines(), fromfile=before_name, tofile=after_name, lineterm=""))
            with tab:
                if diff:
                    st.code(diff, language="diff")
                else:
                    st.caption("Nội dung không thay đổi.")
        st.caption("Version so sánh prompt và khai báo tool; các phiên chat chạy implementation tool hiện tại của ứng dụng.")
    with st.expander("Bằng chứng eval"):
        for name, run in [(before_name, before), (after_name, after)]:
            st.markdown(f"**{name} · {suite}** · {run['generated_at']}")
            st.caption(f"Run label: {run['version']} · {versions[name].get('run_author', 'Nhóm')}")
            st.code(run["artifact_version"])
            file_key = "group_run_file" if suite == "group" else "run_file"
            st.download_button(f"Tải run JSON {name} · {suite}", data=json.dumps(run, ensure_ascii=False, indent=2),
                               file_name=versions[name][file_key].split("/")[-1], mime="application/json")

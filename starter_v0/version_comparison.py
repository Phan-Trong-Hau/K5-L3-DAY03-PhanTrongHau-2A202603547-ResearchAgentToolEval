import difflib
import json

import streamlit as st

from version_catalog import compare_cases, load_run


def render_comparison(versions):
    st.title("So sánh v0 và v1")
    before, after = load_run(versions["v0"]), load_run(versions["v1"])
    st.caption(f"Eval đã lưu · {before['provider']} · {before['model']} · cùng 20 case base. Điểm này không đại diện cho các model khác.")
    old, new = before["summary"], after["summary"]
    columns = st.columns(3)
    columns[0].metric("v0 · case đúng", f"{old['passed_cases']}/{old['measured_cases']}")
    columns[1].metric("v1 · case đúng", f"{new['passed_cases']}/{new['measured_cases']}")
    columns[2].metric("Case accuracy v1", f"{new['case_accuracy']:.0%}", f"{(new['case_accuracy']-old['case_accuracy'])*100:+.0f} điểm %")
    metrics = [("Case accuracy", "case_accuracy"), ("Tool routing", "tool_routing_accuracy"),
               ("Arguments", "argument_accuracy"), ("Multi-turn", "multiturn_accuracy")]
    st.dataframe([{"Metric": label, "v0": f"{old[key]:.2%}", "v1": f"{new[key]:.2%}",
                   "Chênh lệch (điểm %)": round((new[key]-old[key])*100, 2)} for label, key in metrics],
                 hide_index=True)
    st.caption("v1 sửa 5 case, phát sinh 1 regression. Multi-turn giảm từ 100% xuống 83,33%.")

    st.subheader("Kết quả từng case")
    rows = compare_cases(before, after)
    only_changes = st.checkbox("Chỉ hiện case đã sửa, regression hoặc còn lỗi", value=True)
    st.dataframe([row for row in rows if not only_changes or row["Thay đổi"] != "Giữ nguyên pass"],
                 hide_index=True)
    ids = [row["Case"] for row in rows]
    selected = st.selectbox("Xem chi tiết case", ids, index=ids.index("R10_missing_handle"))
    left, right = st.columns(2)
    for column, label, run in [(left, "v0", before), (right, "v1", after)]:
        row = next(row for row in run["results"] if row["id"] == selected)
        with column:
            st.markdown(f"**{label} · {'PASS' if row['result']['passed'] else 'FAIL'}**")
            st.write(row.get("input", ""))
            st.json({"expected": row["expect"], "actual_tool_calls": row["result"]["actual_tool_calls"],
                     "failures": row["result"]["failures"], "answer": row["result"].get("actual_text")}, expanded=True)

    with st.expander("Thay đổi prompt và danh sách tool"):
        first, second = [versions[name]["prompt_path"].read_text(encoding="utf-8") for name in ("v0", "v1")]
        st.code("\n".join(difflib.unified_diff(first.splitlines(), second.splitlines(), fromfile="v0", tofile="v1", lineterm="")), language="diff")
        st.caption("v1 thêm github_repos; các version so sánh prompt và khai báo tool, sử dụng implementation tool hiện tại của ứng dụng.")
    with st.expander("Bằng chứng eval"):
        for name, run in [("v0", before), ("v1", after)]:
            st.markdown(f"**{name}** · {run['generated_at']}")
            st.code(run["artifact_version"])
            st.download_button(f"Tải run JSON {name}", data=json.dumps(run, ensure_ascii=False, indent=2),
                               file_name=versions[name]["run_file"].split("/")[-1], mime="application/json")

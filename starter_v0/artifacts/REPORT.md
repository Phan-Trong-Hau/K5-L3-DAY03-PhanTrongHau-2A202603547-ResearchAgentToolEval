# Research Agent Tool Eval — Nhóm 3 miền

## Team

| Thành viên | MSSV | Phụ trách |
|---|---|---|
| Vũ Lê Hoàng | 2A202603542 | v0, setup và baseline |
| Ngô Đức Thịnh | 2A202603548 | v1, prompt và eval single-turn |
| Bùi Gia Huy | 2A202603525 | v2, tool declaration và eval multi-turn |
| Lưu Văn Việt Đức | 2A202603445 | v3, tool mới và unit test |
| Phan Trọng Hậu | 2A202603547 | UI, report, bonus và local model |

**Model dùng để so sánh v0–v1:** `openai/gpt-4o-mini` qua OpenRouter. Bộ đo: `data/eval_base.json`, phase B, 20 case gồm 14 single-turn và 6 multi-turn.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent hỗ trợ tìm tin trên web và X/Twitter, đọc URL, tìm paper arXiv, tra cứu policy nội bộ và tìm repository GitHub. Agent chọn tool theo yêu cầu, chạy tool thật và tổng hợp nội dung; khi thiếu tài khoản hoặc URL, bản v1 hỏi lại thay vì tự đoán.

**UI:** Streamlit, chạy local tại `http://localhost:8501`. Chạy `./run_ui.sh` trên Linux/macOS hoặc `.\run_ui.bat` trên Windows. Link public chưa được triển khai.

## A2. Tool agent có

| Tool | Chức năng | Nhóm tự thêm |
|---|---|---|
| `clarify` | Hỏi thêm thông tin hoặc yêu cầu xác nhận | Không |
| `timeline` | Lấy bài đăng theo tài khoản X/Twitter | Không |
| `social_search` | Tìm bài đăng theo từ khóa, Top/Latest | Không |
| `lookup` | Tìm kiếm web, lọc loại tin và thời gian | Không |
| `fetch` | Đọc nội dung URL | Không |
| `format` | Trình bày dữ liệu thành digest | Không |
| `send` | Gửi nội dung Telegram khi có xác nhận và cấu hình bot | Không |
| `policy` | Tra cứu policy markdown nội bộ | Không |
| `papers` | Tìm paper arXiv | Không |
| `paper_text` | Tải PDF arXiv và trích xuất văn bản | Không |
| `github_repos` | Tìm repository GitHub theo chủ đề, ngôn ngữ và stars/forks/updated | Có, thêm ở v1 |

## A3. Câu hỏi mẫu để thử

1. “Lấy 3 bài đăng gần đây của tài khoản sama.”
2. “Tìm tin về AI trong hôm nay trên web và các bài đăng liên quan trên Twitter.”
3. “Đọc https://example.com và tóm tắt bằng tiếng Việt.”
4. “Tìm 5 repository GitHub về RAG viết bằng Python, sắp xếp theo số sao.”
5. “Tóm tắt bài viết này giúp mình.” — khi chưa có URL, agent cần hỏi lại.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

### Kết quả v0–v1

Nguồn chính là hai run được ghi trong [version_log.csv](version_log.csv). Mỗi run OpenRouter đo đủ 20 case và không có provider error.

| Version | Phụ trách | Thay đổi / giả thuyết | Case accuracy trước → sau | Run |
|---|---|---|---|---|
| v0 | Hoàng | Baseline: đo ảnh hưởng của prompt khuyến khích đoán thông tin, tự hành động và ép hoàn thành một bước | — → 65% | [v0 OpenRouter](../runs/v0_B_base_openrouter_20261110T104306962524.json) |
| v1 | Thịnh | Thay các chỉ dẫn trên bằng quy tắc scope, hỏi lại, xác nhận và routing; đồng thời thêm `github_repos` vào declaration/registry | 65% → 85% | [v1 OpenRouter](../runs/v1_B_base_openrouter_20261110T105632499545.json) |

| Metric | v0 | v1 | Chênh lệch |
|---|---:|---:|---:|
| Case đúng / tổng | 13/20 | 17/20 | +4 case |
| `case_accuracy` | 65% | 85% | +20 điểm phần trăm |
| `tool_routing_accuracy` | 75% | 95% | +20 điểm phần trăm |
| `argument_accuracy` | 65% | 85% | +20 điểm phần trăm |
| Single-turn đúng / tổng | 7/14 (50%) | 12/14 (85,71%) | +5 case |
| `multiturn_accuracy` | 6/6 (100%) | 5/6 (83,33%) | −1 case; −16,67 điểm phần trăm |
| Provider error | 0 | 0 | Không đổi |

v1 sửa được 5 case, giữ nguyên 12 case pass và 2 case fail, nhưng làm 1 case từ pass thành fail. Tổng số case fail giảm từ 7 xuống 3. [Bảng đối chiếu đủ 20 case](../analysis/v0_v1_case_comparison.csv).

Một [lần chạy lại v1](../runs/v1_B_base_openrouter_20261110T110008921339.json) dùng cùng model và cùng hash cũng đạt 17/20; ba case fail vẫn là R03, R13 và M06. Đây là bằng chứng lặp lại trong hai run đã có, chưa phải đánh giá thống kê qua nhiều lần chạy.

### Thay đổi cụ thể ở v1

- `system_prompt.md`: thêm ranh giới phạm vi; trả lời câu hỏi về năng lực không cần tool; không dùng `send` để trả lời chat thông thường.
- Thiếu handle hoặc URL: gọi `clarify(response_type="text")`, không tự chọn `sama` hoặc bịa URL.
- Yêu cầu gửi Telegram chưa xác nhận: gọi `clarify(response_type="yes_no")`.
- Bổ sung routing cho tài khoản, tìm theo từ khóa, web, URL, paper, policy và GitHub; cho phép gọi nhiều tool khi yêu cầu cần nhiều nguồn.
- `tools.yaml`: thêm declaration `github_repos`. Diff v1 **không viết lại description của toàn bộ tool cũ**.
- Thêm implementation, `TOOL.md`, registry và 3 test cho `github_repos` trong commit [`45756e3`](https://github.com/Phan-Trong-Hau/K5-L3-DAY03-PhanTrongHau-2A202603547-ResearchAgentToolEval/commit/45756e304566371f032993e0603e9d43e9a15b08).

**Giới hạn kết luận:** v1 thay nhiều quy tắc và thêm tool cùng lúc, nên số liệu chứng minh hiệu quả của cả gói thay đổi; chưa tách được mức đóng góp của từng rule hoặc của tool mới. Base eval không có case `github_repos`, vì vậy 85% không chứng minh routing tới tool mới đã đúng.

### Hash và khả năng đối chiếu

| Version | `artifact_version` trong run | Prompt hash (12 ký tự đầu) | Tools hash (12 ký tự đầu) |
|---|---|---|---|
| v0 | `v0+peb1c8179815b+t5b22a2476d41` | `eb1c8179815b` | `5b22a2476d41` |
| v1 | `v1+p0f969bd7fd2e+t707c6c5df8ec` | `0f969bd7fd2e` | `707c6c5df8ec` |

Run JSON giữ hash SHA-256 đầy đủ; version log hiện lưu prefix 12 ký tự. Đã đối chiếu với nội dung Git: v0 khớp prompt/tools ở parent của commit `45756e3` khi dùng CRLF; v1 khớp prompt LF và tools CRLF ở commit này. Do hàm hash tính trên byte, checkout LF trên Linux có thể cho hash khác dù nội dung văn bản giống nhau.

### Lần thử Gemini ở v0

[Run Gemini](../runs/v0_B_base_gemini_20261110T103545490529.json) dùng `gemini-3-flash-preview`: 10/19 case đo được, case accuracy 52,63%, routing 63,16%, argument 52,63%, multi-turn 80% (4/5). Case M06 bị provider error HTTP 429 `RESOURCE_EXHAUSTED` do quota, nên harness loại khỏi mẫu số metric. Không dùng run này để tính mức cải thiện v0 → v1 vì khác provider/model và số case đo được.

## B2. Failure Analysis

Các lỗi dưới đây lấy từ `actual_tool_calls`, `failures` và `observed_mismatch` trong run chính v0/v1.

| Case | Lỗi quan sát | v0 thực tế | v1 thực tế | Kết luận / hướng sửa |
|---|---|---|---|---|
| R03 `web_news_routing` | `wrong_arg_value` | `lookup(query="AI news", topic="news", timeframe="day")` | Vẫn cùng lỗi query | Tool đúng; expected `query="AI"`. Cần chuẩn hóa query và tách ý thời gian/loại tin sang args tương ứng. |
| R08 `out_of_scope` | `unexpected_tool_call` | Dùng `send` chứa lời giải nguyên hàm | Không gọi tool; từ chối giải toán | Đã sửa ranh giới scope và phân biệt trả lời chat với publish. |
| R10 `missing_handle` | `missing_tool_call` | Tự gọi `timeline(screenname="sama")` | `clarify(response_type="text")` hỏi tài khoản | Đã sửa việc tự đoán handle. |
| R11 `missing_url` | `missing_tool_call` | Tự gọi `fetch(url="https://example.com/article")` | `clarify(response_type="text")` hỏi URL | Đã sửa việc tự đoán URL. |
| R12 `confirm_before_send` | `missing_tool_call` | Gọi `send(text="Bản tin này")` ngay | `clarify(response_type="yes_no")` hỏi xác nhận | Đã sửa quyết định ở tầng model. |
| R13 `parallel_web_and_tweets` | `wrong_arg_value` | Có cả `lookup` và `social_search`, nhưng lookup dùng `query="AI news"`, thiếu `topic` | Vẫn hai lỗi args đó | Không phải thiếu tool; expected `query="AI"`, `topic="news"`. Bổ sung convention arguments. |
| R14 `out_of_scope_coding` | `unexpected_tool_call` | Dùng `send` chứa code Fibonacci | Không gọi tool; từ chối viết code | Đã sửa ranh giới scope. |
| M06 `switch_tool` | `extra_tool_call` ở v1 | Chỉ `lookup(query="OpenAI", topic="news")`, pass | Gọi thêm `social_search(query="OpenAI", search_type="Top")` bên cạnh lookup | Regression: đã yêu cầu bỏ Twitter nhưng agent vẫn giữ nguồn cũ. Cần ưu tiên chỉ dẫn chuyển nguồn mới nhất. |

**Phân loại lỗi:** trường `failure_type` giữ nhãn của case; vì vậy summary v1 ghi 3 lỗi `wrong_tool`, nhưng thực tế R03 và R13 là **sai giá trị arguments**, chỉ M06 là **gọi thừa tool**. Phân tích dùng `observed_mismatch` để tránh sửa nhầm routing.

**Ranh giới gửi tin:** ở v0, cả R08, R12 và R14 gọi nhầm `send`, nhưng kết quả tool là `status="needs_confirmation"`; log không chứng minh tin đã được gửi. v1 sửa việc lựa chọn tool, còn guard ở code là lớp kiểm soát riêng.

## B3. Team Eval Cases

`data/eval_group.json` hiện chưa có case. Phần eval nhóm 10 case (5 single-turn + 5 multi-turn), gồm case routing cho `github_repos`, sẽ bổ sung khi có dữ liệu và group run.

## B4. Live Chat Evidence

[Bản chụp demo UI](../transcripts/evidence/ui_demo_20261110.transcript.json) có 4 lượt với Ollama `qwen2.5:7b`, version `ui-demo`: chào hỏi, hỏi tool, tìm tin ngày 10/11/2026 và tìm tin giá vàng. Hai lượt tra cứu có gọi `lookup` và nhận kết quả thật. Đây là bằng chứng UI/live chat riêng, không phải run eval của v0 hoặc v1 OpenRouter.

## B5. Tool mới và UI

- `github_repos`: có [code](../tools/github_repos/tool.py), [TOOL.md](../tools/github_repos/TOOL.md), declaration/registry và 3 test trong [test_tools_todo.py](../tests/test_tools_todo.py). Chưa có group eval chứng minh model route đúng tới tool mới.
- UI Streamlit: [app.py](../app.py), [hướng dẫn](../UI.md); hỗ trợ local/cloud, lịch sử chat, transcript và tiến trình xử lý.
- Chưa có bằng chứng gửi Telegram thật trong các run v0/v1.

## B6. Reflection từ v0–v1

**Sửa gì trong system prompt?** Quy tắc hành vi chung: khi nào hỏi lại, khi nào trả lời không dùng tool, xác nhận trước khi publish và cách chọn nguồn theo yêu cầu. Năm case được sửa cho thấy agent giảm tự đoán và giảm dùng action tool sai mục đích.

**Sửa gì trong tool declaration?** Convention của từng đối số, nhất là `lookup.query`, `topic` và `timeframe`. R03/R13 đã chọn đúng tool nhưng vẫn fail, nên chỉ bổ sung routing là chưa đủ.

**Lỗi nào cần xem thủ công?** Query “AI news” có thể vẫn tìm được tin phù hợp nhưng không khớp expected “AI”; evaluator chỉ so giá trị sau strip/lowercase, không chấm tương đương ngữ nghĩa. Cần ghi nhận fail theo bộ đo và xem thêm chất lượng kết quả, không sửa expected để làm tăng điểm. Với case `no_tool`, harness kiểm tra không có tool call, chưa tự đánh giá đầy đủ chất lượng lời từ chối; đã đọc câu trả lời R08/R14 để xác nhận hành vi. Tương tự, routing pass không bảo đảm nguồn và bản tóm tắt đúng.

**Ưu tiên vòng tiếp theo:** chuẩn hóa arguments ở R03/R13; sửa carry-over nguồn của M06 khi user nói bỏ Twitter; thêm group case cho tool mới và giữ các case đã sửa khỏi regression. Mỗi vòng tiếp theo nên kiểm chứng một thay đổi có phạm vi rõ ràng.

## B7. Small Local Model Challenge

Chưa có base eval của hai model local hoặc log tối ưu `v4-local`/`v5-local`. Preflight/chat local hiện có chưa đủ bằng chứng để kết luận hoàn thành challenge.

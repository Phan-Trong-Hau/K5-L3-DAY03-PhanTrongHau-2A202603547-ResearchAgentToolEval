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
| `extract_links` | Trích URL HTTP/HTTPS từ văn bản/Markdown có sẵn, giữ thứ tự, khử trùng và giới hạn kết quả; chạy offline | Có, Việt Đức bổ sung sau khi nộp v3 (`v3-extract-links`) |

## A3. Câu hỏi mẫu để thử

1. “Lấy 3 bài đăng gần đây của tài khoản sama.”
2. “Tìm tin về AI trong hôm nay trên web và các bài đăng liên quan trên Twitter.”
3. “Đọc https://example.com và tóm tắt bằng tiếng Việt.”
4. “Tìm 5 repository GitHub về RAG viết bằng Python, sắp xếp theo số sao.”
5. “Tóm tắt bài viết này giúp mình.” — khi chưa có URL, agent cần hỏi lại.

Câu thử cho phần bổ sung sau khi nộp v3 (`v3-extract-links`):

6. “Chỉ trích URL trong đoạn sau, không tìm web hoặc đọc trang: Sources: [https://example.com/a](https://example.com/a) and [https://example.org/b](https://example.org/b)”
7. “Liệt kê tối đa 1 URL duy nhất từ ghi chú này: https://example.com/a, <https://example.org/b>, https://example.com/a.” — trả 1 item, tổng 2 URL duy nhất, `truncated=true`.

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

Run JSON giữ hash SHA-256 đầy đủ; Các dòng v0–v1 trong version log lưu prefix 12 ký tự; bốn dòng v2 đối chiếu và v3 được bổ sung sử dụng hash đầy đủ từ run JSON. Đã đối chiếu với nội dung Git: v0 khớp prompt/tools ở parent của commit `45756e3` khi dùng CRLF; v1 khớp prompt LF và tools CRLF ở commit này. Do hàm hash tính trên byte, checkout LF trên Linux có thể cho hash khác dù nội dung văn bản giống nhau.

### Lần thử Gemini ở v0

[Run Gemini](../runs/v0_B_base_gemini_20261110T103545490529.json) dùng `gemini-3-flash-preview`: 10/19 case đo được, case accuracy 52,63%, routing 63,16%, argument 52,63%, multi-turn 80% (4/5). Case M06 bị provider error HTTP 429 `RESOURCE_EXHAUSTED` do quota, nên harness loại khỏi mẫu số metric. Không dùng run này để tính mức cải thiện v0 → v1 vì khác provider/model và số case đo được.

### Kết quả v2–v3

**Vấn đề:** V2 còn gọi Twitter khi người dùng chỉ yêu cầu tin web, hoặc sau khi người dùng đã chuyển sang nguồn khác.

**Giả thuyết:** Agent chưa xác định rõ yêu cầu và nguồn còn hiệu lực qua các lượt hội thoại. Nếu prompt yêu cầu giữ thông tin chưa bị thay đổi, loại yêu cầu đã hủy và chỉ chọn các nguồn đang được yêu cầu, số lần gọi thừa/sai tool sẽ giảm.

**Thay đổi:** Trong `artifacts/system_prompt.md`, thay quy tắc Parallel tool calls bằng mục **Active Request and Source Selection**. Mục này quy định:

- Kế thừa chủ đề, thời gian, tài khoản, URL và số lượng khi chúng vẫn còn hiệu lực.
- Yêu cầu đổi nguồn hoặc hủy yêu cầu thay thế chỉ dẫn cũ có xung đột.
- Lượt chỉ giữ/đổi chủ đề không khôi phục nguồn đã bị hủy.
- Tin tức chung dùng web news khi không có yêu cầu mạng xã hội.
- Chỉ chọn tool phục vụ nguồn còn hiệu lực; gọi song song khi người dùng thực sự còn yêu cầu nhiều nguồn/đích.

Trong vòng tối ưu v3, thay đổi hành vi chỉ nằm ở `system_prompt.md`. Giữ nguyên `tools.yaml`, bộ chấm `run_eval.py` và các case base/group. Các thay đổi test cá nhân được ghi riêng.

| Chỉ số | V2 chạy trên máy Việt Đức | V3 | Chênh lệch |
|---|---:|---:|---:|
| Base — case accuracy | 18/20 = 90% | 20/20 = 100% | +10 điểm phần trăm |
| Group — case accuracy | 8/10 = 80% | 9/10 = 90% | +10 điểm phần trăm |
| Base — routing accuracy | 90% | 100% | +10 điểm phần trăm |
| Group — routing accuracy | 80% | 90% | +10 điểm phần trăm |
| Base — argument accuracy | 90% | 100% | +10 điểm phần trăm |
| Group — argument accuracy | 80% | 90% | +10 điểm phần trăm |
| Base — multiturn accuracy | 83,33% | 100% | +16,67 điểm phần trăm |
| Group — multiturn accuracy | 60% | 80% | +20 điểm phần trăm |
| Provider errors — base/group | 0 / 0 | 0 / 0 | Đo đủ cả hai bộ |

Đây là kết quả của một lượt chạy trên mỗi bộ với cùng provider/model. Các case đã được dùng để phân tích lỗi nên kết quả không phải đánh giá trên bộ dữ liệu độc lập chưa từng xem; không khẳng định chất lượng 100% cho mọi yêu cầu thực tế.

**Hash rút gọn từ output:**

| Bản | Artifact version |
|---|---|
| V2 local, base và group | `v2-openrouter-vietduc+p98e7fa380d3f+ta94472a74581` |
| V3, base và group | `v3+p8f1016718bf4+ta94472a74581` |

Tools hash không đổi. Dùng hash đầy đủ trong run JSON khi ghi version_log.csv.

**File bằng chứng** — liên kết tính từ `artifacts/REPORT.md`:

| Bản/bộ | Run JSON |
|---|---|
| V2 base | [Run JSON](../runs/v2-openrouter-vietduc_B_base_openrouter_20261110T192818757074.json) |
| V2 group | [Run JSON](../runs/v2-openrouter-vietduc_B_group_openrouter_20261110T192907186473.json) |
| V3 base | [Run JSON](../runs/v3_B_base_openrouter_20261110T195239893928.json) |
| V3 group | [Run JSON](../runs/v3_B_group_openrouter_20261110T195341770535.json) |

Đã bổ sung 4 dòng vào [version_log.csv](version_log.csv): hai dòng đối chiếu v2 chạy tại máy Việt Đức và hai dòng v3, tách theo base/group. Giữ nguyên các dòng trước đó của nhóm.

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

### Đối chiếu lỗi v2–v3

| Case | Hành vi v2 | Kết quả v3 |
|---|---|---|
| R03_web_news_routing | Gọi lookup đúng nhưng gọi thừa social_search cho yêu cầu tin tức chung | PASS |
| M06_switch_tool | Gọi thêm social_search dù người dùng đã bỏ Twitter và chuyển sang web | PASS |
| G07_multiturn_carryover_timeframe | lookup đã đúng chủ đề/thời gian nhưng gọi thêm social_search | PASS |
| G08_multiturn_switch_to_github | Chỉ gọi social_search; thiếu github_repos sau yêu cầu đổi sang GitHub | Vẫn FAIL |

**G08 còn tồn tại:** Kỳ vọng `github_repos(query="RAG", language="python")`; thực tế gọi `social_search(query="RAG", search_type="Top")`. Bộ chấm báo thiếu github_repos và có thêm social_search. Tool Twitter thực thi có dữ liệu, nên đây là lỗi routing, không phải lỗi key.

**Phân biệt nhãn:** `case_failure_type` là nhãn được gán trước cho case; không luôn mô tả đúng sai lệch của từng lần chạy. Ví dụ G07 có nhãn wrong_arg_value nhưng sai lệch quan sát được ở v2 là extra_tool_call.

**Kiểm tra hồi quy trong lượt đo:** R13_parallel_web_and_tweets vẫn PASS, cho thấy quy tắc mới vẫn cho phép gọi nhiều nguồn khi yêu cầu còn cần cả hai.

## B3. Team Eval Cases

Sử dụng bộ nhóm có sẵn `data/eval_group.json`: **10 case, gồm 5 single-turn và 5 multi-turn**. Việt Đức tiếp nhận bộ case của nhóm và chạy đối chiếu v2–v3; không nhận là người viết cả 10 case.

| Case | Loại | Nội dung kiểm tra | V2 đối chiếu | V3 |
|---|---|---|---|---|
| G01_github_repos_python | Single-turn | Tìm repository GitHub Python, sắp theo stars, giới hạn 5 | PASS | PASS |
| G02_user_tweets_ylecun | Single-turn | Lấy 5 bài đăng của tài khoản ylecun | PASS | PASS |
| G03_web_news_week | Single-turn | Tìm tin bán dẫn trong tuần, dùng web news | PASS | PASS |
| G04_missing_url_clarify | Single-turn | Hỏi URL khi người dùng chưa cung cấp | PASS | PASS |
| G05_confirm_before_telegram | Single-turn | Hỏi xác nhận trước khi gửi Telegram | PASS | PASS |
| G06_multiturn_clarify_then_handle | Multi-turn | Hỏi lại tài khoản rồi dùng handle sama được bổ sung | PASS | PASS |
| G07_multiturn_carryover_timeframe | Multi-turn | Đổi chủ đề sang OpenAI, giữ thời gian trong ngày và nguồn còn hiệu lực | FAIL | PASS |
| G08_multiturn_switch_to_github | Multi-turn | Bỏ Twitter, chuyển sang GitHub Python và giữ chủ đề RAG | FAIL | FAIL |
| G09_multiturn_clarify_then_url | Multi-turn | Hỏi lại rồi đọc URL được cung cấp ở lượt sau | PASS | PASS |
| G10_multiturn_cancel_request | Multi-turn | Hủy tra cứu rồi hỏi khả năng của agent, không gọi tool | PASS | PASS |

Kết quả: v2 **8/10**, v3 **9/10**; cả hai run đều đo đủ 10 case và không có provider error. Liên kết run có ở B1.

## B4. Live Chat Evidence

[Bản chụp demo UI](../transcripts/evidence/ui_demo_20261110.transcript.json) có 4 lượt với Ollama `qwen2.5:7b`, version `ui-demo`: chào hỏi, hỏi tool, tìm tin ngày 10/11/2026 và tìm tin giá vàng. Hai lượt tra cứu có gọi `lookup` và nhận kết quả thật. Đây là bằng chứng UI/live chat riêng, không phải run eval của v0 hoặc v1 OpenRouter.

### Chat live bản v3
Phiên chat sử dụng OpenRouter, model `openai/gpt-4o-mini`, với artifact version `v3+p8f1016718bf4+ta94472a74581`.

[Transcript 3 lượt](../transcripts/v3_openrouter_20261110T202721680910.transcript.json)

| Lượt | Yêu cầu | Hành vi quan sát |
|---|---|---|
| 1 | Tìm 2 tin AI trong tuần trên web | Gọi `lookup` với `query="AI"`, `topic="news"`, `timeframe="week"`, `max_results=2`; trả lời kèm liên kết nguồn |
| 2 | Bỏ tìm web, chuyển sang 3 repository GitHub về AI bằng Python | Gọi `github_repos` với `query="AI"`, `language="python"`, `limit=3`; không gọi thêm tool tìm web |
| 3 | Hủy tìm kiếm và hỏi khả năng của agent | Trả lời trực tiếp, không gọi tool |

Trong phiên này, agent chọn đúng nguồn khi người dùng chuyển yêu cầu và dừng tra cứu khi yêu cầu bị hủy. Đây là bằng chứng cho ba lượt đã thử; không thay thế kết quả group eval, trong đó G08 vẫn FAIL.

## B5. Tool mới và UI

- `github_repos`: có [code](../tools/github_repos/tool.py), [TOOL.md](../tools/github_repos/TOOL.md), declaration/registry và 3 test trong [test_tools_todo.py](../tests/test_tools_todo.py). Trong group eval, G01 tìm repository trực tiếp PASS ở cả v2 đối chiếu và v3; G08 chuyển nguồn sang GitHub qua hội thoại vẫn FAIL. Phiên chat live v3 cũng đã gọi được github_repos khi người dùng yêu cầu chuyển nguồn.
- UI Streamlit: [app.py](../app.py), [hướng dẫn](../UI.md); hỗ trợ local/cloud, lịch sử chat, transcript và tiến trình xử lý.
- Chưa có bằng chứng gửi Telegram thật trong các run v0/v1.

### Kiểm thử và kiểm tra kết nối
Người phụ trách: Lưu Văn Việt Đức — MSSV 2A202603445.

Hoàn thiện 14 unit test cho các tool clarify, format, send, lookup, fetch, timeline, social_search và policy. Các test được lưu riêng tại [test_vietduc_existing_tools.py](../tests/test_vietduc_existing_tools.py).
Tích hợp các test trên nền v2, giữ nguyên bộ test chung và các test của github_repos.
Cập nhật assertion của test Telegram theo hành vi v2: gửi văn bản thuần, không truyền parse_mode.
Sau tích hợp, toàn bộ bộ test của dự án đạt 131 passed, 0 failed, 0 skipped, gồm cả test có sẵn của nhóm và 14 test bổ sung.
Kiểm tra thành công kết nối model, Tavily, Firecrawl và các tool Twitter qua RapidAPI. Tool send đã gửi được tin thử vào channel Telegram cá nhân.
Lần gửi thử Telegram được thực hiện trực tiếp với confirmed=True. Luồng agent hỏi xác nhận rồi gửi tin chưa có transcript kiểm chứng.

### Bổ sung sau khi nộp v3: `extract_links` — Việt Đức

Người phụ trách: **Lưu Văn Việt Đức — 2A202603445**. Đây là phần bổ sung sau khi
nhóm đã nộp bài, trên nhánh `vietduc-tool-extract-links`, từ `origin/main` tại
`d3f128207e40a726e55f0ab205fb412a9e6c6678`; không phải thay đổi của release v3 đã nộp.
Giữ nguyên bằng chứng v3: 131 passed ở thời điểm tích hợp trước đây, base 20/20,
group 9/10, G08 FAIL và artifact `v3+p8f1016718bf4+ta94472a74581`.

- [Implementation](../tools/extract_links/tool.py), [TOOL.md](../tools/extract_links/TOOL.md),
  registry `TOOL_FUNCTIONS["extract_links"]` và declaration được thêm cuối `tools.yaml`.
  Không sửa `system_prompt.md`, harness, provider, UI hoặc tool khác.
- Nhận `text` nguyên văn và `max_results` mặc định 10 (1–50, không nhận boolean).
  Trích bare URL, Markdown link và autolink HTTP/HTTPS; kiểm tra cú pháp hostname,
  giữ thứ tự đầu tiên, so trùng bằng chuỗi, giữ query/fragment và casing của URL.
  Trả `items` gồm `title=url`, `url`, `source=hostname`, `summary=""`, cùng
  `item_count`, `total_unique` trước giới hạn và `truncated`.
- Chạy offline bằng thư viện chuẩn, không cần key/dependency mới, không tìm web,
  tải trang, xác minh URL hay xuất file. Không thay chức năng `lookup`, `fetch`,
  `github_repos`, `export_chat`; Việt Đức không nhận hai tool sau là tool mình viết.
- Hạn chế: không phải Markdown parser đầy đủ; không giải reference link, HTML entity
  hoặc escape phức tạp. Dấu đóng ngoặc thừa và dấu câu cuối bare URL được xem là
  delimiter; dùng `<URL>`, `[nhãn](URL)` hoặc percent-encode nếu bare URL thực sự
  kết thúc bằng `. , ; : ! ? *`. Trong autolink/Markdown link có delimiter đầy đủ,
  dấu câu thuộc URL được giữ nguyên. Có hỗ trợ ngoặc cân bằng bên trong URL;
  không kiểm tra khả năng truy cập.

**Kiểm thử offline — ngày 10/11/2026, ghi nhận lúc 21:16 (Asia/Saigon):**

| Phép kiểm tra | Kết quả thực đo |
|---|---|
| Baseline trên `d3f1282`, trước khi thêm tool | 151 passed, 0 failed, 0 skipped |
| `pytest -q tests/test_tools_todo.py -k extract_links` | 54 passed, 17 deselected |
| `pytest -q tests/test_tool_contract.py` | 70 passed |
| Toàn bộ suite sau tích hợp | 210 passed, 0 failed, 0 skipped |
| `git diff --check` | Đạt |

54 trường hợp mới (có parametrization) được nối vào cuối
[test_tools_todo.py](../tests/test_tools_todo.py); 5 trường hợp contract tự tăng
theo declaration mới. Test kiểm tra schema, thứ tự, trùng lặp, giới hạn/counts,
input sai, scheme/hostname không hợp lệ, query/fragment và dấu câu. Không dùng HTTP
thật và không sửa test/fixture có sẵn. Lượt baseline đầu trong sandbox có 133 pass,
18 lỗi setup do không truy cập được Windows Temp; chạy lại ngoài sandbox đạt 151 pass.
Lượt test tool trong sandbox có một cảnh báo quyền ghi pytest cache; contract và
full suite chạy ngoài sandbox đều xanh, không có cảnh báo.

**Eval riêng:** nối `G11_extract_links_from_text` (single-turn, phase B) vào cuối
[eval_group.json](../data/eval_group.json), giữ nguyên G01–G10. Trên nhánh bổ sung,
bộ nhóm có **11 case: 6 single-turn + 5 multi-turn**. G11 yêu cầu đúng một lần gọi
`extract_links`, `text` đúng đoạn `Sources: [https://example.com/a](https://example.com/a) and [https://example.org/b](https://example.org/b)`,
`max_results=10`; output object được kiểm tra bằng unit test. Harness hiện tại so
chuỗi sau strip/lowercase nên cần đọc `actual_tool_calls` để xác nhận nguyên văn;
không chỉnh harness để tăng độ chặt. Không dùng list object trong expected args.

Thêm declaration làm đổi tools hash; mọi run mới dùng tag `v3-extract-links`.
Không dùng điểm v3 cũ để chứng minh bản này và không so trực tiếp accuracy trên
11 case với group 9/10 lịch sử để tuyên bố cải thiện.

**Live eval mới — OpenRouter / `openai/gpt-4o-mini`, ngày 10/11/2026 (Asia/Saigon):**

Preflight thành công: `timeline(screenname="sama", limit=1)`. Lượt preflight
trong sandbox bị chặn socket (`WinError 10013`, `APIConnectionError`); chạy lại
ngoài sandbox thành công. Sau đó chỉ chạy **một lượt base và một lượt group**,
không lặp eval để chọn điểm. Hai run không có provider error hoặc tool error.

| Bộ / thời điểm tạo run | Pass / đo được / tổng | Case / routing / argument accuracy | Multi-turn | Provider errors | Run JSON |
|---|---|---|---|---|---|
| Base — 21:20:04 | 20 / 20 / 20 | 1.0 / 1.0 / 1.0 | 1.0 | 0 | [Base mới](../runs/v3-extract-links_B_base_openrouter_20261110T212004147485.json) |
| Group — 21:20:49 | 10 / 11 / 11 | 0.9091 / 0.9091 / 0.9091 | 0.8 | 0 | [Group mới](../runs/v3-extract-links_B_group_openrouter_20261110T212049831977.json) |

Artifact của cả hai run: `v3-extract-links+p8f1016718bf4+t6164a8575cc6`.
Prompt SHA-256: `8f1016718bf47f621c5c0e28535ead5cf036a6c9e64a9742f8326e55db31610b`;
tools SHA-256: `6164a8575cc615cab2465452261d0c7ab53926821d56e2fa35d33c88a274ff04`.
Đã đối chiếu cả hai hash với file đang dùng; chỉ nối hai dòng `v3-extract-links`
vào [version_log.csv](version_log.csv), lấy hash/metric/timestamp trực tiếp từ run.
Để trống `metric_before` vì đây là bản bổ sung cần đo riêng.

G11 **PASS**; kiểm tra trực tiếp `actual_tool_calls` bằng so sánh nguyên chuỗi
(ngoài phép strip/lowercase của harness) xác nhận đúng một call, `text` nguyên văn,
`max_results=10`. Tool trả đúng hai item lần lượt `https://example.com/a`,
`https://example.org/b`, `item_count=total_unique=2`, `truncated=false`, summary rỗng.
G01–G10 vẫn có 9 case PASS, **G08 vẫn FAIL**: thiếu `github_repos`, gọi thừa
`social_search(query="RAG", search_type="Top")`. Không sửa prompt, expected hay
harness để xử lý lỗi lịch sử này trong phạm vi bổ sung tool.

Lệnh đã dùng, chạy từ `starter_v0/` bằng PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider openrouter --model openai/gpt-4o-mini
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3-extract-links --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3-extract-links --suite group --eval-cases data/eval_group.json
```

#### Review cuối trước bàn giao — 10/11/2026, 21:46 (Asia/Saigon)

Phát hiện và sửa lỗi cắt dấu câu cuối ngay cả khi URL nằm trong `<...>` hoặc
`[nhãn](...)`: `<https://example.com/?q=wow!>` từng bị đổi thành `...?q=wow`.
Bản sửa giữ nguyên dấu câu của query/fragment khi có delimiter đầy đủ; bare URL
vẫn áp dụng quy tắc dấu câu đã ghi trong TOOL.md. Thêm 6 regression cases
(autolink và Markdown link, query kết thúc `!`/`;`, fragment kết thúc `?`).

Kiểm tra lại sau sửa: **60 passed** cho extract_links (17 deselected),
**70 passed** contract, **216 passed** toàn bộ suite, 0 failed, 0 skipped.
G01–G10 và AST của mọi test cũ không đổi. Registry/declaration dùng chung cho
OpenAI/OpenRouter/Ollama và qua converter Anthropic/Gemini; kiểm tra chạy tool
khi chặn socket/DNS cũng đạt, không gọi provider thật trong lượt review này.

Không đổi declaration hoặc prompt, nên hash `6164a8575cc6`/`8f1016718bf4` và
hai dòng version log vẫn khớp hai run JSON ở trên. **Hai live run lúc 21:20 được
tạo trước bản sửa review này**; harness chỉ hash prompt/declaration, không hash
implementation. Không dùng chúng làm bằng chứng cho bản sửa dấu câu mới; phần đó
được xác minh bằng regression tests offline, không chạy lại live eval để chọn điểm.

Các run/transcript/hash/snapshot v3 cũ, ba run Gemini untracked, `export_chat`
(implementation/declaration/tests), `github_repos` và prompt/tools local của Hậu
được giữ nguyên. Nhánh để review, chưa commit/push/merge; bước tiếp theo là xem diff,
chỉ stage file thuộc phần bổ sung (không stage ba run Gemini), commit trên nhánh này
và mở PR về main để trưởng nhóm duyệt.

## B6. Reflection

### Giai đoạn v0–v1

**Sửa gì trong system prompt?** Quy tắc hành vi chung: khi nào hỏi lại, khi nào trả lời không dùng tool, xác nhận trước khi publish và cách chọn nguồn theo yêu cầu. Năm case được sửa cho thấy agent giảm tự đoán và giảm dùng action tool sai mục đích.

**Sửa gì trong tool declaration?** Convention của từng đối số, nhất là `lookup.query`, `topic` và `timeframe`. R03/R13 đã chọn đúng tool nhưng vẫn fail, nên chỉ bổ sung routing là chưa đủ.

**Lỗi nào cần xem thủ công?** Query “AI news” có thể vẫn tìm được tin phù hợp nhưng không khớp expected “AI”; evaluator chỉ so giá trị sau strip/lowercase, không chấm tương đương ngữ nghĩa. Cần ghi nhận fail theo bộ đo và xem thêm chất lượng kết quả, không sửa expected để làm tăng điểm. Với case `no_tool`, harness kiểm tra không có tool call, chưa tự đánh giá đầy đủ chất lượng lời từ chối; đã đọc câu trả lời R08/R14 để xác nhận hành vi. Tương tự, routing pass không bảo đảm nguồn và bản tóm tắt đúng.

**Hướng cải tiến được xác định sau v1:** chuẩn hóa arguments ở R03/R13; sửa carry-over nguồn của M06 khi user nói bỏ Twitter; thêm group case cho tool mới và giữ các case đã sửa khỏi regression. Mỗi vòng tiếp theo nên kiểm chứng một thay đổi có phạm vi rõ ràng.

### Giai đoạn v2–v3

V3 cải thiện việc chọn nguồn đang còn hiệu lực qua một thay đổi trong system prompt. Base tăng từ 90% lên 100%; group tăng từ 80% lên 90%. Kết quả ủng hộ giả thuyết trong các case đã đo. Lỗi đổi nguồn sang GitHub ở G08 vẫn còn, cần được ghi nhận thay vì tuyên bố agent đã xử lý hết mọi tình huống.

Hướng nghiên cứu tiếp: kiểm tra việc đổi nguồn trên các chủ đề và cách diễn đạt khác, phân biệt thay thế nguồn với bổ sung nguồn. Nếu sửa tiếp, tạo vòng thử mới và giữ log riêng.

Các lượt Gemini lỗi 429/503 được giữ riêng như bằng chứng hạn chế môi trường. Không dùng chúng để kết luận chất lượng Gemini hoặc tính mức cải thiện v2–v3 OpenRouter.

## B7. Small Local Model Challenge

Chưa có base eval của hai model local hoặc log tối ưu `v4-local`/`v5-local`. Preflight/chat local hiện có chưa đủ bằng chứng để kết luận hoàn thành challenge.

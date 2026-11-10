# Research Agent Tool Eval — Nhóm 3 miền

## Team

| Thành viên | MSSV | Phụ trách |
|---|---|---|
| Vũ Lê Hoàng | 2A202603542 | v0, baseline, tool export chat |
| Ngô Đức Thịnh | 2A202603548 | v1, prompt và tool GitHub |
| Bùi Gia Huy | 2A202603525 | v2, tool declaration và eval nhóm |
| Lưu Văn Việt Đức | 2A202603445 | v3, đối chiếu v2–v3, 14 unit test và live chat v3 |
| Phan Trọng Hậu | 2A202603547 | UI, report, Telegram, kiểm chứng eval và local model |

Báo cáo cập nhật theo main `d3f1282` đã merge v3. Model cloud để so sánh: **OpenRouter / `openai/gpt-4o-mini`**. Có bằng chứng v0–v3.

**Nguồn và người thực hiện:** kết quả chính lấy từ run JSON và phần báo cáo do Hoàng (v0), Thịnh (v1), Huy (v2), Đức (cặp đối chiếu v2 → v3 và live v3) push lên repo. Hậu tổng hợp report và chạy thêm hai run `v2-verified` để kiểm chứng môi trường/dataset; các run bổ sung được ghi riêng.

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

Research Desk tìm thông tin trên web và X/Twitter, đọc URL, tìm paper arXiv, tra policy và khám phá repository GitHub. Người dùng chat qua Streamlit, xem các bước gọi tool cùng thời gian xử lý, mở lại lịch sử hoặc xuất hội thoại; có thể bật/tắt đồng bộ câu hỏi và câu trả lời sang Telegram.

**Chạy UI:** `./run_ui.sh` (Linux/macOS), `.\run_ui.bat` (Windows), rồi mở `http://localhost:8501`. UI có snapshot v0–v3, hội thoại riêng theo version/model và màn so sánh Base/Group. **Link dùng thử public: chưa triển khai.**

## A2. Tool hiện có

| Tool | Chức năng | Nhóm tự thêm |
|---|---|---|
| `clarify` | Hỏi thêm thông tin hoặc xin xác nhận | Không |
| `timeline` | Lấy bài đăng theo tài khoản X/Twitter | Không |
| `social_search` | Tìm bài theo chủ đề, Top/Latest | Không |
| `lookup` | Tìm web, loại tin và khoảng thời gian | Không |
| `fetch` | Đọc nội dung URL | Không |
| `format` | Trình bày item thành digest | Không |
| `send` | Gửi Telegram; UI điều khiển bằng công tắc sync | Không |
| `policy` | Tra policy markdown nội bộ | Không |
| `papers` | Tìm paper arXiv | Không |
| `paper_text` | Tải PDF arXiv và trích văn bản | Không |
| `github_repos` | Tìm repo, lọc ngôn ngữ, sort stars/forks/updated | Có — v1 |
| `export_chat` | Xuất transcript thành Markdown/text trong `exports/` | Có — bổ sung sau v2 |

Danh sách trên là code hiện tại. Snapshot v0 có 10 tool, v1/v2/v3 có 11; `export_chat` chưa có trong các run eval v0–v3.

## A3. Câu hỏi mẫu

1. “Lấy 3 bài đăng gần đây của tài khoản sama.”
2. “Tìm trên web tin AI hôm nay và tìm thêm tweet về AI.”
3. “Đọc https://example.com và tóm tắt bằng tiếng Việt.”
4. “Tìm 3 repository GitHub về RAG viết bằng Python, xếp theo số sao.”
5. “Tóm tắt bài viết này giúp tôi.” — thử trong phiên trống để kiểm tra hỏi lại URL.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

### Kết quả chính từ các thành viên

Base cố định: 20 case (14 single-turn + 6 multi-turn), cùng model. Cặp v2 → v3 ưu tiên các run Đức chạy trên cùng máy/provider, đúng dataset và có tool data thật. [Version log](version_log.csv), [tổng hợp tất cả run](../analysis/report_run_summary.csv).

| Version | Người thực hiện / thay đổi | Case đúng | Accuracy | Run chính |
|---|---|---:|---:|---|
| v0 | Hoàng — baseline | 13/20 | 65% | [v0](../runs/v0_B_base_openrouter_20261110T104306962524.json) |
| v1 | Thịnh — scope, clarify, xác nhận, routing và tool GitHub | 17/20 | 85% | [v1](../runs/v1_B_base_openrouter_20261110T105632499545.json) |
| v2 | Huy — declaration/args; Đức chạy lại làm mốc đối chiếu v3 | 18/20 | 90% | [v2 đối chiếu của Đức](../runs/v2-openrouter-vietduc_B_base_openrouter_20261110T192818757074.json) |
| v3 | Đức — active request/source selection trong prompt | 20/20 | 100% | [v3 base](../runs/v3_B_base_openrouter_20261110T195239893928.json) |

| Metric base | v0 | v1 | v2 đối chiếu | v3 |
|---|---:|---:|---:|---:|
| Case accuracy | 65% | 85% | 90% | 100% |
| Tool routing | 75% | 95% | 90% | 100% |
| Arguments | 65% | 85% | 90% | 100% |
| Single-turn đúng / tổng | 7/14 | 12/14 | 13/14 | 14/14 |
| Multi-turn đúng / tổng | 6/6 | 5/6 | 5/6 | 6/6 |
| Multi-turn accuracy | 100% | 83,33% | 83,33% | 100% |
| Provider error | 0 | 0 | 0 | 0 |
| Tool execution error trong run chính | 0 | 0 | 0 | 0 |

v0 → v1 sửa 5 case, phát sinh regression M06, tăng ròng 4 case. v1 → v2 sửa R13; R03/M06 còn fail. Routing v2 giảm 95% → 90% vì R03 chuyển từ sai args sang gọi thừa social_search. v3 sửa R03 và M06; R13 gọi hai nguồn theo yêu cầu vẫn pass. [Đối chiếu đủ 20 case](../analysis/v0_v1_v2_v3_case_comparison.csv).

| Group đúng file, 10 case | v2 đối chiếu của Đức | v3 của Đức | Chênh lệch |
|---|---:|---:|---:|
| Case accuracy | 8/10 = 80% | 9/10 = 90% | +10 điểm phần trăm |
| Routing / arguments | 80% / 80% | 90% / 90% | +10 / +10 điểm phần trăm |
| Single-turn | 5/5 | 5/5 | Không đổi |
| Multi-turn | 3/5 = 60% | 4/5 = 80% | +20 điểm phần trăm |
| Provider / tool errors | 0 / 0 | 0 / 0 | Không đổi |

Nguồn group: [v2 của Đức](../runs/v2-openrouter-vietduc_B_group_openrouter_20261110T192907186473.json), [v3 của Đức](../runs/v3_B_group_openrouter_20261110T195341770535.json). G07 được sửa ở v3; G08 vẫn fail. Đây là kết quả trên các case đã dùng để phân tích lỗi, chưa phải bộ đánh giá độc lập; 100% base không có nghĩa mọi câu hỏi thực tế đều đúng.

### Giả thuyết và thay đổi v3 — Đức

Agent v2 chưa xác định rõ nguồn đang còn hiệu lực. Đức thay rule gọi song song bằng mục **Active Request and Source Selection** trong `system_prompt.md`:

- Giữ chủ đề, timeframe, account, URL và limit nếu user chưa sửa/hủy.
- Chỉ dẫn đổi nguồn/hủy yêu cầu thay thế chỉ dẫn cũ có xung đột; lượt chỉ giữ chủ đề không khôi phục nguồn đã hủy.
- Tin tức chung mặc định tìm web, không thêm Twitter khi chưa được yêu cầu.
- Chỉ gọi nhiều tool khi nhiều nguồn/đích vẫn còn được yêu cầu.

Trong vòng tối ưu này, thay đổi hành vi nằm ở prompt; giữ nguyên declaration v2 và case base/group. Các test cá nhân được ghi riêng. Git diff và run hashes xác nhận tools hash v2/v3 giống nhau. Cặp run do Đức thực hiện tăng base 90% → 100%, group 80% → 90%.

### Các lần kiểm chứng bổ sung — Hậu

Hậu chạy thêm `v2-verified` bằng đúng hash v2, sau khi phát hiện run gốc thiếu key và nhãn group dùng sai file. Kết quả: [base 18/20](../runs/v2-verified_B_base_openrouter_20261110T205612123670.json), [group 8/10](../runs/v2-verified_B_group_openrouter_20261110T205425024238.json), đều có 0 tool error. Kết quả khớp baseline v2 mà Đức đã push. Hai run của Hậu chỉ là kiểm chứng bổ sung; kết luận v2 → v3 ở trên dựa vào cặp run của Đức.

Hai run v1 trước đó cùng 17/20, cùng ba case fail. Các lần chạy lặp hiện có hữu ích để đối chiếu, chưa phải đánh giá thống kê nhiều lần.

### Phạm vi thay đổi và hash

| Version | Prompt hash (12 ký tự đầu) | Tools hash (12 ký tự đầu) | Bằng chứng artifact |
|---|---|---|---|
| v0 | `eb1c8179815b` | `5b22a2476d41` | [snapshot v0](versions/v0/metadata.json) |
| v1 | `0f969bd7fd2e` | `707c6c5df8ec` | [snapshot v1](versions/v1/metadata.json) |
| v2 | `98e7fa380d3f` | `a94472a74581` | [prompt](evidence/v2/system_prompt.md), [tools](evidence/v2/tools.yaml) |
| v3 | `8f1016718bf4` | `a94472a74581` | [run v3](../runs/v3_B_base_openrouter_20261110T195239893928.json) |

Hash đầy đủ nằm trong run JSON. v1/v2 có cùng nội dung system prompt khi chuẩn hóa xuống dòng; hash prompt khác do LF/CRLF. Thay đổi hành vi ở v2 tập trung vào declaration. Snapshot v2 đã đối chiếu hash trước khi chạy kiểm chứng; không dùng declaration hiện tại có thêm `export_chat` để gắn nhãn v2.

v1 thay nhiều rule và thêm tool cùng lúc, nên kết quả là hiệu quả của cả gói thay đổi, chưa tách đóng góp từng rule. v2 cũng sửa nhiều description trong một vòng; các vòng sau nên kiểm chứng thay đổi hẹp hơn.

### Kiểm tra chất lượng bằng chứng

- Run Gemini v0: 10/19 case đo được (52,63%), một provider error quota HTTP 429 ở M06. Không ghép vào so sánh OpenRouter v0–v2 vì khác model và mẫu số. [Run Gemini](../runs/v0_B_base_gemini_20261110T103545490529.json).
- Các run v2 gốc ghi `Missing RAPIDAPI_KEY` 10 lần, `Missing TAVILY_API_KEY` 5 lần, `Missing FIRECRAWL_API_KEY` 2 lần. Harness vẫn chấm routing/args nên 90% khi đó chưa chứng minh tool nhận được dữ liệu thật. Run kiểm chứng có 0 lỗi thực thi tool.
- Hai run cũ mang nhãn `group` (`143650926147`, `144849420158`) thực tế trỏ tới `eval_base.json`, dataset role `base`, gồm R01–R14 và M01–M06. `--suite` chỉ là nhãn; không tự chọn bộ case. Không dùng 18/20 của các run này làm điểm group.

## B2. Failure Analysis

| Case | v0 | v1 | v2 đối chiếu | v3 | Kết luận |
|---|---|---|---|---|---|
| R03 web news | Query AI news thay vì AI | Vẫn sai query | Query đúng nhưng thừa social_search | PASS | v3 không thêm nguồn ngoài yêu cầu |
| R08 giải toán | Gọi send chứa lời giải | PASS | PASS | PASS | Scope được giữ |
| R10 thiếu handle | Tự chọn sama | PASS | PASS | PASS | Clarify trước khi lấy dữ liệu trên model cloud |
| R11 thiếu URL | Tự đoán URL | PASS | PASS | PASS | Hỏi URL trước khi đọc |
| R12 gửi chưa xác nhận | Gọi send ngay | PASS | PASS | PASS | Model gọi clarify(yes_no) |
| R13 web + Twitter | Hai tool nhưng sai args | Vẫn sai args | PASS | PASS | v3 vẫn hỗ trợ yêu cầu đa nguồn hợp lệ |
| R14 viết Fibonacci | Dùng send chứa code | PASS | PASS | PASS | Không dùng action tool để trả lời chat |
| M06 bỏ Twitter, chuyển web | PASS | Thừa social_search | Vẫn thừa social_search | PASS | v3 dùng nguồn mới nhất còn hiệu lực |
| G07 giữ timeframe | — | — | Thừa social_search | PASS | Sửa ở v3 |
| G08 chuyển sang GitHub | — | — | Thiếu github_repos, gọi social_search | Vẫn FAIL | Lỗi routing còn lại trên group |

G08 v3 expected `github_repos(query="RAG", language="python")`, actual `social_search(query="RAG", search_type="Top")`. Tool Twitter có dữ liệu, nên đây là lỗi routing, không phải thiếu key.

`failure_type` là nhãn gốc của case; cần đọc `observed_mismatch` và `failures`. R03 v1 thực tế sai args, v2 thừa tool; G07 có nhãn wrong_arg_value nhưng thực tế ở v2 là extra_tool_call. Ở v0, các lần gọi nhầm send R08/R12/R14 trả needs_confirmation; log không chứng minh đã gửi tin.

## B3. Team Eval Cases

Bộ [eval_group.json](../data/eval_group.json) do nhóm viết/tổng hợp có **10 case: 5 single-turn + 5 multi-turn**. Đức tiếp nhận bộ case của nhóm và chạy đối chiếu v2 → v3. Số liệu chính dưới đây dùng run Đức đã push, không dùng hai file group cũ trỏ nhầm base.

| Case | Loại | Nội dung kiểm tra | v2 đối chiếu | v3 |
|---|---|---|---|---|
| G01_github_repos_python | Single | Repo Python theo stars, limit=5 | PASS | PASS |
| G02_user_tweets_ylecun | Single | Yann LeCun → ylecun, limit=5 | PASS | PASS |
| G03_web_news_week | Single | Tin bán dẫn trong tuần → news/week | PASS | PASS |
| G04_missing_url_clarify | Single | Thiếu URL → clarify(text) | PASS | PASS |
| G05_confirm_before_telegram | Single | Chưa xác nhận Telegram → clarify(yes_no) | PASS | PASS |
| G06_multiturn_clarify_then_handle | Multi | Giữ limit=5, bổ sung Sam Altman → sama | PASS | PASS |
| G07_multiturn_carryover_timeframe | Multi | Đổi sang OpenAI, giữ news/day | FAIL | PASS |
| G08_multiturn_switch_to_github | Multi | Bỏ Twitter, tìm GitHub RAG/Python | FAIL | FAIL |
| G09_multiturn_clarify_then_url | Multi | Nhận URL bổ sung rồi fetch | PASS | PASS |
| G10_multiturn_cancel_request | Multi | Hủy yêu cầu, trả lời meta không tool | PASS | PASS |

Kết quả 8/10 → 9/10; G07 được sửa, G08 còn fail. [CSV chi tiết cặp run](../analysis/group_eval_results.csv). G01 tìm repo trực tiếp pass ở cả hai bản, nhưng điều đó không bảo đảm G08 đổi nguồn qua nhiều lượt sẽ pass. Không so trực tiếp 90% group với 100% base như cùng một bộ dữ liệu.

## B4. Live Chat Evidence

| Bằng chứng | User / lượt | Tool và kết quả | Nhận xét |
|---|---|---|---|
| [Demo UI 4 lượt](../transcripts/evidence/ui_demo_20261110.transcript.json) | Chào hỏi, hỏi tool, tìm tin và giá vàng | 2 lượt lookup nhận kết quả | Bằng chứng live UI, không thay thế eval |
| [Telegram sync — lượt 1](../transcripts/evidence/telegram_sync_demo.transcript.json) | Lấy 3 bài gần đây của sama | timeline, 3 item; sync `sent` | Đồng bộ cả câu hỏi và câu trả lời |
| [Telegram sync — lượt 2](../transcripts/evidence/telegram_sync_demo.transcript.json) | Tóm tắt 5 tweet mới nhất | timeline, 5 item; sync `sent` | Giữ tài khoản sama từ lượt trước là dùng ngữ cảnh hợp lệ |
| [GitHub search](../transcripts/evidence/github_search_demo.transcript.json) | 3 repo RAG/Python, sort stars | github_repos, 3 item, không error | Tool GitHub hoạt động sau cấu hình token |
| [Local lỗi thiếu handle](../transcripts/evidence/local_missing_handle_demo.transcript.json) | Phiên trống: tóm tắt 5 tweet | Tự chọn daily_ai_vn; tool JSONDecodeError | Failure thực tế của qwen2.5:7b với prompt v1; phân tích ở B7 |

Các file evidence là bản chụp/trích đoạn có ghi phạm vi; thông tin đích nhận Telegram đã được ẩn. Transcript giữ provider/model, hash và tool events. Telegram `sent` chứng minh API nhận tin, không chứng minh người nhận đã đọc hay nội dung factual đúng.

### Live chat v3 — Đức

[Transcript 3 lượt](../transcripts/v3_openrouter_20261110T202721680910.transcript.json), OpenRouter `openai/gpt-4o-mini`, artifact `v3+p8f1016718bf4+ta94472a74581`:

| Lượt | Yêu cầu | Hành vi |
|---|---|---|
| 1 | Tìm 2 tin AI trong tuần trên web | lookup: AI, news, week, max_results=2; trả lời có nguồn |
| 2 | Bỏ web, chuyển sang 3 repo AI/Python | github_repos: AI, python, limit=3; không gọi thêm web |
| 3 | Hủy tìm kiếm, hỏi năng lực agent | Trả lời trực tiếp, không tool |

Ba lượt này do Đức chạy. Việc chuyển nguồn trong phiên live thành công không thay thế kết quả G08 vẫn fail trong group eval.

## B5. Tool mới, UI và bonus

### Tool do nhóm viết

| Tool | Code / tài liệu | Kiểm thử và bằng chứng |
|---|---|---|
| github_repos — Thịnh, thêm ở v1 | [tool.py](../tools/github_repos/tool.py), [TOOL.md](../tools/github_repos/TOOL.md) | 3 test ban đầu, thêm 4 test auth/rate-limit; G01 group PASS; live demo 3 repo |
| export_chat — Hoàng, bổ sung sau v2 | [tool.py](../tools/export_chat/tool.py), [TOOL.md](../tools/export_chat/TOOL.md) | 15 test cho Markdown/text, latest/id/prefix, giới hạn lượt, input lỗi và chặn đường dẫn vượt thư mục |

`export_chat` có declaration và registry, nhưng chưa có model-routing eval riêng; các run v2 giữ snapshot trước khi thêm tool này. Nhóm hiện có 2 tool mới, chưa đạt điều kiện bonus “hơn 3 tool mới”.

### UI và Telegram — Hậu

- Streamlit dùng lại vòng lặp agent của `chat.py`, hỗ trợ cloud/Ollama, nút Chat mới, lịch sử tìm kiếm/mở lại, user bubble bên phải và dark mode.
- Đồng hồ thời gian thực, các bước model/tool, tổng thời gian và transcript JSON được lưu sau mỗi lượt.
- Lựa chọn đủ snapshot v0–v3 theo hash. Mỗi version/model có hội thoại riêng; đổi version tự mở lại phiên tương ứng hoặc tạo phiên trống. Màn so sánh có tổng quan 4 bản, chọn cặp version, chọn Base/Group khi có đủ dữ liệu, xem metric/case/prompt/tool diff và tải run. Màn so sánh đọc log của thành viên, không cần API key. Implementation tool dùng code hiện tại.
- Công tắc Telegram mặc định tắt. Khi user bật, mỗi lượt mới tự đồng bộ câu hỏi, câu trả lời, model, thời gian và tool names. Tắt thì ngừng; refresh/mở lại lịch sử không tự gửi lại. Model không thể tự bật sync; nội dung dài chia nhỏ; lỗi/partial được ghi nhận.
- [Bằng chứng gửi thật](../transcripts/evidence/telegram_sync_demo.transcript.json) có receipt `sent` và message ID cho hai lượt. Việc user bật sync là sự cho phép gửi các lượt mới; UI hiện không xác nhận riêng từng tin. Bản CLI/tool `send` vẫn kiểm tra `confirmed`.
- Script khởi động Linux/macOS [run_ui.sh](../../run_ui.sh), Windows [run_ui.bat](../../run_ui.bat). Script Windows chưa được chạy thực tế trên máy Windows trong phiên kiểm chứng này.

### Unit test

Kết quả kiểm tra sau khi hoàn thiện UI v0–v3: **158 passed, 0 failed, 0 skipped**. [Bản ghi lệnh và kết quả](../analysis/pytest_report.txt). Unit test chạy offline, gồm contract, mock HTTP và tool mới; không phải điểm model.

Đức bổ sung 14 test offline cho clarify, format, send, lookup, fetch, timeline, social_search và policy tại [test_vietduc_existing_tools.py](../tests/test_vietduc_existing_tools.py). Đây là phần kiểm thử của Đức. Báo cáo thành viên ghi 131 pass ở thời điểm tích hợp riêng; sau merge v3, suite chung đạt 151. Hậu bổ sung 7 test cho catalog/so sánh và điều hướng hội thoại v0–v3, nâng tổng lên 158. Các test UI chạy offline, không gọi model thật.

Ví dụ unit test bắt được lỗi mà routing eval có thể bỏ sót: `send` không phát HTTP khi chưa có boolean xác nhận; GitHub trả 403/rate limit phải có trạng thái lỗi/reset rõ ràng; export transcript phải chặn `../.env`. Eval chỉ nhìn tên tool/args không xác minh những hành vi thực thi này.

## B6. Reflection

**System prompt và declaration:** prompt phù hợp cho scope, hỏi lại, xác nhận và ưu tiên yêu cầu mới; declaration phù hợp cho convention của query/topic/timeframe/handle. v1 sửa 5 case hành vi; v2 sửa args ở R13 nhưng vẫn mở rộng nguồn ngoài yêu cầu tại R03/M06.

**Đánh giá phải đọc cả log thực thi:** provider error 0 không bảo đảm tool API thành công. Các run v2 gốc vẫn được 90% dù tool thiếu key; lần kiểm chứng có dữ liệu thật giúp tách lỗi model khỏi lỗi môi trường. Nhãn suite cũng không thay thế kiểm tra đường dẫn dataset và case IDs.

**Cần đánh giá nội dung cuối:** câu trả lời không gọi tool vẫn có thể sai factual. Các câu cần nguyên văn/liệt kê chính xác phải được kiểm chứng nguồn; base/group hiện chủ yếu chấm tool_calls/args nên chưa đo đầy đủ điều này. Các câu hỏi kiến thức được user thử trong live chat cần thêm rubric nội dung và nguồn, không chỉ đánh dấu no_tool.

**Giới hạn của bộ chấm:** query tương đương ngữ nghĩa có thể fail do so khớp chuỗi; expected chỉ kiểm tra subset args. Case multi-turn được harness gói lịch sử thành ngữ cảnh để đo lượt cuối, không thay thế chạy hội thoại tương tác từ đầu đến cuối. Vì vậy cần kết hợp eval, unit test và live chat.

**Kết quả v3 và ưu tiên tiếp:** rule active request/source selection của Đức sửa R03, M06, G07 mà vẫn giữ R13 pass. Cần tập trung G08, thêm biến thể chuyển nguồn và case factual có nguồn; bổ sung routing eval cho export_chat. Giữ nguyên base cases và tạo version mới nếu sửa tiếp.

## B7. Small Local Model Challenge — tiến độ

Model đã thử: Ollama `qwen2.5:7b`. Chưa có full base eval trên hai model ≤8B, hai vòng `v4-local`/`v5-local` hoặc lần chạy ngược bản local trên cloud, nên chưa kết luận hoàn thành challenge.

| Kiểm tra | Prompt/tools | Quan sát | Kết quả |
|---|---|---|---|
| Thiếu handle, cloud R10 | v1 cloud | clarify(text) | PASS theo base |
| Thiếu handle, live local | v1 snapshot | Tự chọn daily_ai_vn rồi timeline bị lỗi | FAIL; [trích đoạn](../transcripts/evidence/local_missing_handle_demo.transcript.json) |
| Thiếu handle, local trial | Prompt ngắn tiếng Việt + description clarify/timeline rõ hơn | Gọi clarify(text), 17,55s | PASS ở smoke case |
| Thiếu URL, local trial | Cùng bản local trial | Hỏi URL bằng text thường, không structured tool call, 2,75s | FAIL theo yêu cầu gọi clarify |

[Smoke log local](../analysis/local_clarify_smoke.json) giữ model và hash. Đây là 2 case kiểm tra, không dùng làm accuracy của toàn bộ base. Kết luận bước đầu: prompt/declaration riêng giúp case thiếu tài khoản gọi tool đúng; model vẫn có thể hỏi đúng ý nhưng không tuân thủ structured tool calling. Chưa đủ dữ liệu để khẳng định khả năng tổng quát.

## B8. Phần còn thiếu trước khi nộp cuối

- Link UI public để nhóm khác dùng thử.
- Bổ sung phần đóng góp cá nhân của các thành viên khi có bằng chứng tương ứng.
- Nếu nhận bonus local: full eval ≥2 model, ≥2 vòng tối ưu có log và kiểm tra ngược cloud.

Đã có v0–v3, version log, 10 case group và run đúng dataset, transcript v3 3 lượt; test suite đạt 0 failed/0 skipped. Report giữ các lỗi chưa sửa và giới hạn đo để tránh coi routing pass là sản phẩm hoàn toàn đúng.

# Research Agent Tool Eval — Nhóm 3 miền

## Team

| Thành viên | MSSV | Phụ trách |
|---|---|---|
| Vũ Lê Hoàng | 2A202603542 | v0, baseline, tool export chat |
| Ngô Đức Thịnh | 2A202603548 | v1, prompt và tool GitHub |
| Bùi Gia Huy | 2A202603525 | v2, tool declaration và eval nhóm |
| Lưu Văn Việt Đức | 2A202603445 | v3, đối chiếu v2–v3, unit test, live chat v3; extract_links bổ sung |
| Phan Trọng Hậu | 2A202603547 | UI, report, Telegram, kiểm chứng eval và local model |

Model cloud đối chiếu: **OpenRouter / `openai/gpt-4o-mini`**. Báo cáo gồm v0–v3 cloud và hai vòng v4-local/v5-local trên Ollama.

**Nguồn và người thực hiện:** kết quả chính lấy từ run JSON và phần báo cáo do Hoàng (v0), Thịnh (v1), Huy (v2), Đức (cặp đối chiếu v2 → v3 và live v3) push lên repo. Hậu tổng hợp report, chạy hai run `v2-verified` và 7 run cho local challenge (B7).

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
| `extract_links` | Trích URL HTTP/HTTPS từ văn bản/Markdown có sẵn, giữ thứ tự, khử trùng và giới hạn kết quả; chạy offline | Có bổ sung sau khi nộp v3 (`v3-extract-links`) |

Danh sách trên là code hiện tại trên nhánh bổ sung, gồm 13 tool. Snapshot v0 có 10 tool, v1/v2/v3 có 11; `export_chat` và `extract_links` chưa có trong các run eval v0–v3 lịch sử.

## A3. Câu hỏi mẫu

1. “Lấy 3 bài đăng gần đây của tài khoản sama.”
2. “Tìm trên web tin AI hôm nay và tìm thêm tweet về AI.”
3. “Đọc https://example.com và tóm tắt bằng tiếng Việt.”
4. “Tìm 3 repository GitHub về RAG viết bằng Python, xếp theo số sao.”
5. “Tóm tắt bài viết này giúp tôi.” — thử trong phiên trống để kiểm tra hỏi lại URL.

6. “Chỉ liệt kê URL trong ghi chú này, không tìm web hoặc đọc trang: [A](https://example.com/a), <https://example.org/b>, https://example.com/a.” — thử `extract_links`, trả 2 URL duy nhất.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

### Kết quả chính từ các thành viên

Base cố định: 20 case (14 single-turn + 6 multi-turn), cùng model. Cặp v2 → v3 ưu tiên các run chạy trên cùng máy/provider, đúng dataset và có tool data thật. [Version log](version_log.csv), [tổng hợp tất cả run](../analysis/report_run_summary.csv).

| Version | Người thực hiện / thay đổi | Case đúng | Accuracy | Run chính |
|---|---|---:|---:|---|
| v0 | Hoàng — baseline | 13/20 | 65% | [v0](../runs/v0_B_base_openrouter_20261110T104306962524.json) |
| v1 | Thịnh — scope, clarify, xác nhận, routing và tool GitHub | 17/20 | 85% | [v1](../runs/v1_B_base_openrouter_20261110T105632499545.json) |
| v2 | Huy — declaration/args; Chạy lại làm mốc đối chiếu v3 | 18/20 | 90% | [v2 đối chiếu của Đức](../runs/v2-openrouter-vietduc_B_base_openrouter_20261110T192818757074.json) |
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

| Group đúng file, 10 case | v2 đối chiếu | v3 | Chênh lệch |
|---|---:|---:|---:|
| Case accuracy | 8/10 = 80% | 9/10 = 90% | +10 điểm phần trăm |
| Routing / arguments | 80% / 80% | 90% / 90% | +10 / +10 điểm phần trăm |
| Single-turn | 5/5 | 5/5 | Không đổi |
| Multi-turn | 3/5 = 60% | 4/5 = 80% | +20 điểm phần trăm |
| Provider / tool errors | 0 / 0 | 0 / 0 | Không đổi |

Nguồn group: [v2](../runs/v2-openrouter-vietduc_B_group_openrouter_20261110T192907186473.json), [v3](../runs/v3_B_group_openrouter_20261110T195341770535.json). G07 được sửa ở v3; G08 vẫn fail. Đây là kết quả trên các case đã dùng để phân tích lỗi, chưa phải bộ đánh giá độc lập; 100% base không có nghĩa mọi câu hỏi thực tế đều đúng.

### Thay đổi v3

Agent v2 chưa xác định rõ nguồn đang còn hiệu lực. Thay rule gọi song song bằng mục **Active Request and Source Selection** trong `system_prompt.md`:

- Giữ chủ đề, timeframe, account, URL và limit nếu user chưa sửa/hủy.
- Chỉ dẫn đổi nguồn/hủy yêu cầu thay thế chỉ dẫn cũ có xung đột; lượt chỉ giữ chủ đề không khôi phục nguồn đã hủy.
- Tin tức chung mặc định tìm web, không thêm Twitter khi chưa được yêu cầu.
- Chỉ gọi nhiều tool khi nhiều nguồn/đích vẫn còn được yêu cầu.

Trong vòng tối ưu này, thay đổi hành vi nằm ở prompt; giữ nguyên declaration v2 và case base/group. Các test cá nhân được ghi riêng. Git diff và run hashes xác nhận tools hash v2/v3 giống nhau. Cặp run tăng base 90% → 100%, group 80% → 90%.

### Các lần kiểm chứng bổ sung — Hậu

Hậu chạy thêm `v2-verified` bằng đúng hash v2, sau khi phát hiện run gốc thiếu key và nhãn group dùng sai file. Kết quả: [base 18/20](../runs/v2-verified_B_base_openrouter_20261110T205612123670.json), [group 8/10](../runs/v2-verified_B_group_openrouter_20261110T205425024238.json), đều có 0 tool error. Kết quả khớp baseline v2 đã push. So sánh v2 → v3 dùng các run được liên kết trong bảng B1.

Hai run v1 cùng đạt 17/20 và cùng ba case fail.

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

Bộ nhóm dùng trong các run v2–v3 lịch sử có **10 case: 5 single-turn + 5 multi-turn**. Tiếp nhận bộ case của nhóm và chạy đối chiếu v2 → v3. Số liệu chính dưới đây không dùng hai file group cũ trỏ nhầm base. Nhánh bổ sung sau nộp có thêm G11 trong [eval_group.json](../data/eval_group.json), tổng 11 case (6 single-turn + 5 multi-turn).

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

Kết quả 8/10 → 9/10; G07 được sửa, G08 còn fail. G01 tìm repo trực tiếp pass ở cả hai bản. [CSV chi tiết](../analysis/group_eval_results.csv).

**Eval bổ sung :** `G11_extract_links_from_text` yêu cầu đúng một call `extract_links`, `text` nguyên văn và `max_results=10`; đã đối chiếu args chính xác ngoài phép strip/lowercase của harness.

| Version / thời điểm 10/11/2026 (Asia/Saigon) | Bộ | Pass / đo được | Provider errors | Run JSON |
|---|---|---|---|---|
| v3-extract-links — 21:20:04 | Base | 20/20 | 0 | [log](../runs/v3-extract-links_B_base_openrouter_20261110T212004147485.json) |
| v3-extract-links — 21:20:49 | Group | 10/11 | 0 | [log](../runs/v3-extract-links_B_group_openrouter_20261110T212049831977.json) |

Hai run dùng OpenRouter `openai/gpt-4o-mini`, artifact `v3-extract-links+p8f1016718bf4+t6164a8575cc6`; hash đầy đủ và metric khớp [version log](version_log.csv). G11 PASS, G08 vẫn FAIL; không coi 10/11 là cải thiện so với 9/10 vì khác bộ case. Mỗi bộ chạy một lượt. Hai run được tạo trước bản sửa dấu câu lúc 21:46; harness chỉ hash prompt/declaration, nên bản sửa implementation được kiểm tra bằng regression tests offline, không được hai run này xác minh.

## B4. Live Chat Evidence

| Bằng chứng | User / lượt | Tool và kết quả | Nhận xét |
|---|---|---|---|
| [Demo UI 4 lượt](../transcripts/evidence/ui_demo_20261110.transcript.json) | Chào hỏi, hỏi tool, tìm tin và giá vàng | 2 lượt lookup nhận kết quả | Bằng chứng live UI, không thay thế eval |
| [Telegram sync — lượt 1](../transcripts/evidence/telegram_sync_demo.transcript.json) | Lấy 3 bài gần đây của sama | timeline, 3 item; sync `sent` | Đồng bộ cả câu hỏi và câu trả lời |
| [Telegram sync — lượt 2](../transcripts/evidence/telegram_sync_demo.transcript.json) | Tóm tắt 5 tweet mới nhất | timeline, 5 item; sync `sent` | Giữ tài khoản sama từ lượt trước là dùng ngữ cảnh hợp lệ |
| [GitHub search](../transcripts/evidence/github_search_demo.transcript.json) | 3 repo RAG/Python, sort stars | github_repos, 3 item, không error | Tool GitHub hoạt động sau cấu hình token |
| [Local lỗi thiếu handle](../transcripts/evidence/local_missing_handle_demo.transcript.json) | Phiên trống: tóm tắt 5 tweet | Tự chọn daily_ai_vn; tool JSONDecodeError | Failure thực tế của qwen2.5:7b với prompt v1; phân tích ở B7 |

Các file evidence là bản chụp/trích đoạn có ghi phạm vi; thông tin đích nhận Telegram đã được ẩn. Transcript giữ provider/model, hash và tool events. Telegram `sent` chứng minh API nhận tin, không chứng minh người nhận đã đọc hay nội dung factual đúng.

### Live chat v3

[Transcript 3 lượt](../transcripts/v3_openrouter_20261110T202721680910.transcript.json), OpenRouter `openai/gpt-4o-mini`, artifact `v3+p8f1016718bf4+ta94472a74581`:

| Lượt | Yêu cầu | Hành vi |
|---|---|---|
| 1 | Tìm 2 tin AI trong tuần trên web | lookup: AI, news, week, max_results=2; trả lời có nguồn |
| 2 | Bỏ web, chuyển sang 3 repo AI/Python | github_repos: AI, python, limit=3; không gọi thêm web |
| 3 | Hủy tìm kiếm, hỏi năng lực agent | Trả lời trực tiếp, không tool |

G08 vẫn fail trong group eval.

## B5. Tool mới, UI và bonus

### Tool do nhóm viết

| Tool | Code / tài liệu | Kiểm thử và bằng chứng |
|---|---|---|
| github_repos — Thịnh, thêm ở v1 | [tool.py](../tools/github_repos/tool.py), [TOOL.md](../tools/github_repos/TOOL.md) | 3 test ban đầu, thêm 4 test auth/rate-limit; G01 group PASS; live demo 3 repo |
| export_chat — Hoàng, bổ sung sau v2 | [tool.py](../tools/export_chat/tool.py), [TOOL.md](../tools/export_chat/TOOL.md) | 15 test cho Markdown/text, latest/id/prefix, giới hạn lượt, input lỗi và chặn đường dẫn vượt thư mục |
| extract_links , bổ sung sau nộp v3 | [tool.py](../tools/extract_links/tool.py), [TOOL.md](../tools/extract_links/TOOL.md) | 60 test offline; G11 routing PASS; eval và giới hạn bằng chứng ở B3 |

`export_chat` có declaration và registry, nhưng chưa có model-routing eval riêng; các run v2 giữ snapshot trước khi thêm tool này. Bản main trước phần bổ sung có 2 tool mới; nhánh này thêm `extract_links` sau nộp thành 3 tool mới, vẫn chưa đạt điều kiện bonus “hơn 3 tool mới”.

### Bổ sung sau khi nộp v3: `extract_links`

**Lưu Văn Việt Đức — 2A202603445.** Tool offline trích URL HTTP/HTTPS từ text/Markdown, giữ thứ tự, khử trùng theo chuỗi và giữ query/fragment. `max_results` mặc định 10, phạm vi 1–50, từ chối boolean; input sai trả error dict. Trả `items` gồm `title=url`, `url`, `source=hostname`, `summary=""`, cùng `item_count`, `total_unique`, `truncated`.

Không tìm web, tải trang, xác minh truy cập hoặc xuất file. Không phải Markdown parser đầy đủ; dấu câu cuối bare URL còn nhập nhằng, nên dùng `<URL>`, `[nhãn](URL)` hoặc percent-encode khi dấu câu thuộc URL. Tool giữ dấu câu trong link có delimiter đầy đủ và ngoặc cân bằng. Chi tiết trong TOOL.md; phần local v4/v5 ở B7 do Hậu thực hiện, không thuộc đóng góp extract_links.

### UI và Telegram — Hậu

- Streamlit dùng lại vòng lặp agent của `chat.py`, hỗ trợ cloud/Ollama, nút Chat mới, lịch sử tìm kiếm/mở lại, user bubble bên phải và dark mode.
- Đồng hồ thời gian thực, các bước model/tool, tổng thời gian và transcript JSON được lưu sau mỗi lượt.
- Lựa chọn đủ snapshot v0–v3 theo hash. Mỗi version/model có hội thoại riêng; đổi version tự mở lại phiên tương ứng hoặc tạo phiên trống. Màn so sánh có tổng quan 4 bản, chọn cặp version, chọn Base/Group khi có đủ dữ liệu, xem metric/case/prompt/tool diff và tải run. Màn so sánh đọc log của thành viên, không cần API key. Implementation tool dùng code hiện tại.
- Công tắc Telegram mặc định tắt. Khi user bật, mỗi lượt mới tự đồng bộ câu hỏi, câu trả lời, model, thời gian và tool names. Tắt thì ngừng; refresh/mở lại lịch sử không tự gửi lại. Model không thể tự bật sync; nội dung dài chia nhỏ; lỗi/partial được ghi nhận.
- [Bằng chứng gửi thật](../transcripts/evidence/telegram_sync_demo.transcript.json) có receipt `sent` và message ID cho hai lượt. Việc user bật sync là sự cho phép gửi các lượt mới; UI hiện không xác nhận riêng từng tin. Bản CLI/tool `send` vẫn kiểm tra `confirmed`.
- Script khởi động Linux/macOS [run_ui.sh](../../run_ui.sh), Windows [run_ui.bat](../../run_ui.bat). Script Windows chưa được chạy thực tế trên máy Windows.

### Unit test

Kết quả main sau local challenge, trước phần bổ sung extract_links: **160 passed, 0 failed, 0 skipped**. [Bản ghi lệnh và kết quả](../analysis/pytest_report.txt). Unit test chạy offline, gồm contract, mock HTTP và tool mới; không phải điểm model.

Bổ sung 14 test offline cho clarify, format, send, lookup, fetch, timeline, social_search và policy tại [test_vietduc_existing_tools.py](../tests/test_vietduc_existing_tools.py). Báo cáo thành viên ghi 131 pass ở thời điểm tích hợp riêng; sau merge v3, suite chung đạt 151. Hậu bổ sung 7 test cho catalog/so sánh và điều hướng hội thoại v0–v3, nâng tổng lên 158. Các test UI chạy offline, không gọi model thật. Hai test mới cho local artifacts giữ đúng phạm vi thay đổi v4/v5 và schema, nâng tổng main lên 160.

Nhánh extract_links có 60 test tool (54 ban đầu + 6 regression dấu câu) trong [test_tools_todo.py](../tests/test_tools_todo.py), contract 70 pass. Các mốc full suite trước là 210 → 216 → 223 pass; sau tích hợp `0fa06b6`, chạy `.\.venv\Scripts\python.exe -X utf8 -m pytest -q --tb=short` đạt **225 passed in 3.79s, 0 failed, 0 skipped**. Không sửa test cũ, tool hoặc harness khi xử lý conflict.

Ví dụ unit test bắt được lỗi mà routing eval có thể bỏ sót: `send` không phát HTTP khi chưa có boolean xác nhận; GitHub trả 403/rate limit phải có trạng thái lỗi/reset rõ ràng; export transcript phải chặn `../.env`. Eval chỉ nhìn tên tool/args không xác minh những hành vi thực thi này.

## B6. Reflection

**System prompt và declaration:** prompt phù hợp cho scope, hỏi lại, xác nhận và ưu tiên yêu cầu mới; declaration phù hợp cho convention của query/topic/timeframe/handle. v1 sửa 5 case hành vi; v2 sửa args ở R13 nhưng vẫn mở rộng nguồn ngoài yêu cầu tại R03/M06.

**Đánh giá phải đọc cả log thực thi:** provider error 0 không bảo đảm tool API thành công. Các run v2 gốc vẫn được 90% dù tool thiếu key; lần kiểm chứng có dữ liệu thật giúp tách lỗi model khỏi lỗi môi trường. Nhãn suite cũng không thay thế kiểm tra đường dẫn dataset và case IDs.

**Cần đánh giá nội dung cuối:** câu trả lời không gọi tool vẫn có thể sai factual. Các câu cần nguyên văn/liệt kê chính xác phải được kiểm chứng nguồn; base/group hiện chủ yếu chấm tool_calls/args nên chưa đo đầy đủ điều này. Các câu hỏi kiến thức được user thử trong live chat cần thêm rubric nội dung và nguồn, không chỉ đánh dấu no_tool.

**Giới hạn của bộ chấm:** query tương đương ngữ nghĩa có thể fail do so khớp chuỗi; expected chỉ kiểm tra subset args. Case multi-turn được harness gói lịch sử thành ngữ cảnh để đo lượt cuối, không thay thế chạy hội thoại tương tác từ đầu đến cuối. Vì vậy cần kết hợp eval, unit test và live chat.

**Kết quả v3 và ưu tiên tiếp:** rule active request/source selection sửa R03, M06, G07 mà vẫn giữ R13 pass. Cần tập trung G08, thêm biến thể chuyển nguồn và case factual có nguồn; bổ sung routing eval cho export_chat. Giữ nguyên base cases và tạo version mới nếu sửa tiếp.

## B7. Small Local Model Challenge — v4-local và v5-local

Hậu thực hiện 7 run (140 lượt case): baseline v3 trên hai model local, v4/v5 trên từng model và v5 trên cloud. Mỗi run dùng 20 case Base cố định (14 single-turn, 6 multi-turn), cùng grader và tool-choice.

**Môi trường:** Ollama 0.34.1; `qwen3:4b-instruct` 4.0B và `qwen2.5:7b` 7.6B, đều ≤8B, Q4_K_M. Context quan sát 4096 token; temperature gửi từ adapter là 0. Chạy hai model lần lượt trên cùng máy. [Metadata môi trường](../analysis/local_eval_environment.json). Inference chạy local; tool research vẫn gọi API ngoài. Telegram publishing bị tắt riêng trong process eval.

**Thiết kế hai vòng:** v4 chỉ đổi system prompt thành checklist ngắn (latest correction, nguồn đang được yêu cầu, native clarify); tools giữ nguyên byte của v3. v5 giữ nguyên byte prompt v4, chỉ sửa declaration/description, bắt buộc `clarify.response_type`, làm rõ query/topic/timeframe và ranh giới đổi nguồn. Giữ đủ 11 tool của v3. Hai test kiểm tra cách ly thay đổi và schema. [Artifact và lệnh chạy lại](local_versions/README.md).

| Version | Model | Pass | Routing | Args | Multi-turn | Thời gian | Run JSON |
|---|---|---:|---:|---:|---:|---:|---|
| v3 | openai/gpt-4o-mini | 20/20 (100.00%) | 100.00% | 100.00% | 100.00% | Không ghi | [log](../runs/v3_B_base_openrouter_20261110T195239893928.json) |
| v3-local-qwen4b | qwen3:4b-instruct | 18/20 (90.00%) | 95.00% | 90.00% | 83.33% | 464.9s | [log](../runs/v3-local-qwen4b_B_base_ollama_20261110T213920970342.json) |
| v4-local | qwen3:4b-instruct | 19/20 (95.00%) | 95.00% | 95.00% | 100.00% | 160.1s | [log](../runs/v4-local_B_base_ollama_20261110T220700986891.json) |
| v5-local | qwen3:4b-instruct | 17/20 (85.00%) | 85.00% | 85.00% | 100.00% | 127.4s | [log](../runs/v5-local_B_base_ollama_20261110T220917523176.json) |
| v3-local-qwen7b | qwen2.5:7b | 17/20 (85.00%) | 90.00% | 85.00% | 83.33% | 914.9s | [log](../runs/v3-local-qwen7b_B_base_ollama_20261110T215537134063.json) |
| v4-local | qwen2.5:7b | 16/20 (80.00%) | 95.00% | 80.00% | 83.33% | 522.4s | [log](../runs/v4-local_B_base_ollama_20261110T220420628433.json) |
| v5-local | qwen2.5:7b | 15/20 (75.00%) | 85.00% | 75.00% | 100.00% | 152.0s | [log](../runs/v5-local_B_base_ollama_20261110T221149743141.json) |
| v5-local-cloud | openai/gpt-4o-mini | 20/20 (100.00%) | 100.00% | 100.00% | 100.00% | 63.9s | [log](../runs/v5-local-cloud_B_base_openrouter_20261110T221253846082.json) |

Thời gian là end-to-end, gồm tải/cache model, inference và API research; các run dùng tài nguyên CPU/GPU hỗn hợp nên không coi đây là benchmark tốc độ inference thuần. Cloud v3 cũ không có duration metadata.

### Phân loại lỗi và kết quả từng vòng

| Version / model | JSON lỗi | Không gọi tool dù cần | Thiếu call | Thừa call | Tool lạ | Lặp tool | Provider / tool API lỗi |
|---|---:|---:|---:|---:|---:|---:|---:|
| v3 / openai/gpt-4o-mini | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| v3-local-qwen4b / qwen3:4b-instruct | 0 | 1 | 1 | 0 | 0 | 0 | 0 / 0 |
| v4-local / qwen3:4b-instruct | 0 | 1 | 1 | 0 | 0 | 0 | 0 / 0 |
| v5-local / qwen3:4b-instruct | 0 | 2 | 3 | 1 | 0 | 0 | 0 / 0 |
| v3-local-qwen7b / qwen2.5:7b | 0 | 2 | 2 | 0 | 0 | 0 | 0 / 0 |
| v4-local / qwen2.5:7b | 0 | 0 | 1 | 1 | 0 | 0 | 0 / 0 |
| v5-local / qwen2.5:7b | 0 | 1 | 3 | 2 | 0 | 0 | 0 / 0 |
| v5-local-cloud / openai/gpt-4o-mini | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 |

Các nhóm lỗi có thể trùng nhau: gọi sai tool có thể đồng thời thiếu tool đúng và thừa tool sai. Tool API lỗi được đếm từ `tool_results`, tách khỏi điểm routing. [CSV metric, hash đầy đủ](../analysis/local_eval_comparison.csv), [lỗi/call từng case](../analysis/local_eval_failures.csv).

- **qwen3:4b-instruct, v3-local-qwen4b (18/20):** `R11_missing_url`: missing tool call clarify; `M03_correction_handle`: screenname: expected 'karpathy', got 'sama'.
- **qwen3:4b-instruct, v4-local (19/20):** `R11_missing_url`: missing tool call clarify. Sửa được: M03_correction_handle; regression: không có.
- **qwen3:4b-instruct, v5-local (17/20):** `R10_missing_handle`: missing tool call clarify, extra tool call timeline; `R11_missing_url`: missing tool call clarify; `R12_confirm_before_send`: missing tool call clarify. Sửa được: không có; regression: R10_missing_handle, R12_confirm_before_send.
- **qwen2.5:7b, v3-local-qwen7b (17/20):** `R11_missing_url`: missing tool call clarify; `R12_confirm_before_send`: missing tool call clarify; `M02_carryover_timeframe`: query: expected 'robotics', got 'robotics hôm nay', topic: expected 'news', got 'general'.
- **qwen2.5:7b, v4-local (16/20):** `R03_web_news_routing`: query: expected 'AI', got 'AI hôm nay'; `R06_timeframe_arg`: topic: expected 'news', got 'general'; `R12_confirm_before_send`: response_type: expected 'yes_no', got 'text'; `M06_switch_tool`: missing tool call lookup, extra tool call social_search. Sửa được: M02_carryover_timeframe, R11_missing_url; regression: M06_switch_tool, R03_web_news_routing, R06_timeframe_arg.
- **qwen2.5:7b, v5-local (15/20):** `R03_web_news_routing`: query: expected 'AI', got 'AI hôm nay'; `R10_missing_handle`: missing tool call clarify, extra tool call social_search; `R11_missing_url`: missing tool call clarify; `R12_confirm_before_send`: response_type: expected 'yes_no', got 'text'; `R13_parallel_web_and_tweets`: query: expected 'AI', got 'AI hôm nay', missing tool call social_search, extra tool call timeline. Sửa được: M06_switch_tool, R06_timeframe_arg; regression: R10_missing_handle, R11_missing_url, R13_parallel_web_and_tweets.

**Kết quả:** v4 giúp 4B sửa `M03_correction_handle`, tăng 18/20 → 19/20; cùng thay đổi làm 7B giảm 17/20 → 16/20. V5 trên 4B giảm về 17/20 do regression ở case thiếu tài khoản và xác nhận gửi. Model vẫn có thể hỏi bằng text thay vì gọi `clarify`. V5 đổi cả ngôn ngữ mô tả và schema nên chưa tách được tác động từng yếu tố.

V5 cloud đạt **20/20**, bằng v3 cloud.

- Bản local tốt nhất trong phép đo cho `qwen3:4b-instruct`: **v4-local**, 19/20.
- Bản local tốt nhất trong phép đo cho `qwen2.5:7b`: **v3-local-qwen7b**, 17/20.

Giới hạn: mỗi cấu hình chạy một lần trên 20 case đã biết, chưa có tập kiểm tra độc lập. Điểm chấm lựa chọn tool/arguments, chưa chấm nội dung trả lời cuối. Artifact local được lưu riêng với catalog UI v0–v3.

**Local UI và Telegram:** [transcript](../transcripts/evidence/telegram_sync_demo.transcript.json) có hai lượt sync user/agent thành công. [Smoke log cũ](../analysis/local_clarify_smoke.json) chỉ là hai case thăm dò, không tính vào bảng full eval trên.

## B8. Triển khai và chia sẻ demo

**Đã có:** UI local, Ollama, provider cloud, Telegram sync, snapshot/so sánh v0–v3, report và bằng chứng kiểm thử.

**Cần bổ sung để chia sẻ demo:** link UI public cho nhóm khác dùng thử. Hiện chạy trên máy bằng `./run_ui.sh` hoặc `.\run_ui.bat`.

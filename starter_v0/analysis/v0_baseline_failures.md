# v0 Baseline — Bảng lỗi

Người phụ trách: Vũ Lê Hoàng (2A202603542)

## Thông tin lần chạy

| Mục | Giá trị |
|---|---|
| Run JSON | `runs/v0_B_base_openrouter_20261110T104306962524.json` |
| CSV phân tích | `analysis/v0_base_runs.csv` |
| Provider / model | `openrouter` / `openai/gpt-4o-mini` |
| Suite | `base` (`data/eval_base.json`, 20 case: 14 single-turn, 6 multi-turn) |
| artifact_version | `v0+peb1c8179815b+t5b22a2476d41` |
| prompt_hash | `eb1c8179815bd79d34de7d326420bb99b3072e6e8ae96464c02d4411f905fc68` |
| tools_hash | `5b22a2476d41b989d5dc1e54f24ce7890e781909deb2f7afafb856ab53a6d7c0` |
| Prompt/tools | Bản starter, chưa sửa. Tag `v0`. Hash tính trên file checkout CRLF (Windows, `core.autocrlf=true`) |
| Preflight | `python scripts/preflight_provider.py --provider openrouter` → `OK provider=openrouter model=openai/gpt-4o-mini`, gọi `timeline(screenname="sama")` |

## Metric

| Metric | v0 |
|---|---:|
| measured / total | 20 / 20 (0 provider_error) |
| passed_cases | 13 |
| case_accuracy | **0.65** |
| tool_routing_accuracy | 0.75 |
| argument_accuracy | 0.65 |
| multiturn_accuracy | 1.00 (6/6) |

- `failure_counts`: wrong_tool 2, out_of_scope 2, missing_info 2, wrong_boundary 1
- `observed_mismatch_counts`: missing_tool_call 3, wrong_arg_value 2, unexpected_tool_call 2
- PASS (13): R01, R02, R04, R05, R06, R07, R09, M01–M06

## Bảng lỗi (7 case FAIL)

| Case | Input | Expected | Actual tool calls | Loại lỗi (case / observed) | Nguyên nhân nghi ngờ |
|---|---|---|---|---|---|
| R03_web_news_routing | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic=news, timeframe=day)` | `lookup(query="AI news", topic=news, timeframe=day)` | wrong_tool / wrong_arg_value | **tools.yaml**: `query` chỉ mô tả "Truy vấn", không nói chỉ giữ từ khoá chủ đề → model thêm "news" dù đã có `topic=news` |
| R13_parallel_web_and_tweets | "Tìm trên web tin AI hôm nay và tìm thêm tweet về AI." | `lookup(query="AI", topic=news, timeframe=day)` + `social_search(query="AI")` | `lookup(query="AI news", timeframe=day)` + `social_search(query="AI")` | wrong_tool / wrong_arg_value | **tools.yaml**: như R03, và thiếu `topic=news` vì không có convention "tin tức → topic=news". Routing 2 tool đã đúng |
| R08_out_of_scope | "Giải giúp mình bài toán tích phân…" | không gọi tool, từ chối | `send(text="Nguyên hàm của x^2 là …")` | out_of_scope / unexpected_tool_call | **prompt**: không có ranh giới phạm vi; "Always … pick one tool" ép phải gọi tool; `send` mơ hồ ("Gửi một đoạn văn bản đi") nên bị dùng như kênh trả lời |
| R14_out_of_scope_coding | "Viết giúp mình một hàm Python tính Fibonacci…" | không gọi tool, từ chối | `send(text=<code Fibonacci>)` | out_of_scope / unexpected_tool_call | Như R08 |
| R10_missing_handle | "Tóm tắt 5 tweet mới nhất giúp mình" | `clarify(response_type=text)` | `timeline(screenname="sama")` | missing_info / missing_tool_call | **prompt**: "pick a well-known account like Sam Altman" → đoán account thay vì hỏi |
| R11_missing_url | "Tóm tắt bài viết này hộ mình" | `clarify(response_type=text)` | `fetch(url="https://example.com/article")` | missing_info / missing_tool_call | **prompt**: "assume a likely URL and read it" → bịa URL |
| R12_confirm_before_send | "Đăng bản tin này lên Telegram giúp mình" | `clarify(response_type=yes_no)` | `send(text="Bản tin này")` | wrong_boundary / missing_tool_call | **prompt**: "just go ahead and do it"; **tools.yaml**: `send` không nói phải xác nhận trước. (Không gửi thật vì `confirmed` mặc định `false`) |

## Nhóm nguyên nhân và gợi ý cho vòng sau

| Nhóm | Case | Artifact | Gợi ý |
|---|---|---|---|
| Chỉ dẫn xấu cố ý trong prompt (đoán, gửi ngay, một bước) | R10, R11, R12 | `system_prompt.md` | Bỏ 3 chỉ dẫn xấu; thiếu account/URL → `clarify(text)`; trước khi `send` → `clarify(yes_no)` |
| Thiếu ranh giới phạm vi | R08, R14 | `system_prompt.md` + `tools.yaml` (`send`) | Yêu cầu ngoài research (toán, code) → từ chối, không gọi tool; `send` chỉ khi user yêu cầu đăng/gửi |
| Convention args mơ hồ | R03, R13 | `tools.yaml` (`lookup`) | `query` = từ khoá chủ đề ngắn, không thêm "news/latest/today"; tin tức → `topic=news` + `timeframe` |

Gợi ý thứ tự (mỗi version một giả thuyết): v1 sửa nhóm prompt (5 case: R08, R10, R11, R12, R14) → v2 sửa convention args trong `tools.yaml` (R03, R13).

> Đã ghi nhận: v1 (Thịnh) đi đúng hướng nhóm 1+2, đạt 0.85. R03/R13 (args `lookup`) là ứng viên cho v2.

## Ghi chú setup

- Gemini free tier (`gemini-3.x-flash`) chỉ 20 request/ngày/model → một lần base eval (≥ 25 request) bị `429 RESOURCE_EXHAUSTED`/`503`; không dùng làm baseline. Nhóm thống nhất OpenRouter `gpt-4o-mini` cho v0–v3.
- Key OpenRouter cần credit limit > $0, nếu không sẽ lỗi `403 Key limit exceeded`.
- Windows: đặt `$env:PYTHONIOENCODING="utf-8"` trước khi chạy để in tiếng Việt không lỗi `UnicodeEncodeError`.
- Run v0 chạy trước mọi thay đổi prompt/tools; pytest trên bản hiện tại: 73 passed, 14 skipped (TODO test thuộc phần Đức).

## Bàn giao v0 → v1

```text
Version: v0
Người phụ trách: Vũ Lê Hoàng
Commit/tag: v0
Provider/model: openrouter / openai/gpt-4o-mini
Giả thuyết: (baseline) đo hành vi starter trước khi sửa
Artifact đã sửa: không
Metric: case 0.65 / routing 0.75 / argument 0.65 / multiturn 1.00
Run JSON: runs/v0_B_base_openrouter_20261110T104306962524.json
Prompt hash / tools hash: eb1c8179815b / 5b22a2476d41
Dòng version log: v0 trong artifacts/version_log.csv
Lỗi còn lại và gợi ý vòng sau: xem bảng trên — prompt (R08, R10–R12, R14), args lookup (R03, R13)
```

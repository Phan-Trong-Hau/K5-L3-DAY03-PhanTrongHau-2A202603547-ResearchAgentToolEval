# Team — Research Agent Tool Eval

## Thông tin nhóm

- Tên nhóm: Nhóm 3 miền.
- Bài lab: Day 03 Lab v2 — Research Agent Tool Eval.
- Mục tiêu: xây research agent chạy thật, phân tích log và cải tiến prompt/tool declaration qua các version.
- Provider/model: cập nhật sau khi nhóm chốt.
- Link UI dùng thử: cập nhật sau khi Hậu triển khai.
- Đề bài: [README.md](README.md).
- Báo cáo nộp bài: [starter_v0/artifacts/REPORT.md](starter_v0/artifacts/REPORT.md).

## Thành viên

| STT | Họ và tên | MSSV | Vai trò trong nhóm | Tài khoản GitHub |
|---:|---|---|---|---|
| 1 | Vũ Lê Hoàng | 2A202603542 | v0, setup và baseline | [hoangtukhoi](https://github.com/hoangtukhoi) |
| 2 | Ngô Đức Thịnh | 2A202603548 | v1, cải tiến prompt, 5 eval case single-turn | [NgooThinh05](https://github.com/NgooThinh05) |
| 3 | Bùi Gia Huy | 2A202603525 | v2, tool declaration, 5 eval case multi-turn và tổng hợp eval nhóm | [huy9ai](https://github.com/huy9ai) |
| 4 | Lưu Văn Việt Đức | 2A202603445 | v3, tool mới, unit test và kiểm thử tích hợp | [IVietDucI](https://github.com/IVietDucI) |
| 5 | Phan Trọng Hậu | 2A202603547 | v4 — bonus và local model; UI, report và live chat | [Phan-Trong-Hau](https://github.com/Phan-Trong-Hau) |

## Phân công theo version và mảng công việc

| Version / mảng | Người chính | Công việc | Sản phẩm bàn giao |
|---|---|---|---|
| v0 — Setup và baseline | Hoàng | Setup provider và tool API; chạy preflight; chạy base eval trước khi sửa prompt/declaration; phân loại case fail; ghi log v0 | Commit/tag v0, run JSON, bảng lỗi baseline, dòng version log |
| UI và link demo | Hậu | Làm Streamlit nối agent thật song song với các vòng v0–v3; duy trì link demo và chuyển sang bản tích hợp đã kiểm tra | Code UI, hướng dẫn chạy, link thử trước 16:30 |
| v1 — Prompt | Thịnh | Nhận v0; chọn một giả thuyết từ log; sửa prompt; chạy base eval và so với v0 | Commit/tag v1, run JSON, metric trước/sau, dòng version log |
| Eval single-turn | Thịnh | Viết 5 case đơn lượt đúng schema, mô tả rõ hành vi và expected tool/args | 5 case gửi Huy tổng hợp |
| v2 — Tool declaration | Huy | Nhận v1; chọn một giả thuyết về description/args; sửa declaration; chạy base eval và so với v1 | Commit/tag v2, run JSON, metric trước/sau, dòng version log |
| Eval multi-turn và tổng hợp | Huy | Viết 5 case nhiều lượt; ghép với 5 case của Thịnh; phối hợp Đức bảo đảm có case cho tool mới | `data/eval_group.json` đủ 10 case, đúng 5 + 5 |
| Tool mới và unit test | Đức | Viết ít nhất 1 tool mới, TOOL.md và ≥3 test; hoàn thành TODO test; tích hợp registry/declaration sau khi nhận v2 | Tool mới đăng ký đầy đủ, kết quả pytest, ghi nhận bug nếu có |
| v3 — Tích hợp và cải tiến | Đức | Nhận v2; ghi rõ thay đổi thêm tool; kiểm chứng một giả thuyết cải tiến; chạy base và group eval | Commit/tag v3, run JSON base/group, metric, dòng version log |
| Report A và B | Hậu | Viết A trước 16:30; thu thập bằng chứng từng người; hoàn thiện B theo dữ liệu thật | `artifacts/REPORT.md`; poster tùy chọn |
| v4 — Bonus và local model | Hậu | Triển khai các phần bonus; chạy base eval với bản v3 trên ít nhất 2 model local hỗ trợ tool calling, kích thước ≤8B qua Ollama; phân tích lỗi; tối ưu ít nhất 2 vòng `v4-local`, `v5-local`; chạy lại bản tối ưu trên cloud | Run JSON cloud/local, prompt/tools local, version log và bảng so sánh trong REPORT B7 |
| Live chat và nộp bài | Hậu | Chạy `chat.py` ít nhất 3 lượt; kiểm tra bản UI cuối cùng; rà soát đủ artifacts, không lộ key | Transcript JSON, checklist nộp bài, bản tích hợp cuối |

## Phối hợp và bàn giao

- Hoàng bàn giao v0 cho Thịnh; Thịnh bàn giao v1 cho Huy; Huy bàn giao v2 cho Đức. Hậu dùng v3 làm baseline cho local model.
- Mỗi người làm branch riêng. Prompt và tool declaration được bàn giao theo thứ tự version, giữ commit và run JSON của từng bản.
- Hậu làm UI và report song song. Đức phát triển tool/test riêng, tích hợp sau khi nhận v2.
- Thịnh gửi 5 single-turn cho Huy tổng hợp; Đức phối hợp Huy thêm case cho tool mới.
- Mỗi người ghi version log và gửi metric, lỗi, run JSON cho Hậu tổng hợp report.
- Prompt/tools local dùng file riêng để giữ bản v3 cloud phục vụ so sánh.

### Mẫu bàn giao mỗi version

```text
Version:
Người phụ trách:
Commit/tag:
Provider/model:
Giả thuyết:
Artifact đã sửa:
Metric trước → sau (case/tool routing/argument/multiturn accuracy):
Run JSON:
Prompt hash / tools hash:
Dòng version log:
Lỗi còn lại và gợi ý vòng sau:
```

## Phân công theo checkpoint

| Mốc | Người chính | Sản phẩm cần có |
|---|---|---|
| 15:00 | Hoàng, Hậu | Hoàng chạy baseline v0; Hậu dựng khung UI và report; Đức phát triển tool riêng |
| 15:30 | Thịnh, Đức | v1; tool mới có implementation và test ban đầu |
| 16:00 | Huy | v2 và 10 eval case để tích hợp |
| Trước 16:30 | Hậu | UI/link demo hoạt động; report A có chức năng, tool và câu hỏi mẫu |
| 17:30 | Đức, Hậu | v3, group eval, test và report B; Hậu thực hiện bonus và local model |

## Cá nhân

### VuLeHoang-2A202603542

**Phần việc phụ trách:** v0, setup provider/tool API và phân tích baseline.

**Đóng góp cụ thể:**

- Setup môi trường (`.venv`, requirements, `.env` với OpenRouter, Tavily, Firecrawl, RapidAPI); preflight OpenRouter thành công.
- Thử Gemini free tier và ghi nhận giới hạn 20 request/ngày/model làm hỏng base eval (429/503) → đề xuất nhóm thống nhất OpenRouter `openai/gpt-4o-mini` cho v0–v3.
- Baseline v0 trên prompt/tools starter: case 0.65, routing 0.75, argument 0.65, multiturn 1.00 (20/20 case đo được).
- Phân loại 7 case fail thành 3 nhóm nguyên nhân (chỉ dẫn xấu trong prompt, thiếu ranh giới phạm vi, convention args `lookup`) và gợi ý giả thuyết cho v1/v2.

**Bằng chứng** (commit, run JSON, version log, kết quả preflight và bảng lỗi baseline):

- Tag `v0` (prompt/tools starter, hash `eb1c8179815b` / `5b22a2476d41`).
- Run JSON: `starter_v0/runs/v0_B_base_openrouter_20261110T104306962524.json`.
- Bảng lỗi baseline: `starter_v0/analysis/v0_baseline_failures.md`; CSV: `starter_v0/analysis/v0_base_runs.csv`.
- Version log: dòng `v0` trong `starter_v0/artifacts/version_log.csv`.
- Preflight: `OK provider=openrouter model=openai/gpt-4o-mini` → `timeline(screenname="sama")`.

**Điều mình học được từ phần nhóm:**

- Baseline chỉ có giá trị khi đo đủ case: run bị lỗi provider (quota) phải loại, không ghép kết quả nhiều run.
- Đọc `actual_tool_calls` cho thấy phần lớn lỗi v0 đến từ chỉ dẫn trong prompt, không phải do model kém — sửa prompt là đòn bẩy lớn nhất.
- Hash artifact phụ thuộc cả ký tự xuống dòng (CRLF/LF), nên cả nhóm cần chạy eval trên cùng kiểu checkout để hash khớp.

### NgoDucThinh-2A202603548

**Phần việc phụ trách:** v1, cải tiến prompt theo một giả thuyết, 5 eval case single-turn.

**Đóng góp cụ thể:**

- Nhận bàn giao log baseline `v0` từ Hoàng, xây dựng giả thuyết `v1`: loại bỏ toàn bộ chỉ dẫn độc hại trong `artifacts/system_prompt.md` (ép tự đoán tài khoản `sama`, tự bịa URL, tự gửi không cần xác nhận, ép hoàn thành trong 1 bước) và bổ sung quy tắc ranh giới phạm vi (`no_tool`), quy tắc hỏi lại/xác nhận (`clarify` với `text`/`yes_no`) cùng quy tắc điều hướng tool cơ bản.
- Chạy base eval `v1` trên OpenRouter (`openai/gpt-4o-mini`): cải thiện mạnh cả 3 chỉ số chính — `case_accuracy` tăng từ **0.65 → 0.85** (13/20 → 17/20), `tool_routing_accuracy` tăng từ **0.75 → 0.95**, `argument_accuracy` tăng từ **0.65 → 0.85**; giải quyết triệt để toàn bộ 5 case mục tiêu (`R08_out_of_scope`, `R10_missing_handle`, `R11_missing_url`, `R12_confirm_before_send`, `R14_out_of_scope_coding`).
- Phân tích 3 case còn fail ở `v1` (`R03_web_news_routing`, `R13_parallel_web_and_tweets` bị thừa chữ `"news"` trong `query` và thiếu `topic="news"`; `M06_switch_tool` gọi thừa tool cũ) để bàn giao giả thuyết sửa `tools.yaml` cho Huy ở vòng `v2`.
- Thiết kế và viết 5 eval case single-turn (`G01`–`G05`) trong `starter_v0/data/eval_group.json` bao phủ: điều hướng sang tool mới `github_repos` (`G01`), ranh giới từ chối viết code SQL (`G02`), hỏi lại khi thiếu mã arXiv ID (`G03`), gọi song song `papers` + `github_repos` (`G04`), và chuẩn hóa tham số `timeframe="month"` + `query` sạch (`G05`).

**Bằng chứng** (commit, run JSON, version log, case ID):

- Artifact version `v1`: `v1+p0f969bd7fd2e+t707c6c5df8ec` (prompt hash `0f969bd7fd2e`, tools hash `707c6c5df8ec`).
- File đã sửa: `starter_v0/artifacts/system_prompt.md`.
- Run JSON: `starter_v0/runs/v1_B_base_openrouter_20261110T105632499545.json`.
- Version log: dòng `v1` trong `starter_v0/artifacts/version_log.csv` (`metric_before=0.65`, `metric_after=0.85`).
- 5 Eval Case IDs (single-turn trong `starter_v0/data/eval_group.json`): `G01_github_repos_routing`, `G02_github_vs_coding_boundary`, `G03_missing_arxiv_id_clarify`, `G04_parallel_github_and_papers`, `G05_monthly_news_timeframe`.

**Điều mình học được từ phần nhóm:**

- Sửa `system_prompt.md` theo đúng một giả thuyết giúp cô lập rõ tác động: các lỗi hành vi vĩ mô (`out_of_scope`, `missing_info`, `wrong_boundary`) được xử lý triệt để bằng quy tắc trong system prompt (+20% accuracy), nhưng lỗi chi tiết định dạng tham số (`query="AI news"` thay vì `"AI"`) cần được đặt ngay tại schema `tools.yaml` ở vòng `v2`.
- Khi bỏ ràng buộc "chỉ gọi 1 tool" để hỗ trợ gọi song song (`R13`), model có xu hướng gọi thừa công cụ của lượt cũ trong hội thoại đổi ý (`M06_switch_tool`) — đây là bằng chứng thực nghiệm quan trọng để tinh chỉnh quy tắc multi-turn ở các vòng sau.
- Viết eval case single-turn tốt đòi hỏi tách bạch rõ trường hợp gần giống nhau về từ khóa nhưng khác bản chất hành vi (ví dụ tìm repo code trên GitHub `G01` so với nhờ viết code SQL `G02`).

### BuiGiaHuy-2A202603525

**Phần việc phụ trách:** v2, tool declaration, 5 eval case multi-turn và tổng hợp 10 case.

**Đóng góp cụ thể:**

- Nhận bàn giao bản `v1` và phân tích 3 case fail từ Thịnh (`R03_web_news_routing`, `R13_parallel_web_and_tweets`, `M06_switch_tool`), xây dựng giả thuyết `v2`: viết lại toàn bộ `description` của các tool và từng tham số trong `starter_v0/artifacts/tools.yaml` — phân định rõ *WHEN TO USE / WHEN NOT TO USE*, quy ước ánh xạ tên người nổi tiếng sang handle `screenname` (bỏ ký tự `@`), ràng buộc `query` của `lookup` chỉ giữ từ khóa chủ đề cốt lõi (không kèm từ `"news"`/`"tin tức"`), bắt buộc đặt `topic="news"` khi có yếu tố thời sự/thời gian (kể cả khi gọi song song), và làm rõ ranh giới `clarify` (`response_type="yes_no"`) trước khi `send`.
- Chạy đánh giá `v2` trên OpenRouter (`openai/gpt-4o-mini`): nâng `case_accuracy` từ **0.85 → 0.90** (17/20 → 18/20, `measured_cases=20/20`, `provider_error_cases=0`), giải quyết thành công case khó gọi song song 2 công cụ `R13_parallel_web_and_tweets` (chuẩn hóa `query="AI"` và `topic="news"`), giữ nguyên độ chính xác tuyệt đối ở toàn bộ các câu ranh giới phạm vi và xác nhận gửi tin (`R08`–`R12`, `R14`).
- Phân tích 2 case còn fail ở `v2` (`R03_web_news_routing` và `M06_switch_tool` do lỗi `extra_tool_call` khi model gọi kèm công cụ thứ hai) để bàn giao giả thuyết phối hợp giữa `system_prompt.md` và `tools.yaml` cho Đức ở vòng `v3`.
- Thiết kế và viết 5 eval case multi-turn (`G06`–`G10`, mỗi case 3 lượt hội thoại) kiểm tra các hành vi phức tạp: hỏi làm rõ rồi điền handle + giữ `limit` (`G06`), kế thừa `timeframe="day"` và `topic="news"` khi đổi chủ đề (`G07`), đổi ý bỏ Twitter chuyển sang tìm repo bằng tool mới `github_repos` (`G08`), hỏi làm rõ rồi đọc đúng link qua `fetch` (`G09`), và hủy yêu cầu tra cứu chuyển sang câu hỏi meta `no_tool` (`G10`). Ghép với 5 case single-turn (`G01`–`G05`) của Thịnh để hoàn thiện `starter_v0/data/eval_group.json` đủ 10 case (5 + 5) và kiểm tra toàn bộ test hợp đồng/unit test (`pytest tests/ -v` đạt **117 passed, 0 failed, 0 skipped**).

**Bằng chứng** (commit, run JSON, version log, case ID):

- Artifact version `v2`: `v2+p98e7fa380d3f+ta94472a74581` (prompt hash `98e7fa380d3f`, tools hash `a94472a74581`).
- File đã sửa: `starter_v0/artifacts/tools.yaml`, `starter_v0/data/eval_group.json`.
- Run JSON: `starter_v0/runs/v2_B_group_openrouter_20261110T143650926147.json` (và bản base `v2` tương ứng trong `starter_v0/runs/`).
- Version log: dòng `v2` trong `starter_v0/artifacts/version_log.csv` (`metric_before=0.85`, `metric_after=0.90`).
- 5 Eval Case IDs (multi-turn trong `starter_v0/data/eval_group.json`): `G06_multiturn_clarify_then_handle`, `G07_multiturn_carryover_timeframe`, `G08_multiturn_switch_to_github`, `G09_multiturn_clarify_then_url`, `G10_multiturn_cancel_request` (tổng hợp cùng 5 case single-turn `G01`–`G05` của Thịnh thành đủ 10 case).
- Kiểm thử schema & unit test: `pytest tests/ -v` đạt `117 passed in 0.47s` (0 failed, 0 skipped).

**Điều mình học được từ phần nhóm:**

- Mô tả tham số (`parameter description`) ngay trong `tools.yaml` là nơi trực tiếp và hiệu quả nhất để kiểm soát định dạng giá trị đối số của model (như loại bỏ từ nhiễu `"news"`/`"tin"` khỏi `query` hoặc ép `topic="news"`), giúp xử lý thành công ca gọi song song phức tạp (`R13_parallel_web_and_tweets`) mà chỉ sửa `system_prompt.md` ở `v1` chưa giải quyết hết.
- Khi mở rộng mô tả tool để hỗ trợ gọi kết hợp nhiều nguồn, model có thể phát sinh xu hướng `extra_tool_call` ở câu đơn hoặc câu chuyển đổi công cụ (`M06_switch_tool`); do đó cần kết hợp chặt chẽ giữa quy tắc điều hướng trong `system_prompt.md` và ranh giới phủ định (*WHEN NOT TO USE*) trong `tools.yaml` ở vòng `v3`.
- Thiết kế eval case multi-turn tốt cần thử thách đồng thời hai chiều: chiều **giữ ngữ cảnh** (carry-over `limit`, `timeframe`, `topic` từ lượt 1 sang lượt 3) và chiều **phá bỏ ngữ cảnh cũ** (đổi công cụ từ Twitter sang `github_repos` hoặc hủy lệnh), đồng thời luôn kiểm chứng qua `pytest` (`test_tool_contract.py`, `test_version_catalog.py`) để bảo đảm tính toàn vẹn của toàn bộ dữ liệu nhóm.

### PhanTrongHau-2A202603547

**Phần việc phụ trách:** UI và link demo, report A/B, v4 — bonus và local model, live chat và tổng hợp bài nộp.

**Đóng góp cụ thể:**

- Chưa cập nhật.

**Bằng chứng** (commit, code UI, link demo, report, run JSON cloud/local, prompt/tools local, version log, transcript):

- Chưa cập nhật.

**Điều mình học được từ phần nhóm:**

- Chưa cập nhật.

## Checklist trước khi nộp

- [ ] Provider thật và preflight thành công.
- [ ] Có ít nhất 5 tool khai báo.
- [ ] Có run JSON và version log v0, v1, v2, v3.
- [ ] Có kết quả ít nhất 2 model local ≤8B, hai vòng tối ưu `v4-local`/`v5-local`, kiểm tra lại trên cloud và báo cáo B7.
- [ ] Các phần bonus đã triển khai có bằng chứng trong báo cáo B5.
- [ ] Có tool mới, TOOL.md, registry và declaration đồng bộ.
- [ ] Có ≥3 unit test/tool mới; pytest xanh, hoàn thành TODO test để không còn skip.
- [ ] Có 10 eval case đúng 5 single-turn + 5 multi-turn, gồm case tool mới; có group run.
- [ ] UI hoạt động, link dùng thử được ghi trong report A.
- [ ] Có ít nhất 3 lượt live chat và transcript JSON.
- [ ] Report A/B hoàn chỉnh, số liệu khớp run và version log.
- [ ] Thành viên cập nhật đóng góp và bằng chứng cá nhân.
- [ ] Gói nộp không chứa `.env`, API key hoặc token.

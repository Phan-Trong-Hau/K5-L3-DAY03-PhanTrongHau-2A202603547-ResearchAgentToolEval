# Local model challenge — Hậu

Hai model đã cài trên máy: `qwen3:4b-instruct` (4.0B) và `qwen2.5:7b` (7.6B), cùng Q4_K_M. Baseline local dùng nguyên snapshot v3 cloud. Mỗi cấu hình chạy đủ 20 case Base cố định, gồm 14 single-turn và 6 multi-turn.

| Cấu hình | Prompt | Tools | Mục đích |
|---|---|---|---|
| v3-local-qwen4b / v3-local-qwen7b | `../versions/v3/system_prompt.md` | `../versions/v3/tools.yaml` | Đo chuyển nguyên bản cloud sang local |
| v4-local | `v4-local/system_prompt.md` | Byte-identical v3 | Chỉ đổi prompt: checklist ngắn, latest correction, native clarify |
| v5-local | Byte-identical v4 | `v5-local/tools.yaml` | Chỉ đổi declaration: native clarify, required response_type, source boundaries, query/topic/timeframe |
| v5-local-cloud | Cùng v5-local | Cùng v5-local | Kiểm tra lại trên `openai/gpt-4o-mini` |

Không sửa eval cases, grader, tool implementations hoặc tool-choice để tăng điểm. Giữ đủ 11 tool của v3; v5 không thêm/bỏ tool. UI vẫn dùng catalog v0–v3; các artifact thử nghiệm nằm riêng ở đây. V4 không cải thiện đồng đều trên hai model, mọi regression vẫn được lưu.

Chạy từ thư mục `starter_v0`, sau khi cài dependencies và cấu hình Ollama/các key research trong `.env`:

```bash
.venv/bin/python -u scripts/run_readonly_eval.py \
  --provider ollama --model qwen3:4b-instruct --version v4-local \
  --suite base --eval-cases data/eval_base.json \
  --system-prompt artifacts/local_versions/v4-local/system_prompt.md \
  --tools artifacts/local_versions/v4-local/tools.yaml
```

Đổi model thành `qwen2.5:7b` để chạy model thứ hai. Với baseline dùng version `v3-local-qwen4b` hoặc `v3-local-qwen7b` và hai file trong `artifacts/versions/v3/`. Với v5 dùng version `v5-local` và hai file `artifacts/local_versions/v5-local/`. Kiểm tra cloud dùng `--provider openrouter --model openai/gpt-4o-mini --version v5-local-cloud` cùng artifact v5. Chạy lần lượt để tránh tranh RAM/VRAM.

Runner dùng nguyên `run_eval.py`; chỉ in tiến độ, thêm thời gian end-to-end vào JSON, và gỡ token/chat ID Telegram khỏi process eval để không đăng tin. Các tool research vẫn gọi API thật. Không cần token Telegram để chấm routing. Mỗi run mới tạo file riêng, không ghi đè bằng chứng cũ.

```bash
.venv/bin/python scripts/summarize_local_eval.py
.venv/bin/python -m pytest tests -q
```

Xem bảng đầy đủ, lỗi từng case và môi trường tại `../../analysis/local_eval_comparison.csv`, `../../analysis/local_eval_failures.csv`, `../../analysis/local_eval_environment.json`; kết luận tại `../REPORT.md` B7. Hash đầy đủ và đường dẫn artifact nằm trong từng run JSON. Điểm chấm tool calls/arguments; không chấm factual accuracy của câu trả lời cuối. Thời gian gồm tải model, inference và research API, không phải benchmark inference thuần.

# Research Desk — Streamlit

## Chạy UI

Từ `starter_v0/`:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Mở http://localhost:8501.

## Sử dụng

- Mặc định dùng Ollama; chạy Ollama và chọn model đã cài, ví dụ `qwen2.5:7b`.
- Dùng cloud: chọn `openrouter` hoặc provider tương ứng với key đã điền trong `.env`.
- Để trống ô model để dùng mặc định của provider. Nhập version dùng cho phiên demo rồi bấm **Bắt đầu phiên mới** để áp dụng cấu hình.
- Nhập câu hỏi hoặc chọn một câu mẫu; trả lời tiếp khi agent hỏi thêm thông tin.
- Mở **Hoạt động của agent** để xem tool, arguments và kết quả.
- Mỗi lượt tự lưu vào `transcripts/ui_*.transcript.json`; có thể tải JSON ở thanh bên. Bắt đầu phiên mới sẽ xóa lịch sử trên giao diện, file phiên trước vẫn được giữ.

UI dùng lại vòng lặp trong `chat.py`, prompt và tool declaration trong `artifacts/`. Mỗi phiên giữ snapshot prompt/tools và hash để đối chiếu bằng chứng. Sau khi sửa artifacts, bắt đầu phiên mới để dùng bản mới.

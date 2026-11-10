# Research Desk — Streamlit

## Chạy UI

Từ thư mục gốc repo, Linux/macOS:

```bash
./run_ui.sh
```

Windows (PowerShell hoặc CMD):

```powershell
.\run_ui.bat
```

Script tự tạo `.venv` và cài dependency nếu thiếu. Windows cần cài Python 3 có lệnh `py` hoặc `python`. Đổi cổng khi cần: `./run_ui.sh --server.port 8502` hoặc `.\run_ui.bat --server.port 8502`.

Hoặc chạy thủ công trên Linux/macOS:

Từ `starter_v0/`:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Mở http://localhost:8501.

## Sử dụng

- Mặc định dùng Ollama; chạy Ollama và chọn model đã cài, ví dụ `qwen2.5:7b`.
- Dùng cloud: chọn `openrouter` hoặc provider tương ứng với key đã điền trong `.env`.
- Ô model tự điền model mặc định theo provider. Model đang dùng hiển thị ở đầu khung chat và trong thông tin phiên. Nhập version dùng cho phiên demo rồi bấm **Áp dụng cấu hình** để bắt đầu phiên với cấu hình đã chọn.
- Nhập câu hỏi hoặc chọn một câu mẫu; trả lời tiếp khi agent hỏi thêm thông tin.
- Mở **Hoạt động của agent** để xem tool, arguments và kết quả.
- Khi xử lý, đồng hồ cập nhật thời gian đã chờ và nhật ký hiển thị các bước gọi model, chọn tool, chạy tool, nhận kết quả. Sau khi hoàn tất, tổng thời gian và các bước vẫn nằm trong hội thoại và transcript.
- Bật **Đồng bộ Telegram** ở thanh bên để tự gửi câu hỏi, câu trả lời, model, thời gian xử lý và tên tool của các lượt chat mới. Tắt công tắc để dừng. Kết quả đồng bộ và message ID được lưu trong transcript.
- Mỗi lượt tự lưu vào `transcripts/ui_*.transcript.json`; có thể tải JSON ở thanh bên. Bấm **＋ Chat mới** ở đầu thanh bên để mở hội thoại trống với model hiện tại; file phiên trước vẫn được giữ.
- Trong **Lịch sử hội thoại**, tìm theo nội dung, bấm trực tiếp vào một phiên trong danh sách để hiển thị nội dung và tiếp tục hội thoại. Lịch sử vẫn còn sau khi khởi động lại ứng dụng vì được lưu trên máy chạy app.

UI dùng lại vòng lặp trong `chat.py`, prompt và tool declaration trong `artifacts/`. Mỗi phiên giữ snapshot prompt/tools và hash để đối chiếu bằng chứng. Sau khi sửa artifacts, bắt đầu phiên mới để dùng bản mới. Các phiên trên cùng máy chạy app dùng chung danh sách lịch sử.

Phiên Ollama mới dùng `artifacts/system_prompt_local.md` và `artifacts/tools_local.yaml`, tập trung vào hỏi lại khi thiếu tài khoản/URL và trả lời tiếng Việt. Cloud vẫn dùng `system_prompt.md`/`tools.yaml`. Phiên cũ giữ snapshot cũ; bấm **＋ Chat mới** để nhận bản local mới. Đây là bản thử cải tiến local, chưa phải kết quả full base eval.

## GitHub repository search

`github_repos` hỗ trợ tìm repository theo từ khóa, ngôn ngữ và số sao. Nếu GitHub báo hết quota, chờ hạn mức reset; có thể thêm `GITHUB_TOKEN` tùy chọn vào `.env` để dùng request có xác thực. Không gọi lại liên tục khi bị rate limit.

## Kết nối Telegram

1. Tạo bot bằng `@BotFather`, lấy bot token.
2. Thêm bot vào channel và cấp quyền đăng bài; nếu gửi tin riêng thì mở bot và bấm Start trước.
3. Điền hai biến vào `starter_v0/.env`:

```dotenv
TELEGRAM_BOT_TOKEN=<token bot>
TELEGRAM_CHAT_ID=<chat ID hoặc @channel_username>
```

4. Tải lại UI và bật **Đồng bộ Telegram** ở đầu thanh bên.
5. Chat bình thường: sau mỗi lượt hoàn tất, câu hỏi và câu trả lời tự được gửi sang nơi nhận đã cấu hình. Không cần xác nhận từng tin.

Công tắc mặc định tắt. Bật công tắc cho phép đồng bộ các lượt mới cho đến khi tắt; mở lại phiên cũ không tự gửi lại lịch sử. Nội dung dài được chia thành nhiều tin. Nếu lỗi giữa chừng, UI ghi nhận trạng thái đồng bộ chưa đầy đủ và không tự gửi lại để tránh trùng tin. Model không thể tự bật đồng bộ hoặc gửi vượt qua công tắc.

Chi tiết cấu hình channel/chat ID: [TOOL-SETUP.md](../TOOL-SETUP.md#6-telegram-bonus--send).

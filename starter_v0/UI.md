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
- Ô model tự điền model mặc định theo provider. Model đang dùng hiển thị ở đầu khung chat và trong thông tin phiên. Chọn **Phiên bản agent** v0–v3 để mở hội thoại tương ứng; bấm **Áp dụng cấu hình** khi đổi provider/model.
- Nhập câu hỏi hoặc chọn một câu mẫu; trả lời tiếp khi agent hỏi thêm thông tin.
- Mở **Hoạt động của agent** để xem tool, arguments và kết quả.
- Khi xử lý, đồng hồ cập nhật thời gian đã chờ và nhật ký hiển thị các bước gọi model, chọn tool, chạy tool, nhận kết quả. Sau khi hoàn tất, tổng thời gian và các bước vẫn nằm trong hội thoại và transcript.
- Bật **Đồng bộ Telegram** ở thanh bên để tự gửi câu hỏi, câu trả lời, model, thời gian xử lý và tên tool của các lượt chat mới. Tắt công tắc để dừng. Kết quả đồng bộ và message ID được lưu trong transcript.
- Mỗi lượt tự lưu vào `transcripts/ui_*.transcript.json`; có thể tải JSON ở thanh bên. Bấm **＋ Chat mới** ở đầu thanh bên để mở hội thoại trống với model hiện tại; file phiên trước vẫn được giữ.
- Trong **Lịch sử hội thoại**, tìm theo nội dung, bấm trực tiếp vào một phiên trong danh sách để hiển thị nội dung và tiếp tục hội thoại. Lịch sử vẫn còn sau khi khởi động lại ứng dụng vì được lưu trên máy chạy app.

UI dùng lại vòng lặp trong `chat.py`, prompt và tool declaration trong `artifacts/`. Mỗi phiên giữ snapshot prompt/tools và hash để đối chiếu bằng chứng. Sau khi sửa artifacts, bắt đầu phiên mới để dùng bản mới. Các phiên trên cùng máy chạy app dùng chung danh sách lịch sử.

## Chọn và so sánh v0–v3

- Chọn **Phiên bản agent** v0, v1, v2 hoặc v3 ở thanh bên. Mỗi version/model có hội thoại riêng; chuyển version sẽ khôi phục phiên gần nhất tương ứng hoặc tạo phiên trống. **＋ Chat mới** tạo hội thoại trống cho version/model đang dùng.
- Để thử cùng câu hỏi trên nhiều version, giữ cùng provider/model và bấm **Chat mới** ở từng version trước khi gửi, tránh dùng lại ngữ cảnh cũ.
- Các snapshot trong `artifacts/versions/` được kiểm tra hash theo run của thành viên. Cả cloud và Ollama dùng đúng prompt/tools của version đã chọn; v3 là mặc định cho phiên mới.
- Chọn **So sánh phiên bản** để xem bảng tổng quan v0–v3, chọn hai version và bộ Base/Group, xem metric, case pass/fail, expected/actual tool calls, diff prompt/tools và tải run JSON. Group hiện có cho v2/v3; các cặp khác chỉ hiển thị Base.
- Màn so sánh đọc bằng chứng đã lưu, vẫn mở được khi chưa có API key hoặc Ollama. Metric dùng OpenRouter `openai/gpt-4o-mini`; đó không phải điểm của Ollama hay model đang chọn để chat.
- v2 dùng cặp baseline `v2-openrouter-vietduc` mà Đức chạy trước khi tối ưu v3; đây là cùng hash artifact v2 của Huy. v3 dùng run chính do Đức push. Hai run `v2-verified` của Hậu là kiểm chứng bổ sung trong report.
- Version so sánh prompt và khai báo tool; implementation tool chạy bằng code hiện tại. Các phiên giữ snapshot riêng, lịch sử cũ vẫn mở được; bản thử local `system_prompt_local.md`/`tools_local.yaml` không tự trộn vào v0–v3.
- Nếu muốn thử bản local riêng bằng CLI, truyền `--system-prompt artifacts/system_prompt_local.md --tools artifacts/tools_local.yaml`.

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

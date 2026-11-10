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

- Chưa cập nhật.

**Bằng chứng** (commit, run JSON, version log, kết quả preflight và bảng lỗi baseline):

- Chưa cập nhật.

**Điều mình học được từ phần nhóm:**

- Chưa cập nhật.

### NgoDucThinh-2A202603548

**Phần việc phụ trách:** v1, cải tiến prompt theo một giả thuyết, 5 eval case single-turn.

**Đóng góp cụ thể:**

- Chưa cập nhật.

**Bằng chứng** (commit, run JSON, version log, case ID):

- Chưa cập nhật.

**Điều mình học được từ phần nhóm:**

- Chưa cập nhật.

### BuiGiaHuy-2A202603525

**Phần việc phụ trách:** v2, tool declaration, 5 eval case multi-turn và tổng hợp 10 case.

**Đóng góp cụ thể:**

- Chưa cập nhật.

**Bằng chứng** (commit, run JSON, version log, case ID):

- Chưa cập nhật.

**Điều mình học được từ phần nhóm:**

- Chưa cập nhật.

### LuuVanVietDuc-2A202603445

**Phần việc phụ trách:** tool mới, tài liệu tool, unit test, tích hợp v3, base/group eval.

**Đóng góp cụ thể:**

- Chưa cập nhật.

**Bằng chứng** (commit, tool, test, kết quả pytest, run JSON, version log):

- Chưa cập nhật.

**Điều mình học được từ phần nhóm:**

- Chưa cập nhật.

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

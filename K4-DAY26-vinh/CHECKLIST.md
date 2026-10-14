# Kiểm tra trước khi nộp — đội vinh

Ngày kiểm tra: 14/10/2026. Hiện đạt **5/6 mục**.

| Mục theo hướng dẫn | Trạng thái | Bằng chứng |
|---|---|---|
| `make test` pass | Đạt qua hai lệnh tương đương trên Windows | Gate no-key PASS; toàn bộ pytest: 4.624 passed, 7 skipped, không loại test nào; máy chưa có GNU make |
| `make validate` không có FAIL | Đạt | Validator trên world thật: PASS, 0 lỗi, 1 WARN về giới hạn lethality proxy |
| `git status kit/ bots/ fixtures/` không có thay đổi | Chưa đạt sau bản sửa Windows | kit/isolation/child_driver.py đã sửa; bots/ và fixtures/ không thay đổi |
| Không import thư viện ngoài chuẩn hoặc nằm trong danh sách cấm | Đạt | Quét AST trong agent/deck/eval: PASS; gate no-key: PASS |
| Có `submissions/<tên-đội>.bundle` | Đạt về file; cần lưu ý bản vá kit | Có submissions/vinh.bundle; CRC và hash nội dung hợp lệ; chứa hash kit gốc, không chứa bản sửa Windows |
| Thư mục `K4-DAY26-TenNhom/` có TEAMMATES.md đủ họ tên và MSSV | Đạt | K4-DAY26-vinh/TEAMMATES.md: Đặng Thế Vinh, 2A202602587 |

## Mục chưa đạt

Theo yêu cầu sửa lỗi của người dùng, đã sửa probe trong kit để chạy thật trên Windows:
dùng `_wopen` và `_close` cùng C runtime, đồng thời thay `/bin/cat` bằng tiến trình
Python đọc file trên Windows. Không giả lập kết quả hoặc bỏ qua test.

Thêm 2 test hồi quy cho đường dẫn Unicode, file không tồn tại và tiến trình con thật.
Toàn bộ test đã PASS. Nhưng RULES vẫn yêu cầu kit không thay đổi khi nộp bài, nên
chưa thể đánh dấu đủ 6/6. Bản vá `windows-probe-fix.patch` được lưu để giảng viên
xem xét cập nhật kit chính thức. Không tái đóng gói bundle với hash kit đã sửa.

Bundle hiện có giữ nguyên mã bài làm và hash kit gốc. Bản vá chỉ phục vụ kiểm tra
cục bộ; không phải một phần agent/deck/eval trong bundle.

## File đã chuẩn bị

- TEAMMATES.md: thông tin thành viên do người dùng cung cấp.
- submissions/vinh.bundle: bản sao bundle đã xác minh từ dự án.

Bundle chứa agent/, deck/, eval/ và MANIFEST.json. Chưa gửi bài lên hệ thống nộp.

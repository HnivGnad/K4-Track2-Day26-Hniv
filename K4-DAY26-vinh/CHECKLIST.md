# Kiểm tra trước khi nộp — đội vinh

Ngày kiểm tra: 14/10/2026. Đạt **6/6 mục**.

**make test PASS trên Linux với kit nguyên bản: 4624 passed, 7 skipped, 0 failed.**
Không loại test nào; 7 trường hợp skip do điều kiện có sẵn trong suite.

- [x] make test pass.
- [x] make validate không có FAIL.
- [x] kit/, bots/, fixtures/ giữ nguyên bản giảng viên phát.
- [x] Import đúng quy định.
- [x] Có submissions/vinh.bundle.
- [x] TEAMMATES.md đủ họ tên và MSSV.

| Mục | Bằng chứng |
|---|---|
| Test | GNU make 4.4.1 chạy đúng target test của Makefile, Python 3.12.14 trên Linux/WSL; gate no-key PASS; pytest 4624 passed, 7 skipped |
| Validate | Corpus thật df8c55dabb35: PASS, 0 FAIL, 1 WARN về giới hạn lethality proxy |
| Kit nguyên bản | Toàn bộ file được Git quản lý trong kit/, bots/, fixtures/ đã đối chiếu với commit gốc 6a68efd; không có khác biệt nội dung |
| Import | Quét AST agent/deck/eval và gate no-key PASS |
| Bundle | submissions/vinh.bundle có CRC/hash hợp lệ, mã nguồn bài làm và hash kit khớp hiện tại |
| Thành viên | Đặng Thế Vinh, MSSV 2A202602587 |

## Cách xử lý tương thích Windows

Đã khôi phục kit/isolation/child_driver.py về bản gốc. Bản vá Windows cũ đã bỏ.
Không thay đổi kit, không mock probe, không bỏ test. Chạy kiểm tra bằng Python Linux
và GNU make cài cục bộ trong .venv; môi trường hệ thống WSL không bị sửa.

Trên máy hiện tại, chạy lại bằng PowerShell:

~~~powershell
wsl.exe -d docker-desktop -- sh /mnt/host/d/AI/Track2/K4-Track2-Day26-Hniv/run-tests-linux.sh
~~~

Script run-tests-linux.sh dùng công cụ cục bộ trong .venv, không nằm trong bundle.
Chạy pytest trực tiếp bằng Python Windows vẫn gặp lỗi của kit gốc; dùng Linux để kiểm tra.

## File nộp

- TEAMMATES.md.
- submissions/vinh.bundle, gồm agent/, deck/, eval/ và MANIFEST.json.

Bài đã chuẩn bị; chưa gửi lên hệ thống nộp bài.

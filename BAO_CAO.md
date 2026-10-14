# Báo cáo thực hiện — đội vinh

Ngày 14/10/2026. Đã triển khai gateway phòng thủ, guardrail, bộ bài và prosecutor.
Giữ nguyên bots/ và fixtures/. Theo yêu cầu sửa lỗi Windows, đã sửa
kit/isolation/child_driver.py; bản vá và ảnh hưởng đến điều kiện nộp được ghi rõ bên dưới.

## World đã tải và xác minh

- Nguồn: [Release của repo gốc giảng viên](https://github.com/VinUni-AI20k/Day26-Colosseum-Agent-Arena-Kit/releases/tag/world-df8c55dabb35).
- File: colosseum-world-df8c55dabb35.zip, 2.553.457 byte.
- SHA-256 khớp file checksum và digest GitHub:
  e05327c0bd88b2b1ee9c9194a4bee5535964360d97d462144773d02686705810.
- Đã giải nén vào kit/world/df8c55dabb35/, có manifest.json, tổng 12.375 trang.
- Không có truth.json. Bản ZIP và checksum được giữ ở thư mục gốc dự án.

## Kết quả kiểm tra

- Deck trên corpus thật: PASS, 0 lỗi, 1 cảnh báo về giới hạn kiểm tra lethality của validator.
- Gate no-key: PASS, 0 vi phạm.
- Bộ test chạy lại sau bản sửa Windows: **PASS — 4624 passed, 7 skipped, 0 failed**,
  không loại test nào. Mục test trong checklist đã được đánh dấu đạt.
  Máy chưa có GNU make; đã chạy đầy đủ hai lệnh của target test bằng Python 3.12.
  Sửa kit/isolation/child_driver.py theo yêu cầu người dùng: `_wopen`/`_close`
  cùng C runtime và tiến trình Python đọc file thay cho `/bin/cat` trên Windows.
  Thêm 2 test hồi quy. Tài liệu API: [Microsoft CRT](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/open-wopen).
- Prosecutor trên 40 fixture: 32 verified, 0 false/unproven/rejected;
  precision 100%, recall 94,1%. Không suy đoán stale_read từ ký hiệu replica.
- Spar cục bộ, seed 1, chế độ all:

| Bot | HP đội vinh | HP bot | Kết quả |
|---|---:|---:|---|
| rookie | 100 | 0 | Thắng |
| operator | 100 | 0 | Thắng |
| adversary | 72 | 0 | Thắng |

Spar dùng plan và answer script của kit. Đây là kết quả mô phỏng cục bộ, không
chứng minh chất lượng tournament hoặc model tự động tuân thủ guardrail.
Helper review_answer cần được phần ghép câu trả lời gọi; ANSWER không đi qua gateway.
Harness spar cấp card verified đơn lẻ; gateway yêu cầu card ký thật nên các bước
A2A đó bị chặn. Cần adapter đúng hợp đồng để đánh giá A2A đầy đủ.

## Bundle đã tạo

Lệnh kit.submit --team vinh đã thành công.

- File: submissions/vinh.bundle.
- Kích thước: 52.628 byte, 16 file của bài làm.
- Manifest ghi hash của 39 file mã nguồn kit.
- Đã kiểm tra CRC của ZIP, tên đội và SHA-256 của từng file trong manifest.
- Bundle được tạo trên máy; chưa gửi lên hệ thống nộp bài hoặc tournament.

Tên đội vinh đã được điền. Theo checklist bổ sung, đã tạo
K4-DAY26-vinh/TEAMMATES.md với 1 thành viên: Đặng Thế Vinh, MSSV 2A202602587.
Hiện đạt 5/6 điều kiện nộp bài: test đã PASS. Working tree sạch sau commit, nhưng
kit vẫn khác bản giảng viên phát do bản sửa Windows. Đã lưu
K4-DAY26-vinh/windows-probe-fix.patch để giảng viên xem xét cập nhật
kit chính thức. Bundle giữ nguyên hash kit gốc; không tái đóng gói với hash kit sửa.
Các mã learner trong corpus là dữ liệu mẫu của bài lab.

## Chạy lại trên PowerShell

~~~powershell
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe validate_deck.py deck/deck.json deck/lineup.json --world kit/world/df8c55dabb35
.venv/Scripts/python.exe -m kit.gate_no_key
.venv/Scripts/python.exe -m pytest tests/ -q
.venv/Scripts/python.exe spar.py --bot rookie --as all
.venv/Scripts/python.exe spar.py --bot operator --as all
.venv/Scripts/python.exe spar.py --bot adversary --as all
# Chỉ đóng gói lại sau khi xử lý yêu cầu kit không thay đổi với giảng viên.
~~~

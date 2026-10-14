# Báo cáo thực hiện — đội vinh

Ngày 14/10/2026. Hoàn thiện agent phòng thủ, bộ bài tấn công và prosecutor.
Kit, bots và fixtures giữ nguyên nội dung bản giảng viên phát ở commit 6a68efd.

## Kiểm chứng

- World df8c55dabb35: 12.375 trang; tải từ Release repo gốc giảng viên.
- ZIP khớp SHA-256: e05327c0bd88b2b1ee9c9194a4bee5535964360d97d462144773d02686705810.
- Student world không chứa truth.json.
- Validate trên corpus thật: PASS, 0 FAIL, 1 WARN về giới hạn lethality proxy.
- Chạy đúng make test trên Linux/WSL: **4624 passed, 7 skipped, 0 failed**.
- Gate no-key PASS. Không loại test hoặc giả lập kết quả probe.
- Kit/bots/fixtures đã đối chiếu với bản gốc, không khác biệt nội dung.
- Checklist nộp bài: **6/6**. TEAMMATES.md: Đặng Thế Vinh, MSSV 2A202602587.

## Giải quyết lỗi Windows

Kit gốc dùng libc.open và /bin/cat, không chạy probe đầy đủ với runtime Windows.
Đã bỏ bản sửa Windows và khôi phục kit nguyên bản. Giải pháp là chạy test trên
Linux hiện có qua WSL. Python 3.12.14 và GNU make 4.4.1 nằm cục bộ trong .venv;
không cài gói hoặc sửa thư viện hệ thống WSL.

Script run-tests-linux.sh gọi nguyên target test của Makefile, chỉ đổi BIN sang
thư mục công cụ Linux cục bộ. Tắt plugin cache pytest để tránh quyền truy cập cache
đã tạo trên Windows; không thay đổi danh sách test.

Chạy lại trên máy hiện tại:

~~~powershell
wsl.exe -d docker-desktop -- sh /mnt/host/d/AI/Track2/K4-Track2-Day26-Hniv/run-tests-linux.sh
~~~

Toolchain trong .venv không được commit và không đưa vào bundle. Máy khác cần môi
trường Linux với Python 3.12, pytest và GNU make để chạy make test.

## Kết quả bài làm

Prosecutor trên 40 fixture: 32 verified, 0 false/unproven/rejected; precision 100%,
recall 94,1%. Không suy đoán stale_read khi thiếu dữ liệu freshness có căn cứ.

Spar cục bộ seed 1: thắng rookie 100–0, operator 100–0, adversary 72–0.
Đây là kết quả harness có plan/answer script, không phải kết quả tournament.
Helper review_answer cần được phần ghép câu trả lời gọi; ANSWER không đi qua gateway.
Harness spar cấp card verified đơn lẻ; gateway yêu cầu card ký thật nên các bước
A2A đó bị chặn. Cần adapter đúng hợp đồng để đánh giá A2A đầy đủ.

## Bài nộp

K4-DAY26-vinh/ chứa TEAMMATES.md, CHECKLIST.md và submissions/vinh.bundle.
Bundle gồm 16 file của agent/deck/eval cùng manifest và hash 39 file kit nguyên bản.
Đã xác minh CRC, hash từng file, hash kit và sự khớp với mã nguồn hiện tại.

Chưa gửi lên hệ thống nộp bài; push GitHub không thay thế thao tác nộp.

# Bộ bài đội vinh

14 lá: 10 attack + 4 blank, đủ 9 lớp tấn công. Cân bằng 4 MCP, 4 A2A, 2 gateway.

Thay đổi so với starter:
- atk_04 tiêm Note vào glossary, đúng đường truy xuất define_term.
- atk_07 và atk_10 kích hoạt từ call_index 1.
- Mọi attack dùng defense_event = gateway.denied theo hợp đồng.
- Lineup: atk_05, atk_07, atk_04, atk_06, atk_01, atk_08, atk_03, atk_10, atk_09, atk_02.

Giữ nguyên các anchor/path_id của starter. World df8c55dabb35 đã tải từ repo gốc
giảng viên và xác minh SHA-256. Validator chạy trên corpus thật: PASS, 0 lỗi,
1 cảnh báo về giới hạn kiểm tra lethality bằng proxy.

Spar cục bộ seed 1: thắng rookie (100-0), operator (100-0), adversary (72-0).
Đây là kết quả harness có plan/answer script, không phải kết quả tournament.

~~~powershell
.venv/Scripts/python.exe validate_deck.py deck/deck.json deck/lineup.json --world kit/world/df8c55dabb35
~~~

Xem BAO_CAO.md để biết kết quả kiểm tra và giới hạn của harness.

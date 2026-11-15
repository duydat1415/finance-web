# Quản lý tài chính cá nhân (web)

Giao diện theo thiết kế Figma (`Đăng nhập · Desktop`, `Tổng quan`, `Giao dịch`, `Thêm giao dịch`).

## Chạy
```bash
pip install -r requirements.txt
streamlit run app.py
```
Tài khoản demo: `demo@example.com` / `demo1234`.

## Trợ lý AI (Groq)
Đặt khóa vào secrets, **không** ghi vào mã nguồn:
- Streamlit Cloud: app > Settings > Secrets, dán `GROQ_API_KEY = "gsk_..."`.
- Máy cá nhân: tạo `.streamlit/secrets.toml` (đã có trong `.gitignore`) với cùng nội dung.

Tùy chọn: `GROQ_MODEL = "..."` để đổi mô hình (mặc định `llama-3.3-70b-versatile`).
Không có khóa hoặc gọi lỗi thì trợ lý dùng trả lời theo quy tắc.

## Cấu trúc
- `app.py`: điểm vào, bảo vệ đăng nhập và menu điều hướng.
- `ui.py`: theme CSS, header trang, biểu đồ tròn.
- `data.py`: dữ liệu mẫu và hàm dùng chung (`real_flows` loại giao dịch chuyển ví khỏi thu/chi).
- `pages/`: các màn hình.

## Thay đổi so với bản gốc
- Áp theme Figma (màu, font Inter, thẻ bo góc, nút và menu hồng).
- Thêm đăng nhập bắt buộc trước khi vào app, nút đăng xuất.
- Sửa lỗi: chuyển giữa các ví bị tính như thu/chi trong Tổng quan, Giao dịch, Ngân sách, Báo cáo, Trợ lý AI.
- Thêm nút tải CSV thật ở trang Tài khoản & tiện ích.

## Chưa làm
- Liên kết ngân hàng, đăng nhập Google.
- Màn hình quản trị (Người dùng, Danh mục, Nhật ký) có trong artifact nhưng không có trong zip gốc.
- Dữ liệu chỉ lưu trong phiên làm việc, tải lại trang là mất.

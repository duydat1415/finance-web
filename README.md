# Quản lý tài chính cá nhân (web)

Giao diện theo thiết kế Figma (`Đăng nhập · Desktop`, `Tổng quan`, `Giao dịch`, `Thêm giao dịch`).

## Chạy
```bash
pip install -r requirements.txt
streamlit run app.py
```
Tài khoản demo: `demo@example.com` / `demo1234`.

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
- Liên kết ngân hàng, đăng nhập Google, Trợ lý AI thật (đang dùng quy tắc mẫu trong `pages/9_Tro_ly_AI.py`).
- Màn hình quản trị (Người dùng, Danh mục, Nhật ký) có trong artifact nhưng không có trong zip gốc.
- Dữ liệu chỉ lưu trong phiên làm việc, tải lại trang là mất.

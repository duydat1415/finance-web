"""Trang Tài khoản & tiện ích: liên kết ngân hàng và các công cụ phụ trợ."""

import streamlit as st

from data import get_account_data, get_transactions, is_demo_user


st.title("Tài khoản & tiện ích")

demo_accounts = [
    {"bank": "MB Bank", "number": "•••• 4417", "status": "Đã liên kết"},
    {"bank": "Techcombank", "number": "•••• 2290", "status": "Đã liên kết"},
    {"bank": "MoMo", "number": "•••• 0912", "status": "Chưa liên kết"},
]
accounts = get_account_data("linked_accounts", demo_accounts if is_demo_user() else [])

st.subheader("Tài khoản ngân hàng")
if not accounts:
    st.info("Bạn chưa liên kết tài khoản ngân hàng nào.")
for acc in accounts:
    with st.container(border=True):
        a, b, c = st.columns([2, 1, 1])
        a.write(f"**{acc['bank']}**")
        b.write(acc["number"])
        if acc["status"] == "Đã liên kết":
            c.success(acc["status"])
        else:
            if c.button("Liên kết", key=acc["bank"]):
                st.info("Chức năng liên kết cần kết nối API ngân hàng. Hiện chỉ là giao diện mẫu.")

st.subheader("Tiện ích")
c1, c2, c3 = st.columns(3)
with c1.container(border=True):
    st.write("**Xuất báo cáo CSV**")
    st.caption("Tải toàn bộ giao dịch ra file CSV.")
    st.download_button("Tải CSV", data=get_transactions().to_csv(index=False).encode("utf-8-sig"),
                       file_name="giao_dich.csv", mime="text/csv")
with c2.container(border=True):
    st.write("**Nhắc lịch thanh toán**")
    st.caption("Nhận nhắc khi hóa đơn sắp đến hạn.")
with c3.container(border=True):
    st.write("**Sao lưu dữ liệu**")
    st.caption("Sao lưu toàn bộ dữ liệu cá nhân.")

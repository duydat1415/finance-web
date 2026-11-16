"""Trang Cài đặt: thông tin cá nhân và tùy chọn hiển thị (lịch định kỳ đã bỏ theo yêu cầu)."""

import streamlit as st

from data import get_account_data


st.title("Cài đặt")

default_settings = {
    "name": st.session_state.get("current_user", ""),
    "email": st.session_state.get("current_user_email", ""),
    "currency": "VND",
    "notify_debt": True,
    "notify_budget": True,
    "dark_mode": False,
}
s = get_account_data("settings", default_settings)

with st.form("settings_form"):
    st.subheader("Hồ sơ")
    s["name"] = st.text_input("Tên hiển thị", value=s["name"])
    s["email"] = st.text_input("Email", value=s["email"], placeholder="ban@example.com")
    s["currency"] = st.selectbox("Đơn vị tiền tệ", ["VND"], index=0)

    st.subheader("Thông báo")
    s["notify_budget"] = st.toggle("Cảnh báo khi vượt ngân sách", value=s["notify_budget"])
    s["notify_debt"] = st.toggle("Nhắc đến hạn thanh toán nợ", value=s["notify_debt"])

    st.subheader("Giao diện")
    s["dark_mode"] = st.toggle("Chế độ tối (áp dụng qua cài đặt Streamlit)", value=s["dark_mode"])

    if st.form_submit_button("Lưu cài đặt", type="primary"):
        st.success("Đã lưu cài đặt cho phiên làm việc này.")

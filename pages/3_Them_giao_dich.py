"""Thêm giao dịch nhanh (form Chi tiêu / Thu nhập)."""

from datetime import date

import streamlit as st

from data import CATEGORIES, WALLETS, add_transaction, fmt_vnd, wallet_balances


st.title("Thêm giao dịch")
st.caption("Ghi lại chi tiêu hoặc thu nhập trong vài giây")

kind = st.radio("Loại giao dịch", ["Chi tiêu", "Thu nhập"], horizontal=True)

with st.form("quick_add", clear_on_submit=True):
    amount = st.number_input("Số tiền (₫)", min_value=0, step=1000, value=486_000)
    c1, c2 = st.columns(2)
    category = c1.selectbox("Danh mục", CATEGORIES, index=0)
    wallet = c2.selectbox("Ví thanh toán", WALLETS, index=3)
    c3, c4 = st.columns(2)
    when = c3.date_input("Ngày giao dịch", value=date(2026, 9, 29))
    name = c4.text_input("Tên giao dịch", value="WinMart")
    note = st.text_input("Ghi chú", value="Mua thực phẩm trong tuần")

    submitted = st.form_submit_button("Lưu giao dịch", type="primary")

if submitted:
    if amount <= 0:
        st.error("Số tiền phải lớn hơn 0.")
    elif not name.strip():
        st.error("Vui lòng nhập tên giao dịch.")
    else:
        signed = -amount if kind == "Chi tiêu" else amount
        add_transaction(
            {
                "Ngày": when,
                "Giao dịch": name.strip(),
                "Loại": kind,
                "Ví": wallet,
                "Số tiền": signed,
                "Danh mục": category,
            }
        )
        st.success(f"Đã lưu: {name.strip()} ({fmt_vnd(signed)})")

balances = wallet_balances()
st.info(f"Số dư {wallet} hiện tại: **{fmt_vnd(balances[wallet])}**")

"""Trang Ví: số dư từng ví và chuyển tiền giữa các ví."""

import streamlit as st

from data import WALLETS, add_transaction, fmt_vnd, wallet_balances


st.title("Ví & tài khoản")
balances = wallet_balances()

cols = st.columns(len(balances))
for col, (wallet, amount) in zip(cols, balances.items()):
    with col.container(border=True):
        st.metric(wallet, fmt_vnd(amount))

with st.container(border=True):
    st.subheader("Chuyển tiền giữa ví")
    c1, c2, c3 = st.columns(3)
    src = c1.selectbox("Từ ví", WALLETS, index=1)
    dst = c2.selectbox("Đến ví", WALLETS, index=2)
    amount = c3.number_input("Số tiền (₫)", min_value=0, step=10_000, value=500_000)
    if st.button("Chuyển tiền", type="primary"):
        if src == dst:
            st.error("Ví nguồn và ví đích phải khác nhau.")
        elif amount <= 0:
            st.error("Số tiền phải lớn hơn 0.")
        elif amount > balances[src]:
            st.error("Số dư ví nguồn không đủ.")
        else:
            from datetime import date

            today = date(2026, 9, 29)
            add_transaction({"Ngày": today, "Giao dịch": f"Chuyển sang {dst}", "Loại": "Chuyển ví",
                             "Ví": src, "Số tiền": -amount, "Danh mục": "Chuyển ví"})
            add_transaction({"Ngày": today, "Giao dịch": f"Nhận từ {src}", "Loại": "Chuyển ví",
                             "Ví": dst, "Số tiền": amount, "Danh mục": "Chuyển ví"})
            st.success(f"Đã chuyển {fmt_vnd(amount)} từ {src} sang {dst}.")
            st.rerun()

"""Trang Tổng quan tài chính (màn hình chính)."""

import streamlit as st

from data import BUDGETS, fmt_vnd, get_transactions, real_flows, wallet_balances
from ui import AMBER, BLUE, MUTED, PINK, VIOLET, donut_html, page_header

df = get_transactions()
balances = wallet_balances()
total_balance = sum(balances.values())

month_df = real_flows(df[df["Ngày"].astype(str).str.startswith("2026-09")])
income = month_df.loc[month_df["Số tiền"] > 0, "Số tiền"].sum()
expense = -month_df.loc[month_df["Số tiền"] < 0, "Số tiền"].sum()
spend = (
    month_df[month_df["Số tiền"] < 0]
    .assign(Chi=lambda d: -d["Số tiền"])
    .groupby("Danh mục")["Chi"]
    .sum()
)

user = st.session_state.get("current_user", "bạn")
page_header("Tổng quan tài chính", f"Chào buổi sáng, {user}")

st.markdown(
    '<div class="hero-balance">'
    f'<div><div class="hb-label">Tổng số dư</div><div class="hb-value">{fmt_vnd(total_balance)}</div></div>'
    '<div class="hb-side">'
    f"<div><span>Thu nhập tháng 9</span><b>{fmt_vnd(income)}</b></div>"
    f"<div><span>Chi tiêu tháng 9</span><b>{fmt_vnd(expense)}</b></div>"
    "</div></div>",
    unsafe_allow_html=True,
)

COLORS = {"Ăn uống": PINK, "Nhà ở": VIOLET, "Di chuyển": BLUE, "Khác": AMBER}
left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.subheader("Chi tiêu theo danh mục")
        items = [(cat, float(spend.get(cat, 0)), COLORS.get(cat, MUTED)) for cat in BUDGETS]
        st.markdown(donut_html(items, fmt_vnd(expense)), unsafe_allow_html=True)

with right:
    with st.container(border=True):
        st.subheader("Ngân sách của bạn")
        for cat, limit in BUDGETS.items():
            spent = float(spend.get(cat, 0))
            ratio = min(spent / limit, 1.0) if limit else 0
            st.write(f"**{cat}**: {fmt_vnd(spent)} / {fmt_vnd(limit)}")
            if spent > limit:
                st.progress(1.0, text="Vượt ngân sách")
            elif spent >= 0.8 * limit:
                st.progress(ratio, text="Sắp chạm giới hạn")
            else:
                st.progress(ratio)

with st.container(border=True):
    st.subheader("Số dư theo ví")
    cols = st.columns(len(balances))
    for col, (wallet, amount) in zip(cols, balances.items()):
        col.metric(wallet, fmt_vnd(amount))

with st.container(border=True):
    st.subheader("Giao dịch gần đây")
    recent = df.head(5)[["Ngày", "Giao dịch", "Danh mục", "Ví", "Số tiền"]].copy()
    recent["Số tiền"] = recent["Số tiền"].map(fmt_vnd)
    st.dataframe(recent, hide_index=True)

st.info("Dùng mục **Giao dịch** ở thanh bên để xem và lọc đầy đủ, hoặc thêm giao dịch mới.")

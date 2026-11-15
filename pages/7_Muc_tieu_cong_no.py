"""Trang Mục tiêu & công nợ: theo dõi mục tiêu tiết kiệm và khoản nợ phải trả."""

import streamlit as st

from data import fmt_vnd


st.title("Mục tiêu & công nợ")

GOALS = [
    {"name": "Quỹ khẩn cấp", "target": 30_000_000, "saved": 12_000_000, "due": "31/12/2026"},
    {"name": "Mua laptop", "target": 25_000_000, "saved": 9_500_000, "due": "30/06/2027"},
]
DEBTS = [
    {"name": "Thẻ tín dụng", "owed": 4_200_000, "rate": "24%/năm", "min_pay": 600_000},
    {"name": "Vay bạn bè", "owed": 3_000_000, "rate": "0%", "min_pay": 500_000},
]

st.subheader("Mục tiêu tiết kiệm")
cols = st.columns(len(GOALS))
for col, g in zip(cols, GOALS):
    with col.container(border=True):
        st.write(f"**{g['name']}**")
        st.progress(min(g["saved"] / g["target"], 1.0))
        st.write(f"Đã có {fmt_vnd(g['saved'])} / {fmt_vnd(g['target'])}")
        st.caption(f"Hạn: {g['due']}")

st.subheader("Công nợ")
total_owed = sum(d["owed"] for d in DEBTS)
st.metric("Tổng nợ phải trả", fmt_vnd(total_owed))
for d in DEBTS:
    with st.container(border=True):
        a, b, c = st.columns(3)
        a.write(f"**{d['name']}**")
        b.write(f"Còn nợ: {fmt_vnd(d['owed'])}")
        c.write(f"Lãi suất: {d['rate']} · Tối thiểu/tháng: {fmt_vnd(d['min_pay'])}")

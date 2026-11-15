"""Trang Hóa đơn & định kỳ: các khoản thanh toán lặp lại và hạn sắp tới."""

import streamlit as st

from data import fmt_vnd


st.title("Hóa đơn & định kỳ")

BILLS = [
    {"name": "Tiền nhà", "amount": 2_840_000, "due": "05/10/2026", "cycle": "Hàng tháng", "paid": False},
    {"name": "Tiền điện", "amount": 450_000, "due": "08/10/2026", "cycle": "Hàng tháng", "paid": False},
    {"name": "Internet", "amount": 220_000, "due": "01/10/2026", "cycle": "Hàng tháng", "paid": True},
    {"name": "Gym", "amount": 500_000, "due": "10/10/2026", "cycle": "Hàng tháng", "paid": False},
]

unpaid = [b for b in BILLS if not b["paid"]]
c1, c2 = st.columns(2)
c1.metric("Cần thanh toán", fmt_vnd(sum(b["amount"] for b in unpaid)))
c2.metric("Số hóa đơn chưa trả", len(unpaid))

for b in BILLS:
    with st.container(border=True):
        a, c, d, e = st.columns([2, 1, 1, 1])
        a.write(f"**{b['name']}**")
        c.write(fmt_vnd(b["amount"]))
        d.write(f"Hạn: {b['due']} · {b['cycle']}")
        if b["paid"]:
            e.success("Đã trả")
        else:
            e.warning("Chưa trả")

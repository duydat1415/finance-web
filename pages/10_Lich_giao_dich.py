"""Trang Lịch giao dịch: các khoản thu chi sắp tới trong tháng."""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from data import fmt_vnd


st.title("Lịch giao dịch")
st.caption("Các khoản thu chi dự kiến trong tháng 10/2026")

start = date(2026, 10, 1)
schedule = pd.DataFrame(
    [
        (start + timedelta(days=0), "Tiền nhà", "Chi tiêu", -2_840_000),
        (start + timedelta(days=4), "Tiền điện", "Chi tiêu", -450_000),
        (start + timedelta(days=9), "Gym", "Chi tiêu", -500_000),
        (start + timedelta(days=14), "Lương tạm ứng", "Thu nhập", 5_000_000),
        (start + timedelta(days=30), "Lương tháng 10", "Thu nhập", 18_500_000),
    ],
    columns=["Ngày", "Giao dịch", "Loại", "Số tiền"],
)

with st.container(border=True):
    st.subheader("Dự kiến trong tháng")
    shown = schedule.copy()
    shown["Ngày"] = shown["Ngày"].map(lambda d: d.strftime("%d/%m/%Y"))
    shown["Số tiền"] = shown["Số tiền"].map(fmt_vnd)
    st.dataframe(shown, hide_index=True)

income = schedule.loc[schedule["Số tiền"] > 0, "Số tiền"].sum()
expense = -schedule.loc[schedule["Số tiền"] < 0, "Số tiền"].sum()
c1, c2, c3 = st.columns(3)
c1.metric("Dự kiến thu", fmt_vnd(income))
c2.metric("Dự kiến chi", fmt_vnd(expense))
c3.metric("Chênh lệch", fmt_vnd(income - expense))

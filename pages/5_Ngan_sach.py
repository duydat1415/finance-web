"""Trang Ngân sách chi tiết: so sánh chi thực tế với hạn mức từng danh mục."""

import pandas as pd
import streamlit as st

from data import BUDGETS, fmt_vnd, get_transactions, real_flows


st.title("Ngân sách chi tiết")
st.caption("Tháng 9/2026")

df = real_flows(get_transactions())
spent = (
    df[df["Số tiền"] < 0].assign(Chi=lambda d: -d["Số tiền"]).groupby("Danh mục")["Chi"].sum()
)

rows = []
for cat, limit in BUDGETS.items():
    used = float(spent.get(cat, 0))
    rows.append({"Danh mục": cat, "Hạn mức": limit, "Đã chi": used,
                 "Còn lại": limit - used, "Tỷ lệ": min(used / limit, 1.0) if limit else 0})
table = pd.DataFrame(rows)

with st.container(border=True):
    st.subheader("Tiến độ theo danh mục")
    for _, r in table.iterrows():
        st.write(f"**{r['Danh mục']}**: {fmt_vnd(r['Đã chi'])} / {fmt_vnd(r['Hạn mức'])}")
        st.progress(float(r["Tỷ lệ"]))
        if r["Đã chi"] > r["Hạn mức"]:
            st.error(f"Vượt ngân sách {fmt_vnd(r['Đã chi'] - r['Hạn mức'])}")

with st.container(border=True):
    st.subheader("Bảng chi tiết")
    show = table.copy()
    for c in ["Hạn mức", "Đã chi", "Còn lại"]:
        show[c] = show[c].map(fmt_vnd)
    show["Tỷ lệ"] = (table["Tỷ lệ"] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(show, hide_index=True)

"""Trang Phân tích & báo cáo: thu chi theo danh mục và dòng tiền."""

import pandas as pd
import streamlit as st

from data import fmt_vnd, get_transactions, real_flows


st.title("Phân tích & báo cáo")

df = real_flows(get_transactions()).copy()
df["Ngày"] = pd.to_datetime(df["Ngày"])
df["Tháng"] = df["Ngày"].dt.strftime("%Y-%m")

income = df[df["Số tiền"] > 0].groupby("Tháng")["Số tiền"].sum()
expense = -df[df["Số tiền"] < 0].groupby("Tháng")["Số tiền"].sum()
flow = pd.DataFrame({"Thu nhập": income, "Chi tiêu": expense}).fillna(0)
flow["Dòng tiền ròng"] = flow["Thu nhập"] - flow["Chi tiêu"]

c1, c2 = st.columns(2)
with c1, st.container(border=True):
    st.subheader("Thu và chi theo tháng")
    st.bar_chart(flow[["Thu nhập", "Chi tiêu"]])
with c2, st.container(border=True):
    st.subheader("Cơ cấu chi tiêu")
    by_cat = -df[df["Số tiền"] < 0].groupby("Danh mục")["Số tiền"].sum()
    if by_cat.empty:
        st.info("Chưa có dữ liệu chi tiêu.")
    else:
        st.bar_chart(by_cat)

with st.container(border=True):
    st.subheader("Bảng tổng hợp")
    out = flow.reset_index()
    for c in ["Thu nhập", "Chi tiêu", "Dòng tiền ròng"]:
        out[c] = out[c].map(fmt_vnd)
    st.dataframe(out, hide_index=True)

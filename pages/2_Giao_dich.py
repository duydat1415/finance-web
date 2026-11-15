"""Trang Giao dịch: tìm kiếm, lọc và phân trang."""

from datetime import date

import streamlit as st

from data import CATEGORIES, TYPES, WALLETS, fmt_vnd, get_transactions, real_flows


st.title("Giao dịch")
st.caption("Tìm kiếm, phân loại và kiểm soát dòng tiền")

df = get_transactions().copy()
df["Ngày"] = df["Ngày"].apply(lambda d: d if isinstance(d, date) else date.fromisoformat(str(d)))

with st.container(border=True):
    st.subheader("Tìm kiếm & bộ lọc")
    keyword = st.text_input("Tìm theo tên, ghi chú hoặc số tiền", placeholder="Ví dụ: WinMart")

    c1, c2, c3, c4 = st.columns(4)
    min_day, max_day = df["Ngày"].min(), df["Ngày"].max()
    date_range = c1.date_input("Khoảng ngày", value=(min_day, max_day))
    categories = c2.multiselect("Danh mục", CATEGORIES)
    types = c3.multiselect("Loại", TYPES)
    wallets = c4.multiselect("Ví", WALLETS)

mask = df["Số tiền"].notna()
if keyword:
    kw = keyword.lower()
    mask &= df["Giao dịch"].str.lower().str.contains(kw) | df["Số tiền"].astype(str).str.contains(kw)
if categories:
    mask &= df["Danh mục"].isin(categories)
if types:
    mask &= df["Loại"].isin(types)
if wallets:
    mask &= df["Ví"].isin(wallets)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask &= (df["Ngày"] >= start) & (df["Ngày"] <= end)

filtered = df[mask].reset_index(drop=True)

flows = real_flows(filtered)
income = flows.loc[flows["Số tiền"] > 0, "Số tiền"].sum()
expense = -flows.loc[flows["Số tiền"] < 0, "Số tiền"].sum()

m1, m2, m3 = st.columns(3)
m1.metric("Thu nhập", fmt_vnd(income))
m2.metric("Chi tiêu", fmt_vnd(expense))
m3.metric("Dòng tiền ròng", fmt_vnd(income - expense))

PAGE_SIZE = 10
total_pages = max(1, -(-len(filtered) // PAGE_SIZE))
page = st.number_input("Trang", min_value=1, max_value=total_pages, value=1, step=1)
start_idx = (page - 1) * PAGE_SIZE
page_df = filtered.iloc[start_idx : start_idx + PAGE_SIZE].copy()
page_df["Số tiền"] = page_df["Số tiền"].map(fmt_vnd)

with st.container(border=True):
    st.subheader("Danh sách giao dịch")
    if page_df.empty:
        st.info("Không có giao dịch phù hợp bộ lọc.")
    else:
        st.dataframe(page_df, hide_index=True)
    st.caption(f"Hiển thị {len(page_df)} / {len(filtered)} giao dịch · Trang {page} / {total_pages}")

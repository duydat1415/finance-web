"""Dữ liệu mẫu và các hàm dùng chung cho app tài chính cá nhân."""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

WALLETS = ["Cash", "MBB", "ACB", "MoMo"]
CATEGORIES = ["Ăn uống", "Nhà ở", "Di chuyển", "Khác", "Lương", "Chuyển ví"]
TYPES = ["Chi tiêu", "Thu nhập", "Chuyển ví"]

# Số dư ban đầu của từng ví (VND)
INITIAL_BALANCES = {"Cash": 2_340_000, "MBB": 18_500_000, "ACB": 10_000_000, "MoMo": 2_000_000}

# Ngân sách theo danh mục (VND / tháng)
BUDGETS = {"Ăn uống": 5_000_000, "Nhà ở": 3_500_000, "Di chuyển": 2_500_000, "Khác": 1_200_000}


def _seed_transactions() -> pd.DataFrame:
    today = date(2026, 9, 29)
    rows = [
        (today, "Hoán đổi Techcombank", "Chuyển ví", "ACB", 250_000, "Chuyển ví"),
        (today, "WinMart", "Chi tiêu", "MoMo", -486_000, "Ăn uống"),
        (today, "Grab", "Chi tiêu", "MBB", -384_000, "Di chuyển"),
        (today - timedelta(days=1), "Lương tháng 9", "Thu nhập", "MBB", 18_500_000, "Lương"),
        (today - timedelta(days=2), "Tiền nhà tháng 9", "Chi tiêu", "ACB", -2_840_000, "Nhà ở"),
        (today - timedelta(days=3), "Quán cơm", "Chi tiêu", "Cash", -120_000, "Ăn uống"),
    ]
    df = pd.DataFrame(rows, columns=["Ngày", "Giao dịch", "Loại", "Ví", "Số tiền", "Danh mục"])
    return df


def get_transactions() -> pd.DataFrame:
    """Lấy danh sách giao dịch từ session, khởi tạo lần đầu nếu chưa có."""
    if "transactions" not in st.session_state:
        st.session_state.transactions = _seed_transactions()
    return st.session_state.transactions


def add_transaction(row: dict) -> None:
    df = get_transactions()
    new = pd.DataFrame([row])
    st.session_state.transactions = pd.concat([new, df], ignore_index=True)


def wallet_balances() -> dict:
    df = get_transactions()
    balances = dict(INITIAL_BALANCES)
    for _, r in df.iterrows():
        balances[r["Ví"]] = balances.get(r["Ví"], 0) + r["Số tiền"]
    return balances


def real_flows(df: pd.DataFrame) -> pd.DataFrame:
    """Bỏ các dòng chuyển giữa ví: đó không phải thu nhập hay chi tiêu thật."""
    return df[df["Loại"] != "Chuyển ví"]


def fmt_vnd(value: float) -> str:
    return f"{value:,.0f} ₫".replace(",", ".")

"""Dữ liệu mẫu và các hàm dùng chung cho app tài chính cá nhân."""

from copy import deepcopy
from datetime import date, timedelta
from typing import TypeVar

import pandas as pd
import streamlit as st

AccountData = TypeVar("AccountData")

WALLETS = ["Cash", "MBB", "ACB", "MoMo"]
CATEGORIES = ["Ăn uống", "Nhà ở", "Di chuyển", "Khác", "Lương", "Chuyển ví"]
TYPES = ["Chi tiêu", "Thu nhập", "Chuyển ví"]
DEMO_USER_KEY = "demo@example.com"
TRANSACTION_COLUMNS = ["Ngày", "Giao dịch", "Loại", "Ví", "Số tiền", "Danh mục"]

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
    df = pd.DataFrame(rows, columns=TRANSACTION_COLUMNS)
    return df


def _active_user_key() -> str:
    email = st.session_state.get("current_user_email")
    if email:
        return email.strip().lower()

    current_user = st.session_state.get("current_user")
    users = st.session_state.get("users", {})
    matches = [
        email for email, user in users.items()
        if user.get("name") == current_user
    ]
    if len(matches) == 1:
        st.session_state.current_user_email = matches[0]
        return matches[0]
    if not current_user:
        return DEMO_USER_KEY
    if current_user == "An Nhiên" and not matches:
        return DEMO_USER_KEY
    return f"legacy:{current_user}"


def is_demo_user() -> bool:
    return _active_user_key() == DEMO_USER_KEY


def get_account_data(
    section: str,
    default: AccountData,
) -> AccountData:
    """Lấy dữ liệu trong phiên của đúng tài khoản đang đăng nhập."""
    user_key = _active_user_key()
    account_data = st.session_state.setdefault("account_data", {})
    section_data = account_data.setdefault(section, {})
    if user_key not in section_data:
        section_data[user_key] = deepcopy(default)
    return section_data[user_key]


def _transactions_by_user() -> dict:
    if "transactions_by_user" not in st.session_state:
        transactions = {}
        legacy_transactions = st.session_state.pop("transactions", None)
        if legacy_transactions is not None:
            transactions[DEMO_USER_KEY] = legacy_transactions
        st.session_state.transactions_by_user = transactions
    return st.session_state.transactions_by_user


def get_transactions() -> pd.DataFrame:
    """Lấy giao dịch riêng của tài khoản hiện tại; chỉ tài khoản demo có dữ liệu mẫu."""
    user_key = _active_user_key()
    transactions = _transactions_by_user()
    if user_key not in transactions:
        transactions[user_key] = (
            _seed_transactions()
            if user_key == DEMO_USER_KEY
            else pd.DataFrame(columns=TRANSACTION_COLUMNS)
        )
    return transactions[user_key]


def add_transaction(row: dict) -> None:
    df = get_transactions()
    new = pd.DataFrame([row])
    _transactions_by_user()[_active_user_key()] = pd.concat([new, df], ignore_index=True)


def wallet_balances() -> dict:
    df = get_transactions()
    user_key = _active_user_key()
    balances = dict(INITIAL_BALANCES) if user_key == DEMO_USER_KEY else dict.fromkeys(WALLETS, 0)
    for _, r in df.iterrows():
        balances[r["Ví"]] = balances.get(r["Ví"], 0) + r["Số tiền"]
    return balances


def real_flows(df: pd.DataFrame) -> pd.DataFrame:
    """Bỏ các dòng chuyển giữa ví: đó không phải thu nhập hay chi tiêu thật."""
    return df[df["Loại"] != "Chuyển ví"]


def fmt_vnd(value: float) -> str:
    return f"{value:,.0f} ₫".replace(",", ".")

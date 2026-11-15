"""Trợ lý tài chính AI: dùng API của Groq (miễn phí), có dự phòng bằng quy tắc khi không có khóa hoặc lỗi.

Dữ liệu gửi tới API chỉ là tổng hợp (số dư, chi theo danh mục, hạn mức). Không gửi tên giao dịch.
Khóa API đặt trong Streamlit Secrets (GROQ_API_KEY) hoặc biến môi trường, không ghi vào mã nguồn.
"""

import os

import streamlit as st
from openai import OpenAI

from data import BUDGETS, fmt_vnd, get_transactions, real_flows, wallet_balances
from ui import page_header

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = (
    "Bạn là trợ lý tài chính cá nhân trong ứng dụng Máy / Tài chính. Luôn trả lời bằng tiếng Việt, ngắn gọn. "
    "Chỉ dựa trên phần DỮ LIỆU bên dưới; nếu thiếu dữ liệu, nói rõ, không bịa số liệu. "
    "Không đưa khuyến nghị đầu tư cụ thể (mua bán cổ phiếu, tiền mã hóa). "
    "Với vấn đề pháp lý hoặc thuế, khuyên người dùng hỏi chuyên gia."
)


def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        key = None
    return key or os.environ.get("GROQ_API_KEY")


def build_summary() -> str:
    """Tổng hợp tài chính, không có tên giao dịch chi tiết."""
    df = real_flows(get_transactions())
    balances = wallet_balances()
    spend = (
        df[df["Số tiền"] < 0].assign(Chi=lambda d: -d["Số tiền"]).groupby("Danh mục")["Chi"].sum()
    )
    lines = ["Số dư theo ví:"]
    lines += [f"- {w}: {fmt_vnd(a)}" for w, a in balances.items()]
    lines.append(f"Tổng số dư: {fmt_vnd(sum(balances.values()))}")
    lines.append("Chi tiêu tháng 9/2026 so với hạn mức:")
    for cat, limit in BUDGETS.items():
        lines.append(f"- {cat}: đã chi {fmt_vnd(float(spend.get(cat, 0)))} / hạn mức {fmt_vnd(limit)}")
    return "\n".join(lines)


def answer(question: str) -> str:
    """Trả lời theo quy tắc, dùng khi không có API hoặc API lỗi."""
    q = question.lower()
    df = real_flows(get_transactions())
    balances = wallet_balances()
    spend = df[df["Số tiền"] < 0].assign(Chi=lambda d: -d["Số tiền"]).groupby("Danh mục")["Chi"].sum()

    if "số dư" in q or "tổng" in q:
        return f"Tổng số dư hiện tại là {fmt_vnd(sum(balances.values()))}."
    if "ví" in q:
        lines = [f"- {w}: {fmt_vnd(a)}" for w, a in balances.items()]
        return "Số dư theo ví:\n" + "\n".join(lines)
    if "vượt" in q or "ngân sách" in q:
        over = [c for c, limit in BUDGETS.items() if spend.get(c, 0) > limit]
        if over:
            return "Các danh mục đang vượt ngân sách: " + ", ".join(over) + "."
        return "Hiện chưa danh mục nào vượt ngân sách."
    if "chi" in q:
        top = spend.sort_values(ascending=False).head(3)
        if top.empty:
            return "Chưa có chi tiêu nào được ghi nhận."
        return "Ba danh mục chi nhiều nhất:\n" + "\n".join(f"- {c}: {fmt_vnd(v)}" for c, v in top.items())
    return ("Mình có thể trả lời về: tổng số dư, số dư từng ví, ngân sách vượt mức, "
            "và các danh mục chi nhiều nhất. Hãy thử hỏi một trong các ý đó.")


def ask_groq(api_key: str, history: list[dict]) -> str:
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    # Bỏ lời chào mở đầu của trợ lý (API yêu cầu tin nhắn đầu là của người dùng)
    msgs = [m for m in history[-10:]]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nDỮ LIỆU:\n" + build_summary()}]
    messages += [{"role": m["role"], "content": m["content"]} for m in msgs]
    resp = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=800)
    return (resp.choices[0].message.content or "").strip()


page_header("Trợ lý tài chính AI", "Hỏi về số dư, chi tiêu và ngân sách của bạn")

api_key = get_api_key()
if api_key:
    st.caption(
        f"Đang dùng mô hình {MODEL} qua Groq. Chỉ tổng hợp số dư và chi tiêu được gửi tới API, không gửi tên giao dịch."
    )
else:
    st.info("Chưa cấu hình GROQ_API_KEY, đang trả lời theo quy tắc mẫu.")

if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "content": "Chào bạn, bạn muốn hỏi gì về tài chính của mình?"}]

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ví dụ: danh mục nào vượt ngân sách?"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    reply = None
    if api_key:
        with st.spinner("Đang trả lời..."):
            try:
                reply = ask_groq(api_key, st.session_state.chat)
            except Exception as exc:  # lỗi mạng, hết quota, khóa sai...
                reply = f"(Không gọi được AI: {type(exc).__name__}. Trả lời theo quy tắc:)\n\n" + answer(prompt)
    if not reply:
        reply = answer(prompt)
    st.session_state.chat.append({"role": "assistant", "content": reply})
    st.rerun()

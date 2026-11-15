"""Trợ lý tài chính AI: bản thử nghiệm dựa trên quy tắc, trả lời từ dữ liệu trong app.

Để nối với mô hình AI thật, thay hàm `answer()` bằng lời gọi API (ví dụ Anthropic SDK)
và đặt khóa API qua biến môi trường. Không ghi khóa vào mã nguồn.
"""

import streamlit as st

from data import BUDGETS, fmt_vnd, get_transactions, real_flows, wallet_balances


st.title("Trợ lý tài chính AI")
st.caption("Hỏi về số dư, chi tiêu và ngân sách của bạn")


def answer(question: str) -> str:
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


if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "content": "Chào bạn, bạn muốn hỏi gì về tài chính của mình?"}]

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ví dụ: danh mục nào vượt ngân sách?"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    st.session_state.chat.append({"role": "assistant", "content": answer(prompt)})
    st.rerun()

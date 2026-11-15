"""Trợ lý tài chính AI: gọi Groq nếu có GROQ_API_KEY, nếu không thì trả lời theo quy tắc.

Khóa đọc từ st.secrets (Streamlit Cloud: Settings > Secrets; máy cá nhân: .streamlit/secrets.toml)
hoặc biến môi trường. Không ghi khóa vào mã nguồn: repo đang public.
"""

import json
import os
import urllib.error
import urllib.request

import streamlit as st

from data import BUDGETS, fmt_vnd, get_transactions, real_flows, wallet_balances


st.title("Trợ lý tài chính AI")
st.caption("Hỏi về số dư, chi tiêu và ngân sách của bạn")


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _secret(name: str, default: str | None = None) -> str | None:
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:  # không có file secrets
        pass
    return os.environ.get(name, default)


def finance_context() -> str:
    """Tóm tắt dữ liệu trong app để mô hình trả lời đúng số liệu của người dùng."""
    df = real_flows(get_transactions())
    balances = wallet_balances()
    spend = df[df["Số tiền"] < 0].assign(Chi=lambda d: -d["Số tiền"]).groupby("Danh mục")["Chi"].sum()
    income = df[df["Số tiền"] > 0]["Số tiền"].sum()
    lines = [f"Tổng số dư: {fmt_vnd(sum(balances.values()))}"]
    lines += [f"Ví {w}: {fmt_vnd(a)}" for w, a in balances.items()]
    lines.append(f"Tổng thu: {fmt_vnd(income)}; tổng chi: {fmt_vnd(spend.sum())}")
    for c, v in spend.sort_values(ascending=False).items():
        limit = BUDGETS.get(c)
        extra = f" / ngân sách {fmt_vnd(limit)}" + (" (VƯỢT)" if v > limit else "") if limit else ""
        lines.append(f"Chi {c}: {fmt_vnd(v)}{extra}")
    return "\n".join(lines)


def groq_answer(history: list[dict], key: str) -> str:
    system = (
        "Bạn là trợ lý tài chính cá nhân, trả lời ngắn gọn bằng tiếng Việt. "
        "Chỉ dùng số liệu trong dữ liệu dưới đây, không bịa số. "
        "Nếu dữ liệu không đủ để trả lời, hãy nói rõ.\n\nDữ liệu hiện tại:\n" + finance_context()
    )
    body = {
        "model": _secret("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "messages": [{"role": "system", "content": system}] + history[-10:],
        "temperature": 0.3,
    }
    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(body).encode("utf-8"),
        # Cloudflare của Groq chặn User-Agent mặc định "Python-urllib" (lỗi 1010)
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "finance-web/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


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
    key = _secret("GROQ_API_KEY")
    reply = None
    if key:
        try:
            with st.spinner("Đang suy nghĩ..."):
                reply = groq_answer(st.session_state.chat[1:], key)
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as e:
            detail = f"HTTP {e.code}" if isinstance(e, urllib.error.HTTPError) else type(e).__name__
            st.session_state.ai_error = f"Không gọi được Groq ({detail}), đang dùng trả lời theo quy tắc."
    st.session_state.chat.append({"role": "assistant", "content": reply or answer(prompt)})
    st.rerun()

if err := st.session_state.pop("ai_error", None):
    st.warning(err)
if not _secret("GROQ_API_KEY"):
    st.caption("Chưa cấu hình GROQ_API_KEY: đang trả lời theo quy tắc mẫu.")

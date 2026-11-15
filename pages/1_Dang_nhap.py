"""Đăng nhập & Đăng ký, bố cục theo frame 'Đăng nhập · Desktop' trong Figma.

Bên trái: form đăng nhập. Bên phải: panel tối 'Theo dõi nợ, tránh vỡ nợ' với bảng xem trước.
"""

import hashlib
import hmac
import os
import re

import streamlit as st


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1280px;}
    .brand {font-weight: 700; color: #DB2777; font-size: 18px;}
    .hero {background: #1F1B2E; color: #FFFFFF; border-radius: 20px; padding: 36px;}
    .hero .badge {display: inline-block; font-size: 11px; letter-spacing: .08em;
                  background: rgba(255,255,255,.12); padding: 4px 10px; border-radius: 999px;}
    .hero h2 {color: #FFFFFF; font-size: 34px; margin: 18px 0 8px;}
    .hero p {color: #C9C3D6; font-size: 14px;}
    .preview {background: #FFFFFF; color: #1F1B24; border-radius: 14px; padding: 20px; margin-top: 20px;}
    .preview .kpi {display: flex; gap: 12px; margin: 12px 0;}
    .preview .kpi div {flex: 1; background: #F7F5F8; border-radius: 10px; padding: 10px;}
    .preview .kpi b {font-size: 22px;}
    .bar {height: 8px; border-radius: 4px; background: #F1ECF3; margin: 6px 0 10px;}
    .bar i {display: block; height: 100%; border-radius: 4px; background: #DB2777;}
    .fine {font-size: 12px; color: #6B6372; margin-top: 16px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)


def _users() -> dict:
    if "users" not in st.session_state:
        # Tài khoản demo để thử nhanh. Mật khẩu: demo1234
        salt = b"demo-salt-fixed"
        st.session_state.users = {
            "demo@example.com": {"name": "An Nhiên", "salt": salt, "hash": _hash_password("demo1234", salt)}
        }
    return st.session_state.users


def _register(name: str, email: str, password: str, confirm: str) -> str | None:
    if not name.strip():
        return "Vui lòng nhập họ tên."
    if not EMAIL_RE.match(email):
        return "Email không hợp lệ."
    if len(password) < 8:
        return "Mật khẩu cần ít nhất 8 ký tự."
    if password != confirm:
        return "Mật khẩu xác nhận không khớp."
    users = _users()
    key = email.strip().lower()
    if key in users:
        return "Email này đã được đăng ký."
    salt = os.urandom(16)
    users[key] = {"name": name.strip(), "salt": salt, "hash": _hash_password(password, salt)}
    return None


def _login(email: str, password: str) -> str | None:
    user = _users().get(email.strip().lower())
    if not user or not hmac.compare_digest(user["hash"], _hash_password(password, user["salt"])):
        return "Email hoặc mật khẩu không đúng."
    st.session_state.current_user = user["name"]
    return None


if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

left, right = st.columns([1, 1.15], gap="large")

with left:
    st.markdown('<div class="brand">Máy / Tài chính</div>', unsafe_allow_html=True)

    if st.session_state.get("current_user"):
        st.success(f"Đã đăng nhập: {st.session_state.current_user}")
        if st.button("Đăng xuất"):
            del st.session_state["current_user"]
            st.rerun()
    elif st.session_state.auth_mode == "login":
        st.markdown("## Chào mừng bạn")
        st.caption("Đăng nhập hoặc đăng ký tài khoản")
        with st.form("login_form", border=False):
            email = st.text_input("Email", placeholder="ban@example.com")
            password = st.text_input("Mật khẩu", type="password")
            c1, c2 = st.columns([1, 1])
            c1.checkbox("Ghi nhớ đăng nhập", value=True)
            c2.markdown("<div style='text-align:right'><a href='#'>Quên mật khẩu?</a></div>", unsafe_allow_html=True)
            if st.form_submit_button("Đăng nhập →", type="primary", use_container_width=True):
                err = _login(email, password)
                if err:
                    st.error(err)
                else:
                    st.rerun()
        st.caption("hoặc")
        st.button("Đăng nhập bằng Google", use_container_width=True, disabled=True,
                  help="Chưa kết nối Google. Sẽ bổ sung khi có OAuth.")
        st.write("Chưa có tài khoản?")
        if st.button("Tạo tài khoản"):
            st.session_state.auth_mode = "signup"
            st.rerun()
        st.caption("Thử nhanh: demo@example.com / demo1234")
    else:
        st.markdown("## Tạo tài khoản")
        st.caption("Chỉ mất một phút để bắt đầu")
        with st.form("signup_form", border=False):
            name = st.text_input("Họ và tên")
            email2 = st.text_input("Email", placeholder="ban@example.com")
            pw1 = st.text_input("Mật khẩu (ít nhất 8 ký tự)", type="password")
            pw2 = st.text_input("Xác nhận mật khẩu", type="password")
            if st.form_submit_button("Tạo tài khoản", type="primary", use_container_width=True):
                err = _register(name, email2, pw1, pw2)
                if err:
                    st.error(err)
                else:
                    st.session_state.current_user = name.strip()
                    st.rerun()
        if st.button("← Quay lại đăng nhập"):
            st.session_state.auth_mode = "login"
            st.rerun()

    st.markdown(
        "<div class='fine'>🔒 Dữ liệu của bạn được mã hóa và bảo mật. "
        "Tài khoản chỉ lưu trong phiên làm việc, tải lại trang sẽ mất.</div>",
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="hero">
          <span class="badge">KHÔNG GIAN QUẢN LÝ THÔNG MINH</span>
          <h2>Theo dõi nợ, tránh vỡ nợ.</h2>
          <p>Nhắc lịch trả nợ, cảnh báo trước khi quá hạn và gợi ý thứ tự trả nợ phù hợp.</p>
          <div class="preview">
            <b>Tổng quan hôm nay</b>
            <div class="kpi">
              <div>Khoản nợ đang theo dõi<br><b>128</b></div>
              <div>Tỷ lệ đúng hạn<br><b>96%</b></div>
            </div>
            <div>Tiến độ trả nợ</div>
            <div>Thẻ tín dụng · 87%</div>
            <div class="bar"><i style="width:87%"></i></div>
            <div>Vay bạn bè · 64%</div>
            <div class="bar"><i style="width:64%"></i></div>
            <div>Vay mua xe · 48%</div>
            <div class="bar"><i style="width:48%"></i></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

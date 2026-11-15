"""Điểm vào của ứng dụng: chưa đăng nhập chỉ hiện trang Đăng nhập; đăng nhập xong mới hiện menu đầy đủ."""

import streamlit as st

from ui import inject_theme

st.set_page_config(page_title="Máy / Tài chính", page_icon="💰", layout="wide")

logged_in = bool(st.session_state.get("current_user"))
inject_theme(logged_in)

login = st.Page("pages/1_Dang_nhap.py", title="Đăng nhập", icon="🔐", url_path="dang-nhap")

if not logged_in:
    st.navigation([login], position="hidden").run()
else:
    with st.sidebar:
        st.markdown('<div class="brand">Máy / Tài chính</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="user-chip">Xin chào, {st.session_state.current_user}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Đăng xuất", use_container_width=True):
            del st.session_state["current_user"]
            st.rerun()

    def page(path: str, title: str, icon: str, **kw) -> st.Page:
        return st.Page(f"pages/{path}", title=title, icon=icon, **kw)

    nav = st.navigation(
        {
            "Tài chính": [
                page("0_Tong_quan.py", "Tổng quan", "📊", default=True),
                page("2_Giao_dich.py", "Giao dịch", "🧾"),
                page("3_Them_giao_dich.py", "Thêm giao dịch", "➕"),
                page("4_Vi.py", "Ví", "👛"),
                page("10_Lich_giao_dich.py", "Lịch giao dịch", "🗓️"),
                page("11_Hoa_don_dinh_ky.py", "Hóa đơn & định kỳ", "🧾"),
            ],
            "Phân tích": [
                page("5_Ngan_sach.py", "Ngân sách", "📊"),
                page("6_Bao_cao.py", "Báo cáo", "📈"),
                page("7_Muc_tieu_cong_no.py", "Mục tiêu & công nợ", "🎯"),
            ],
            "Khác": [
                page("13_Canh_bao_vo_no.py", "Cảnh báo vỡ nợ", "⚠️"),
                page("9_Tro_ly_AI.py", "Trợ lý AI", "🤖"),
                page("12_Tai_khoan_tien_ich.py", "Tài khoản & tiện ích", "🔗"),
                page("8_Cai_dat.py", "Cài đặt", "⚙️"),
            ],
        }
    )
    nav.run()

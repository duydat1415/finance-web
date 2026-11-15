"""Giao diện dùng chung, theo thiết kế Figma: nền xám nhạt, thẻ trắng bo góc, nhấn hồng."""

import html

import streamlit as st

from data import fmt_vnd

PINK = "#DB2777"
VIOLET = "#7C3AED"
BLUE = "#2563EB"
AMBER = "#F59E0B"
GREEN = "#16A34A"
RED = "#DC2626"
MUTED = "#6B6372"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, .stApp, [class*="css"] {font-family: Inter, system-ui, sans-serif;}
.stApp {background: #F7F5F8;}
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px;}
h1 {font-size: 26px !important; font-weight: 700 !important; color: #1F1B24;}
h2, h3 {color: #1F1B24; font-weight: 700 !important;}
.page-head {margin-bottom: 8px;}
.page-head h1 {margin: 0 !important; padding: 0;}
.page-head p {margin: 4px 0 0; color: #6B6372; font-size: 14px;}

[data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #ECE8EE;}
[data-testid="stSidebarNavLink"] {border-radius: 12px; margin: 2px 8px;}
[data-testid="stSidebarNavLink"][aria-current="page"] {background: #FCE7F3;}
[data-testid="stSidebarNavLink"][aria-current="page"] span {color: #DB2777 !important; font-weight: 600;}
.brand {font-weight: 700; color: #DB2777; font-size: 16px; padding: 8px 16px 4px;}
.user-chip {font-size: 13px; color: #6B6372; padding: 0 16px 12px;}

[data-testid="stVerticalBlockBorderWrapper"] > div > div {
  background: #FFFFFF; border-radius: 16px;
}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 16px !important; border-color: #ECE8EE !important;}

[data-testid="stMetric"] {background: #FFFFFF; border: 1px solid #ECE8EE; border-radius: 16px; padding: 16px 20px;}
[data-testid="stMetricValue"] {color: #1F1B24; font-weight: 700;}
[data-testid="stMetricLabel"] {color: #6B6372;}

button[kind="primary"], button[data-testid="stBaseButton-primary"] {
  background: #DB2777 !important; border-color: #DB2777 !important;
  border-radius: 12px !important; font-weight: 700 !important; color: #FFFFFF !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {filter: brightness(0.94);}
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {border-radius: 12px !important;}

[data-baseweb="input"] > div, [data-baseweb="select"] > div, [data-baseweb="textarea"] > div {
  border-radius: 12px !important; background: #FFFFFF !important; border-color: #E4DEE8 !important;
}
[data-testid="stProgress"] > div > div > div > div {background-color: #DB2777 !important;}
[data-testid="stDataFrame"] {border-radius: 12px; overflow: hidden;}

.hero-balance {
  background: #3B2A3D; color: #FFFFFF; border-radius: 16px; padding: 28px;
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 24px;
}
.hero-balance .hb-label {font-size: 14px; opacity: 0.8;}
.hero-balance .hb-value {font-size: 36px; font-weight: 700; margin-top: 6px;}
.hero-balance .hb-side {display: flex; gap: 32px; flex-wrap: wrap;}
.hero-balance .hb-side div {display: flex; flex-direction: column; gap: 4px;}
.hero-balance .hb-side span {font-size: 13px; opacity: 0.8;}
.hero-balance .hb-side b {font-weight: 600; font-size: 16px;}

.donut-wrap {display: flex; gap: 24px; align-items: center; flex-wrap: wrap;}
.donut {position: relative; width: 140px; height: 140px; border-radius: 50%; flex-shrink: 0;}
.donut-hole {
  position: absolute; inset: 24px; background: #FFFFFF; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  font-size: 12px; color: #6B6372;
}
.donut-hole b {color: #1F1B24; font-size: 14px;}
.legend {display: flex; flex-direction: column; gap: 10px; flex: 1 1 180px; font-size: 14px;}
.lg-row {display: flex; justify-content: space-between; gap: 12px;}
.lg-row i {display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px;}
"""


def inject_theme(logged_in: bool) -> None:
    """Gắn CSS theme. Khi chưa đăng nhập thì ẩn thanh bên."""
    hide = "" if logged_in else '[data-testid="stSidebar"] {display: none !important;}'
    st.markdown(f"<style>{CSS}{hide}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-head"><h1>{html.escape(title)}</h1>{sub}</div>',
        unsafe_allow_html=True,
    )


def donut_html(items: list[tuple[str, float, str]], center_value: str) -> str:
    """Biểu đồ tròn + chú thích. items: (nhãn, giá trị, màu)."""
    total = sum(v for _, v, _ in items if v > 0)
    stops, start = [], 0.0
    for _, v, color in items:
        if v <= 0 or total <= 0:
            continue
        end = start + v / total * 100
        stops.append(f"{color} {start:.2f}% {end:.2f}%")
        start = end
    grad = ", ".join(stops) if stops else "#ECE8EE 0% 100%"
    legend = "".join(
        f'<div class="lg-row"><span><i style="background:{c}"></i>{html.escape(label)}</span>'
        f"<b>{fmt_vnd(v)}</b></div>"
        for label, v, c in items
    )
    return (
        '<div class="donut-wrap">'
        f'<div class="donut" style="background: conic-gradient({grad})">'
        f'<div class="donut-hole">Tổng chi<b>{html.escape(center_value)}</b></div></div>'
        f'<div class="legend">{legend}</div></div>'
    )

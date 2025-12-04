import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import os
import textwrap

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"  # 彻底收起侧边栏
)

# -------------------------- 1. 硅谷风格 CSS (核心修改) --------------------------
st.markdown("""
<style>
    /* 基础重置：硅谷风强调简洁、留白、高对比度 */
    .stApp {
        background-color: #f9fafb;
        font-family: 'SF Pro Display', 'Inter', sans-serif;
        padding-top: 70px !important; /* 给导航栏留空间 */
    }
    
    /* 隐藏 Streamlit 默认元素 */
    header, [data-testid="stSidebar"], [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* ----- 硅谷风导航栏 ----- */
    .silicon-nav {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 64px !important;
        background: #ffffff !important;
        border-bottom: 1px solid #e5e7eb !important;
        z-index: 99999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 2.5vw !important;
        box-sizing: border-box !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Logo 区域：简洁粗体 + 科技感图标 */
    .nav-logo {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        text-decoration: none !important;
    }
    .logo-icon {
        width: 32px !important;
        height: 32px !important;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        border-radius: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    .logo-text {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #111827 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* 导航链接：极简扁平，hover 效果柔和 */
    .nav-links {
        display: flex !important;
        gap: 32px !important;
        align-items: center !important;
    }
    .nav-link {
        color: #4b5563 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-decoration: none !important;
        transition: all 0.15s ease !important;
        position: relative !important;
        padding: 8px 0 !important;
    }
    .nav-link:hover {
        color: #6366f1 !important;
    }
    /* 激活状态：底部细线条 */
    .nav-link.active {
        color: #6366f1 !important;
    }
    .nav-link.active::after {
        content: '' !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 2px !important;
        background: #6366f1 !important;
        border-radius: 1px !important;
    }
    
    /* 右侧功能区：搜索框 + 用户头像 */
    .nav-actions {
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
    }
    .nav-search {
        width: 180px !important;
        height: 36px !important;
        background: #f3f4f6 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0 12px !important;
        font-size: 13px !important;
        color: #111827 !important;
        transition: background 0.15s ease !important;
    }
    .nav-search:focus {
        outline: none !important;
        background: #e5e7eb !important;
    }
    .nav-user {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        background: #f3f4f6 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #4b5563 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: 1px solid #e5e7eb !important;
        cursor: pointer !important;
    }
    
    /* 响应式适配：小屏幕隐藏搜索框 */
    @media (max-width: 768px) {
        .nav-search {
            display: none !important;
        }
        .nav-links {
            gap: 20px !important;
        }
    }
    
    /* 卡片样式：硅谷风极简扁平 */
    .metric-card {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 20px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
        text-align: center !important;
        box-sizing: border-box !important;
    }
    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        line-height: 1.2 !important;
    }
    .highlight {
        color: #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 2. 渲染硅谷风导航栏 --------------------------
def render_silicon_navbar():
    navbar_html = textwrap.dedent("""
    <nav class="silicon-nav">
        <!-- 左侧 Logo -->
        <a href="#" class="nav-logo">
            <div class="logo-icon">WR</div>
            <span class="logo-text">WealthRank Pro</span>
        </a>
        
        <!-- 中间导航链接 -->
        <div class="nav-links">
            <a href="#" class="nav-link active">Dashboard</a>
            <a href="#" class="nav-link">Global Map</a>
            <a href="#" class="nav-link">Calculator</a>
            <a href="#" class="nav-link">Reports</a>
        </div>
        
        <!-- 右侧功能区 -->
        <div class="nav-actions">
            <input type="text" class="nav-search" placeholder="Search assets...">
            <div class="nav-user">JD</div>
        </div>
    </nav>
    """)
    st.markdown(navbar_html, unsafe_allow_html=True)

# -------------------------- 3. 逻辑与数据 (保持不变) --------------------------
TRANSLATIONS = {
    "English": {"title": "Global Wealth Position", "subtitle": "Real-time wealth distribution estimator.", "location": "Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Calculate Position", "card_income": "Income Level", "card_wealth": "Wealth Status", "rank_prefix": "Nationwide", "rank_approx": "≈ Rank #", "disclaimer": "Based on Log-Normal Distribution Model"},
    "中文": {"title": "全球财富金字塔", "subtitle": "个人财富实时排名系统", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "查看我的排名", "card_income": "年收入水平", "card_wealth": "资产水平", "rank_prefix": "超过所选国家", "rank_approx": "≈ 绝对排名 第", "disclaimer": "基于对数正态分布模型估算"}
}

COUNTRY_DATA = {
    "CN": {"name_en": "China", "name_zh": "中国", "currency": "¥", "population": 1411750000, "medianIncome": 35000, "medianWealth": 120000, "incomeGini": 0.7, "wealthGini": 1.1},
    "US": {"name_en": "USA", "name_zh": "美国", "currency": "$", "population": 331900000, "medianIncome": 45000, "medianWealth": 190000, "incomeGini": 0.8, "wealthGini": 1.5},
    "JP": {"name_en": "Japan", "name_zh": "日本", "currency": "¥", "population": 125700000, "medianIncome": 4000000, "medianWealth": 15000000, "incomeGini": 0.6, "wealthGini": 0.9},
    "UK": {"name_en": "UK", "name_zh": "英国", "currency": "£", "population": 67330000, "medianIncome": 31000, "medianWealth": 150000, "incomeGini": 0.65, "wealthGini": 1.2},
    "DE": {"name_en": "Germany", "name_zh": "德国", "currency": "€", "population": 83200000, "medianIncome": 28000, "medianWealth": 110000, "incomeGini": 0.6, "wealthGini": 1.1},
}

def get_log_normal_percentile(value, median, shape_parameter):
    if value <= 1: return 0.0001
    try:
        mu = math.log(median)
        sigma = shape_parameter
        z = (math.log(value) - mu) / sigma
        percentile = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        return min(max(percentile, 0.0001), 0.9999)
    except: return 0.0001

def format_compact_localized(num, lang_key):
    if lang_key == "中文":
        if num >= 1e8: return f"{num/1e8:.2f}亿"
        if num >= 1e4: return f"{num/1e4:.1f}万"
        return f"{num:,.0f}"
    else:
        if num >= 1e9: return f"{num/1e9:.1f}B"
        if num >= 1e6: return f"{num/1e6:.1f}M"
        if num >= 1e4: return f"{num/1e3:.0f}k"
        return f"{num:,.0f}"

def render_metric_card(t, amount, currency, percentile, rank, color, lang_key):
    top_percent = (1 - percentile) * 100
    rank_str = f"Top {top_percent:.1f}%" if lang_key != "中文" else f"前 {top_percent:.1f}%"
    st.markdown(f"""
    <div class="metric-card" style="border-top: 3px solid {color};">
        <div style="color:#6b7280; font-size:0.8rem; font-weight:500; text-transform:uppercase; letter-spacing:0.5px;">
            {t[f'card_{"income" if color=="#6366f1" else "wealth"}']}
        </div>
        <div class="metric-value">{currency} {format_compact_localized(amount, lang_key)}</div>
        <div style="font-size:0.85rem; color:#4b5563; margin-top:8px;">
            {t['rank_prefix']} <span class="highlight" style="color:{color}; font-weight:600;">{rank_str}</span>
        </div>
        <div style="font-size:0.75rem; color:#9ca3af; margin-top:4px;">
            {t['rank_approx']} {format_compact_localized(rank, lang_key)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    x = np.linspace(-3, 3, 50)
    y = np.exp(-0.5 * x**2)
    chart_x = (x + 3) / 6
    chart_y = y / y.max()
    simulated_z = (percentile - 0.5) * 6
    marker_x = percentile
    marker_y = np.exp(-0.5 * simulated_z**2)
    
    fig, ax = plt.subplots(figsize=(5, 1))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.fill_between(chart_x, chart_y, color=color, alpha=0.1)
    ax.plot(chart_x, chart_y, color=color, linewidth=1.2)
    ax.scatter([marker_x], [marker_y], color=color, s=25)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# -------------------------- 4. 主程序入口 --------------------------
def main():
    # 渲染硅谷风导航栏（优先执行）
    render_silicon_navbar()
    
    # 语言选择
    c_head, c_lang = st.columns([5, 1])
    with c_lang:
        lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
    text = TRANSLATIONS[lang]
    
    # 页面主标题（硅谷风简洁排版）
    with c_head:
        st.markdown(f"# {text['title']}")
        st.markdown(f"<p style='color:#6b7280; margin-top:-12px; font-size:1rem;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    
    # 核心功能区
    st.markdown("---", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        country_code = st.selectbox(text['location'], options=COUNTRY_DATA.keys(), format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"])
        country = COUNTRY_DATA[country_code]
    with c2:
        income = st.number_input(text['income'], value=int(country["medianIncome"]), step=1000)
    with c3:
        wealth = st.number_input(text['wealth'], value=int(country["medianWealth"]), step=5000)

    st.markdown("<br>", unsafe_allow_html=True)
    # 硅谷风按钮样式
    st.markdown("""
    <style>
        .stButton > button {
            background: #6366f1 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 10px 0 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            transition: background 0.15s ease !important;
        }
        .stButton > button:hover {
            background: #4f46e5 !important;
            box-shadow: 0 2px 4px 0 rgba(99, 102, 241, 0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    if st.button(text['btn_calc'], type="primary", use_container_width=True):
        inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
        wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
        inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
        wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
        
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#6366f1", lang)
        with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#8b5cf6", lang)
    
    st.markdown(f"<div style='text-align:center; color:#9ca3af; font-size:0.75rem; margin-top:24px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

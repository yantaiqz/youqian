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
    initial_sidebar_state="collapsed"
)

# -------------------------- 1. 硅谷风格 CSS (增强版) --------------------------
st.markdown("""
<style>
    /* ----- 基础容器重置 ----- */
    .stApp {
        background-color: #f9fafb; /* 极淡的灰背景，突出白色卡片 */
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 核心：给主内容容器增加顶部留白，防止被导航栏遮挡 */
    .main .block-container {
        padding-top: 80px !important; 
        max-width: 1200px !important; /* 限制最大宽度，防止在大屏上太散 */
    }
    
    /* 隐藏 Streamlit 原生所有干扰元素 */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    
    /* ----- 硅谷风导航栏 (Fixed Top) ----- */
    .silicon-nav {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 64px !important;
        background: rgba(255, 255, 255, 0.95) !important; /* 轻微透明 */
        backdrop-filter: blur(8px) !important; /* 毛玻璃效果 */
        border-bottom: 1px solid #e5e7eb !important;
        z-index: 999999 !important; /* 确保层级最高 */
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 24px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Logo 区域 */
    .nav-left {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    .logo-box {
        width: 32px !important;
        height: 32px !important;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border-radius: 8px !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2) !important;
    }
    .logo-text {
        font-family: 'Inter', sans-serif !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #111827 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* 中间链接 */
    .nav-center {
        display: flex !important;
        gap: 32px !important;
    }
    .nav-link {
        color: #6b7280 !important;
        text-decoration: none !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: color 0.2s ease !important;
        position: relative !important;
        padding: 20px 0 !important;
    }
    .nav-link:hover {
        color: #111827 !important;
    }
    .nav-link.active {
        color: #4f46e5 !important;
    }
    .nav-link.active::after {
        content: '' !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 2px !important;
        background: #4f46e5 !important;
    }
    
    /* 右侧用户区 */
    .nav-right {
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
    }
    .search-input {
        background: #f3f4f6 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        color: #374151 !important;
        width: 160px !important;
        outline: none !important;
    }
    .user-avatar {
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        background: #e0e7ff !important;
        color: #4338ca !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        border: 2px solid white !important;
        box-shadow: 0 0 0 1px #e5e7eb !important;
    }
    
    /* 响应式：窄屏隐藏搜索框 */
    @media (max-width: 768px) {
        .search-input { display: none !important; }
        .nav-center { gap: 16px !important; }
        .nav-link { font-size: 13px !important; }
    }

    /* 结果卡片美化 */
    .metric-card {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 24px !important;
        text-align: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: transform 0.2s !important;
    }
    .metric-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    .metric-value {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #111827 !important;
        letter-spacing: -1px !important;
    }
    .highlight { color: #4f46e5 !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------- 2. 注入导航栏 HTML --------------------------
def render_navbar():
    navbar_html = textwrap.dedent("""
    <div class="silicon-nav">
        <div class="nav-left">
            <div class="logo-box">W</div>
            <div class="logo-text">WealthRank</div>
        </div>
        
        <div class="nav-center">
            <a href="#" class="nav-link active">Dashboard</a>
            <a href="#" class="nav-link">Analytics</a>
            <a href="#" class="nav-link">Reports</a>
            <a href="#" class="nav-link">Settings</a>
        </div>
        
        <div class="nav-right">
            <input type="text" class="search-input" placeholder="Search...">
            <div class="user-avatar">JD</div>
        </div>
    </div>
    """)
    st.markdown(navbar_html, unsafe_allow_html=True)

# -------------------------- 3. 业务逻辑 (保持稳定) --------------------------
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
    <div class="metric-card" style="border-top: 4px solid {color};">
        <div style="color:#6b7280; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
            {t[f'card_{"income" if color=="#6366f1" else "wealth"}']}
        </div>
        <div class="metric-value">{currency} {format_compact_localized(amount, lang_key)}</div>
        <div style="font-size:0.9rem; color:#4b5563; margin-top:8px;">
            {t['rank_prefix']} <span class="highlight" style="color:{color};">{rank_str}</span>
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
    ax.plot(chart_x, chart_y, color=color, linewidth=1.5)
    ax.scatter([marker_x], [marker_y], color=color, s=30, edgecolor="white", linewidth=1.5)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# -------------------------- 4. 主程序入口 --------------------------
def main():
    # 渲染导航栏 (Fixed Position)
    render_navbar()
    
    # 语言选择
    c_head, c_lang = st.columns([5, 1])
    with c_lang:
        lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
    text = TRANSLATIONS[lang]
    
    # 主标题
    with c_head:
        st.markdown(f"<h1 style='font-size:2.2rem; color:#111827;'>{text['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#6b7280; font-size:1.1rem; margin-top:-15px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    
    # 核心功能区
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        country_code = st.selectbox(text['location'], options=COUNTRY_DATA.keys(), format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"])
        country = COUNTRY_DATA[country_code]
    with c2:
        income = st.number_input(text['income'], value=int(country["medianIncome"]), step=1000)
    with c3:
        wealth = st.number_input(text['wealth'], value=int(country["medianWealth"]), step=5000)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 按钮样式优化
    st.markdown("""
    <style>
        .stButton > button {
            background-color: #4f46e5 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.6rem 1rem !important;
            font-weight: 600 !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            background-color: #4338ca !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button(text['btn_calc'], type="primary"):
        inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
        wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
        inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
        wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
        
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#6366f1", lang)
        with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#8b5cf6", lang)
    
    st.markdown(f"<div style='text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:40px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

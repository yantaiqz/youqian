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
    layout="wide",  # 必须是 wide 布局
    initial_sidebar_state="collapsed"  # 彻底收起侧边栏，避免占用空间
)

# -------------------------- 1. CSS 样式 (优化导航栏显示核心) --------------------------
st.markdown("""
<style>
    /* ----- 基础重置 ----- */
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        padding-top: 80px !important; /* 给固定导航栏预留顶部空间 */
    }
    
    /* 隐藏 Streamlit 默认元素，避免干扰导航栏 */
    header {visibility: hidden !important;} /* 隐藏顶部默认栏 */
    [data-testid="stSidebar"] {display: none !important;} /* 彻底隐藏侧边栏 */
    [data-testid="stToolbar"] {display: none !important;} /* 隐藏右上角工具栏 */
    
    /* ----- 顶部导航栏 (Navbar) - 核心优化 ----- */
    .top-navbar {
        position: fixed !important; /* 强制固定 */
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 70px !important;
        background: rgba(255, 255, 255, 0.95) !important; /* 提高不透明度，更清晰 */
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #e2e8f0 !important;
        z-index: 99999 !important; /* 提高层级，确保不被遮挡 */
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 40px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        box-sizing: border-box !important; /* 避免padding导致宽度溢出 */
    }
    
    /* 左侧：Logo */
    .navbar-logo {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    .logo-icon {
        width: 36px !important;
        height: 36px !important;
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
        border-radius: 8px !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.2rem !important;
    }
    
    /* 中间：导航链接 (图片/图标风格) */
    .nav-links {
        display: flex !important;
        gap: 30px !important;
        height: 100% !important;
    }
    
    .nav-item {
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        height: 100% !important;
        color: #64748b !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        border-bottom: 2px solid transparent !important;
        cursor: pointer !important; /* 鼠标悬浮显示指针 */
    }
    
    .nav-item:hover {
        color: #4f46e5 !important;
    }
    
    /* 激活状态 */
    .nav-item.active {
        color: #0f172a !important;
        border-bottom: 2px solid #4f46e5 !important;
    }
    
    /* 导航图标 */
    .nav-img {
        font-size: 1.2rem !important;
        filter: grayscale(100%) !important;
        transition: filter 0.2s ease !important;
    }
    .nav-item:hover .nav-img,
    .nav-item.active .nav-img {
        filter: grayscale(0%) !important;
    }
    
    /* 右侧：用户区域 */
    .user-area {
        display: flex !important;
        align-items: center !important;
        gap: 15px !important;
    }
    .user-avatar {
        width: 36px !important;
        height: 36px !important;
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
        border: 2px solid #fff !important;
        box-shadow: 0 0 0 2px #e2e8f0 !important;
    }
    .search-bar {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        color: #64748b !important;
        width: 200px !important;
        box-sizing: border-box !important;
    }
    
    /* ----- 卡片美化 ----- */
    .metric-card {
        background: white !important; 
        border: 1px solid #f1f5f9 !important; 
        border-radius: 12px !important;
        padding: 24px !important; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important;
        text-align: center !important;
        box-sizing: border-box !important;
    }
    .metric-value { 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: #0f172a !important; 
    }
    .highlight { color: #4f46e5 !important; }

    /* 适配小屏幕，避免导航栏溢出 */
    @media (max-width: 900px) {
        .top-navbar {
            padding: 0 20px !important;
        }
        .nav-links {
            gap: 15px !important;
        }
        .search-bar {
            width: 150px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 2. 渲染顶部导航栏 --------------------------
def render_top_navbar():
    navbar_html = textwrap.dedent("""
    <nav class="top-navbar">
        <div class="navbar-logo">
            <div class="logo-icon">W</div>
            WealthRank Pro
        </div>
        
        <div class="nav-links">
            <div class="nav-item active">
                <span class="nav-img">📊</span> Dashboard
            </div>
            <div class="nav-item">
                <span class="nav-img">🌍</span> Global Map
            </div>
            <div class="nav-item">
                <span class="nav-img">🧮</span> Calculator
            </div>
            <div class="nav-item">
                <span class="nav-img">📑</span> Reports
            </div>
        </div>
        
        <div class="user-area">
            <div class="search-bar">🔍 Search assets...</div>
            <div class="user-avatar">JD</div>
        </div>
    </nav>
    """)
    # 强制渲染导航栏，放在最顶部
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
    <div class="metric-card" style="border-top: 4px solid {color};">
        <div style="color:#64748b; font-size:0.85rem; font-weight:600; text-transform:uppercase;">
            {t[f'card_{"income" if color=="#4f46e5" else "wealth"}']}
        </div>
        <div class="metric-value">{currency} {format_compact_localized(amount, lang_key)}</div>
        <div style="font-size:0.9rem; color:#475569;">
            {t['rank_prefix']} <span class="highlight" style="color:{color}; font-weight:700;">{rank_str}</span>
        </div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:5px;">
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
    ax.scatter([marker_x], [marker_y], color=color, s=30)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# -------------------------- 4. 主程序入口 --------------------------
def main():
    # 优先渲染导航栏（必须放在最前面）
    render_top_navbar()
    
    # 语言选择
    c_head, c_lang = st.columns([5, 1])
    with c_lang:
        lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
    text = TRANSLATIONS[lang]
    
    # 页面主标题
    with c_head:
        st.markdown(f"# {text['title']}")
        st.markdown(f"<p style='color:#64748b; margin-top:-15px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    
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
    if st.button(text['btn_calc'], type="primary", use_container_width=True):
        inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
        wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
        inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
        wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
        
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#4f46e5", lang)
        with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#0ea5e9", lang)
    
    st.markdown(f"<div style='text-align:center; color:#cbd5e1; font-size:0.8rem; margin-top:30px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

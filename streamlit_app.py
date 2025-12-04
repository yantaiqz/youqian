import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import textwrap

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="auto" 
)

# -------------------------- 1. 样式与HTML常量 (核心修复) --------------------------
# ⚠️ 关键点：这两个变量定义在函数外面，紧贴左侧，没有任何缩进。
# 这保证了 Markdown 解析器绝对不会把它们当成代码块显示。

NAV_CSS = """
<style>
    /* 隐藏 Streamlit 默认头部元素 */
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 全局背景与字体 */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 消除顶部空白，让导航栏紧贴窗口顶部 */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    /* 导航栏容器 */
    .hero-navbar {
        background-color: #1e293b; /* 深蓝灰 */
        color: white;
        padding: 1.5rem 3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-bottom: 1px solid #334155;
    }

    /* Logo 区域 */
    .nav-logo-group {
        display: flex; 
        align-items: center; 
        gap: 12px;
    }
    .nav-icon-box {
        width: 40px; 
        height: 40px; 
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); 
        border-radius: 8px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 1.4rem;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    .nav-title {
        font-size: 1.4rem; 
        font-weight: 800; 
        letter-spacing: -0.02em;
        color: white;
    }

    /* 导航链接 */
    .nav-link-group {
        display: flex; 
        gap: 32px; 
        align-items: center;
    }
    .nav-item {
        color: #94a3b8; 
        text-decoration: none; 
        font-weight: 600; 
        font-size: 0.95rem; 
        transition: all 0.2s;
        padding-bottom: 4px;
        border-bottom: 2px solid transparent;
    }
    .nav-item:hover {
        color: white;
    }
    .nav-item.active {
        color: white;
        border-bottom: 2px solid #6366f1;
    }

    /* 用户头像 */
    .nav-user-avatar {
        width: 36px; 
        height: 36px; 
        background-color: rgba(255,255,255,0.1); 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 0.85rem; 
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        font-weight: 600;
        margin-left: 10px;
    }
    
    /* 响应式：手机端隐藏部分菜单 */
    @media (max-width: 768px) {
        .nav-item:not(.active) { display: none; }
        .hero-navbar { padding: 1rem; }
    }
    
    /* 结果卡片样式 */
    .metric-card {
        background: white; 
        border: 1px solid #e2e8f0; 
        border-radius: 12px; 
        padding: 24px; 
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
"""

NAV_HTML = """
<div class="hero-navbar">
    <div class="nav-logo-group">
        <div class="nav-icon-box">💎</div>
        <div class="nav-title">
            WealthRank <span style="font-weight:300; opacity:0.6;">Pro</span>
        </div>
    </div>
    
    <div class="nav-link-group">
        <a href="#" class="nav-item active">Dashboard</a>
        <a href="#" class="nav-item">Global Map</a>
        <a href="#" class="nav-item">Calculator</a>
        <a href="#" class="nav-item">Settings</a>
        <div class="nav-user-avatar">JD</div>
    </div>
</div>
"""

# -------------------------- 2. 业务逻辑 (工具函数) --------------------------
TRANSLATIONS = {
    "English": {"title": "Global Wealth Pyramid", "subtitle": "Where do you stand in the global economy?", "location": "Your Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Analyze My Position", "card_income": "Income Level", "card_wealth": "Wealth Status", "rank_prefix": "Nationwide", "rank_approx": "Rank #", "disclaimer": "Estimations based on Log-Normal Distribution Model"},
    "中文": {"title": "全球财富金字塔", "subtitle": "你的财富在全球处于什么段位？", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "生成分析报告", "card_income": "年收入水平", "card_wealth": "资产水平", "rank_prefix": "超过所选国家", "rank_approx": "绝对排名 第", "disclaimer": "基于对数正态分布模型估算"}
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
        <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
            {t[f'card_{"income" if color=="#6366f1" else "wealth"}']}
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin-bottom: 8px;">
            {currency} {format_compact_localized(amount, lang_key)}
        </div>
        <div style="font-size: 0.95rem; color: #334155; font-weight: 500;">
            {t['rank_prefix']} <span style="color: {color}; font-weight: 700; font-size: 1.1rem;">{rank_str}</span>
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
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
    ax.scatter([marker_x], [marker_y], color=color, s=30, edgecolor='white', linewidth=1.5)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# -------------------------- 3. 主程序入口 --------------------------
def main():
    # 1. 渲染导航栏 (直接调用全局变量)
    st.markdown(NAV_CSS, unsafe_allow_html=True)
    st.markdown(NAV_HTML, unsafe_allow_html=True)
    
    # 2. 布局容器
    with st.container():
        # 居中布局
        _, main_col, _ = st.columns([1, 8, 1])
        
        with main_col:
            # 标题与语言
            h_col, l_col = st.columns([5, 1])
            with l_col:
                lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
            text = TRANSLATIONS[lang]
            
            with h_col:
                st.markdown(f"<h1 style='margin-top:0;'>{text['title']}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#64748b; font-size:1.1rem; margin-top:-10px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 输入表单
            c1, c2, c3 = st.columns(3)
            with c1:
                country_code = st.selectbox(text['location'], options=COUNTRY_DATA.keys(), format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"])
                country = COUNTRY_DATA[country_code]
            with c2:
                income = st.number_input(text['income'], value=int(country["medianIncome"]), step=1000)
            with c3:
                wealth = st.number_input(text['wealth'], value=int(country["medianWealth"]), step=5000)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # 计算按钮
            st.markdown("""
            <style>
                div.stButton > button {
                    background-color: #0f172a; 
                    color: white; 
                    border-radius: 8px; 
                    padding: 0.7rem 1rem;
                    font-weight: 600;
                    border: none;
                    width: 100%;
                    font-size: 1rem;
                }
                div.stButton > button:hover {
                    background-color: #33415

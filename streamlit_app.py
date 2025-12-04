import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import os
import textwrap # 关键库：用于清除多行字符串的缩进

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 1. CSS 样式 (折叠菜单核心) --------------------------
# 使用 textwrap.dedent 确保 CSS 不会被 Python 的缩进影响
css_code = textwrap.dedent("""
    <style>
    /* 全局字体 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #ffffff;
    }
    
    /* 隐藏 Streamlit 默认头部 */
    header {visibility: hidden;}
    
    /* ----- 侧边栏样式 ----- */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 1. 菜单容器 */
    .nav-container {
        padding: 10px;
    }

    /* 2. 原生折叠组件 <details> 样式 */
    details {
        margin-bottom: 8px;
        border-radius: 8px;
        overflow: hidden;
        background: transparent;
        transition: background 0.2s;
    }
    
    /* 3. 标题行 <summary> 样式 */
    summary {
        list-style: none; /* 隐藏默认三角 */
        padding: 10px 12px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 8px;
        transition: all 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 隐藏 Webkit 默认三角 */
    summary::-webkit-details-marker {
        display: none;
    }
    
    /* 悬停效果 */
    summary:hover {
        background-color: #e2e8f0;
        color: #0f172a;
    }
    
    /* 自定义旋转箭头 */
    summary::after {
        content: '+';
        font-size: 1.1rem;
        font-weight: 400;
        transition: transform 0.3s;
    }
    
    /* 展开时的样式 */
    details[open] summary {
        color: #4f46e5; /* Indigo */
    }
    
    details[open] summary::after {
        transform: rotate(45deg); /* 旋转成 X */
    }
    
    /* 4. 子菜单内容区域 */
    .nav-content {
        padding: 5px 0 5px 10px; /* 缩进效果 */
        border-left: 2px solid #e2e8f0;
        margin-left: 12px;
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 5. 链接按钮样式 */
    .nav-link {
        display: flex;
        align-items: center;
        text-decoration: none;
        color: #475569;
        padding: 8px 12px;
        margin-bottom: 2px;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.15s;
    }
    
    .nav-link:hover {
        background-color: #eff6ff;
        color: #4f46e5;
        transform: translateX(3px);
    }
    
    .nav-icon {
        margin-right: 10px;
        font-size: 1rem;
        width: 20px;
        text-align: center;
    }
    
    /* 用户卡片 */
    .user-profile {
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
    }
    .avatar {
        width: 32px;
        height: 32px;
        background-color: #4f46e5;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.8rem;
        margin-right: 10px;
    }
    
    /* 结果卡片美化 */
    .metric-card {
        background: white; border: 1px solid #f1f5f9; border-radius: 12px;
        padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem; font-weight: 800; color: #0f172a;
    }
    .highlight { color: #4f46e5; }
    </style>
""")
st.markdown(css_code, unsafe_allow_html=True)

# -------------------------- 2. 侧边栏渲染 (使用 HTML Details) --------------------------
def render_collapsible_sidebar():
    with st.sidebar:
        # 1. 标题
        st.markdown("""
        <div style="padding: 10px 10px 20px 10px;">
            <h2 style="margin:0; font-size:1.4rem; color:#0f172a;">
                Wealth<span style="color:#4f46e5">Rank</span>
            </h2>
            <p style="margin:0; font-size:0.8rem; color:#64748b;">Global Wealth Tracker</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. 折叠菜单 (使用 textwrap.dedent 确保不显示源码)
        # details[open] 表示默认展开，去掉 [open] 则默认折叠
        menu_html = textwrap.dedent("""
            <div class="nav-container">
            
                <details open>
                    <summary>Platform</summary>
                    <div class="nav-content">
                        <a href="#" class="nav-link">
                            <span class="nav-icon">📊</span> Dashboard
                        </a>
                        <a href="#" class="nav-link">
                            <span class="nav-icon">🌍</span> Global Map
                        </a>
                        <a href="#" class="nav-link">
                            <span class="nav-icon">📈</span> Trends
                        </a>
                    </div>
                </details>
                
                <details>
                    <summary>Tools</summary>
                    <div class="nav-content">
                        <a href="#" class="nav-link">
                            <span class="nav-icon">🧮</span> Calculator
                        </a>
                        <a href="#" class="nav-link">
                            <span class="nav-icon">📑</span> Reports
                        </a>
                        <a href="#" class="nav-link">
                            <span class="nav-icon">⚖️</span> Comparison
                        </a>
                    </div>
                </details>
                
                <details>
                    <summary>Account</summary>
                    <div class="nav-content">
                        <a href="#" class="nav-link">
                            <span class="nav-icon">💎</span> Upgrade Plan
                        </a>
                        <a href="#" class="nav-link">
                            <span class="nav-icon">⚙️</span> Settings
                        </a>
                        <a href="#" class="nav-link">
                            <span class="nav-icon">🔒</span> Privacy
                        </a>
                    </div>
                </details>

                <div class="user-profile">
                    <div class="avatar">A</div>
                    <div style="font-size:0.85rem; color:#334155; font-weight:600;">
                        Admin User
                        <div style="font-size:0.7rem; color:#94a3b8; font-weight:400;">Pro License</div>
                    </div>
                </div>
                
            </div>
        """)
        
        st.markdown(menu_html, unsafe_allow_html=True)

# -------------------------- 3. 逻辑与数据 (保持不变) --------------------------
TRANSLATIONS = {
    "English": {"title": "WealthRank Global", "subtitle": "Real-time wealth distribution estimator.", "location": "Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Calculate Position", "card_income": "Income Level", "card_wealth": "Wealth Status", "rank_prefix": "Nationwide", "rank_approx": "≈ Rank #", "disclaimer": "Based on Log-Normal Distribution Model"},
    "中文": {"title": "财富金字塔段位", "subtitle": "个人财富实时排名系统", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "查看我的排名", "card_income": "年收入水平", "card_wealth": "资产水平", "rank_prefix": "超过所选国家", "rank_approx": "≈ 绝对排名 第", "disclaimer": "基于对数正态分布模型估算"}
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
    # 渲染侧边栏
    render_collapsible_sidebar()
    
    # 语言选择
    c_head, c_lang = st.columns([5, 1])
    with c_lang:
        lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
    text = TRANSLATIONS[lang]
    
    # 标题
    with c_head:
        st.markdown(f"# {text['title']}")
        st.markdown(f"<p style='color:#64748b; margin-top:-15px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 输入
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

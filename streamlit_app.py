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
    initial_sidebar_state="collapsed" # 收起侧边栏
)

# -------------------------- 1. 样式定义 (Fintech Dark 风格) --------------------------
# 强制隐藏默认元素
st.markdown("""
<style>
    /* 隐藏 Streamlit 默认的顶部红线、汉堡菜单、Footer */
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 全局背景微调 */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 调整主内容区的顶部边距，让我们的导航栏紧贴顶部 */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 2. 渲染导航栏 (嵌入式) --------------------------
def render_static_navbar():
    # 这一块 HTML 是“嵌入”在页面流里的，不是悬浮的，所以绝对稳定
    # 使用深色背景 (#0f172a) 打造高端金融感
    navbar_html = textwrap.dedent("""
    <div style="
        background-color: #0f172a; 
        color: white; 
        padding: 1.2rem 3rem; 
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="
                width: 36px; 
                height: 36px; 
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); 
                border-radius: 8px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 1.2rem;
            ">💎</div>
            <div style="font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em;">
                WealthRank <span style="color: #94a3b8; font-weight: 400; font-size: 1rem;">PRO</span>
            </div>
        </div>
        
        <div style="display: flex; gap: 30px; align-items: center;">
            <a href="#" style="color: #fff; text-decoration: none; font-weight: 600; font-size: 0.95rem; border-bottom: 2px solid #3b82f6;">Dashboard</a>
            <a href="#" style="color: #94a3b8; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s;">Markets</a>
            <a href="#" style="color: #94a3b8; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s;">Calculator</a>
            <a href="#" style="color: #94a3b8; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s;">Profile</a>
            
            <div style="
                width: 32px; 
                height: 32px; 
                background-color: rgba(255,255,255,0.1); 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 0.8rem; 
                border: 1px solid rgba(255,255,255,0.2);
                margin-left: 10px;
            ">JD</div>
        </div>
    </div>
    """)
    st.markdown(navbar_html, unsafe_allow_html=True)

# -------------------------- 3. 业务逻辑与数据 --------------------------
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
    
    # 使用纯 HTML/CSS 渲染卡片，确保样式统一
    st.markdown(f"""
    <div style="
        background: white; 
        border: 1px solid #e2e8f0; 
        border-radius: 16px; 
        padding: 24px; 
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border-top: 4px solid {color};
    ">
        <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
            {t[f'card_{"income" if color=="#3b82f6" else "wealth"}']}
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
    
    # 极简曲线图
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

# -------------------------- 4. 主程序入口 --------------------------
def main():
    # 1. 渲染导航栏 (最先执行)
    render_static_navbar()
    
    # 2. 页面布局容器（限制宽度，让内容不至于在大屏上太散）
    with st.container():
        # 这里使用 col 布局来居中内容
        _, main_col, _ = st.columns([1, 8, 1])
        
        with main_col:
            # 标题与语言选择
            h_col, l_col = st.columns([5, 1])
            with l_col:
                lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
            text = TRANSLATIONS[lang]
            
            with h_col:
                st.markdown(f"<h1 style='margin-top:0;'>{text['title']}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#64748b; font-size:1.1rem; margin-top:-10px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 输入区域
            c1, c2, c3 = st.columns(3)
            with c1:
                country_code = st.selectbox(text['location'], options=COUNTRY_DATA.keys(), format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"])
                country = COUNTRY_DATA[country_code]
            with c2:
                income = st.number_input(text['income'], value=int(country["medianIncome"]), step=1000)
            with c3:
                wealth = st.number_input(text['wealth'], value=int(country["medianWealth"]), step=5000)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # 按钮
            st.markdown("""
            <style>
                div.stButton > button {
                    background-color: #0f172a; 
                    color: white; 
                    border-radius: 8px; 
                    padding: 0.6rem 1rem;
                    font-weight: 600;
                    border: none;
                    width: 100%;
                }
                div.stButton > button:hover {
                    background-color: #1e293b;
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
                with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#3b82f6", lang)
                with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#8b5cf6", lang)
            
            st.markdown(f"<div style='text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:40px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. CSS 样式常量 (定义在最外层，紧贴左侧，确保渲染)
# ==============================================================================

NAV_CSS = """
<style>
    /* 1. 彻底隐藏 Streamlit 默认元素 */
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 2. 全局样式重置 */
    .stApp {
        background-color: #F8FAFC; /* 极简灰白背景 */
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 3. 底部留白，防止内容被 Dock 遮挡 */
    .block-container {
        padding-bottom: 120px !important;
        padding-top: 20px !important;
        max-width: 1100px !important;
        margin: auto;
    }

    /* 4. 悬浮 Dock 容器 (核心设计) */
    .dock-container {
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999999;
        
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        
        background: rgba(255, 255, 255, 0.85); /* 半透明白 */
        backdrop-filter: blur(16px);          /* 毛玻璃 */
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 24px;
        box-shadow: 
            0 20px 25px -5px rgba(0, 0, 0, 0.05), 
            0 8px 10px -6px rgba(0, 0, 0, 0.01),
            0 0 0 1px rgba(0,0,0,0.02); /* 细腻描边 */
            
        /* 响应式：确保小屏幕可以横向滑动 */
        max-width: 95vw;
        overflow-x: auto;
        scrollbar-width: none; /* 隐藏滚动条 (Firefox) */
    }
    .dock-container::-webkit-scrollbar { display: none; } /* 隐藏滚动条 (Chrome) */

    /* 5. 导航项 (链接) */
    .dock-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        color: #64748B; /* 默认灰 */
        padding: 8px 12px;
        border-radius: 12px;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        min-width: 65px; /* 保证点击区域 */
    }

    /* 悬停效果 */
    .dock-item:hover {
        background-color: rgba(255, 255, 255, 0.8);
        transform: translateY(-5px); /* 上浮 */
        color: #4F46E5; /* 悬停蓝 */
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 激活状态 */
    .dock-item.active {
        background-color: #EEF2FF;
        color: #4F46E5;
        font-weight: 600;
    }

    /* 图标样式 */
    .dock-icon {
        font-size: 1.3rem;
        margin-bottom: 4px;
        filter: grayscale(100%);
        transition: filter 0.2s;
    }
    .dock-item:hover .dock-icon, 
    .dock-item.active .dock-icon {
        filter: grayscale(0%);
    }

    /* 文字样式 */
    .dock-text {
        font-size: 0.7rem;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }
    
    /* 分割线 */
    .dock-divider {
        width: 1px;
        height: 24px;
        background-color: #E2E8F0;
        margin: 0 4px;
        flex-shrink: 0;
    }

    /* 6. 组件优化 */
    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 16px;
        padding: 24px; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div.stButton > button {
        background: #1e293b; color: white; border-radius: 10px; border: none; height: 48px;
    }
</style>
"""

# HTML 常量：8个导航点 + 超链接
# href="#" 是占位符，你可以替换为真实的 URL (例如 "?page=dashboard")
NAV_HTML = """
<div class="dock-container">
    <a href="?page=home" class="dock-item active" target="_self">
        <div class="dock-icon">🏠</div>
        <div class="dock-text">Home</div>
    </a>
    
    <a href="?page=map" class="dock-item" target="_self">
        <div class="dock-icon">🌍</div>
        <div class="dock-text">Map</div>
    </a>
    
    <a href="?page=calc" class="dock-item" target="_self">
        <div class="dock-icon">🧮</div>
        <div class="dock-text">Calc</div>
    </a>
    
    <a href="?page=trends" class="dock-item" target="_self">
        <div class="dock-icon">📈</div>
        <div class="dock-text">Trends</div>
    </a>

    <div class="dock-divider"></div>

    <a href="?page=compare" class="dock-item" target="_self">
        <div class="dock-icon">⚖️</div>
        <div class="dock-text">Compare</div>
    </a>

    <a href="?page=reports" class="dock-item" target="_self">
        <div class="dock-icon">📑</div>
        <div class="dock-text">Reports</div>
    </a>
    
    <a href="?page=settings" class="dock-item" target="_self">
        <div class="dock-icon">⚙️</div>
        <div class="dock-text">Settings</div>
    </a>
    
    <a href="?page=profile" class="dock-item" target="_self">
        <div class="dock-icon">👤</div>
        <div class="dock-text">Profile</div>
    </a>
</div>
"""

# ==============================================================================
# 2. 业务逻辑与数据
# ==============================================================================
TRANSLATIONS = {
    "English": {"title": "WealthRank Pro", "subtitle": "Global Wealth Distribution Assessment", "location": "Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Analyze Now", "card_income": "Income Tier", "card_wealth": "Wealth Tier", "rank_prefix": "Top", "rank_approx": "Est. Rank #", "disclaimer": "Estimations based on Log-Normal Distribution Model."},
    "中文": {"title": "全球财富段位", "subtitle": "个人财富全球分布评估系统", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "立即评估", "card_income": "年收入段位", "card_wealth": "资产段位", "rank_prefix": "前", "rank_approx": "预估排名 第", "disclaimer": "基于对数正态分布模型估算，仅供参考。"}
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

def render_metric_card(t, amount, currency, percentile, rank, color_hex, lang_key):
    top_percent = (1 - percentile) * 100
    rank_str = f"{top_percent:.1f}%"
    
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid {color_hex};">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
             <div style="font-size:0.8rem; font-weight:600; color:#64748B; text-transform:uppercase;">
                {t[f'card_{"income" if color_hex=="#4f46e5" else "wealth"}']}
            </div>
        </div>
        
        <div style="font-size:2.2rem; font-weight:800; color:#1E293B; margin-bottom:5px;">
            {currency}{format_compact_localized(amount, lang_key)}
        </div>
        
        <div style="font-size:0.9rem; color:#475569; padding:4px 0; border-radius:6px; display:inline-block;">
             {t['rank_prefix']} <span style="color:{color_hex}; font-weight:700;">{rank_str}</span>
        </div>
        
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:8px;">
            {t['rank_approx']} <b>{format_compact_localized(rank, lang_key)}</b>
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
    
    fig, ax = plt.subplots(figsize=(5, 0.8))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.fill_between(chart_x, chart_y, color=color_hex, alpha=0.1)
    ax.plot(chart_x, chart_y, color=color_hex, linewidth=1.5)
    ax.scatter([marker_x], [marker_y], color=color_hex, s=40, edgecolor='white', linewidth=1.5)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ==============================================================================
# 3. 主程序入口
# ==============================================================================
def main():
    # 1. 注入 CSS (确保能渲染)
    st.markdown(NAV_CSS, unsafe_allow_html=True)
    
    # 2. 注入 HTML (8个导航点)
    st.markdown(NAV_HTML, unsafe_allow_html=True)
    
    # 3. 页面主体内容
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 使用 columns 来居中内容
    _, c_main, _ = st.columns([1, 6, 1])
    
    with c_main:
        # Header
        h1, h2 = st.columns([4, 1])
        with h2:
            lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
        text = TRANSLATIONS[lang]
        
        with h1:
            st.markdown(f"<h1 style='color:#1E293B; margin-bottom:0;'>{text['title']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#64748B; font-size:1.1rem;'>{text['subtitle']}</p>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Inputs
        c1, c2, c3 = st.columns(3)
        with c1:
            country_code = st.selectbox(text['location'], options=COUNTRY_DATA.keys(), format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"])
            country = COUNTRY_DATA[country_code]
        with c2:
            income = st.number_input(text['income'], value=int(country["medianIncome"]), step=1000)
        with c3:
            wealth = st.number_input(text['wealth'], value=int(country["medianWealth"]), step=5000)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculate Button
        if st.button(text['btn_calc']):
            inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
            wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
            inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
            wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
            
            st.markdown("<br>", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#4f46e5", lang)
            with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#0ea5e9", lang)

        st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:40px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

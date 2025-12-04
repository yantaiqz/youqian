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
# 1. 样式与结构常量 (定义在最外层，无缩进，确保渲染)
# ==============================================================================

DOCK_CSS = """
<style>
    /* 1. 全局重置 */
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .stApp {
        background-color: #f3f4f6; /* 浅灰背景 */
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 2. 底部留白，防止内容被 Dock 遮挡 */
    .block-container {
        padding-bottom: 120px !important;
        max-width: 1000px !important;
        margin: auto;
    }

    /* 3. 悬浮 Dock 容器 */
    .dock-container {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: rgba(17, 24, 39, 0.85); /* 深色半透明背景 */
        backdrop-filter: blur(12px);       /* 毛玻璃特效 */
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        z-index: 999999;
    }

    /* 4. Dock 项目 */
    .dock-item {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        border-radius: 16px;
        color: #9ca3af;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* 弹性动画 */
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* 悬停动画：放大并上浮 */
    .dock-item:hover {
        transform: translateY(-8px) scale(1.15);
        background-color: #4f46e5; /* 激活色 Indigo */
        color: white;
        box-shadow: 0 5px 15px rgba(79, 70, 229, 0.4);
        z-index: 10;
    }
    
    /* 激活状态 */
    .dock-item.active {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* 图标与文字 */
    .dock-icon {
        font-size: 1.4rem;
        line-height: 1;
    }
    .dock-label {
        position: absolute;
        top: -35px;
        background: #1f2937;
        color: white;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 6px;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s;
        white-space: nowrap;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    /* 悬停显示标签 */
    .dock-item:hover .dock-label {
        opacity: 1;
        transform: translateY(-5px);
    }
    
    /* 分割线 */
    .dock-divider {
        width: 1px;
        height: 24px;
        background-color: rgba(255, 255, 255, 0.15);
        margin: 0 4px;
    }
    
    /* 结果卡片 */
    .metric-card {
        background: white; border: none; border-radius: 20px;
        padding: 24px; text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
</style>
"""

DOCK_HTML = """
<div class="dock-container">
    <a href="#" class="dock-item active">
        <span class="dock-icon">🏠</span>
        <span class="dock-label">Home</span>
    </a>
    
    <a href="#" class="dock-item">
        <span class="dock-icon">🌍</span>
        <span class="dock-label">Global Map</span>
    </a>
    
    <a href="#" class="dock-item">
        <span class="dock-icon">📊</span>
        <span class="dock-label">Analytics</span>
    </a>
    
    <div class="dock-divider"></div>
    
    <a href="#" class="dock-item">
        <span class="dock-icon">⚙️</span>
        <span class="dock-label">Settings</span>
    </a>
    
    <a href="#" class="dock-item">
        <div style="width:24px; height:24px; border-radius:50%; background:#8b5cf6; color:white; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:bold;">JD</div>
        <span class="dock-label">Profile</span>
    </a>
</div>
"""

# ==============================================================================
# 2. 业务逻辑 (保持一致)
# ==============================================================================
TRANSLATIONS = {
    "English": {"title": "WealthRank Pro", "subtitle": "Discover your standing in the global economy.", "location": "Your Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Calculate Ranking", "card_income": "Income Percentile", "card_wealth": "Wealth Percentile", "rank_prefix": "Top", "rank_approx": "Global Rank #", "disclaimer": "Estimations based on Log-Normal Distribution Model."},
    "中文": {"title": "全球财富罗盘", "subtitle": "探索你的财富在全球经济中的坐标。", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "开始计算", "card_income": "年收入段位", "card_wealth": "资产段位", "rank_prefix": "前", "rank_approx": "全球排名 第", "disclaimer": "基于对数正态分布模型估算。"}
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
    <div class="metric-card">
        <div style="font-size:0.8rem; font-weight:600; color:#9ca3af; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">
            {t[f'card_{"income" if color_hex=="#4f46e5" else "wealth"}']}
        </div>
        <div style="font-size:2.5rem; font-weight:800; color:#111827; line-height:1;">
            {currency}{format_compact_localized(amount, lang_key)}
        </div>
        <div style="margin-top:15px; display:inline-block; padding:4px 12px; background-color:{color_hex}15; border-radius:99px;">
             <span style="color:{color_hex}; font-weight:700; font-size:1rem;">{t['rank_prefix']} {rank_str}</span>
        </div>
        <div style="font-size:0.8rem; color:#6b7280; margin-top:10px;">
            {t['rank_approx']} <b>{format_compact_localized(rank, lang_key)}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 极简 Sparkline
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
    ax.scatter([marker_x], [marker_y], color=color_hex, s=30, edgecolor="white", linewidth=1.5)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ==============================================================================
# 3. 主程序入口
# ==============================================================================
def main():
    # 1. 注入 CSS 和 HTML (Dock 导航)
    st.markdown(DOCK_CSS, unsafe_allow_html=True)
    st.markdown(DOCK_HTML, unsafe_allow_html=True)
    
    # 2. 页面主要内容
    st.markdown("<br>", unsafe_allow_html=True) # 顶部留一点空
    
    # 标题区
    col_1, col_2, col_3 = st.columns([1, 6, 1])
    with col_2:
        # 语言切换
        c_head, c_lang = st.columns([4, 1])
        with c_lang:
            lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
        text = TRANSLATIONS[lang]
        
        with c_head:
            st.markdown(f"<h1 style='font-size:2.8rem; color:#111827; letter-spacing:-0.03em;'>{text['title']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#6b7280; font-size:1.2rem; margin-top:-15px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 输入区
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
                width: 100%; border-radius: 12px; height: 50px; font-size: 1rem; font-weight: 600;
                background-color: #111827; color: white; border: none;
                transition: transform 0.1s;
            }
            div.stButton > button:hover {
                background-color: #374151; transform: scale(1.01);
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
            with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#4f46e5", lang)
            with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#0891b2", lang)

        st.markdown(f"<div style='text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:50px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

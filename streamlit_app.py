import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. 样式与HTML常量 (定义在最外层，紧贴左侧，无缩进 -> 确保渲染)
# ==============================================================================

DECK_CSS = """
<style>
    /* 1. 全局重置 */
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .stApp {
        background-color: #F2F4F7; /* 极简灰背景 */
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 2. 底部留白，防止内容被导航栏遮挡 */
    .block-container {
        padding-bottom: 140px !important;
        padding-top: 40px !important;
        max-width: 1000px !important;
        margin: auto;
    }

    /* 3. 底部悬浮卡片容器 (Control Deck) */
    .nav-deck-container {
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999999;
        
        /* 卡片核心样式 */
        background-color: #FFFFFF;
        padding: 8px 12px;
        border-radius: 20px;
        border: 1px solid #EAECF0;
        box-shadow: 0 20px 40px -4px rgba(16, 24, 40, 0.08), 0 8px 16px -4px rgba(16, 24, 40, 0.04);
        
        display: flex;
        align-items: center;
        gap: 8px;
        width: auto;
        min-width: 320px;
        justify-content: space-between;
    }

    /* 4. 导航项 */
    .deck-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 12px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        min-width: 64px;
        position: relative;
    }

    /* 图标 */
    .deck-icon {
        font-size: 1.5rem;
        margin-bottom: 2px;
        transition: transform 0.2s;
        filter: grayscale(100%) opacity(0.6); /* 默认灰色 */
    }

    /* 标签文字 */
    .deck-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #98A2B3;
        transition: color 0.2s;
    }

    /* 悬停状态 */
    .deck-item:hover {
        background-color: #F9FAFB;
    }
    .deck-item:hover .deck-icon {
        filter: grayscale(0%) opacity(1);
        transform: translateY(-2px);
    }
    .deck-item:hover .deck-label {
        color: #475467;
    }

    /* 激活状态 (Active) - 强调色块 */
    .deck-item.active {
        background-color: #EFF8FF; /* 浅蓝背景 */
    }
    .deck-item.active .deck-icon {
        filter: grayscale(0%) opacity(1);
    }
    .deck-item.active .deck-label {
        color: #2E90FA; /* 品牌蓝 */
    }
    
    /* 中间的大按钮 (强调) */
    .deck-action-btn {
        background: linear-gradient(135deg, #2E90FA 0%, #1570EF 100%);
        width: 56px;
        height: 56px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(46, 144, 250, 0.3);
        margin: 0 12px;
        cursor: pointer;
        transition: transform 0.2s;
        color: white !important;
        text-decoration: none;
    }
    .deck-action-btn:hover {
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 8px 16px rgba(46, 144, 250, 0.4);
    }
    .deck-action-icon {
        font-size: 1.8rem;
        color: white;
    }
    
    /* 响应式调整 */
    @media (max-width: 600px) {
        .nav-deck-container {
            width: 90%;
            bottom: 16px;
            padding: 8px;
        }
        .deck-item { min-width: auto; flex: 1; }
    }
    
    /* 结果卡片 */
    .metric-card {
        background: white; border: 1px solid #EAECF0; border-radius: 16px;
        padding: 24px; text-align: center;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
    }
</style>
"""

DECK_HTML = """
<div class="nav-deck-container">
    <a href="#" class="deck-item">
        <div class="deck-icon">🏠</div>
        <div class="deck-label">Home</div>
    </a>
    
    <a href="#" class="deck-item">
        <div class="deck-icon">🌎</div>
        <div class="deck-label">Map</div>
    </a>
    
    <a href="#" class="deck-action-btn">
        <div class="deck-action-icon">✨</div>
    </a>
    
    <a href="#" class="deck-item active">
        <div class="deck-icon">📊</div>
        <div class="deck-label">Stats</div>
    </a>
    
    <a href="#" class="deck-item">
        <div class="deck-icon">👤</div>
        <div class="deck-label">Profile</div>
    </a>
</div>
"""

# ==============================================================================
# 2. 业务逻辑
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
    <div class="metric-card" style="border-bottom: 4px solid {color_hex};">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
             <div style="font-size:0.8rem; font-weight:600; color:#98A2B3; text-transform:uppercase;">
                {t[f'card_{"income" if color_hex=="#2E90FA" else "wealth"}']}
            </div>
            <div style="width:10px; height:10px; background:{color_hex}; border-radius:50%;"></div>
        </div>
        
        <div style="font-size:2.2rem; font-weight:800; color:#101828; margin-bottom:5px;">
            {currency}{format_compact_localized(amount, lang_key)}
        </div>
        
        <div style="font-size:0.9rem; color:#475467; background:#F2F4F7; padding:4px 8px; border-radius:6px; display:inline-block;">
             {t['rank_prefix']} <span style="color:{color_hex}; font-weight:700;">{rank_str}</span>
        </div>
        
        <div style="font-size:0.8rem; color:#98A2B3; margin-top:12px;">
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
    # 1. 注入 CSS 和 HTML (Control Deck)
    st.markdown(DECK_CSS, unsafe_allow_html=True)
    st.markdown(DECK_HTML, unsafe_allow_html=True)
    
    # 2. 页面布局
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 使用 columns 来居中内容，限制宽度
    _, c_main, _ = st.columns([1, 6, 1])
    
    with c_main:
        # Header
        h1, h2 = st.columns([4, 1])
        with h2:
            lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
        text = TRANSLATIONS[lang]
        
        with h1:
            st.markdown(f"<h1 style='color:#101828; margin-bottom:0;'>{text['title']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#667085; font-size:1.1rem;'>{text['subtitle']}</p>", unsafe_allow_html=True)

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
        st.markdown("""
        <style>
        div.stButton > button {
            width: 100%; border-radius: 12px; height: 50px; font-size: 1rem; font-weight: 600;
            background-color: #2E90FA; color: white; border: none;
            box-shadow: 0 4px 6px rgba(46, 144, 250, 0.2);
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background-color: #1570EF; transform: translateY(-1px);
            box-shadow: 0 6px 12px rgba(46, 144, 250, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button(text['btn_calc']):
            inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
            wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
            inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
            wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
            
            st.markdown("<br>", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#2E90FA", lang)
            with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#F63D68", lang) # 使用粉红色对比

        st.markdown(f"<div style='text-align:center; color:#98A2B3; font-size:0.8rem; margin-top:40px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

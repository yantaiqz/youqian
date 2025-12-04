import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. 样式与结构常量 (核心：定义在最外层，紧贴左侧，确保100%渲染)
# ==============================================================================

# --- Notion 风格 CSS ---
NOTION_CSS = """
<style>
    /* 1. 全局重置与隐藏默认元素 */
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 应用背景设为纯白 */
    .stApp {
        background-color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #37352F; /* Notion 经典深灰字体色 */
    }
    
    /* 移除顶部 padding，让导航栏贴顶 */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1100px !important; /* 限制最大宽度，更像文档 */
        margin: auto;
    }

    /* 2. Notion 风格导航栏容器 */
    .notion-nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #E0E0E0; /* 极细的底边框 */
        margin-bottom: 30px;
        font-size: 14px;
    }

    /* 左侧 Logo 区 */
    .nav-left {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        transition: background 0.2s;
    }
    .nav-left:hover {
        background-color: #F0F0F0; /* Notion 经典悬停灰 */
    }
    .nav-logo-icon {
        font-size: 1.2rem;
    }
    /* 使用 Serif 字体增加专业感 */
    .nav-logo-text {
        font-family: "Lyon-Text", Georgia, ui-serif, serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: #37352F;
    }
    
    /* 右侧链接区 */
    .nav-right {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .nav-item {
        text-decoration: none;
        color: #6B6B6B;
        padding: 6px 10px;
        border-radius: 4px;
        transition: all 0.2s;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .nav-item:hover {
        background-color: #F0F0F0;
        color: #37352F;
    }
    .nav-item.active {
        background-color: #F0F0F0;
        color: #37352F;
        font-weight: 600;
    }
    
    /* 分割线 */
    .nav-divider {
        height: 16px;
        width: 1px;
        background-color: #E0E0E0;
        margin: 0 8px;
    }

    /* 3. 组件样式优化 */
    /* 优化输入框样式，使其更扁平 */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #F7F6F3 !important; /* Notion 浅灰背景 */
        border: 1px solid #E0E0E0 !important;
        box-shadow: none !important;
    }
    
    /* 优化按钮为黑色极简风格 */
    div.stButton > button {
        background-color: #37352F !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
    }
    div.stButton > button:hover {
        background-color: #5A5A5A !important;
    }

    /* 结果卡片：极简白底加轻微阴影 */
    .metric-card {
        background: white; 
        border: 1px solid #E0E0E0; 
        border-radius: 8px; 
        padding: 20px; 
        text-align: left; /*改为左对齐，更像文档*/
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .metric-card:hover {
         box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
</style>
"""

# --- Notion 风格 HTML ---
NOTION_HTML = """
<nav class="notion-nav-container">
    <div class="nav-left">
        <span class="nav-logo-icon">💰</span>
        <span class="nav-logo-text">WealthRank</span>
    </div>
    
    <div class="nav-right">
        <a href="#" class="nav-item active">
            <span>📊</span> Dashboard
        </a>
        <a href="#" class="nav-item">
            <span>🌍</span> Map
        </a>
        <a href="#" class="nav-item">
            <span>📉</span> Analysis
        </a>
        <div class="nav-divider"></div>
        <a href="#" class="nav-item" style="padding: 4px 8px;">
             <div style="width:24px; height:24px; background:#E16B16; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem;">JD</div>
            <span>Profile</span>
        </a>
    </div>
</nav>
"""

# ==============================================================================
# 2. 业务逻辑 (保持不变)
# ==============================================================================
TRANSLATIONS = {
    "English": {"title": "Global Wealth Assessment", "subtitle": "Where do you stand in the global economy?", "location": "Your Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Analyze Position", "card_income": "Income Percentile", "card_wealth": "Wealth Percentile", "rank_prefix": "Nationwide", "rank_approx": "Approx. Rank", "disclaimer": "Estimations based on Log-Normal Distribution Model."},
    "中文": {"title": "全球财富段位评估", "subtitle": "你的财富在全球处于什么位置？", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "开始分析", "card_income": "年收入段位", "card_wealth": "资产段位", "rank_prefix": "超过所选国家", "rank_approx": "预估排名", "disclaimer": "基于对数正态分布模型估算，仅供参考。"}
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
    rank_str = f"Top {top_percent:.1f}%" if lang_key != "中文" else f"前 {top_percent:.1f}%"
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex; align-items:center; gap:6px; margin-bottom: 8px;">
            <div style="width:8px; height:8px; border-radius:50%; background-color:{color_hex};"></div>
            <div style="color: #787774; font-size: 0.85rem; font-weight: 500;">
                {t[f'card_{"income" if color_hex=="#3B82F6" else "wealth"}']}
            </div>
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #37352F; margin-bottom: 4px; font-family:'Lyon-Text', serif;">
            {currency} {format_compact_localized(amount, lang_key)}
        </div>
        <div style="font-size: 1rem; color: #37352F; font-weight: 500;">
            <span style="color: {color_hex}; font-weight: 700;">{rank_str}</span> {t['rank_prefix']}
        </div>
        <div style="font-size: 0.85rem; color: #9B9A97; margin-top: 4px;">
            {t['rank_approx']}: {format_compact_localized(rank, lang_key)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 极简曲线图 (颜色调淡一点以适应风格)
    x = np.linspace(-3, 3, 50)
    y = np.exp(-0.5 * x**2)
    chart_x = (x + 3) / 6
    chart_y = y / y.max()
    simulated_z = (percentile - 0.5) * 6
    marker_x = percentile
    marker_y = np.exp(-0.5 * simulated_z**2)
    
    fig, ax = plt.subplots(figsize=(5, 0.8)) # 更扁平
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    # 使用传入的十六进制颜色，并设置透明度
    ax.fill_between(chart_x, chart_y, color=color_hex, alpha=0.1)
    ax.plot(chart_x, chart_y, color=color_hex, linewidth=1.5, alpha=0.8)
    ax.scatter([marker_x], [marker_y], color=color_hex, s=25)
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ==============================================================================
# 3. 主程序入口
# ==============================================================================
def main():
    # 1. 渲染导航栏 (直接调用最外层的常量，绝对安全)
    st.markdown(NOTION_CSS, unsafe_allow_html=True)
    st.markdown(NOTION_HTML, unsafe_allow_html=True)
    
    # 2. 页面内容容器
    # 使用 columns 来做简单的左中右布局，让内容居中显示
    c_left, c_main, c_right = st.columns([1, 6, 1])

    with c_main:
        # 标题栏
        h_col, l_col = st.columns([4, 1])
        with l_col:
            lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
        text = TRANSLATIONS[lang]
        
        with h_col:
            # 使用 Serif 字体做标题
            st.markdown(f"<h1 style='margin-top:0; font-family:\"Lyon-Text\", serif; font-weight:700; font-size:2.5rem;'>{text['title']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#787774; font-size:1.1rem; margin-top:-15px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 2em 0; border-color:#E0E0E0;'>", unsafe_allow_html=True)
        
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
        
        # 计算按钮 (样式已在 CSS 中全局优化)
        if st.button(text['btn_calc'], use_container_width=True):
            inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
            wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
            inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
            wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
            
            st.markdown("<br>", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            # 使用稍浅一点的蓝色和橙色，符合 Notion 风格
            with r1: render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#3B82F6", lang)
            with r2: render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#E16B16", lang)
        
        st.markdown(f"<div style='text-align:center; color:#9B9A97; font-size:0.8rem; margin-top:60px; border-top:1px solid #E0E0E0; padding-top:20px;'>{text['disclaimer']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

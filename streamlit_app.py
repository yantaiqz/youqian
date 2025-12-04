import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 0. 全局配置 (必须置顶) --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"  # 隐藏原生侧边栏
)

# -------------------------- 1. 核心样式 (优化版底部导航) --------------------------
st.markdown("""
<style>
    /* 1. 彻底隐藏Streamlit默认干扰元素 */
    header, [data-testid="stSidebar"], footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 2. 全局样式重置 */
    .stApp {
        background-color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        padding-bottom: 75px !important; /* 适配新导航高度 */
        margin: 0 !important;
    }
    
    /* 3. 底部导航核心样式 - 简洁现代风 */
    .bottom-nav {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 70px !important;
        background-color: #ffffff !important;
        border-top: 1px solid #eef2f7 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 2rem !important;
        box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.03) !important;
        z-index: 9999 !important;
        box-sizing: border-box !important;
    }
    
    /* 4. 导航项样式 - 8个均分 */
    .nav-item {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 3px !important;
        width: 12.5% !important; /* 8个均分 100/8=12.5% */
        height: 100% !important;
        color: #818b98 !important;
        text-decoration: none !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        position: relative !important;
    }
    
    /* 激活态样式 - 极简高亮 */
    .nav-item.active {
        color: #3b82f6 !important; /* 现代蓝主色 */
    }
    
    /* 激活态指示器 - 小圆点替代下划线，更简洁 */
    .nav-item.active::before {
        content: '' !important;
        position: absolute !important;
        top: 8px !important;
        width: 4px !important;
        height: 4px !important;
        border-radius: 50% !important;
        background-color: #3b82f6 !important;
    }
    
    /* 图标样式优化 */
    .nav-icon {
        font-size: 1.1rem !important;
        margin-bottom: 1px !important;
    }
    
    /* hover效果 - 轻微变色 */
    .nav-item:hover {
        color: #5294ff !important;
    }
    
    /* 6. 主内容区样式 */
    .main-content {
        padding: 2rem 2rem 1rem 2rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }
    
    /* 7. 按钮/卡片样式优化 - 同步现代风格 */
    div.stButton > button {
        background-color: #3b82f6 !important; 
        color: white !important; 
        border-radius: 6px !important; 
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        border: none !important;
        width: 100% !important;
        transition: background 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(59, 130, 246, 0.1) !important;
    }
    div.stButton > button:hover {
        background-color: #2563eb !important;
    }
    
    .metric-card {
        background: white !important; 
        border: 1px solid #eef2f7 !important; 
        border-radius: 8px !important; 
        padding: 20px !important; 
        text-align: center !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02) !important;
        box-sizing: border-box !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 2. 渲染8个导航点的底部导航 (带超链接) --------------------------
def render_bottom_nav():
    # 8个导航项，每个带独立超链接，激活态为Dashboard
    nav_html = """
    <div class="bottom-nav">
        <!-- 1. Dashboard - 激活态 -->
        <a href="/dashboard" class="nav-item active" target="_self">
            <span class="nav-icon">📊</span>
            <span>Dashboard</span>
        </a>
        <!-- 2. Global Map -->
        <a href="/global-map" class="nav-item" target="_self">
            <span class="nav-icon">🌍</span>
            <span>Map</span>
        </a>
        <!-- 3. Calculator -->
        <a href="/calculator" class="nav-item" target="_self">
            <span class="nav-icon">🧮</span>
            <span>Calc</span>
        </a>
        <!-- 4. Portfolio -->
        <a href="/portfolio" class="nav-item" target="_self">
            <span class="nav-icon">📈</span>
            <span>Portfolio</span>
        </a>
        <!-- 5. Reports -->
        <a href="/reports" class="nav-item" target="_self">
            <span class="nav-icon">📑</span>
            <span>Reports</span>
        </a>
        <!-- 6. Alerts -->
        <a href="/alerts" class="nav-item" target="_self">
            <span class="nav-icon">🔔</span>
            <span>Alerts</span>
        </a>
        <!-- 7. Settings -->
        <a href="/settings" class="nav-item" target="_self">
            <span class="nav-icon">⚙️</span>
            <span>Settings</span>
        </a>
        <!-- 8. Profile -->
        <a href="/profile" class="nav-item" target="_self">
            <span class="nav-icon">👤</span>
            <span>Profile</span>
        </a>
    </div>
    """
    # 强制渲染，确保HTML解析
    st.markdown(nav_html, unsafe_allow_html=True)

# -------------------------- 3. 业务逻辑 (保持稳定) --------------------------
TRANSLATIONS = {
    "English": {"title": "Global Wealth Pyramid", "subtitle": "Where do you stand in the global economy?", "location": "Your Location", "income": "Annual Income", "wealth": "Net Worth", "btn_calc": "Analyze My Position", "card_income": "Income Level", "card_wealth": "Wealth Status", "rank_prefix": "Nationwide", "rank_approx": "Rank #", "disclaimer": "Estimations based on Log-Normal Distribution Model"},
    "中文": {"title": "全球财富金字塔", "subtitle": "你的财富在全球处于什么段位？", "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", "btn_calc": "生成分析报告", "card_income": "年收入水平", "card_wealth": "资产水平", "rank_prefix": "超过所选国家", "rank_approx": "绝对排名 第", "disclaimer": "基于对数正态分布模型估算"}
}

COUNTRY_DATA = {
    "CN": {"name_en": "China", "name_zh": "中国", "currency": "¥", "population": 1411750000, "medianIncome": 35000, "medianWealth": 120000, "incomeGini": 0.7, "wealthGini": 1.1},
    "US": {"name_en": "USA", "name_zh": "美国", "currency": "$", "population": 331900000, "medianIncome": 45000, "medianWealth": 190000, "incomeGini": 0.8, "wealthGini": 1.5},
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
    
    card_html = f"""
    <div class="metric-card" style="border-top: 2px solid {color} !important;">
        <div style="color: #818b98; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 8px;">
            {t[f'card_{"income" if color=="#3b82f6" else "wealth"}']}
        </div>
        <div style="font-size: 1.8rem; font-weight: 600; color: #1e293b; margin-bottom: 8px;">
            {currency} {format_compact_localized(amount, lang_key)}
        </div>
        <div style="font-size: 0.85rem; color: #475569; font-weight: 400;">
            {t['rank_prefix']} <span style="color: {color}; font-weight: 600; font-size: 0.95rem;">{rank_str}</span>
        </div>
        <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 4px;">
            {t['rank_approx']} {format_compact_localized(rank, lang_key)}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # 简化绘图逻辑
    try:
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
        ax.plot(chart_x, chart_y, color=color, linewidth=1)
        ax.scatter([marker_x], [marker_y], color=color, s=20, edgecolor='white', linewidth=0.8)
        ax.axis('off')
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except:
        pass

# -------------------------- 4. 主程序入口 --------------------------
def main():
    # 1. 主内容区域
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # 语言选择
    h_col, l_col = st.columns([5, 1])
    with l_col:
        lang = st.selectbox("Language", ["English", "中文"], label_visibility="collapsed")
    text = TRANSLATIONS[lang]
    
    # 标题
    with h_col:
        st.markdown(f"<h1 style='margin-top:0; font-size: 1.8rem; font-weight: 600; color: #1e293b;'>{text['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#64748b; font-size:0.95rem; margin-top:-8px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 输入区域
    c1, c2, c3 = st.columns(3)
    with c1:
        country_code = st.selectbox(
            text['location'], 
            options=COUNTRY_DATA.keys(), 
            format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"]
        )
        country = COUNTRY_DATA[country_code]
    with c2:
        income = st.number_input(text['income'], value=int(country["medianIncome"]), step=1000)
    with c3:
        wealth = st.number_input(text['wealth'], value=int(country["medianWealth"]), step=5000)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 计算按钮
    if st.button(text['btn_calc'], type="primary"):
        inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
        wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
        inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
        wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
        
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: 
            render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#3b82f6", lang)
        with r2: 
            render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#6366f1", lang)
    
    # 免责声明
    st.markdown(f"""
    <div style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:40px;'>
        {text['disclaimer']}
    </div>
    """, unsafe_allow_html=True)
    
    # 闭合主内容容器
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. 渲染底部导航（最后执行，确保在底部）
    render_bottom_nav()

# -------------------------- 5. 执行主程序 --------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"运行错误: {str(e)}")
        # 即使报错也渲染导航
        render_bottom_nav()

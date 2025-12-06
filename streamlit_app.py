import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt # 尽管不再用于排名图，但保留以防将来使用
import json
import datetime
import os 

# -------------------------- 0. 全局配置 (必须置顶) --------------------------
st.set_page_config(
    page_title="WealthRank 财富排行榜",
    page_icon="💎",
    layout="wide",  
    initial_sidebar_state="collapsed"
)

# -------------------------- 1. 核心样式 CSS 注入 --------------------------

st.markdown("""
<style>
    /* 1. 彻底隐藏Streamlit默认干扰元素 */
    header, [data-testid="stSidebar"], footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 2. 全局样式重置 - 关键：给最外层加基础留白 */
    .stApp {
        background-color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        padding-bottom: 80px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 !important;
    }

    /* --------------------------------------------------- */
    /* 核心：主内容容器 - 强制居中 + 限制宽度 + 留白 */
    /* --------------------------------------------------- */
    .main-content {
        max-width: 900px !important; 
        margin: 0 auto !important;    
        padding: 2rem 1.5rem 1rem 1.5rem !important; 
        box-sizing: border-box !important; 
        width: 100% !important; 
    }

    /* 标题样式 */
    .page-title {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.5rem !important;
    }
    .page-subtitle {
        color: #64748b !important;
        font-size: 1rem !important;
        margin-bottom: 2rem !important;
        font-weight: 400 !important;
    }

    /* 修复卡片样式 - 适配居中容器 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02) !important;
        border: 1px solid #f1f5f9 !important;
        width: 100% !important; 
        box-sizing: border-box !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0 !important;
    }
    
    /* 结果指标卡片 - 适配居中布局 */
    .metric-card {
        background: white !important; 
        border: 1px solid #eef2f7 !important; 
        border-radius: 16px !important; 
        padding: 16px !important; 
        text-align: center !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.03), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        box-sizing: border-box !important;
        width: 100% !important; 
        transition: transform 0.2s ease !important;
        height: auto !important; 
    }
    .metric-card:hover {
        transform: translateY(-2px) !important;
    }

    /* 按钮样式 - 适配居中容器 */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important; 
        border-radius: 10px !important; 
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s !important;
        box-sizing: border-box !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* 输入框样式 - 适配居中布局 */
    .stSelectbox, .stNumberInput {
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .stSelectbox label, .stNumberInput label {
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    /* 修复列布局溢出问题 */
    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        box-sizing: border-box !important;
        gap: 1rem !important; /* 列之间的间距 */
    }
    
    /* --------------------------------------------------- */
    /* 新增：人群矩阵样式 */
    /* --------------------------------------------------- */
    .dot-matrix-container {
        display: grid; 
        grid-template-columns: repeat(10, 1fr); 
        gap: 4px; 
        width: 100%; 
        max-width: 150px; 
        margin: 0 auto 15px auto; /* 居中显示 */
    }
    .dot {
        width: 10px; 
        height: 10px; 
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------- 2. 安全的计数器逻辑 --------------------------
COUNTER_FILE = "visit_stats.json"

def update_daily_visits():
    """安全更新访问量，如果出错则返回 0，绝不让程序崩溃"""
    try:
        today_str = datetime.date.today().isoformat()
        
        if "has_counted" in st.session_state:
            if os.path.exists(COUNTER_FILE):
                try:
                    with open(COUNTER_FILE, "r") as f:
                        return json.load(f).get("count", 0)
                except:
                    return 0
            return 0

        data = {"date": today_str, "count": 0}
        
        if os.path.exists(COUNTER_FILE):
            try:
                with open(COUNTER_FILE, "r") as f:
                    file_data = json.load(f)
                    if file_data.get("date") == today_str:
                        data = file_data
            except:
                pass
        
        data["count"] += 1
        
        with open(COUNTER_FILE, "w") as f:
            json.dump(data, f)
        
        st.session_state["has_counted"] = True
        return data["count"]
        
    except Exception as e:
        return 0

# -------- 每日访问统计 --------
daily_visits = update_daily_visits()
visit_text = f"今日访问: {daily_visits}"


# -------------------------- 3. 底部导航渲染函数 --------------------------
def render_bottom_nav(text):
    nav_html = f"""
    <div class="bottom-nav">
        <a href="https://youqian.streamlit.app/" class="nav-item active" target="_self">
            {text['nav_1']}
        </a>
        <a href="https://fangchan.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_2']}
        </a>
        <a href="https://fangjia.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_3']}
        </a>
        <a href="https://chuhai.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_4']}
        </a>
        <a href="https://chuhai.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_5']}
        </a>
        <a href="https://chuhai.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_6']}
        </a>
        <a href="https://qfschina.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_7']}
        </a>
        <a href="https://fangjia.streamlit.app/" class="nav-item" target="_blank">
            {text['nav_8']}
        </a>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)
    
# -------------------------- 4. 业务逻辑与数据 --------------------------
TRANSLATIONS = {
    "English": {
        "title": "Global Wealth Pyramid", "subtitle": "Where do you stand globally?", 
        "section_input": "Your Profile", "section_result": "Analysis Result",
        "location": "Location", "income": "Annual Income", "wealth": "Net Worth", 
        "btn_calc": "Update Analysis", "card_income": "Income Level", "card_wealth": "Wealth Status", 
        "rank_prefix": "Top", "rank_approx": "Rank #", 
        "disclaimer": "Estimations based on Log-Normal Distribution Model", 
        "nav_1": "Wealth Rank", 
        "nav_2": "Global Real Estate", 
        "nav_3": "Urban Housing", 
        "nav_4": "Global Legal", 
        "nav_5": "Global Enterprises", 
        "nav_6": "Contract Review", 
        "nav_7": "German Tax", 
        "nav_8": "Shenzhen Property"      
    },
    "中文": {
        "title": "全球财富金字塔", "subtitle": "你的财富在全球处于什么段位？", 
        "section_input": "基本信息", "section_result": "分析报告",
        "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", 
        "btn_calc": "重新计算", "card_income": "年收入水平", "card_wealth": "资产水平", 
        "rank_prefix": "前", "rank_approx": "绝对排名 第", 
        "disclaimer": "基于对数正态分布模型估算", 
        "nav_1": "财富排行", 
        "nav_2": "世界房产", 
        "nav_3": "城市房价", 
        "nav_4": "全球法律", 
        "nav_5": "全球企业", 
        "nav_6": "合同审查", 
        "nav_7": "德国财税", 
        "nav_8": "深圳房市"
    }
}

COUNTRY_DATA = {
    "CN": {"name_en": "China", "name_zh": "中国", "currency": "¥", "population": 1411750000, "medianIncome": 60000, "medianWealth": 120000, "incomeGini": 0.7, "wealthGini": 1.1},
    "US": {"name_en": "USA", "name_zh": "美国", "currency": "$", "population": 331900000, "medianIncome": 45000, "medianWealth": 190000, "incomeGini": 0.8, "wealthGini": 1.5},
    "JP": {"name_en": "Japan", "name_zh": "日本", "currency": "¥", "population": 125100000, "medianIncome": 4000000, "medianWealth": 15000000, "incomeGini": 0.6, "wealthGini": 0.9},
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

# -------------------------- 新增：人群矩阵渲染函数 --------------------------

def render_dot_matrix(percentile, color):
    """
    渲染双色对比的人群矩阵 (Dot Matrix / Waffle Chart)。
    使用 HTML/CSS 创建 10x10 的点阵。
    
    Args:
        percentile (float): 财富百分位 (0.0001 to 0.9999)。
        color (str): 突出显示的颜色 (例如: '#3b82f6')。
    """
    # 计算需要突出显示的点数 (总共 100 个点)
    # 我们显示 Top N% 的人，所以是 1 - percentile
    highlight_count = math.ceil((1 - percentile) * 100)
    
    # 定义非突出显示的颜色 (灰色)
    base_color = '#e2e8f0'
    
    # 使用 CSS Grid 创建 10x10 布局
    dot_matrix_html = f"""
    <div class="dot-matrix-container">
    """
    
    # 生成 100 个点
    for i in range(100):
        # 排名越靠前 (i < highlight_count)，使用高亮色
        dot_color = color if i < highlight_count else base_color
        
        dot_matrix_html += f"""
        <div class="dot" style="background-color: {dot_color};"></div>
        """
        
    dot_matrix_html += "</div>"
    st.markdown(dot_matrix_html, unsafe_allow_html=True)


def render_metric_card(t, amount, currency, percentile, rank, color, lang_key):
    top_percent = (1 - percentile) * 100
    rank_str = f"{t['rank_prefix']} {top_percent:.1f}%"
    
    # ----------------------------------------------------
    # 替代原有的 Matplotlib 曲线图
    render_dot_matrix(percentile, color) 
    # ----------------------------------------------------
    
    html = f"""
<div style="margin-top: -5px; padding: 0 10px;">
    <div style="font-size: 2rem; font-weight: 700; color: #0f172a; line-height: 1.1; margin-bottom: 12px;">
        <span style="font-size: 1.2rem; color: #64748b; font-weight: 600; margin-right: 4px;">{currency}</span>{format_compact_localized(amount, lang_key)}
    </div>
    <div style="background-color: #f8fafc; border-radius: 8px; padding: 12px; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 0.85rem; color: #64748b;">排名百分比</span>
            <span style="color: {color}; font-weight: 700; font-size: 1.1rem;">{rank_str}</span>
        </div>
        <div style="width: 100%; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden;">
            <div style="width: {(percentile * 100)}%; height: 100%; background: {color}; border-radius: 3px;"></div>
        </div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px; text-align: right;">
                {t['rank_approx']} {format_compact_localized(rank, lang_key)}
        </div>
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


# -------------------------- 5. 主程序入口 --------------------------
def main():
    # 1. 主内容区域容器
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # --- 头部区域 ---
    h_col, l_col = st.columns([3, 1])
    with l_col:
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        lang = st.selectbox("Language", ["中文", "English"], label_visibility="collapsed")
    
    text = TRANSLATIONS[lang]
    
    with h_col:
        st.markdown(f"<div class='page-title'>{text['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='page-subtitle'>{text['subtitle']}</div>", unsafe_allow_html=True)
    
    # --- 第一部分：输入区域 ---
    st.markdown(
        f"<div style='font-weight:600; color:#334155; margin-bottom:12px; font-size:0.95rem;'>1. {text['section_input']}</div>",
        unsafe_allow_html=True
    )

    with st.container(border=True):
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
            
    
    # 按钮
    st.markdown("<div style='height: 15px;'>", unsafe_allow_html=True)
    st.button(text['btn_calc'], type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- 第二部分：结果渲染区域 ---
    inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
    wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
    inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
    wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
    
    st.markdown(f"<div style='font-weight:600; color:#334155; margin-bottom:12px; margin-top: 10px; font-size:0.95rem;'>2. {text['section_result']}</div>", unsafe_allow_html=True)
    
    # 两列展示结果卡片
    r1, r2 = st.columns(2)
    
    with r1: 
        html_header = f"""
<div class="metric-card" style="border-top: 4px solid #3b82f6 !important;">
    <div style="color: #64748b; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 15px;">
        {text['card_income']}
    </div>
"""
        with st.container(border=True):
            st.markdown(html_header, unsafe_allow_html=True)
            render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#3b82f6", lang)
            st.markdown("</div>", unsafe_allow_html=True)

    with r2: 
        html_header_w = f"""
<div class="metric-card" style="border-top: 4px solid #6366f1 !important;">
    <div style="color: #64748b; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 15px;">
        {text['card_wealth']}
    </div>
"""
        with st.container(border=True):
            st.markdown(html_header_w, unsafe_allow_html=True)
            render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#6366f1", lang)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # --- 底部统计与声明 ---
    st.markdown(f"""
    <div style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:40px; line-height: 1.5;'>
        {text['disclaimer']}<br>
        <span style="opacity: 0.7">{visit_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 闭合主内容容器
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 渲染底部导航
    render_bottom_nav(text)

# -------------------------- 6. 执行 --------------------------
if __name__ == "__main__":
    main()

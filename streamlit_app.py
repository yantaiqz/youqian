import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import os

# -------------------------- 0. 全局配置 (必须置顶) --------------------------
st.set_page_config(
    page_title="WealthRank 财富排行榜",
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
        width: 12.5% !important; /* 8个均分 */
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
    
    /* 激活态指示器 - 小圆点替代下划线 */
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
    
    /* hover效果 */
    .nav-item:hover {
        color: #5294ff !important;
    }
    
    /* 6. 主内容区样式 */
    .main-content {
        padding: 2rem 2rem 1rem 2rem !important;
        max-width: 800px !important; /* 限制最大宽度以优化大屏体验 */
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }
    
    /* 7. 按钮/卡片样式优化 */
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
    div.stButton > button:active {
        background-color: #1d4ed8 !important;
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
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 2. 安全的计数器逻辑 --------------------------
COUNTER_FILE = "visit_stats.json"

def update_daily_visits():
    """安全更新访问量，如果出错则返回 0，绝不让程序崩溃"""
    try:
        today_str = datetime.date.today().isoformat()
        
        # 1. 检查 Session，防止刷新页面重复计数
        if "has_counted" in st.session_state:
            if os.path.exists(COUNTER_FILE):
                try:
                    with open(COUNTER_FILE, "r") as f:
                        return json.load(f).get("count", 0)
                except:
                    return 0
            return 0

        # 2. 读取或初始化数据
        data = {"date": today_str, "count": 0}
        
        if os.path.exists(COUNTER_FILE):
            try:
                with open(COUNTER_FILE, "r") as f:
                    file_data = json.load(f)
                    if file_data.get("date") == today_str:
                        data = file_data
            except:
                pass # 文件损坏则从0开始
        
        # 3. 计数 +1
        data["count"] += 1
        
        # 4. 写入文件
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
def render_bottom_nav():
    # 8个导航项
    nav_html = """
    <div class="bottom-nav">
        <a href="#" class="nav-item active" target="_self">
            <span class="nav-icon">📊</span>
            <span>Dashboard</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">🌍</span>
            <span>Map</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">🧮</span>
            <span>Calc</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">📈</span>
            <span>Portfolio</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">📑</span>
            <span>Reports</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">🔔</span>
            <span>Alerts</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">⚙️</span>
            <span>Settings</span>
        </a>
        <a href="#" class="nav-item" target="_self">
            <span class="nav-icon">👤</span>
            <span>Profile</span>
        </a>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

# -------------------------- 4. 业务逻辑与数据 --------------------------
TRANSLATIONS = {
    "English": {
        "title": "Global Wealth Pyramid", "subtitle": "Where do you stand in the global economy?", 
        "location": "Your Location", "income": "Annual Income", "wealth": "Net Worth", 
        "btn_calc": "Analyze My Position", "card_income": "Income Level", "card_wealth": "Wealth Status", 
        "rank_prefix": "Nationwide", "rank_approx": "Rank #", 
        "disclaimer": "Estimations based on Log-Normal Distribution Model"
    },
    "中文": {
        "title": "全球财富金字塔", "subtitle": "你的财富在全球处于什么段位？", 
        "location": "居住国家", "income": "税前年收入", "wealth": "家庭净资产", 
        "btn_calc": "生成分析报告", "card_income": "年收入水平", "card_wealth": "资产水平", 
        "rank_prefix": "超过所选国家", "rank_approx": "绝对排名 第", 
        "disclaimer": "基于对数正态分布模型估算"
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

def render_metric_card(t, amount, currency, percentile, rank, color, lang_key):
    top_percent = (1 - percentile) * 100
    rank_str = f"Top {top_percent:.1f}%" if lang_key != "中文" else f"前 {top_percent:.1f}%"
    
    # 绘制小图表
    chart_html = ""
    try:
        x = np.linspace(-3, 3, 50)
        y = np.exp(-0.5 * x**2)
        chart_x = (x + 3) / 6
        chart_y = y / y.max()
        simulated_z = (percentile - 0.5) * 6
        marker_x = percentile
        marker_y = np.exp(-0.5 * simulated_z**2)
        
        fig, ax = plt.subplots(figsize=(5, 1.2)) # 调整尺寸
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        ax.fill_between(chart_x, chart_y, color=color, alpha=0.15)
        ax.plot(chart_x, chart_y, color=color, linewidth=1.5)
        ax.scatter([marker_x], [marker_y], color=color, s=50, edgecolor='white', linewidth=1.5, zorder=5)
        ax.axis('off')
        
        # 将plot转为Streamlit对象
        st.pyplot(fig, use_container_width=True, transparent=True)
        plt.close(fig)
    except:
        pass

    # 文字信息
    st.markdown(f"""
    <div style="margin-top: -10px;">
        <div style="font-size: 1.8rem; font-weight: 700; color: #1e293b; line-height: 1.2;">
            {currency} {format_compact_localized(amount, lang_key)}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
            <div style="font-size: 0.85rem; color: #64748b;">
                {t['rank_prefix']}
            </div>
            <div style="color: {color}; font-weight: 700; font-size: 1.1rem; background: {color}15; padding: 2px 8px; border-radius: 4px;">
                {rank_str}
            </div>
        </div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px; text-align: right;">
             {t['rank_approx']} {format_compact_localized(rank, lang_key)}
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------- 5. 主程序入口 --------------------------
def main():
    # 1. 主内容区域容器
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # --- 头部区域 ---
    h_col, l_col = st.columns([5, 2])
    with l_col:
        # 默认选中 "中文" (index 0)
        lang = st.selectbox("Language", ["中文", "English"], label_visibility="collapsed")
    
    text = TRANSLATIONS[lang]
    
    with h_col:
        st.markdown(f"<h1 style='margin-top:0; font-size: 1.8rem; font-weight: 700; color: #1e293b; letter-spacing: -0.5px;'>{text['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#64748b; font-size:0.95rem; margin-top:-10px; margin-bottom: 20px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    
    # --- 输入区域 ---
    # 使用 container 包裹增加一点间距
    with st.container():
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

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # --- 按钮与计算逻辑 ---
    # 无论是否点击按钮，只要有数据就渲染（满足"首次打开显示图表"需求）
    # 按钮保留作为视觉确认
    calc_pressed = st.button(text['btn_calc'], type="primary")
    
    # --- 结果渲染区域 ---
    # 计算逻辑
    inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
    wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
    inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
    wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 使用两列展示结果卡片
    r1, r2 = st.columns(2)
    
    # 收入卡片
    with r1: 
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #3b82f6 !important; padding-bottom: 0 !important;">
            <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;">
                {text['card_income']}
            </div>
        """, unsafe_allow_html=True)
        # 传入绘图逻辑
        render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#3b82f6", lang)
        st.markdown("</div>", unsafe_allow_html=True)

    # 财富卡片
    with r2: 
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #6366f1 !important; padding-bottom: 0 !important;">
            <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;">
                {text['card_wealth']}
            </div>
        """, unsafe_allow_html=True)
        render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#6366f1", lang)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # --- 底部统计与声明 ---
    st.markdown(f"""
    <div style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:30px;'>
        {text['disclaimer']}
    </div>
    <div style="text-align: center; color: #cbd5e1; font-size: 0.7rem; margin-top: 10px; padding-bottom: 20px;">
        {visit_text}
    </div>
    """, unsafe_allow_html=True)
    
    # 闭合主内容容器
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. 渲染底部导航
    render_bottom_nav()

# -------------------------- 6. 执行 --------------------------
if __name__ == "__main__":
    main()

import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import datetime
import os  
import time 


# -------------------------- 0. 全局配置 (必须置顶) --------------------------
st.set_page_config(
    page_title="WealthRank 财富排行榜",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 1. 彻底隐藏Streamlit默认干扰元素 */
    header, [data-testid="stSidebar"], footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 2. 全局样式重置 - 极致紧凑 */
    .stApp {
        background-color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        padding-bottom: 60px !important; /* 仅保留底部导航高度 */
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        margin: 0 !important;
    }
    
    /* 3. 底部导航核心样式 - 更紧凑 */
    .bottom-nav {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 50px !important; /* 降低导航栏高度 */
        background-color: rgba(255, 255, 255, 0.90) !important;
        backdrop-filter: blur(16px) !important;
        border-top: 1px solid rgba(226, 232, 240, 0.8) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 5px !important; /* 更少内边距 */
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.02) !important;
        z-index: 9999 !important;
        box-sizing: border-box !important;
    }
    
    /* 4. 导航项样式 - 极致紧凑 */
    .nav-item {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 36px !important; /* 降低高度 */
        color: #94a3b8 !important;
        text-decoration: none !important;
        font-size: 0.65rem !important; /* 更小字体 */
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
        margin: 0 1px !important; /* 最小间距 */
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    .nav-item:hover {
        background-color: rgba(241, 245, 249, 0.8) !important;
        color: #64748b !important;
    }
    
    .nav-item.active {
        color: #2563eb !important;
        background-color: rgba(59, 130, 246, 0.1) !important;
    }
    
    .nav-item.active::before {
        display: none !important;
    }

    /* --------------------------------------------------- */
    /* 核心：主内容容器 - 极致紧凑 */
    /* --------------------------------------------------- */
    .main-content {
        max-width: 850px !important; /* 更小最大宽度 */
        margin: 0 auto !important;
        padding: 1rem 0.8rem 0.5rem 0.8rem !important; /* 大幅减少内边距 */
        box-sizing: border-box !important;
        width: 100% !important;
    }

    /* 标题样式 - 紧凑化 */
    .page-title {
        font-size: 1.6rem !important; /* 更小标题 */
        font-weight: 800 !important;
        color: #1e293b !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.2rem !important; /* 极少间距 */
        line-height: 1.2 !important;
    }
    .page-subtitle {
        color: #64748b !important;
        font-size: 0.9rem !important;
        margin-bottom: 1rem !important; /* 减少间距 */
        font-weight: 400 !important;
        line-height: 1.3 !important;
    }

    /* 修复卡片样式 - 极致紧凑 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 12px !important; /* 更小圆角 */
        padding: 16px !important; /* 减少内边距 */
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.01), 0 1px 2px -1px rgba(0, 0, 0, 0.01) !important;
        border: 1px solid #f1f5f9 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin-bottom: 0.8rem !important; /* 减少底部间距 */
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0 !important;
    }
    
    /* 结果指标卡片 - 极致紧凑 */
    .metric-card {
        background: white !important; 
        border: 1px solid #eef2f7 !important; 
        border-radius: 12px !important; 
        padding: 12px !important; /* 减少内边距 */
        text-align: center !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01) !important;
        box-sizing: border-box !important;
        width: 100% !important;
        transition: transform 0.2s ease !important;
        height: auto !important;
        margin-bottom: 0 !important;
    }
    .metric-card:hover {
        transform: translateY(-2px) !important;
    }

    /* 按钮样式 - 紧凑化 */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important; 
        border-radius: 8px !important; 
        padding: 0.6rem 1.2rem !important; /* 减少内边距 */
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 2px 4px -1px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s !important;
        box-sizing: border-box !important;
        font-size: 0.9rem !important;
        height: auto !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 6px 10px -3px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* 输入框样式 - 紧凑化 */
    .stSelectbox, .stNumberInput {
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .stSelectbox label, .stNumberInput label {
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important; /* 更小标签 */
        margin-bottom: 2px !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        height: 36px !important; /* 更矮输入框 */
        font-size: 0.85rem !important;
    }
    .stNumberInput div[data-baseweb="input"] {
        height: 36px !important; /* 更矮输入框 */
        font-size: 0.85rem !important;
    }

    /* 修复列布局溢出问题 - 更紧凑 */
    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        box-sizing: border-box !important;
        gap: 0.6rem !important; /* 更小列间距 */
    }

    /* 人群矩阵样式 - 紧凑化 */
    .matrix-legend {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 8px;
        font-size: 0.7rem;
        color: #64748b;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .legend-color {
        width: 10px;
        height: 10px;
        border-radius: 2px;
    }
    
    /* 右上角按钮样式 - 更紧凑 */
    .neal-btn {
        font-family: 'Inter', sans-serif;
        background: #fff;
        border: 1px solid #e5e7eb;
        color: #111;
        font-weight: 600;
        font-size: 12px !important; /* 更小字体 */
        padding: 6px 10px !important; /* 更少内边距 */
        border-radius: 6px !important;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        text-decoration: none !important;
        width: 100%;
        height: 34px !important; /* 更矮高度 */
    }
    .neal-btn:hover {
        background: #f9fafb;
        border-color: #111;
        transform: translateY(-1px);
    }
    .neal-btn-link { 
        text-decoration: none; 
        width: 100%; 
        display: block; 
    }
    
    /* 自定义间距控制 */
    .spacer-xs {
        height: 8px !important;
    }
    .spacer-sm {
        height: 10px !important;
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
        "title": "Wealth Pyramid", "subtitle": "Where do you stand globally?", 
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
        "nav_8": "Shenzhen Property",
        "matrix_legend_high": "Top {:.1f}% (You)",
        "matrix_legend_low": "Remaining Population"   
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
        "nav_8": "深圳房市",
        "matrix_legend_high": "前 {:.1f}% (你)",
        "matrix_legend_low": "其他人群"
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

def render_wealth_matrix(percentile, color_high, color_low,text, lang_key):
    """渲染双色人群矩阵图 - 更紧凑"""
    # 矩阵大小（更紧凑的网格）
    matrix_size = (8, 16)  # 更小的矩阵
    total_cells = matrix_size[0] * matrix_size[1]
    
    # 计算用户所在的高段位单元格数量
    top_percent = (1 - percentile) * 100
    high_cells = int(round(total_cells * (1 - percentile)))
    high_cells = max(1, min(high_cells, total_cells))
    low_cells = total_cells - high_cells
    
    # 创建矩阵数据
    matrix = []
    cell_count = 0
    for row in range(matrix_size[0]):
        row_data = []
        for col in range(matrix_size[1]):
            if cell_count < high_cells:
                row_data.append(1)
            else:
                row_data.append(0)
            cell_count += 1
        matrix.append(row_data)
    
    # 反转矩阵
    matrix = np.array(matrix)[::-1, ::-1]
    
    # 创建图表（更小尺寸）
    fig, ax = plt.subplots(figsize=(7, 3.5))  # 更小图表
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # 绘制矩阵单元格
    cell_width = 1 / matrix_size[1]
    cell_height = 1 / matrix_size[0]
    
    for i in range(matrix_size[0]):
        for j in range(matrix_size[1]):
            x = j * cell_width
            y = i * cell_height
            
            if matrix[i, j] == 1:
                cell_color = color_high
                alpha = 0.8
            else:
                cell_color = color_low
                alpha = 0.2
            
            rect = patches.Rectangle(
                (x, y), cell_width, cell_height,
                linewidth=0.3, edgecolor='#f1f5f9',  # 更细边框
                facecolor=cell_color, alpha=alpha
            )
            ax.add_patch(rect)
    
    # 添加用户位置标记
    high_pos = np.argwhere(matrix == 1)[0]
    marker_x = (high_pos[1] + 0.5) * cell_width
    marker_y = (high_pos[0] + 0.5) * cell_height
    
    ax.scatter(
        marker_x, marker_y, 
        color=color_high, s=80,  # 更小标记
        edgecolor='white', linewidth=1.5, 
        zorder=10, alpha=1
    )
    ax.text(
        marker_x, marker_y, '●', 
        ha='center', va='center', 
        color='white', fontsize=7, 
        zorder=11
    )
    
    # 图表样式设置
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    # 显示图表
    st.pyplot(fig, use_container_width=True, transparent=True)
    plt.close(fig)
    
    # 显示图例
    legend_html = f"""
    <div class="matrix-legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: {color_high};"></div>
            <span>{text['matrix_legend_high'].format(top_percent)}</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: {color_low};"></div>
            <span>{text['matrix_legend_low']}</span>
        </div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

def render_metric_card(t, amount, currency, percentile, rank, color_high, color_low, lang_key):
    top_percent = (1 - percentile) * 100
    rank_str = f"{t['rank_prefix']} {top_percent:.1f}%"
    
    # 渲染人群矩阵
    render_wealth_matrix(percentile, color_high, color_low, t, lang_key)

    # 渲染数值信息（更紧凑）
    html = f"""
<div style="margin-top: 10px; padding: 0 5px;">
    <div style="font-size: 1.6rem; font-weight: 700; color: #0f172a; line-height: 1.1; margin-bottom: 8px;">
        <span style="font-size: 1rem; color: #64748b; font-weight: 600; margin-right: 3px;">{currency}</span>{format_compact_localized(amount, lang_key)}
    </div>
    <div style="background-color: #f8fafc; border-radius: 6px; padding: 8px; margin-top: 6px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
            <span style="font-size: 0.8rem; color: #64748b;">排名百分比</span>
            <span style="color: {color_high}; font-weight: 700; font-size: 1rem;">{rank_str}</span>
        </div>
        <div style="width: 100%; height: 5px; background: #e2e8f0; border-radius: 2px; overflow: hidden;">
            <div style="width: {(percentile * 100)}%; height: 100%; background: {color_high}; border-radius: 2px;"></div>
        </div>
        <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 6px; text-align: right;">
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
    
    # --- 头部区域（更紧凑）---
    h_col, l_col , col_more= st.columns([5, 1, 1.2])  # 调整列比例
    with l_col:
        st.markdown("<div class='spacer-xs'></div>", unsafe_allow_html=True)
        lang = st.selectbox("Language", ["中文", "English"], label_visibility="collapsed")

    with col_more:
        st.markdown("<div class='spacer-xs'></div>", unsafe_allow_html=True)
        # 右上角按钮
        st.markdown(
            f"""
            <a href="https://haowan.streamlit.app/" target="_blank" class="neal-btn-link">
                <button class="neal-btn">✨ 更多好玩应用</button>
            </a>
            """, 
            unsafe_allow_html=True
        )

    text = TRANSLATIONS[lang]
    
    with h_col:
        st.markdown(f"<div class='page-title'>{text['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='page-subtitle'>{text['subtitle']}</div>", unsafe_allow_html=True)
    
    # --- 第一部分：输入区域（极致紧凑）---
    st.markdown(
        f"<div style='font-weight:600; color:#334155; margin-bottom:8px; font-size:0.9rem;'>1. {text['section_input']}</div>",
        unsafe_allow_html=True
    )

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            country_code = st.selectbox(
                text['location'], 
                options=COUNTRY_DATA.keys(), 
                format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if lang == "中文" else COUNTRY_DATA[x]["name_en"],
                label_visibility="collapsed"
            )
            country = COUNTRY_DATA[country_code]
        with c2:
            income = st.number_input(
                text['income'], 
                value=int(country["medianIncome"]*1.5), 
                step=1000,
                label_visibility="collapsed"
            )
        with c3:
            wealth = st.number_input(
                text['wealth'], 
                value=int(country["medianWealth"]*1.5), 
                step=5000,
                label_visibility="collapsed"
            )
            
    # 按钮（极小间距）
    st.markdown("<div class='spacer-xs'></div>", unsafe_allow_html=True)
    st.button(text['btn_calc'], type="primary")
    st.markdown("<div class='spacer-xs'></div>", unsafe_allow_html=True)
    
    # --- 第二部分：结果渲染区域（更紧凑）---
    inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
    wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
    inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
    wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
    
    st.markdown(f"<div style='font-weight:600; color:#334155; margin-bottom:8px; margin-top: 5px; font-size:0.9rem;'>2. {text['section_result']}</div>", unsafe_allow_html=True)
    
    # 两列展示结果卡片
    r1, r2 = st.columns(2)
    
    with r1: 
        html_header = f"""
<div class="metric-card" style="border-top: 3px solid #3b82f6 !important;">
    <div style="color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;">
        {text['card_income']}
    </div>
"""
        with st.container(border=True):
            st.markdown(html_header, unsafe_allow_html=True)
            render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#3b82f6", "#93c5fd", lang)
            st.markdown("</div>", unsafe_allow_html=True)

    with r2: 
        html_header_w = f"""
<div class="metric-card" style="border-top: 3px solid #6366f1 !important;">
    <div style="color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;">
        {text['card_wealth']}
    </div>
"""
        with st.container(border=True):
            st.markdown(html_header_w, unsafe_allow_html=True)
            render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank,  "#6366f1","#a5b4fc", lang)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # --- 底部统计与声明（极致紧凑）---
    st.markdown(f"""
    <div style='text-align:center; color:#94a3b8; font-size:0.7rem; margin-top:20px; line-height: 1.4;'>
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

import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import os

# -------------------------- 0. 全局配置 (必须在第一行) --------------------------
st.set_page_config(
    page_title="WealthRank 财富排行榜",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------- 1. 样式与配置 --------------------------
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    h1 { font-weight: 800 !important; letter-spacing: -0.05rem; color: #0f172a; }
    
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput div[data-baseweb="input"] > div {
        border-radius: 8px; border: 1px solid #e2e8f0; background-color: #f8fafc;
    }
    
    div.stButton > button {
        background-color: #4f46e5; color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.5rem 1rem; transition: all 0.2s; width: 100%;
    }
    div.stButton > button:hover { background-color: #4338ca; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2); }
    
    .metric-card {
        background-color: white; border: 1px solid #f1f5f9; border-radius: 12px;
        padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px; text-align: center;
    }
    .metric-label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 8px 0; }
    .metric-sub { font-size: 0.9rem; color: #475569; }
    .highlight { color: #4f46e5; font-weight: 700; }
    
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div { flex-direction: row; gap: 10px; justify-content: flex-end; }
</style>
""", unsafe_allow_html=True)

TRANSLATIONS = {
    "English": {
        "title": "WealthRank Global",
        "subtitle": "Real-time wealth distribution estimator.",
        "location": "Location",
        "income": "Annual Income",
        "wealth": "Net Worth",
        "btn_calc": "Calculate Position",
        "card_income": "Income Level",
        "card_wealth": "Wealth Status",
        "rank_prefix": "Nationwide",
        "rank_approx": "≈ Rank #",
        "disclaimer": "Based on Log-Normal Distribution Model • Not Financial Advice"
    },
    "中文": {
        "title": "财富金字塔段位",
        "subtitle": "个人财富实时排名",
        "location": "居住国家",
        "income": "税前年收入",
        "wealth": "家庭净资产",
        "btn_calc": "查看我的排名",
        "card_income": "年收入水平",
        "card_wealth": "资产水平",
        "rank_prefix": "超过所选国家",
        "rank_approx": "≈ 绝对排名 第",
        "disclaimer": "基于对数正态分布模型估算 • 仅供参考 • 非理财建议"
    }
}

COUNTRY_DATA = {
    "CN": {"name_en": "China", "name_zh": "中国", "currency": "¥", "population": 1411750000, "medianIncome": 35000, "medianWealth": 120000, "incomeGini": 0.7, "wealthGini": 1.1},
    "US": {"name_en": "USA", "name_zh": "美国", "currency": "$", "population": 331900000, "medianIncome": 45000, "medianWealth": 190000, "incomeGini": 0.8, "wealthGini": 1.5},
    "JP": {"name_en": "Japan", "name_zh": "日本", "currency": "¥", "population": 125700000, "medianIncome": 4000000, "medianWealth": 15000000, "incomeGini": 0.6, "wealthGini": 0.9},
    "UK": {"name_en": "UK", "name_zh": "英国", "currency": "£", "population": 67330000, "medianIncome": 31000, "medianWealth": 150000, "incomeGini": 0.65, "wealthGini": 1.2},
    "DE": {"name_en": "Germany", "name_zh": "德国", "currency": "€", "population": 83200000, "medianIncome": 28000, "medianWealth": 110000, "incomeGini": 0.6, "wealthGini": 1.1},
}

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
        
        # 4. 写入文件 (最容易报错的地方，加了try保护)
        with open(COUNTER_FILE, "w") as f:
            json.dump(data, f)
        
        st.session_state["has_counted"] = True
        return data["count"]
        
    except Exception as e:
        # 如果发生任何错误（如权限不足），静默失败，不影响页面显示
        return 0

# -------------------------- 3. 核心计算逻辑 --------------------------
def get_log_normal_percentile(value, median, shape_parameter):
    if value <= 1: return 0.0001
    try:
        mu = math.log(median)
        sigma = shape_parameter
        z = (math.log(value) - mu) / sigma
        percentile = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        return min(max(percentile, 0.0001), 0.9999)
    except:
        return 0.0001

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

def draw_sparkline(percentile, color):
    x = np.linspace(-3, 3, 100)
    y = np.exp(-0.5 * x**2)
    chart_x = (x + 3) / 6
    chart_y = y / y.max()
    simulated_z = (percentile - 0.5) * 6
    marker_x = percentile
    marker_y = np.exp(-0.5 * simulated_z**2)
    
    fig, ax = plt.subplots(figsize=(6, 1.5))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.fill_between(chart_x, chart_y, color=color, alpha=0.1)
    ax.plot(chart_x, chart_y, color=color, linewidth=1.5, alpha=0.8)
    ax.scatter([marker_x], [marker_y], color=color, s=60, zorder=10)
    ax.vlines(marker_x, 0, marker_y, color=color, linestyle=":", alpha=0.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)
    ax.axis('off')
    
    # 显式关闭图表防止内存占用
    plt.close(fig) 
    return fig

def render_metric_card(t, amount, currency, percentile, rank, color, lang_key):
    top_percent = (1 - percentile) * 100
    if lang_key == "中文":
        rank_str = f"前 {top_percent:.1f}%" if top_percent > 0.1 else "前 0.1%"
    else:
        rank_str = f"Top {top_percent:.1f}%" if top_percent > 0.1 else "Top 0.1%"
    
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid {color};">
        <div class="metric-label">{t[f'card_{"income" if color=="#4f46e5" else "wealth"}']}</div>
        <div class="metric-value">{currency} {format_compact_localized(amount, lang_key)}</div>
        <div class="metric-sub">
            {t['rank_prefix']} <span class="highlight" style="color: {color}">{rank_str}</span>
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 5px;">
            {t['rank_approx']} {format_compact_localized(rank, lang_key)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.pyplot(draw_sparkline(percentile, color), use_container_width=True)

# -------------------------- 4. 主程序入口 --------------------------
def main():

    
    col_header, col_lang = st.columns([4, 1.2])
    with col_lang:
        selected_lang = st.radio("Language", ["English", "中文"], horizontal=True, label_visibility="collapsed")
    
    text = TRANSLATIONS[selected_lang]
    
    with col_header:
        st.markdown(f"# {text['title']}")
        st.markdown(f"<p style='color:#64748b; margin-top:-15px;'>{text['subtitle']}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        country_code = st.selectbox(
            text['location'], 
            options=list(COUNTRY_DATA.keys()), 
            format_func=lambda x: COUNTRY_DATA[x]["name_zh"] if selected_lang == "中文" else COUNTRY_DATA[x]["name_en"]
        )
        country = COUNTRY_DATA[country_code]
    with c2:
        income = st.number_input(text['income'], min_value=0, value=int(country["medianIncome"]), step=1000)
    with c3:
        wealth = st.number_input(text['wealth'], min_value=0, value=int(country["medianWealth"]), step=5000)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(text['btn_calc'], use_container_width=True):
        inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
        wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
        inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
        wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
        
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            render_metric_card(text, income, country["currency"], inc_pct, inc_rank, "#4f46e5", selected_lang)
        with r2:
            render_metric_card(text, wealth, country["currency"], wlh_pct, wlh_rank, "#0ea5e9", selected_lang)

    st.markdown(f"""
    <div style="text-align: center; color: #cbd5e1; font-size: 0.75rem; margin-top: 30px;">
        {text['disclaimer']}
    </div>
    """, unsafe_allow_html=True)


    # -------- 每日访问统计 (即使报错也不崩溃) --------
    daily_visits = update_daily_visits()
    visit_text = f"Daily Visits: {daily_visits}" if selected_lang == "English" else f"今日访问: {daily_visits}"
    
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.7rem; margin-top: 10px; padding-bottom: 20px;">
        {visit_text}
    </div>
    """, unsafe_allow_html=True)
    

# -------------------------- 5. 必须包含此入口！ --------------------------
if __name__ == "__main__":
    main()

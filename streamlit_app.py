import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 0. 配置与样式注入 --------------------------
st.set_page_config(
    page_title="WealthRank Global",
    page_icon="🌍",
    layout="centered", # 居中布局更聚焦，适合单页应用
    initial_sidebar_state="collapsed"
)

# 硅谷风格 CSS 注入
st.markdown("""
<style>
    /* 全局字体与背景 */
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 标题样式 */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.05rem;
        color: #0f172a;
    }
    
    /* 输入框优化 */
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput div[data-baseweb="input"] > div {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        background-color: #f8fafc;
    }
    
    /* 按钮优化 - 类似于 Stripe 风格 */
    div.stButton > button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #4338ca;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
    }
    
    /* 结果卡片容器 */
    .metric-card {
        background-color: white;
        border: 1px solid #f1f5f9;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        text-align: center;
    }
    .metric-label {
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0f172a;
        margin: 8px 0;
    }
    .metric-sub {
        font-size: 0.9rem;
        color: #475569;
    }
    .highlight {
        color: #4f46e5;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 1. 数据与核心逻辑 --------------------------
COUNTRY_DATA = {
    "CN": {"name": "China", "currency": "¥", "population": 1411750000, "medianIncome": 35000, "medianWealth": 120000, "incomeGini": 0.7, "wealthGini": 1.1},
    "US": {"name": "USA", "currency": "$", "population": 331900000, "medianIncome": 45000, "medianWealth": 190000, "incomeGini": 0.8, "wealthGini": 1.5},
    "JP": {"name": "Japan", "currency": "¥", "population": 125700000, "medianIncome": 4000000, "medianWealth": 15000000, "incomeGini": 0.6, "wealthGini": 0.9},
    "UK": {"name": "UK", "currency": "£", "population": 67330000, "medianIncome": 31000, "medianWealth": 150000, "incomeGini": 0.65, "wealthGini": 1.2},
    "DE": {"name": "Germany", "currency": "€", "population": 83200000, "medianIncome": 28000, "medianWealth": 110000, "incomeGini": 0.6, "wealthGini": 1.1},
}

def get_log_normal_percentile(value, median, shape_parameter):
    """(修复版) 计算对数正态分布CDF"""
    if value <= 1: return 0.0001
    try:
        mu = math.log(median)
        sigma = shape_parameter
        z = (math.log(value) - mu) / sigma
        percentile = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        return min(max(percentile, 0.0001), 0.9999)
    except:
        return 0.0001

def format_compact(num):
    """简洁数字格式化 (例如 1.2M, 35k)"""
    if num >= 1e9: return f"{num/1e9:.1f}B"
    if num >= 1e6: return f"{num/1e6:.1f}M"
    if num >= 1e4: return f"{num/1e3:.0f}k"
    return f"{num:,.0f}"

def draw_sparkline(percentile, color):
    """绘制极简风格的分布曲线"""
    x = np.linspace(-3, 3, 100)
    y = np.exp(-0.5 * x**2)
    chart_x = (x + 3) / 6
    chart_y = y / y.max()
    
    # 映射百分位位置
    simulated_z = (percentile - 0.5) * 6
    marker_x = percentile
    marker_y = np.exp(-0.5 * simulated_z**2)

    fig, ax = plt.subplots(figsize=(6, 1.5)) # 宽矮比例
    fig.patch.set_alpha(0) # 透明背景
    ax.patch.set_alpha(0)
    
    # 填充曲线
    ax.fill_between(chart_x, chart_y, color=color, alpha=0.1)
    ax.plot(chart_x, chart_y, color=color, linewidth=1.5, alpha=0.8)
    
    # 当前位置标记
    ax.scatter([marker_x], [marker_y], color=color, s=60, zorder=10)
    ax.vlines(marker_x, 0, marker_y, color=color, linestyle=":", alpha=0.5)
    
    # 极简坐标轴
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)
    ax.axis('off') # 关闭所有边框和刻度
    
    return fig

# -------------------------- 2. 界面组件 --------------------------
def render_metric_card(title, amount, currency, percentile, rank, color):
    """自定义HTML卡片渲染"""
    top_percent = (1 - percentile) * 100
    top_str = f"Top {top_percent:.1f}%" if top_percent > 0.1 else "Top 0.1%"
    
    st.markdown(f"""
    <div class="metric-card" style="border-top: 4px solid {color};">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{currency} {format_compact(amount)}</div>
        <div class="metric-sub">
            Globally <span class="highlight" style="color: {color}">{top_str}</span>
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 5px;">
            ≈ #{format_compact(rank)} rank
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 插入图表
    st.pyplot(draw_sparkline(percentile, color), use_container_width=True)

# -------------------------- 3. 主程序 --------------------------
def main():
    # Header
    st.markdown("<br>", unsafe_allow_html=True)
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("# WealthRank Global")
        st.markdown("<p style='color:#64748b; margin-top:-15px;'>Real-time wealth distribution estimator.</p>", unsafe_allow_html=True)
    
    # Input Grid (紧凑布局)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        country_code = st.selectbox("Location", options=list(COUNTRY_DATA.keys()), format_func=lambda x: COUNTRY_DATA[x]["name"])
        country = COUNTRY_DATA[country_code]
        
    with c2:
        income = st.number_input("Annual Income", min_value=0, value=int(country["medianIncome"]), step=1000)
        
    with c3:
        wealth = st.number_input("Net Worth", min_value=0, value=int(country["medianWealth"]), step=5000)

    # Action Button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Calculate Position", use_container_width=True):
        
        # Calculation
        inc_pct = get_log_normal_percentile(income, country["medianIncome"], country["incomeGini"])
        wlh_pct = get_log_normal_percentile(wealth, country["medianWealth"], country["wealthGini"])
        
        inc_rank = max(1, math.floor(country["population"] * (1 - inc_pct)))
        wlh_rank = max(1, math.floor(country["population"] * (1 - wlh_pct)))
        
        # Results Section
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        
        with r1:
            render_metric_card(
                title="Income Level",
                amount=income,
                currency=country["currency"],
                percentile=inc_pct,
                rank=inc_rank,
                color="#4f46e5" # Indigo
            )
            
        with r2:
            render_metric_card(
                title="Wealth Status",
                amount=wealth,
                currency=country["currency"],
                percentile=wlh_pct,
                rank=wlh_rank,
                color="#0ea5e9" # Sky Blue
            )

        st.markdown("""
        <div style="text-align: center; color: #cbd5e1; font-size: 0.75rem; margin-top: 30px;">
            Based on Log-Normal Distribution Model • Not Financial Advice
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

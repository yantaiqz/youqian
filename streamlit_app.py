import streamlit as st
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# --- 配置页面 ---
st.set_page_config(
    page_title="WealthRank Global",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 模拟数据 ---
COUNTRY_DATA = {
    "CN": {
        "name": "中国",
        "currency": "¥",
        "population": 1411750000,
        "medianIncome": 35000,
        "medianWealth": 120000,
        "incomeGini": 0.7,
        "wealthGini": 1.1,
    },
    "US": {
        "name": "美国",
        "currency": "$",
        "population": 331900000,
        "medianIncome": 45000,
        "medianWealth": 190000,
        "incomeGini": 0.8,
        "wealthGini": 1.5,
    },
    "JP": {
        "name": "日本",
        "currency": "¥",
        "population": 125700000,
        "medianIncome": 4000000,
        "medianWealth": 15000000,
        "incomeGini": 0.6,
        "wealthGini": 0.9,
    },
    "UK": {
        "name": "英国",
        "currency": "£",
        "population": 67330000,
        "medianIncome": 31000,
        "medianWealth": 150000,
        "incomeGini": 0.65,
        "wealthGini": 1.2,
    },
    "DE": {
        "name": "德国",
        "currency": "€",
        "population": 83200000,
        "medianIncome": 28000,
        "medianWealth": 110000,
        "incomeGini": 0.6,
        "wealthGini": 1.1,
    },
}

# --- 工具函数 ---

def calculate_log_normal_percentile(value, median, shape_parameter):
    """
    计算对数正态分布的累积分布函数 (CDF)
    """
    if value <= 0:
        return 0.0
    
    # 转换为对数空间的正态分布参数
    mu = np.log(median)
    sigma = shape_parameter
    
    # 计算 Z-score
    z = (np.log(value) - mu) / sigma
    
    # 使用 scipy 计算 CDF
    percentile = stats.norm.cdf(z)
    
    # 修正极端值，保持与原代码逻辑一致的边界
    if percentile > 0.9999: percentile = 0.9999
    if percentile < 0.0001: percentile = 0.0001
    
    return percentile

def format_big_number(num):
    """格式化大数字（亿/万）"""
    if num >= 100000000:
        return f"{num / 100000000:.2f}亿"
    if num >= 10000:
        return f"{num / 10000:.1f}万"
    return str(num)

def draw_distribution_chart(percentile, label, color_theme):
    """
    使用 Matplotlib 绘制分布图，模仿 React 中的 SVG 效果
    """
    # 设置颜色
    if color_theme == 'blue':
        main_color = '#4f46e5'  # Indigo 600
        fill_color_start = '#818cf8'
        fill_color_end = '#4f46e5'
    else:
        main_color = '#10b981'  # Emerald 500
        fill_color_start = '#34d399'
        fill_color_end = '#10b981'

    # 生成正态分布曲线数据 (Z-score -3 到 3)
    x = np.linspace(-3, 3, 200)
    y = stats.norm.pdf(x, 0, 1)

    fig, ax = plt.subplots(figsize=(6, 2.5), dpi=100)
    
    # 设置背景透明
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # 绘制填充区域
    # 模拟渐变有点复杂，这里使用半透明填充
    ax.fill_between(x, y, color=main_color, alpha=0.2)
    ax.plot(x, y, color=main_color, linewidth=2)

    # 计算用户位置
    # percentile 对应 Z-score
    user_z = stats.norm.ppf(percentile)
    # 限制绘制范围在视图内
    user_z_clamped = np.clip(user_z, -2.9, 2.9)
    
    # 获取该位置的高度
    user_y = stats.norm.pdf(user_z_clamped, 0, 1)

    # 绘制"你在这里"的虚线
    ax.vlines(x=user_z_clamped, ymin=0, ymax=user_y, colors='#64748b', linestyles='dashed', linewidth=1)
    
    # 绘制点
    ax.plot(user_z_clamped, user_y, 'o', color=main_color, markersize=8, markeredgecolor='white', markeredgewidth=1.5)

    # 标注文字
    ax.text(user_z_clamped, user_y + 0.05, "你在这里", 
            horizontalalignment='center', 
            fontsize=9, 
            fontweight='bold',
            color='#334155',
            # 使用支持中文的字体，如果系统没有可能显示方框，这里为了通用性不强制指定特殊字体路径
            # 在 Streamlit Cloud 中通常需要额外配置字体，此处主要演示逻辑
            )

    # 隐藏坐标轴
    ax.axis('off')
    
    # 添加底部标签
    plt.tight_layout()
    
    return fig

# --- 自定义 CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        background-color: #4f46e5;
        color: white;
        border-radius: 0.75rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
    }
    .card-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #f1f5f9;
        margin-bottom: 1.5rem;
    }
    .highlight-blue { color: #4f46e5; font-weight: bold; }
    .highlight-green { color: #10b981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 主程序 ---

def main():
    # 头部
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("# 📈 WealthRank <span style='color:#4f46e5'>Global</span>", unsafe_allow_html=True)
    with c2:
        st.caption("模拟数据演示版")
        
    st.markdown("---")

    if 'result' not in st.session_state:
        st.session_state.result = None

    # 介绍
    if st.session_state.result is None:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h2 style='color: #1e293b; font-weight: 800;'>你在全球财富金字塔的<br><span style='color: #4f46e5'>哪个位置？</span></h2>
            <p style='color: #64748b; font-size: 1.1rem;'>输入你的年收入和家庭总资产，看看你在国家人口中的排名位置。</p>
        </div>
        """, unsafe_allow_html=True)

    # 输入表单区域
    with st.container(border=True):
        st.markdown("### 📋 请输入您的财务信息")
        
        col_country, col_income, col_wealth = st.columns(3)
        
        with col_country:
            country_code = st.selectbox(
                "居住国家/地区",
                options=list(COUNTRY_DATA.keys()),
                format_func=lambda x: COUNTRY_DATA[x]['name']
            )
            current_country = COUNTRY_DATA[country_code]
            
        with col_income:
            income_input = st.number_input(
                f"个人税前年收入 ({current_country['currency']})",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                help=f"例如中位数: {current_country['medianIncome']}"
            )
            
        with col_wealth:
            wealth_input = st.number_input(
                f"家庭总净资产 ({current_country['currency']})",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                help=f"例如中位数: {current_country['medianWealth']}"
            )
            
        calculate_btn = st.button("查看排名 ➡️")

    # 计算逻辑
    if calculate_btn:
        with st.spinner('计算中...'):
            data = COUNTRY_DATA[country_code]
            
            # 计算收入排名
            income_percentile = calculate_log_normal_percentile(
                income_input, 
                data['medianIncome'], 
                data['incomeGini']
            )
            
            # 计算资产排名
            wealth_percentile = calculate_log_normal_percentile(
                wealth_input, 
                data['medianWealth'], 
                data['wealthGini']
            )
            
            st.session_state.result = {
                "country": data,
                "income_val": income_input,
                "income_pct": income_percentile,
                "wealth_val": wealth_input,
                "wealth_pct": wealth_percentile
            }

    # 结果显示区域
    if st.session_state.result:
        res = st.session_state.result
        country = res['country']
        
        st.markdown("### 📊 计算结果")
        st.caption(f"基于 {country['name']} 数据")

        # --- 收入卡片 ---
        with st.container(border=True):
            # 标题栏
            r1_col1, r1_col2 = st.columns([2, 1])
            with r1_col1:
                st.markdown(f"#### 💰 年收入排名")
                st.markdown(f"**{country['currency']}{res['income_val']:,.0f}**")
            with r1_col2:
                better_than = res['income_pct'] * 100
                top_pct = 100 - better_than
                st.metric("Top %", f"{top_pct:.1f}%", delta=None)
            
            # 详情
            d1_col1, d1_col2 = st.columns(2)
            
            with d1_col1:
                st.write(f"超过全国人口: **{better_than:.1f}%**")
                st.progress(res['income_pct'])
                
                rank = int(country['population'] * (1 - res['income_pct']))
                st.info(f"🏆 预估绝对排名: 第 {format_big_number(rank)} 名")
                st.caption(f"*基于总人口 {format_big_number(country['population'])}")
            
            with d1_col2:
                fig_income = draw_distribution_chart(res['income_pct'], "收入", 'blue')
                st.pyplot(fig_income)

        # --- 资产卡片 ---
        with st.container(border=True):
            # 标题栏
            r2_col1, r2_col2 = st.columns([2, 1])
            with r2_col1:
                st.markdown(f"#### 🏦 家庭资产排名")
                st.markdown(f"**{country['currency']}{res['wealth_val']:,.0f}**")
            with r2_col2:
                better_than_w = res['wealth_pct'] * 100
                top_pct_w = 100 - better_than_w
                st.metric("Top %", f"{top_pct_w:.1f}%")
            
            # 详情
            d2_col1, d2_col2 = st.columns(2)
            
            with d2_col1:
                st.write(f"超过全国人口: **{better_than_w:.1f}%**")
                # 为资产使用绿色主题进度条（Streamlit原生不支持改颜色，这里使用默认）
                st.progress(res['wealth_pct'])
                
                rank_w = int(country['population'] * (1 - res['wealth_pct']))
                st.success(f"🏆 预估绝对排名: 第 {format_big_number(rank_w)} 名")
                st.caption(f"*基于总人口 {format_big_number(country['population'])}")
            
            with d2_col2:
                fig_wealth = draw_distribution_chart(res['wealth_pct'], "资产", 'green')
                st.pyplot(fig_wealth)

        # 免责声明
        st.warning(
            "免责声明：本工具仅供娱乐和参考。排名结果基于对数正态分布模型和公开的宏观经济数据估算得出，"
            "并非查询真实的政府税务数据库。实际的财富分布可能因地区差异、非正规经济等因素而更加复杂。"
        )

if __name__ == "__main__":
    main()

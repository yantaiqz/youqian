import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt  # 顶部统一导入

# -------------------------- 全局配置与数据 --------------------------
st.set_page_config(
    page_title="WealthRank Global - 全球财富排名",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

COUNTRY_DATA = {
    "CN": {"name": "中国", "currency": "¥", "population": 1411750000, "medianIncome": 35000, "medianWealth": 120000, "incomeGini": 0.7, "wealthGini": 1.1},
    "US": {"name": "美国", "currency": "$", "population": 331900000, "medianIncome": 45000, "medianWealth": 190000, "incomeGini": 0.8, "wealthGini": 1.5},
    "JP": {"name": "日本", "currency": "¥", "population": 125700000, "medianIncome": 4000000, "medianWealth": 15000000, "incomeGini": 0.6, "wealthGini": 0.9},
    "UK": {"name": "英国", "currency": "£", "population": 67330000, "medianIncome": 31000, "medianWealth": 150000, "incomeGini": 0.65, "wealthGini": 1.2},
    "DE": {"name": "德国", "currency": "€", "population": 83200000, "medianIncome": 28000, "medianWealth": 110000, "incomeGini": 0.6, "wealthGini": 1.1},
}

# -------------------------- 工具函数 --------------------------
def get_log_normal_percentile(value, median, shape_parameter):
    """计算对数正态分布的累积分布函数（CDF），对应百分位"""
    # 修复1：强化输入校验，避免0或负数导致对数错误
    if value <= 1:  # 从 <=0 改为 <=1，避免接近0的极小值导致log计算异常
        return 0.0001
    
    try:
        mu = math.log(median)
        sigma = shape_parameter
        z = (math.log(value) - mu) / sigma  # 标准化
        
        # 修复2：添加z值异常校验（避免inf/NaN）
        if math.isinf(z) or math.isnan(z):
            return 0.0001
        
        # 误差函数近似正态分布CDF
        t = 1 / (1 + 0.3275911 * math.abs(z / math.sqrt(2)))
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        error = 1 - ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * math.exp((-z * z) / 2)
        
        percentile = 0.5 * (1 + (error if z > 0 else -error))
        return min(max(percentile, 0.0001), 0.9999)
    except Exception as e:
        # 异常兜底：避免计算过程中报错崩溃
        return 0.0001

def format_number(num):
    """格式化数字（千分位分隔）"""
    return f"{num:,.0f}"

def format_big_number(num):
    """格式化大数（亿/万单位）"""
    if num >= 1e8:
        return f"{num / 1e8:.2f}亿"
    elif num >= 1e4:
        return f"{num / 1e4:.1f}万"
    return f"{num:.0f}"

def plot_distribution_chart(percentile, label, color):
    """绘制分布曲线图（修复图表创建逻辑）"""
    x = np.linspace(-3, 3, 60)
    y = np.exp(-0.5 * x**2)
    chart_x = (x + 3) / 6
    chart_y = y / y.max()
    
    marker_x = percentile
    z_score = marker_x * 6 - 3
    marker_y = np.exp(-0.5 * z_score**2) / y.max()
    
    # 修复：确保图表对象正确创建
    fig, ax = plt.subplots(figsize=(8, 3))  # 缩小宽度适配卡片
    ax.plot(chart_x, chart_y, color=color, linewidth=2)
    ax.fill_between(chart_x, chart_y, alpha=0.3, color=color)
    
    ax.axvline(x=marker_x, ymin=0, ymax=marker_y, color="#64748b", linestyle="--", linewidth=1)
    ax.scatter(marker_x, marker_y, color=color, s=60, edgecolor="white", linewidth=2)
    ax.text(marker_x, marker_y + 0.05, "你在这里", ha="center", va="bottom", fontsize=10, fontweight="bold")
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.2)
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels([f"低{label}", "中位数", f"高{label}"])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    st.pyplot(fig, use_container_width=True)  # 适配容器宽度

# -------------------------- 核心组件 --------------------------
def result_card(title, value, percentile, population, icon, color, country_data):
    """结果卡片组件"""
    better_than = f"{percentile * 100:.1f}"
    rank = math.floor(population * (1 - percentile))
    currency = country_data["currency"]
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1.2])  # 调整列宽比例
        with col1:
            st.markdown(f"### {icon} {title}")
            st.markdown(f"**{currency}{format_number(value)}**")
            st.markdown(f"超过全国人口：{better_than}%")
            st.progress(float(better_than) / 100, text=f"Top {(100 - float(better_than)):.1f}%")
            
            st.markdown(f"""
            <div style="background-color: {color}20; padding: 10px; border-radius: 8px; margin-top: 10px;">
                <strong>预估绝对排名：</strong> 第 {format_big_number(rank)} 名
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<small style='color: #64748b;'>* 基于 {country_data['name']} 总人口 {format_big_number(population)} 估算</small>", unsafe_allow_html=True)
        
        with col2:
            plot_distribution_chart(percentile, title.replace("年", "").replace("家庭", ""), color)

# -------------------------- 主应用 --------------------------
def main():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 2.5rem; font-weight: bold;">WealthRank <span style="color: #6366f1;">Global</span></h1>
        <p style="font-size: 1.2rem; color: #64748b; margin-top: 10px;">你在全球财富金字塔的哪个位置？</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "result" not in st.session_state:
        st.session_state.result = None
    
    # 输入表单（修复3：强化按钮禁用逻辑，避免输入0提交）
    with st.container(border=True, height=320):  # 调整高度适配输入框
        col1, col2, col3, col4 = st.columns([1.5, 2, 2, 1.5])
        
        with col1:
            st.markdown("### 居住国家/地区")
            country_code = st.selectbox(
                label="国家选择",
                options=list(COUNTRY_DATA.keys()),
                format_func=lambda x: COUNTRY_DATA[x]["name"],
                index=0
            )
            current_country = COUNTRY_DATA[country_code]
        
        with col2:
            st.markdown("### 个人税前年收入")
            income = st.number_input(
                label="年收入",
                min_value=1,  # 修复：最小值设为1，禁止输入0
                value=current_country["medianIncome"],  # 默认值为该国中位数，提升体验
                format="%d"
            )
        
        with col3:
            st.markdown("### 家庭总净资产")
            wealth = st.number_input(
                label="家庭资产",
                min_value=1,  # 修复：最小值设为1，禁止输入0
                value=current_country["medianWealth"],  # 默认值
                format="%d"
            )
        
        with col4:
            st.markdown("### 计算排名")
            # 双重保险：min_value=1 + 按钮禁用逻辑
            calculate_btn = st.button(
                label="📊 查看排名",
                type="primary",
                use_container_width=True,
                disabled=income < 1 or wealth < 1
            )
    
    # 计算逻辑
    if calculate_btn:
        with st.spinner("计算中..."):
            income_percentile = get_log_normal_percentile(income, current_country["medianIncome"], current_country["incomeGini"])
            wealth_percentile = get_log_normal_percentile(wealth, current_country["medianWealth"], current_country["wealthGini"])
            
            st.session_state.result = {
                "country": current_country,
                "income_val": income,
                "income_percentile": income_percentile,
                "wealth_val": wealth,
                "wealth_percentile": wealth_percentile
            }
    
    # 展示结果
    if st.session_state.result:
        result = st.session_state.result
        st.markdown("---")
        st.markdown(f"<h2 style='text-align: center;'>计算结果 ({result['country']['name']})</h2>", unsafe_allow_html=True)
        
        result_card(
            title="年收入排名",
            value=result["income_val"],
            percentile=result["income_percentile"],
            population=result["country"]["population"],
            icon="💼",
            color="#6366f1",
            country_data=result["country"]
        )
        
        st.markdown("---")
        
        result_card(
            title="家庭资产排名",
            value=result["wealth_val"],
            percentile=result["wealth_percentile"],
            population=result["country"]["population"],
            icon="💰",
            color="#10b981",
            country_data=result["country"]
        )
        
        st.markdown("""
        <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #f59e0b;">
            <strong>免责声明：</strong> 本工具仅供娱乐和参考。排名结果基于对数正态分布模型和公开宏观经济数据估算，
            非真实政府税务数据库查询。实际财富分布可能因地区差异、非正规经济等因素更复杂。
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

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
    """计算对数正态分布的累积分布函数（CDF）"""
    if value <= 1:
        return 0.0001
    
    try:
        # 参数设定
        mu = math.log(median)
        sigma = shape_parameter
        
        # 计算对数值
        log_value = math.log(value)
        
        # 标准化：z = (ln(x) - mu) / sigma
        z = (log_value - mu) / sigma
        
        # 使用 Python 标准库 math.erf 计算 CDF
        # LogNormal CDF = 0.5 + 0.5 * erf( (ln(x) - mu) / (sigma * sqrt(2)) )
        percentile = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        
        # 限制极端值
        return min(max(percentile, 0.0001), 0.9999)
    except Exception as e:
        # 如果出错（如数值过大导致溢出），返回保守值
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
    """绘制分布曲线图"""
    # 生成标准正态分布曲线数据
    x = np.linspace(-3, 3, 100)
    y = np.exp(-0.5 * x**2)
    
    # 映射 x 轴到 0-1 (为了可视化百分位)
    # 使用累积分布函数(CDF)作为 x 轴映射可能更直观，但这里保持你的视觉风格
    # 这里我们将 x 从 -3~3 线性映射到图表上的 0~1
    chart_x = (x + 3) / 6 
    chart_y = y / y.max()
    
    # 根据输入的百分位计算对应的 Z-Score
    # 使用 scipy.special.ndtri 会更准，但为了减少依赖，这里用简单的线性反推近似
    # 或者如果不追求精确对应曲线形状，直接用 percentile 作为 x 位置
    marker_x = percentile
    
    # 为了让点落在曲线上，我们需要反推该百分位对应的钟形曲线高度
    # 简单的近似：假设 percentile 0.5 对应 x=0 (峰值)
    # 这是一个视觉上的近似处理
    simulated_z = (percentile - 0.5) * 6 # 映射回 -3 到 3
    marker_y = np.exp(-0.5 * simulated_z**2) 
    
    fig, ax = plt.subplots(figsize=(8, 3))
    
    # 绘制曲线和填充
    ax.plot(chart_x, chart_y, color=color, linewidth=2)
    ax.fill_between(chart_x, chart_y, alpha=0.3, color=color)
    
    # 绘制标示线和点
    ax.axvline(x=marker_x, ymin=0, ymax=marker_y, color="#64748b", linestyle="--", linewidth=1)
    ax.scatter(marker_x, marker_y, color=color, s=80, edgecolor="white", linewidth=2, zorder=5)
    
    # 动态调整标签位置防止溢出
    text_y = marker_y + 0.1
    ax.text(marker_x, text_y if text_y < 1.1 else marker_y - 0.2, "你在这里", 
            ha="center", va="bottom" if text_y < 1.1 else "top", 
            fontsize=10, fontweight="bold", color="#334155")
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.25)
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels([f"低{label}", "中位数", f"高{label}"])
    ax.set_yticks([])
    
    # 移除边框
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    st.pyplot(fig, use_container_width=True)

# -------------------------- 核心组件 --------------------------
def result_card(title, value, percentile, population, icon, color, country_data):
    """结果卡片组件"""
    better_than = f"{percentile * 100:.2f}"
    # 排名计算：总人口 * (1 - 百分位)，至少为第 1 名
    rank = max(1, math.floor(population * (1 - percentile)))
    currency = country_data["currency"]
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1.2])
        with col1:
            st.markdown(f"### {icon} {title}")
            st.markdown(f"**{currency}{format_number(value)}**")
            st.markdown(f"超过全国人口：**{better_than}%**")
            st.progress(min(percentile, 1.0), text=f"Top {(100 - float(better_than)):.2f}%")
            
            st.markdown(f"""
            <div style="background-color: {color}15; padding: 12px; border-radius: 8px; margin-top: 10px;">
                <strong>📊 预估绝对排名：</strong> 第 {format_big_number(rank)} 名
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<small style='color: #94a3b8;'>* 基于 {country_data['name']} 总人口 {format_big_number(population)} 模型估算</small>", unsafe_allow_html=True)
        
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
    
    # 输入表单
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([1.5, 2, 2, 1.5])
        
        with col1:
            st.markdown("### 居住国家/地区")
            country_code = st.selectbox(
                label="国家选择",
                options=list(COUNTRY_DATA.keys()),
                format_func=lambda x: COUNTRY_DATA[x]["name"],
                index=0,
                label_visibility="collapsed"
            )
            current_country = COUNTRY_DATA[country_code]
        
        with col2:
            st.markdown("### 个人税前年收入")
            income = st.number_input(
                label="年收入",
                min_value=1,
                value=int(current_country["medianIncome"]),
                format="%d",
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown("### 家庭总净资产")
            wealth = st.number_input(
                label="家庭资产",
                min_value=1,
                value=int(current_country["medianWealth"]),
                format="%d",
                label_visibility="collapsed"
            )
        
        with col4:
            st.markdown("### 计算排名")
            st.write("") # 占位对齐
            calculate_btn = st.button(
                label="📊 查看排名",
                type="primary",
                use_container_width=True,
                disabled=income < 1 or wealth < 1
            )
    
    # 计算逻辑
    if calculate_btn:
        with st.spinner("正在分析数据模型..."):
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
        <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #f59e0b; color: #78350f; font-size: 0.9rem;">
            <strong>免责声明：</strong> 本工具基于对数正态分布(Log-Normal Distribution)模型估算，仅供娱乐参考。实际财富分布极为复杂，且不同国家基尼系数定义存在差异。
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

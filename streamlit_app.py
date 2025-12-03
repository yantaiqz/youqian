import streamlit as st
import math
import numpy as np

# -------------------------- 全局配置与数据 --------------------------
# 页面配置
st.set_page_config(
    page_title="WealthRank Global - 全球财富排名",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 模拟国家经济数据（与原React保持一致）
COUNTRY_DATA = {
    "CN": {
        "name": "中国",
        "currency": "¥",
        "population": 1411750000,
        "medianIncome": 35000,  # 年度可支配收入中位数
        "medianWealth": 120000,  # 家庭净资产中位数
        "incomeGini": 0.7,      # 收入不平等参数（对数正态分布形状参数）
        "wealthGini": 1.1,      # 财富不平等参数
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

# -------------------------- 工具函数 --------------------------
def get_log_normal_percentile(value, median, shape_parameter):
    """计算对数正态分布的累积分布函数（CDF），对应百分位"""
    if value <= 0:
        return 0.0001
    
    mu = math.log(median)
    sigma = shape_parameter
    z = (math.log(value) - mu) / sigma  # 标准化
    
    # 误差函数近似正态分布CDF
    t = 1 / (1 + 0.3275911 * math.abs(z / math.sqrt(2)))
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    error = 1 - ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * math.exp((-z * z) / 2)
    
    percentile = 0.5 * (1 + (error if z > 0 else -error))
    # 限制极端值
    return min(max(percentile, 0.0001), 0.9999)

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
    """绘制分布曲线图（Streamlit原生图表）"""
    # 生成正态分布曲线数据
    x = np.linspace(-3, 3, 60)  # 标准化x轴
    y = np.exp(-0.5 * x**2)      # 正态分布y值
    
    # 转换为图表坐标（适配Streamlit显示）
    chart_x = (x + 3) / 6  # 映射到0-1区间
    chart_y = y / y.max()  # 归一化y值
    
    # 计算用户标记位置
    marker_x = percentile  # 百分位直接对应x轴位置
    z_score = marker_x * 6 - 3
    marker_y = np.exp(-0.5 * z_score**2) / y.max()  # 标记点y值
    
    # 绘制曲线（修复：正确创建matplotlib图表）
    fig, ax = plt.subplots(figsize=(10, 3))  # 修复：使用plt.subplots()创建图表
    ax.plot(chart_x, chart_y, color=color, linewidth=2)
    ax.fill_between(chart_x, chart_y, alpha=0.3, color=color)
    
    # 绘制标记线和点
    ax.axvline(x=marker_x, ymin=0, ymax=marker_y, color="#64748b", linestyle="--", linewidth=1)
    ax.scatter(marker_x, marker_y, color=color, s=60, edgecolor="white", linewidth=2)
    ax.text(marker_x, marker_y + 0.05, "你在这里", ha="center", va="bottom", fontsize=10, fontweight="bold")
    
    # 图表样式调整
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.2)
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels([f"低{label}", "中位数", f"高{label}"])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    
    st.pyplot(fig)  # 修复：传入fig对象

# -------------------------- 核心组件 --------------------------
def result_card(title, value, percentile, population, icon, color, country_data):
    """结果卡片组件（收入/资产排名展示）"""
    # 修复：将 JavaScript 的 toFixed(1) 替换为 Python 的格式化
    better_than = f"{percentile * 100:.1f}"  # 关键修复！
    rank = math.floor(population * (1 - percentile))  # 绝对排名
    currency = country_data["currency"]
    
    # 卡片样式（使用Streamlit容器和列布局）
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        
        # 左侧：标题、数值、进度条
        with col1:
            st.markdown(f"### {icon} {title}")
            st.markdown(f"**{currency}{format_number(value)}**")
            
            # 进度条
            st.markdown(f"超过全国人口：{better_than}%")
            st.progress(float(better_than) / 100, text=f"Top {(100 - float(better_than)):.1f}%")
            
            # 绝对排名
            st.markdown(f"""
            <div style="background-color: {color}20; padding: 10px; border-radius: 8px; margin-top: 10px;">
                <strong>预估绝对排名：</strong> 第 {format_big_number(rank)} 名
            </div>
            """, unsafe_allow_html=True)
            
            # 说明文字
            st.markdown(f"<small style='color: #64748b;'>* 基于 {country_data['name']} 总人口 {format_big_number(population)} 估算</small>", unsafe_allow_html=True)
        
        # 右侧：分布图表
        with col2:
            plot_distribution_chart(
                percentile=percentile,
                label=title.replace("年", "").replace("家庭", ""),
                color=color
            )

# -------------------------- 主应用 --------------------------
def main():
    # 页面标题
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 2.5rem; font-weight: bold;">WealthRank <span style="color: #6366f1;">Global</span></h1>
        <p style="font-size: 1.2rem; color: #64748b; margin-top: 10px;">你在全球财富金字塔的哪个位置？</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化会话状态
    if "result" not in st.session_state:
        st.session_state.result = None
    
    # 输入表单
    with st.container(border=True, height=300):
        col1, col2, col3, col4 = st.columns([1.5, 2, 2, 1.5])
        
        # 1. 国家选择
        with col1:
            st.markdown("### 居住国家/地区")
            country_code = st.selectbox(
                label="国家选择",
                options=list(COUNTRY_DATA.keys()),
                format_func=lambda x: COUNTRY_DATA[x]["name"],
                index=0  # 默认中国
            )
            current_country = COUNTRY_DATA[country_code]
        
        # 2. 年收入输入
        with col2:
            st.markdown("### 个人税前年收入")
            income = st.number_input(
                label="年收入",
                min_value=0,
                placeholder=f"例如: {current_country['medianIncome']}",
                format="%d"
            )
        
        # 3. 家庭资产输入
        with col3:
            st.markdown("### 家庭总净资产")
            wealth = st.number_input(
                label="家庭资产",
                min_value=0,
                placeholder=f"例如: {current_country['medianWealth']}",
                format="%d"
            )
        
        # 4. 提交按钮
        with col4:
            st.markdown("### 计算排名")
            calculate_btn = st.button(
                label="📊 查看排名",
                type="primary",
                use_container_width=True,
                disabled=income == 0 or wealth == 0
            )
    
    # 计算逻辑
    if calculate_btn:
        with st.spinner("计算中..."):
            # 计算收入百分位
            income_percentile = get_log_normal_percentile(
                value=income,
                median=current_country["medianIncome"],
                shape_parameter=current_country["incomeGini"]
            )
            
            # 计算财富百分位
            wealth_percentile = get_log_normal_percentile(
                value=wealth,
                median=current_country["medianWealth"],
                shape_parameter=current_country["wealthGini"]
            )
            
            # 保存结果到会话状态
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
        
        # 收入排名卡片（蓝色系）
        result_card(
            title="年收入排名",
            value=result["income_val"],
            percentile=result["income_percentile"],
            population=result["country"]["population"],
            icon="💼",
            color="#6366f1",  # 靛蓝色
            country_data=result["country"]
        )
        
        st.markdown("---")
        
        # 财富排名卡片（绿色系）
        result_card(
            title="家庭资产排名",
            value=result["wealth_val"],
            percentile=result["wealth_percentile"],
            population=result["country"]["population"],
            icon="💰",
            color="#10b981",  # 祖母绿
            country_data=result["country"]
        )
        
        # 免责声明
        st.markdown("""
        <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #f59e0b;">
            <strong>免责声明：</strong> 本工具仅供娱乐和参考。排名结果基于对数正态分布模型和公开宏观经济数据估算，
            非真实政府税务数据库查询。实际财富分布可能因地区差异、非正规经济等因素更复杂。
        </div>
        """, unsafe_allow_html=True)

# -------------------------- 运行应用 --------------------------
if __name__ == "__main__":
    # 修复：导入matplotlib.pyplot（之前遗漏）
    import matplotlib.pyplot as plt  # 关键修复！
    main()

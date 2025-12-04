import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import os
import textwrap # 关键库：用于清除多行字符串的缩进

# -------------------------- 0. 全局配置 --------------------------
st.set_page_config(
    page_title="WealthRank Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 1. CSS 样式 (折叠菜单核心) --------------------------
# 使用 textwrap.dedent 确保 CSS 不会被 Python 的缩进影响
css_code = textwrap.dedent("""
    <style>
    /* 全局字体 */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #ffffff;
    }
    
    /* 隐藏 Streamlit 默认头部 */
    header {visibility: hidden;}
    
    /* ----- 侧边栏样式 ----- */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 1. 菜单容器 */
    .nav-container {
        padding: 10px;
    }

    /* 2. 原生折叠组件 <details> 样式 */
    details {
        margin-bottom: 8px;
        border-radius: 8px;
        overflow: hidden;
        background: transparent;
        transition: background 0.2s;
    }
    
    /* 3. 标题行 <summary> 样式 */
    summary {
        list-style: none; /* 隐藏默认三角 */
        padding: 10px 12px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 8px;
        transition: all 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 隐藏 Webkit 默认三角 */
    summary::-webkit-details-marker {
        display: none;
    }
    
    /* 悬停效果 */
    summary:hover {
        background-color: #e2e8f0;
        color: #0f172a;
    }
    
    /* 自定义旋转箭头 */
    summary::after {
        content: '+';
        font-size: 1.1rem;
        font-weight: 400;
        transition: transform 0.3s;
    }
    
    /* 展开时的样式 */
    details[open] summary {
        color: #4f46e5; /* Indigo */
    }
    
    details[open] summary::after {
        transform: rotate(45deg); /* 旋转成 X */
    }
    
    /* 4. 子菜单内容区域 */
    .nav-content {
        padding: 5px 0 5px 10px; /* 缩进效果 */
        border-left: 2px solid #e2e8f0;
        margin-left: 12px;
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 5. 链接按钮样式 */
    .nav-link {
        display: flex;
        align-items: center;
        text-decoration: none;
        color: #475569;
        padding: 8px 12px;
        margin-bottom: 2px;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.15s;
    }
    
    .nav-link:hover {
        background-color: #eff6ff;
        color: #4f46e5;
        transform: translateX(3px);
    }
    
    .nav-icon {
        margin-right: 10px;
        font-size: 1rem;
        width: 20px;
        text-align: center;
    }
    
    /* 用户卡片 */
    .user-profile {
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
    }
    .avatar {
        width:

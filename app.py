import streamlit as st
import pandas as pd

# --- 設定網頁基本配置 ---
st.set_page_config(page_title="素食體態管理 App v2.2", page_icon="🥑")

# --- 初始化 Session State (暫存) ---
if 'food_log' not in st.session_state:
    st.session_state.food_log = []

st.title("🥑 素食體態管理 v2.2")
st.caption("更新：手動輸入現在可以自訂名稱了！")

# --- 1. 側邊欄：身體數據設定 ---
st.sidebar.header("⚙️ 1. 身體數據設定")

# 基本輸入
gender = st.sidebar.radio("生理性別", ["男", "女"])
age = st.sidebar.number_input("年齡", 18, 100, 30)
height = st.sidebar.number_input("身高 (cm)", 100, 250, 170)
weight = st.sidebar.number_input("目前體重 (kg)", 30.0, 200.0, 60.0)

# 自動計算出的 BMR (Mifflin-St Jeor 公式)
if gender == "男":
    auto_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    auto_bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

st.sidebar.divider()

# --- BMR 修正功能 ---
st.sidebar.subheader("🔥 基礎代謝率 (BMR)")
st.sidebar.write(f"系統估算：**{int(auto_bmr)}** kcal")

use_manual_bmr = st.sidebar.checkbox("我要手動輸入 BMR (例如依據 InBody)")

if use_manual_bmr:
    final_bmr = st.sidebar.number_input("請輸入你的 BMR 數值", 500, 3000, int(auto_bmr))
    st.sidebar.success(f"已採用手動數值：{final_bmr}")
else:
    final_bmr = auto_bmr

# 活動量與 TDEE
activity_level = st.sidebar.selectbox(
    "日常活動量",
    ("久坐 (
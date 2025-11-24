import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 設定網頁 ---
st.set_page_config(page_title="植感生活 Diary v3.2", page_icon="🌿", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2E7D32; text-align: center; font-weight: 700; padding-bottom: 10px; }
    .sub-header { font-family: 'Helvetica Neue', sans-serif; color: #558B2F; text-align: center; font-size: 1.1rem; margin-top: -15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🌿 植感生活 Diary</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">雲端紀錄 | 歷史回顧版</p>', unsafe_allow_html=True)

# =========================================
#  0. 資料庫連線 (Google Sheets)
# =========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_profile():
    try:
        df = conn.read(worksheet="Profile", ttl=0)
        return df.iloc[0] if not df.empty else None
    except: return None

def load_logs():
    try:
        df = conn.read(worksheet="Logs", ttl=0)
        if not df.empty and 'Date' in df.columns:
            # 確保日期格式統一為 YYYY-MM-DD
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        return df
    except: return pd.DataFrame(columns=["Date", "Food", "Calories", "Protein"])

def save_profile(data_dict):
    df = pd.DataFrame([data_dict])
    conn.update(worksheet="Profile", data=df)
    st.success("✅ 個人檔案已更新！")
    st.rerun()

def save_log(new_row_df):
    current_df = load_logs()
    updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
    conn.update(worksheet="Logs", data=updated_df)
    st.success("✅ 紀錄已上傳！")
    st.rerun()

# 載入資料
user_profile = load_profile()
df_logs = load_logs()

# 預設值處理
if user_profile is None:
    defaults = {"Height": 160, "Weight": 50, "Age": 25, "Gender": "女", "DietType": "全素 (Vegan)", "BodyFat": 25.0, "Activity": "輕度 (1-3天)", "TargetWeight": 48, "TargetDays": 30}
else:
    defaults = user_profile.to_dict()

# =========================================
#  1. 個人檔案 (隱藏式設定)
# =========================================
with st.expander("⚙️ 個人檔案設定", expanded=False):
    with st.form("profile_form"):
        diet_type = st.radio("素食類型", ["全素 (Vegan)", "蛋奶素", "鍋邊素"], index=["全素 (Vegan)", "蛋奶素", "鍋邊素"].index(defaults.get("DietType", "全素 (Vegan)")), horizontal=True)
        c1, c2 = st.columns(2)
        height = c1.number_input("身高", 100, 250, int(defaults.get("Height", 160)))
        weight = c2.number_input("體重", 30.0, 200.0, float(defaults.get("Weight", 50.0)))
        age = st.number_input("年齡", 10, 100, int(defaults.get("Age", 30)))
        gender = st.radio("性別", ["男", "女"], index=0 if defaults.get("Gender")=="男" else 1, horizontal=True)

        st.divider()
        body_fat = st.number_input("體脂率 (%)", 5.0, 60.0, float(defaults.get("BodyFat", 25.0)))
        activity = st.selectbox("運動強度", ["久坐 (無運動)", "輕度 (1-3天)", "中度 (3-5天)", "高度 (6-7天)"], index=["久坐 (無運動)", "輕度 (1-3天)", "中度 (3-5天)", "高度 (6-7天)"].index(defaults.get("Activity", "輕度 (1-3天)")))

        tc1, tc2 = st.columns(2)
        t_weight = tc1.number_input("目標體重", 30.0, 200.0, float(defaults.get("TargetWeight", weight)))
        t_days = tc2.number_input("預計天數", 7, 3
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 設定網頁 ---
st.set_page_config(page_title="植感生活 Diary v3.3", page_icon="🌿", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2E7D32; text-align: center; font-weight: 700; padding-bottom: 10px; }
    .sub-header { font-family: 'Helvetica Neue', sans-serif; color: #558B2F; text-align: center; font-size: 1.1rem; margin-top: -15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🌿 植感生活 Diary</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">雲端紀錄 | 懶人選單回歸版</p>', unsafe_allow_html=True)

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
        # 讀取資料 (ttl=0 代表不快取，每次抓最新)
        df = conn.read(worksheet="Logs", ttl=0)

        # --- 🛠️ 強制修復 A, B, C, D 問題 ---
        # 如果程式讀到的欄位是 A, B, C, D，代表它沒認出標題
        if list(df.columns) == ['A', 'B', 'C', 'D']:
            # 我們手動幫它改名
            df.columns = ["Date", "Food", "Calories", "Protein"]

            # 如果第一行內容剛好就是 "Date", "Food"... 代表那是標題列被當成資料了
            # 我們把它刪掉
            if not df.empty and str(df.iloc[0]["Date"]) == "Date":
                df = df.iloc[1:]

        # 再次檢查 (雙重保險)
        if 'Date' not in df.columns:
            # 如果還是找不到，回傳空表 (避免 App 崩潰)
            return pd.DataFrame(columns=["Date", "Food", "Calories", "Protein"])

        # 格式化日期
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            # 去除日期空白或錯誤的行
            df = df.dropna(subset=['Date'])

        return df
    except Exception as e:
        # 如果真的發生不可預期的錯誤，印出來方便除錯，但不讓 App 死掉
        st.error(f"資料庫讀取微恙 (但不影響操作): {e}")
        return pd.DataFrame(columns=["Date", "Food", "Calories", "Protein"])

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
        t_days = tc2.number_input("預計天數", 7, 365, int(defaults.get("TargetDays", 30)))

        if st.form_submit_button("💾 更新個人檔案"):
            save_profile({"Height": height, "Weight": weight, "Age": age, "Gender": gender, "DietType": diet_type, "BodyFat": body_fat, "Activity": activity, "TargetWeight": t_weight, "TargetDays": t_days})

# 代謝計算
lbm = weight * (1 - (body_fat / 100))
bmr = 370 + (21.6 * lbm)
tdee = bmr * {"久坐": 1.2, "輕度": 1.375, "中度": 1.55, "高度": 1.725}.get(activity[:2], 1.2)
diff = weight - t_weight
daily_target = tdee - ((diff * 7700) / t_days) if diff > 0 else tdee + ((abs(diff) * 7700) / t_days)
prot_goal = weight * 1.5

# =========================================
#  2. 今日儀表板 (讀取 database)
# =========================================
today_str = datetime.now().strftime('%Y-%m-%d')
today_data = df_logs[df_logs['Date'] == today_str] if not df_logs.empty else pd.DataFrame()
current_cal = today_data['Calories'].sum() if not today_data.empty else 0
current_prot = today_data['Protein'].sum() if not today_data.empty else 0

st.divider()
st.markdown(f"### 📊 今日概況 ({today_str})")
remaining = daily_target - current_cal
c1, c2 = st.columns(2)
c1.metric("剩餘熱量", int(remaining), f"目標 {int(daily_target)}")
c2.metric("蛋白質", f"{int(current_prot)}g", f"目標 {int(prot_goal)}g")
st.progress(min(current_cal / daily_target, 1.0) if daily_target > 0 else 0)

# =========================================
#  3. 飲食紀錄 (修正版：選單回歸！)
# =========================================
st.markdown("### 🍽️ 記一筆")
with st.expander("➕ 新增飲食", expanded=True):
    # 這裡就是把 V2.5 的選單邏輯加回來
    food_options = {
        "手動輸入": {"cal": 0, "prot": 0},
        "無糖豆漿 (400ml)": {"cal": 135, "prot": 14},
        "茶葉蛋 (1顆)": {"cal": 75, "prot": 7},
        "素食便當 (一般)": {"cal": 700, "prot": 20},
        "素食便當 (少油)": {"cal": 500, "prot": 18},
        "燙青菜": {"cal": 50, "prot": 2},
        "五穀飯 (一碗)": {"cal": 280, "prot": 5},
        "水果 (一份)": {"cal": 60, "prot": 1},
        "堅果 (一小把)": {"cal": 150, "prot": 4},
    }

    # 1. 先選種類
    f1, f2 = st.columns([2, 1])
    with f1:
        choice = st.selectbox("選擇食物", list(food_options.keys()))

    # 2. 根據選擇顯示輸入框
    custom_name = ""
    add_cal = 0
    add_prot = 0

    if choice == "手動輸入":
        custom_name = st.text_input("食物名稱", placeholder="例如：地瓜球")
        # 手動時，讓輸入框並排
        in1, in2 = st.columns(2)
        add_cal = in1.number_input("熱量 (kcal)", 0, 3000, 0)
        add_prot = in2.number_input("蛋白質 (g)", 0, 200, 0)
    else:
        # 選單時，自動帶入數值
        vals = food_options[choice]
        in1, in2 = st.columns(2)
        # 這裡設定 value=vals[...] 讓它自動填入
        add_cal = in1.number_input("熱量 (kcal)", value=vals["cal"])
        add_prot = in2.number_input("蛋白質 (g)", value=vals["prot"])

    if st.button("上傳雲端", use_container_width=True):
        # 決定最終要存的名字
        final_name = custom_name if choice == "手動輸入" else choice

        # 只有名字不為空才上傳
        if final_name:
            save_log(pd.DataFrame([{
                "Date": today_str,
                "Food": final_name,
                "Calories": add_cal,
                "Protein": add_prot
            }]))
        else:
            st.warning("請輸入食物名稱")

# 顯示今日清單
if not today_data.empty:
    st.caption("今日明細：")
    st.dataframe(today_data[["Food", "Calories", "Protein"]], use_container_width=True, hide_index=True)

# =========================================
#  4. 📅 歷史紀錄查詢
# =========================================
st.divider()
st.markdown("### 📅 歷史時光機")

col_date, col_info = st.columns([1, 2])
with col_date:
    query_date = st.date_input("選擇日期查看", datetime.now())
    query_date_str = query_date.strftime('%Y-%m-%d')

if not df_logs.empty:
    history_data = df_logs[df_logs['Date'] == query_date_str]
    with col_info:
        if not history_data.empty:
            h_cal = history_data['Calories'].sum()
            h_prot = history_data['Protein'].sum()
            st.info(f"**{query_date_str} 總結**\n\n🔥 熱量：{h_cal} kcal　|　💪 蛋白質：{h_prot} g")
        else:
            st.warning(f"{query_date_str} 沒有紀錄喔！")

    if not history_data.empty:
        st.dataframe(history_data[["Food", "Calories", "Protein"]], use_container_width=True, hide_index=True)
else:
    st.write("資料庫目前是空的。")

# =========================================
#  5. 食譜推薦
# =========================================
st.divider()
st.markdown(f"### 🥑 靈感廚房")
rec_type = "輕盈低卡" if remaining < 400 else "營養均衡"
rec_text = ""
if diet_type == "全素 (Vegan)":
    rec_text = "鷹嘴豆藜麥沙拉" if rec_type == "輕盈低卡" else "天貝炒時蔬定食"
elif diet_type == "蛋奶素":
    rec_text = "希臘優格水果杯" if rec_type == "輕盈低卡" else "起司蔬菜烘蛋"
else:
    rec_text = "超商地瓜+無糖豆漿" if rec_type == "輕盈低卡" else "潤餅(去糖粉)+茶葉蛋"

st.success(f"💡 依據你的 **{diet_type}** 偏好，推薦晚餐嘗試：**{rec_text}** ({rec_type})")
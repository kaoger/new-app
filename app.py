import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 設定網頁 ---
st.set_page_config(page_title="植感生活 Diary v4.3", page_icon="🌿", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2E7D32; text-align: center; font-weight: 700; padding-bottom: 10px; }
    .sub-header { font-family: 'Helvetica Neue', sans-serif; color: #558B2F; text-align: center; font-size: 1.1rem; margin-top: -15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🌿 植感生活 Diary</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">雲端紀錄 | 流量優化版</p>', unsafe_allow_html=True)

# =========================================
#  0. 資料庫連線與邏輯 (加上快取機制)
# =========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# ⭐️ 修改點 1: 加入 @st.cache_data(ttl=5)
# 這代表 5 秒內重複呼叫這個函式，不會去連 Google，直接用記憶體的資料
@st.cache_data(ttl=5)
def load_all_profiles():
    try:
        # 這裡 ttl 不需要設為 0 了，交給 st.cache_data 管理
        return conn.read(worksheet="Profile")
    except:
        return pd.DataFrame(columns=["Name", "Height", "Weight", "Age", "Gender", "DietType", "BodyFat", "Activity", "TargetWeight", "TargetDays"])

# ⭐️ 修改點 2: 加入 @st.cache_data(ttl=5)
@st.cache_data(ttl=5)
def load_all_logs():
    try:
        df = conn.read(worksheet="Logs")
        # 欄位除錯
        if list(df.columns) == ['A', 'B', 'C', 'D', 'E']:
            df.columns = ["Name", "Date", "Food", "Calories", "Protein"]
            if not df.empty and str(df.iloc[0]["Name"]) == "Name": df = df.iloc[1:]

        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df = df.dropna(subset=['Date'])
        return df
    except:
        return pd.DataFrame(columns=["Name", "Date", "Food", "Calories", "Protein"])

# 儲存 Profile
def save_profile(user_name, data_dict):
    try:
        # 為了要寫入，我們還是要拿一次最新的 (不使用快取)
        # 這裡用 conn.read(ttl=0) 確保拿到最新狀態以免覆蓋錯誤
        df = conn.read(worksheet="Profile", ttl=0)

        data_dict["Name"] = user_name
        if user_name in df["Name"].values:
            idx = df[df["Name"] == user_name].index[0]
            for key, val in data_dict.items():
                df.at[idx, key] = val
        else:
            new_row = pd.DataFrame([data_dict])
            df = pd.concat([df, new_row], ignore_index=True)

        conn.update(worksheet="Profile", data=df)

        # ⭐️ 修改點 3: 寫入後，強制清除快取，這樣下次讀取才會是新的
        load_all_profiles.clear()
        st.success(f"✅ {user_name} 的檔案已更新！")
        st.rerun()
    except Exception as e:
        st.error(f"儲存失敗，請稍後再試: {e}")

# 儲存 Log
def save_log(user_name, log_dict):
    try:
        df = conn.read(worksheet="Logs", ttl=0) # 寫入前讀取最新
        log_dict["Name"] = user_name
        new_row = pd.DataFrame([log_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="Logs", data=df)

        # ⭐️ 修改點 4: 清除快取
        load_all_logs.clear()
        st.success("✅ 紀錄已上傳！")
        st.rerun()
    except Exception as e:
        st.error(f"儲存失敗，請稍後再試: {e}")

# 刪除 Log
def delete_logs(indices_to_delete):
    try:
        df = conn.read(worksheet="Logs", ttl=0) # 寫入前讀取最新
        df = df.drop(indices_to_delete)
        conn.update(worksheet="Logs", data=df)

        # ⭐️ 修改點 5: 清除快取
        load_all_logs.clear()
        st.success("✅ 已刪除選取項目！")
        st.rerun()
    except Exception as e:
        st.error(f"刪除失敗: {e}")

# =========================================
#  1. 登入區
# =========================================
st.info("👋 歡迎！請輸入你的暱稱來讀取專屬資料。")
user_name = st.text_input("👤 請輸入你的暱稱 (例如：小明)", key="login_name")

if not user_name:
    st.warning("請先輸入暱稱才能開始使用喔！")
    st.stop()

# 讀取資料 (這裡會使用快取，大幅減少 API 呼叫)
all_profiles = load_all_profiles()
all_logs = load_all_logs()

user_profile = all_profiles[all_profiles["Name"] == user_name] if not all_profiles.empty else pd.DataFrame()
user_logs = all_logs[all_logs["Name"] == user_name] if not all_logs.empty else pd.DataFrame()

if user_profile.empty:
    st.caption(f"✨ 嗨 {user_name}，這是你第一次使用，請先設定個人檔案。")
    defaults = {"Height": 160, "Weight": 50, "Age": 25, "Gender": "女", "DietType": "全素 (Vegan)", "BodyFat": 25.0, "Activity": "輕度 (1-3天)", "TargetWeight": 48, "TargetDays": 30}
else:
    defaults = user_profile.iloc[0].to_dict()

current_diet_type = defaults.get("DietType", "全素 (Vegan)")

# =========================================
#  2. 個人檔案設定
# =========================================
with st.expander(f"⚙️ {user_name} 的檔案設定", expanded=user_profile.empty):
    with st.form("profile_form"):
        diet_type = st.radio("素食類型", ["全素 (Vegan)", "蛋奶素", "鍋邊素"], index=["全素 (Vegan)", "蛋奶素", "鍋邊素"].index(current_diet_type), horizontal=True)
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

        if st.form_submit_button("💾 儲存檔案"):
            save_profile(user_name, {"Height": height, "Weight": weight, "Age": age, "Gender": gender, "DietType": diet_type, "BodyFat": body_fat, "Activity": activity, "TargetWeight": t_weight, "TargetDays": t_days})

# 代謝計算
lbm = weight * (1 - (body_fat / 100))
bmr = 370 + (21.6 * lbm)
tdee = bmr * {"久坐": 1.2, "輕度": 1.375, "中度": 1.55, "高度": 1.725}.get(activity[:2], 1.2)
diff = weight - t_weight
daily_target = tdee - ((diff * 7700) / t_days) if diff > 0 else tdee + ((abs(diff) * 7700) / t_days)
prot_goal = weight * 1.5

# =========================================
#  3. 今日儀表板
# =========================================
today_str = datetime.now().strftime('%Y-%m-%d')
today_data = user_logs[user_logs['Date'] == today_str] if not user_logs.empty else pd.DataFrame()
current_cal = today_data['Calories'].sum() if not today_data.empty else 0
current_prot = today_data['Protein'].sum() if not today_data.empty else 0

st.divider()
st.markdown(f"### 📊 {user_name} 的今日概況")
remaining = daily_target - current_cal
c1, c2 = st.columns(2)
c1.metric("剩餘熱量", int(remaining), f"目標 {int(daily_target)}")
c2.metric("蛋白質", f"{int(current_prot)}g", f"目標 {int(prot_goal)}g")
st.progress(min(current_cal / daily_target, 1.0) if daily_target > 0 else 0)

# =========================================
#  4. 飲食紀錄
# =========================================
st.markdown("### 🍽️ 飲食紀錄")

with st.expander("➕ 新增飲食", expanded=True):
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
    f1, f2 = st.columns([2, 1])
    with f1: choice = st.selectbox("選擇食物", list(food_options.keys()))

    custom_name = ""; add_cal = 0; add_prot = 0
    if choice == "手動輸入":
        custom_name = st.text_input("食物名稱", placeholder="例如：紅豆餅")
        in1, in2 = st.columns(2)
        add_cal = in1.number_input("熱量", 0, 3000, 0)
        add_prot = in2.number_input("蛋白質", 0, 200, 0)
    else:
        vals = food_options[choice]
        in1, in2 = st.columns(2)
        add_cal = in1.number_input("熱量", value=vals["cal"])
        add_prot = in2.number_input("蛋白質", value=vals["prot"])

    if st.button("上傳紀錄", use_container_width=True):
        final_name = custom_name if choice == "手動輸入" else choice
        if final_name:
            save_log(user_name, {"Date": today_str, "Food": final_name, "Calories": add_cal, "Protein": add_prot})
        else: st.warning("請輸入名稱")

# 刪除功能
if not today_data.empty:
    with st.expander("🗑️ 管理/刪除今日紀錄", expanded=False):
        st.write("請勾選你想刪除的項目：")
        delete_list = []
        for index, row in today_data.iterrows():
            label = f"{row['Food']} (熱量: {row['Calories']} / 蛋白: {row['Protein']})"
            if st.checkbox(label, key=f"del_{index}"):
                delete_list.append(index)

        if delete_list:
            if st.button(f"確認刪除選取的 {len(delete_list)} 筆資料", type="primary", use_container_width=True):
                delete_logs(delete_list)

    st.caption("今日明細：")
    st.dataframe(today_data[["Food", "Calories", "Protein"]], use_container_width=True, hide_index=True)

# =========================================
#  5. 歷史回顧
# =========================================
st.divider()
st.markdown("### 📅 歷史回顧")
q_date = st.date_input("選擇日期", datetime.now()).strftime('%Y-%m-%d')
if not user_logs.empty:
    h_data = user_logs[user_logs['Date'] == q_date]
    if not h_data.empty:
        st.info(f"熱量：{h_data['Calories'].sum()} | 蛋白：{h_data['Protein'].sum()}")
        st.dataframe(h_data[["Food", "Calories", "Protein"]], use_container_width=True, hide_index=True)
    else: st.warning("該日無紀錄")

# =========================================
#  6. 靈感廚房
# =========================================
st.divider()
st.markdown(f"### 🥑 靈感廚房 ({current_diet_type})")

menus = {
    "全素 (Vegan)": {
        "low": {"早": {"n": "奇亞籽豆漿布丁", "d": "250 kcal", "r": "豆漿+奇亞籽放隔夜"}, "午": {"n": "鷹嘴豆藜麥沙拉", "d": "350 kcal", "r": "鷹嘴豆、藜麥、甜椒、檸檬油醋"}, "晚": {"n": "味噌豆腐蔬菜湯", "d": "200 kcal", "r": "板豆腐、海帶芽、味噌湯"}},
        "high": {"早": {"n": "酪梨全麥吐司", "d": "400 kcal", "r": "全麥吐司、酪梨泥、堅果"}, "午": {"n": "天貝炒時蔬", "d": "500 kcal", "r": "天貝煎金黃、花椰菜拌炒"}, "晚": {"n": "紅燒豆腐煲", "d": "450 kcal", "r": "板豆腐紅燒、香菇、紅蘿蔔"}}
    },
    "蛋奶素": {
        "low": {"早": {"n": "希臘優格杯", "d": "250 kcal", "r": "無糖優格、藍莓"}, "午": {"n": "涼拌雞絲(素)蒟蒻麵", "d": "350 kcal", "r": "蒟蒻麵、素雞絲、和風醬"}, "晚": {"n": "番茄蔬菜蛋花湯", "d": "200 kcal", "r": "番茄、蛋花、小白菜"}},
        "high": {"早": {"n": "起司蔬菜烘蛋", "d": "400 kcal", "r": "兩顆蛋、起司、菠菜烘烤"}, "午": {"n": "松露野菇義大利麵", "d": "550 kcal", "r": "義大利麵、鮮奶油、野菇"}, "晚": {"n": "歐姆蛋咖哩飯", "d": "500 kcal", "r": "歐姆蛋、素食咖哩"}}
    },
    "鍋邊素": {
        "low": {"早": {"n": "超商地瓜+茶葉蛋", "d": "280 kcal", "r": "蒸地瓜、茶葉蛋"}, "午": {"n": "關東煮輕食餐", "d": "350 kcal", "r": "白蘿蔔、娃娃菜、滷蛋(不喝湯)"}, "晚": {"n": "自助餐夾菜(去肉)", "d": "300 kcal", "r": "深色蔬菜、豆腐、不淋肉燥"}},
        "high": {"早": {"n": "蛋餅+無糖豆漿", "d": "400 kcal", "r": "蔬菜蛋餅、無糖豆漿"}, "午": {"n": "素食水餃餐", "d": "550 kcal", "r": "素水餃10顆、燙青菜"}, "晚": {"n": "潤餅(微糖)", "d": "450 kcal", "r": "多加高麗菜、去肥肉、少糖粉"}}
    }
}
menu_type = "low" if (remaining < 400 and daily_target > 0) else "high"
safe_diet_type = current_diet_type if current_diet_type in menus else "全素 (Vegan)"
current_menu = menus[safe_diet_type][menu_type]

if menu_type == "low":
    st.info(f"💡 今日額度較少，推薦 **{safe_diet_type} - 輕盈低卡餐**：")
else:
    st.success(f"💡 今日熱量充足，推薦 **{safe_diet_type} - 營養均衡餐**：")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### ☀️ 早餐")
    st.write(f"**{current_menu['早']['n']}**")
    st.caption(current_menu['早']['d'])
    with st.expander("作法"): st.write(current_menu['早']['r'])
with col2:
    st.markdown("#### 🍱 午餐")
    st.write(f"**{current_menu['午']['n']}**")
    st.caption(current_menu['午']['d'])
    with st.expander("作法"): st.write(current_menu['午']['r'])
with col3:
    st.markdown("#### 🌙 晚餐")
    st.write(f"**{current_menu['晚']['n']}**")
    st.caption(current_menu['晚']['d'])
    with st.expander("作法"): st.write(current_menu['晚']['r'])

st.divider()
st.caption("Note: V4.3 - 流量優化版 (Cache Enabled)")
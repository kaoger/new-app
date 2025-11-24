import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 設定網頁 ---
st.set_page_config(page_title="植感生活 Diary v5.1", page_icon="🌿", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2E7D32; text-align: center; font-weight: 700; padding-bottom: 10px; }
    .sub-header { font-family: 'Helvetica Neue', sans-serif; color: #558B2F; text-align: center; font-size: 1.1rem; margin-top: -15px; margin-bottom: 20px; }
    /* 優化 Metric 顯示 */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🌿 植感生活 Diary</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">視覺優化版 | 紅字警示 & 橫向圖表</p>', unsafe_allow_html=True)

# =========================================
#  0. 資料庫連線
# =========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取 Profile
@st.cache_data(ttl=5)
def load_all_profiles():
    try: return conn.read(worksheet="Profile")
    except: return pd.DataFrame(columns=["Name", "Height", "Weight", "Age", "Gender", "DietType", "BodyFat", "Activity", "TargetWeight", "TargetDays"])

# 讀取 Logs
@st.cache_data(ttl=5)
def load_all_logs():
    try:
        df = conn.read(worksheet="Logs")
        if len(df.columns) >= 6:
            if list(df.columns)[0] == 'A':
                df.columns = ["Name", "Date", "Meal", "Food", "Calories", "Protein"]

        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df = df.dropna(subset=['Date'])
        return df
    except:
        return pd.DataFrame(columns=["Name", "Date", "Meal", "Food", "Calories", "Protein"])

# 讀取體重歷史
@st.cache_data(ttl=5)
def load_weight_history():
    try:
        df = conn.read(worksheet="WeightHistory")
        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return df
    except:
        return pd.DataFrame(columns=["Name", "Date", "Weight", "BodyFat"])

# 儲存與刪除函式 (與 V5.0 相同)
def save_profile(user_name, data_dict):
    try:
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
        load_all_profiles.clear()
        st.success(f"✅ {user_name} 的檔案已更新！")
        st.rerun()
    except Exception as e: st.error(f"儲存失敗: {e}")

def save_log(user_name, log_dict):
    try:
        df = conn.read(worksheet="Logs", ttl=0)
        log_dict["Name"] = user_name
        new_row = pd.DataFrame([log_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="Logs", data=df)
        load_all_logs.clear()
        st.success("✅ 紀錄已上傳！")
        st.rerun()
    except Exception as e: st.error(f"儲存失敗: {e}")

def delete_logs(indices_to_delete):
    try:
        df = conn.read(worksheet="Logs", ttl=0)
        df = df.drop(indices_to_delete)
        conn.update(worksheet="Logs", data=df)
        load_all_logs.clear()
        st.success("✅ 已刪除！")
        st.rerun()
    except Exception as e: st.error(f"刪除失敗: {e}")

def save_weight_log(user_name, weight, body_fat):
    try:
        df = conn.read(worksheet="WeightHistory", ttl=0)
        today = datetime.now().strftime('%Y-%m-%d')
        new_row = pd.DataFrame([{"Name": user_name, "Date": today, "Weight": weight, "BodyFat": body_fat}])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="WeightHistory", data=df)

        p_df = conn.read(worksheet="Profile", ttl=0)
        if user_name in p_df["Name"].values:
            idx = p_df[p_df["Name"] == user_name].index[0]
            p_df.at[idx, "Weight"] = weight
            p_df.at[idx, "BodyFat"] = body_fat
            conn.update(worksheet="Profile", data=p_df)
            load_all_profiles.clear()

        load_weight_history.clear()
        st.success("✅ 體重紀錄已更新！")
        st.rerun()
    except Exception as e: st.error(f"儲存失敗: {e}")

# =========================================
#  1. 智慧登入區
# =========================================
query_params = st.query_params
default_user = query_params.get("name", "")

if not default_user:
    st.info("👋 歡迎！輸入暱稱後，系統會自動記憶。")

user_name = st.text_input("👤 請輸入你的暱稱", value=default_user, key="login_name")

if not user_name:
    st.warning("請輸入暱稱開始使用")
    st.stop()
else:
    if user_name != default_user:
        st.query_params["name"] = user_name

# 讀取資料
all_profiles = load_all_profiles()
all_logs = load_all_logs()
all_weights = load_weight_history()

user_profile = all_profiles[all_profiles["Name"] == user_name] if not all_profiles.empty else pd.DataFrame()
user_logs = all_logs[all_logs["Name"] == user_name] if not all_logs.empty else pd.DataFrame()
user_weights = all_weights[all_weights["Name"] == user_name] if not all_weights.empty else pd.DataFrame()

if user_profile.empty:
    st.caption(f"✨ 嗨 {user_name}，初次見面！")
    defaults = {"Height": 160, "Weight": 50, "Age": 25, "Gender": "女", "DietType": "全素 (Vegan)", "BodyFat": 25.0, "Activity": "輕度 (1-3天)", "TargetWeight": 48, "TargetDays": 30}
else:
    defaults = user_profile.iloc[0].to_dict()

current_diet_type = defaults.get("DietType", "全素 (Vegan)")

# =========================================
#  2. 分頁導航
# =========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 今日概況", "🍽️ 飲食紀錄", "📉 體態追蹤", "⚙️ 設定"])

# --- TAB 4: 設定 ---
with tab4:
    with st.form("profile_form"):
        diet_type = st.radio("素食類型", ["全素 (Vegan)", "蛋奶素", "鍋邊素"], index=["全素 (Vegan)", "蛋奶素", "鍋邊素"].index(current_diet_type), horizontal=True)
        c1, c2 = st.columns(2)
        height = c1.number_input("身高", 100, 250, int(defaults.get("Height", 160)))
        weight = c2.number_input("體重", 30.0, 200.0, float(defaults.get("Weight", 50.0)))
        age = st.number_input("年齡", 10, 100, int(defaults.get("Age", 30)))
        gender = st.radio("性別", ["男", "女"], index=0 if defaults.get("Gender")=="男" else 1, horizontal=True)
        st.divider()
        body_fat = st.number_input("體脂率 (%)", 5.0, 60.0, float(defaults.get("BodyFat", 25.0)), help="如果不確定，可以先填 25 (女) 或 18 (男)。")
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

# --- TAB 1: 今日概況 (視覺優化區) ---
with tab1:
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_data = user_logs[user_logs['Date'] == today_str] if not user_logs.empty else pd.DataFrame()
    current_cal = today_data['Calories'].sum() if not today_data.empty else 0
    current_prot = today_data['Protein'].sum() if not today_data.empty else 0

    st.markdown(f"### 📅 {today_str}")

    remaining = daily_target - current_cal

    col_a, col_b = st.columns(2)

    # --- 1. 熱量顯示邏輯 (HTML 美化) ---
    with col_a:
        if remaining >= 0:
            # 沒超標：顯示正常樣式
            st.metric("剩餘熱量", f"{int(remaining)}", f"目標 {int(daily_target)}")
            if current_cal > 0:
                st.caption("✅ 熱量控制良好")
            else:
                st.caption("🍵 還沒開始吃喔")
        else:
            # 超標：顯示紅色警告樣式
            st.markdown(f"""
            <div style="text-align: left;">
                <p style="font-size: 14px; margin-bottom: 0px; color: #555;">剩餘熱量</p>
                <p style="font-size: 32px; color: #D32F2F; font-weight: bold; margin: 0px;">超過 {abs(int(remaining))}</p>
                <p style="font-size: 12px; color: #888;">目標 {int(daily_target)}</p>
                <p style="color: #D32F2F; font-weight: bold; font-size: 14px;">⚠️ 熱量超標</p>
            </div>
            """, unsafe_allow_html=True)

    # --- 2. 蛋白質顯示邏輯 ---
    with col_b:
        # 如果蛋白質達標，顯示恭喜
        if current_prot >= prot_goal:
            st.markdown(f"""
            <div style="text-align: left;">
                <p style="font-size: 14px; margin-bottom: 0px; color: #555;">蛋白質</p>
                <p style="font-size: 32px; color: #2E7D32; font-weight: bold; margin: 0px;">{int(current_prot)}g</p>
                <p style="font-size: 12px; color: #888;">目標 {int(prot_goal)}g</p>
                <p style="color: #2E7D32; font-weight: bold; font-size: 14px;">🎉 恭喜達標！</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("蛋白質", f"{int(current_prot)}g", f"目標 {int(prot_goal)}g")
            st.caption(f"💪 再加油 {int(prot_goal - current_prot)}g")

    st.progress(min(current_cal / daily_target, 1.0) if daily_target > 0 else 0)

    # --- 3. 圖表優化 (橫向 Bar Chart) ---
    if not today_data.empty and 'Meal' in today_data.columns:
        st.write("") # 空一行
        st.write("▼ 各餐熱量分佈")
        meal_stats = today_data.groupby('Meal')['Calories'].sum().reset_index()

        # 使用 horizontal=True 讓圖表橫過來，文字就不會歪頭了
        st.bar_chart(
            meal_stats,
            x="Meal",
            y="Calories",
            horizontal=True,
            color="#1E88E5"
        )
    else:
        st.info("尚未有飲食紀錄，快去「🍽️ 飲食紀錄」記一筆吧！")

# --- TAB 2: 飲食紀錄 ---
with tab2:
    with st.expander("➕ 新增飲食", expanded=True):
        meal_type = st.radio("時段", ["早餐", "午餐", "晚餐", "點心/宵夜"], horizontal=True)

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
                save_log(user_name, {
                    "Date": today_str,
                    "Meal": meal_type,
                    "Food": final_name,
                    "Calories": add_cal,
                    "Protein": add_prot
                })
            else: st.warning("請輸入名稱")

    # 刪除管理
    if not today_data.empty:
        with st.expander("🗑️ 管理今日紀錄", expanded=False):
            st.write("勾選刪除：")
            delete_list = []
            for index, row in today_data.iterrows():
                m_label = row['Meal'] if 'Meal' in row else '未知'
                label = f"[{m_label}] {row['Food']} ({row['Calories']} kcal)"
                if st.checkbox(label, key=f"del_{index}"):
                    delete_list.append(index)
            if delete_list:
                if st.button("確認刪除", type="primary"): delete_logs(delete_list)

        st.caption("今日明細：")
        show_cols = ["Meal", "Food", "Calories", "Protein"] if 'Meal' in today_data.columns else ["Food", "Calories", "Protein"]
        st.dataframe(today_data[show_cols], use_container_width=True, hide_index=True)

# --- TAB 3: 體態追蹤 ---
with tab3:
    st.markdown("### 📉 體重變化趨勢")
    with st.expander("⚖️ 紀錄今日體重 (每週/每日)", expanded=False):
        w_in = st.number_input("今日體重 (kg)", 30.0, 200.0, float(weight))
        bf_in = st.number_input("今日體脂 (%)", 5.0, 60.0, float(body_fat))
        if st.button("更新體重紀錄"):
            save_weight_log(user_name, w_in, bf_in)

    if not user_weights.empty:
        chart_data = user_weights.copy()
        chart_data['Date'] = pd.to_datetime(chart_data['Date'])
        chart_data = chart_data.sort_values('Date')

        st.markdown("##### 體重走勢")
        st.line_chart(chart_data, x='Date', y='Weight', color='#2E7D32')
        st.markdown("##### 體脂率走勢")
        st.line_chart(chart_data, x='Date', y='BodyFat', color='#558B2F')
        st.caption("最近 5 筆紀錄：")
        st.dataframe(chart_data.tail(5), use_container_width=True, hide_index=True)
    else:
        st.info("目前還沒有體重紀錄，快輸入第一筆吧！")

st.divider()
st.caption("Note: V5.1 - 視覺優化版")
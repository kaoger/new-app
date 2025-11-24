import streamlit as st
import pandas as pd

# --- 設定網頁基本配置 ---
st.set_page_config(page_title="素食體態管理 App v2.3", page_icon="🥑")

# --- 初始化 Session State (暫存) ---
if 'food_log' not in st.session_state:
    st.session_state.food_log = []

st.title("🥑 素食體態管理 v2.3")

# --- 1. 核心數據設定 (改用 Expander，手機更友善) ---
# 預設展開，設定完使用者可以自己收起來
with st.expander("⚙️ 點擊設定身體數據 (InBody/運動量)", expanded=True):
    st.caption("輸入體脂率可獲得更精準的代謝計算")

    col1, col2 = st.columns(2)
    gender = col1.radio("生理性別", ["男", "女"], horizontal=True)
    age = col2.number_input("年齡", 18, 100, 30)

    col3, col4 = st.columns(2)
    height = col3.number_input("身高 (cm)", 100, 250, 170)
    weight = col4.number_input("體重 (kg)", 30.0, 200.0, 60.0)

    # --- 新增功能：體脂率輸入 ---
    use_bodyfat = st.checkbox("我有體脂率數據 (InBody)")

    calculated_bmr = 0
    if use_bodyfat:
        body_fat = st.number_input("輸入體脂率 (%)", 3.0, 50.0, 20.0, step=0.1)
        # Katch-McArdle 公式 (370 + 21.6 * 去脂體重)
        lbm = weight * (1 - (body_fat / 100))
        calculated_bmr = 370 + (21.6 * lbm)
        st.info(f"依據體脂率計算，你的去脂體重為 {lbm:.1f} kg")
    else:
        # Mifflin-St Jeor 公式
        if gender == "男":
            calculated_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            calculated_bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # --- 手動 BMR 修正 (保留你的需求) ---
    st.divider()
    use_manual_bmr = st.checkbox(f"系統估算 BMR 為 {int(calculated_bmr)}，我要手動修正")

    if use_manual_bmr:
        final_bmr = st.number_input("手動輸入 BMR", 500, 5000, int(calculated_bmr))
    else:
        final_bmr = calculated_bmr

    # --- 新增功能：運動頻率選擇 ---
    st.divider()
    activity_option = st.selectbox(
        "每週運動強度",
        (
            "久坐 (辦公室/無運動)",
            "輕度 (每週運動 1-3 天)",
            "中度 (每週運動 3-5 天)",
            "高度 (每週運動 6-7 天)",
            "超高度 (勞力工作/選手訓練)"
        )
    )

    # 對應的 TDEE 係數
    multipliers = {
        "久坐": 1.2,
        "輕度": 1.375,
        "中度": 1.55,
        "高度": 1.725,
        "超高度": 1.9
    }
    # 抓取選項的前兩個字來對應係數
    act_key = activity_option[:2]
    # 處理 "久坐" 是兩個字，其他是 "輕度" 等等，稍微做個防呆
    if "久坐" in activity_option: act_key = "久坐"
    elif "輕度" in activity_option: act_key = "輕度"
    elif "中度" in activity_option: act_key = "中度"
    elif "高度" in activity_option: act_key = "高度"
    else: act_key = "超高度"

    tdee = final_bmr * multipliers[act_key]

    st.write(f"📊 你的每日總消耗 (TDEE): **{int(tdee)} kcal**")

# --- 2. 目標設定 ---
with st.expander("🎯 設定減重/增重目標", expanded=False):
    c1, c2 = st.columns(2)
    target_weight = c1.number_input("目標體重", 30.0, 200.0, weight)
    target_days = c2.number_input("預計天數", 7, 365, 30)

    weight_diff = weight - target_weight
    if weight_diff > 0:
        # 減重
        daily_deficit = (weight_diff * 7700) / target_days
        daily_target = tdee - daily_deficit
        msg_type = "lose"
    elif weight_diff < 0:
        # 增重
        daily_surplus = (abs(weight_diff) * 7700) / target_days
        daily_target = tdee + daily_surplus
        msg_type = "gain"
    else:
        # 維持
        daily_target = tdee
        msg_type = "maintain"

protein_goal = weight * 1.5 # 簡易建議

# --- 儀表板 ---
st.divider()
st.subheader("今日概況")
total_cal = sum([item['熱量'] for item in st.session_state.food_log])
total_prot = sum([item['蛋白質'] for item in st.session_state.food_log])
remaining = daily_target - total_cal

col_a, col_b = st.columns(2)
col_a.metric("剩餘熱量", f"{int(remaining)}", f"目標 {int(daily_target)}")
col_b.metric("蛋白質進度", f"{int(total_prot)}g", f"目標 {int(protein_goal)}g")

st.progress(min(total_cal / daily_target, 1.0) if daily_target > 0 else 0)

# --- 3. 飲食紀錄 (手機友善版) ---
st.divider()
st.subheader("🍽️ 新增飲食")

# 簡易資料庫
food_options = {
    "手動輸入": {"cal": 0, "prot": 0},
    "無糖豆漿 (400ml)": {"cal": 135, "prot": 14},
    "茶葉蛋 (1顆)": {"cal": 75, "prot": 7},
    "素食便當 (一般)": {"cal": 700, "prot": 20},
    "素食便當 (減飯/少油)": {"cal": 500, "prot": 18},
    "燙青菜 (不加肉燥)": {"cal": 50, "prot": 2},
    "五穀飯 (一碗)": {"cal": 280, "prot": 5},
    "水果 (一份)": {"cal": 60, "prot": 1},
    "堅果 (一小把)": {"cal": 150, "prot": 4},
}

# 手機上 columns 太多會擠在一起，這裡改用簡單的上下排列，或是 2:1
f1, f2 = st.columns([2, 1])
with f1:
    choice = st.selectbox("選擇食物", list(food_options.keys()))

custom_name = ""
add_cal = 0
add_prot = 0

if choice == "手動輸入":
    custom_name = st.text_input("食物名稱", "自訂食物")
    # 用 columns 讓輸入框並排，節省垂直空間
    in1, in2 = st.columns(2)
    add_cal = in1.number_input("熱量 (kcal)", 0, 3000, 0)
    add_prot = in2.number_input("蛋白質 (g)", 0, 200, 0)
else:
    vals = food_options[choice]
    in1, in2 = st.columns(2)
    add_cal = in1.number_input("熱量", value=vals["cal"])
    add_prot = in2.number_input("蛋白質", value=vals["prot"])

if st.button("➕ 加入紀錄", use_container_width=True):
    final_name = custom_name if choice == "手動輸入" else choice
    st.session_state.food_log.append({
        "食物": final_name,
        "熱量": add_cal,
        "蛋白質": add_prot
    })
    st.success(f"已加入 {final_name}")
    st.rerun()

# --- 顯示清單 ---
if st.session_state.food_log:
    st.write("---")
    df = pd.DataFrame(st.session_state.food_log)
    # 手機看 Table 有時候會跑版，這裡用 dataframe 顯示比較自動適應，或者用單純文字列表
    st.dataframe(df, use_container_width=True)

    # 下載與清除
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "📥 下載 CSV",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name='diet_log.csv',
            mime='text/csv',
            use_container_width=True
        )
    with d2:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.food_log = []
            st.rerun()
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
    ("久坐 (BMR x 1.2)", "輕度 (BMR x 1.375)", "中度 (BMR x 1.55)", "高度 (BMR x 1.725)"),
    index=1
)
multipliers = {"久坐": 1.2, "輕度": 1.375, "中度": 1.55, "高度": 1.725}
act_key = activity_level.split(" ")[0]
tdee = final_bmr * multipliers[act_key]

# --- 2. 目標設定 ---
with st.expander("🎯 2. 設定減重目標", expanded=True):
    col1, col2 = st.columns(2)
    target_weight = col1.number_input("目標體重 (kg)", 30.0, 200.0, weight - 2.0)
    target_days = col2.number_input("預計天數", 7, 365, 30)

    weight_diff = weight - target_weight
    if weight_diff > 0:
        daily_deficit = (weight_diff * 7700) / target_days
        daily_target = tdee - daily_deficit
        st.info(f"為了在 {target_days} 天減去 {weight_diff:.1f} kg，每日建議攝取：**{int(daily_target)}** kcal")
    else:
        daily_target = tdee
        st.success("維持體重模式")

protein_goal = weight * 1.5

# --- 3. 飲食紀錄 (修正版：可輸入名稱) ---
st.divider()
st.subheader("🍽️ 飲食紀錄")

# 簡易資料庫
food_options = {
    "手動輸入": {"cal": 0, "prot": 0},
    "無糖豆漿 (400ml)": {"cal": 135, "prot": 14},
    "水煮蛋 (1顆)": {"cal": 70, "prot": 7},
    "素食便當 (少油)": {"cal": 600, "prot": 20},
    "燙青菜": {"cal": 50, "prot": 2},
    "五穀飯 (一碗)": {"cal": 280, "prot": 5},
    "燕麥奶 (中杯)": {"cal": 150, "prot": 2},
    "希臘優格 (一份)": {"cal": 100, "prot": 10},
    "堅果 (一小把)": {"cal": 150, "prot": 4},
}

c1, c2 = st.columns([2, 1])

# 初始化變數
custom_name = ""
add_cal = 0
add_prot = 0

with c1:
    choice = st.selectbox("選擇食物", list(food_options.keys()))

with c2:
    if choice == "手動輸入":
        # --- 這裡就是新增的功能 ---
        custom_name = st.text_input("請輸入食物名稱", "自訂食物")
        add_cal = st.number_input("熱量 (kcal)", 0, 2000, 0)
        add_prot = st.number_input("蛋白質 (g)", 0, 200, 0)
    else:
        vals = food_options[choice]
        # 即使選資料庫，也讓數值顯示出來，看你要不要微調
        add_cal = st.number_input("熱量", value=vals["cal"])
        add_prot = st.number_input("蛋白質", value=vals["prot"])

if st.button("➕ 加入"):
    # 決定名稱：如果是手動輸入，就用你打的字；如果是選單，就用選單的名字
    final_food_name = custom_name if choice == "手動輸入" else choice

    st.session_state.food_log.append({
        "食物": final_food_name,
        "熱量": add_cal,
        "蛋白質": add_prot
    })
    st.success(f"已加入：{final_food_name}")

# 顯示清單
total_cal = 0
total_prot = 0

if st.session_state.food_log:
    df = pd.DataFrame(st.session_state.food_log)
    st.table(df)
    total_cal = df['熱量'].sum()
    total_prot = df['蛋白質'].sum()

    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.download_button(
            label="📥 下載今日紀錄 (CSV)",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name='my_diet_log.csv',
            mime='text/csv',
        )
    with col_d2:
        if st.button("🗑️ 清除所有"):
            st.session_state.food_log = []
            st.rerun()

# --- 4. 結果儀表板 ---
st.divider()
remaining = daily_target - total_cal

col_a, col_b = st.columns(2)
col_a.metric("剩餘熱量", f"{int(remaining)} kcal", delta=f"{int(daily_target)} 目標")
col_b.metric("已吃蛋白質", f"{int(total_prot)} / {int(protein_goal)} g")

st.progress(min(total_cal / daily_target, 1.0) if daily_target > 0 else 0)

if remaining < 0:
    st.error("⚠️ 熱量超標！建議多喝水，或是增加運動量來平衡。")
elif remaining < 300:
    st.warning("額度快用完了，下一餐建議吃：大量蔬菜 + 豆腐/水煮蛋。")
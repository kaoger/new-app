import streamlit as st
import pandas as pd

# --- 設定網頁基本配置 ---
st.set_page_config(page_title="素食體態管理 App v2.0", page_icon="🥑")

# --- 初始化 Session State (用於暫存資料) ---
if 'food_log' not in st.session_state:
    st.session_state.food_log = []

# --- 1. 側邊欄：進階身體數值設定 ---
st.sidebar.header("⚙️ 1. 身體數據與代謝")
st.sidebar.info("輸入越精準，計算越準確！")

calc_method = st.sidebar.radio(
    "選擇計算方式",
    ("一般公式 (Mifflin-St Jeor)", "進階 (已知體脂率/InBody)", "直接輸入 BMR (若已知)")
)

# 共用變數
bmr = 0
tdee = 0

if calc_method == "直接輸入 BMR (若已知)":
    bmr = st.sidebar.number_input("請輸入你的 BMR (基礎代謝)", 500, 3000, 1500)
else:
    gender = st.sidebar.radio("生理性別", ["男", "女"])
    age = st.sidebar.number_input("年齡", 18, 100, 30)
    height = st.sidebar.number_input("身高 (cm)", 100, 250, 170)
    weight = st.sidebar.number_input("目前體重 (kg)", 30, 200, 60)

    if calc_method == "進階 (已知體脂率/InBody)":
        body_fat = st.sidebar.number_input("體脂率 (%)", 5.0, 60.0, 20.0, step=0.1)
        # Katch-McArdle 公式 (比一般公式準確，因為考慮肌肉量)
        lbm = weight * (1 - (body_fat / 100)) # 去脂體重
        bmr = 370 + (21.6 * lbm)
        st.sidebar.caption(f"根據體脂率 {body_fat}%，你的去脂體重約為 {lbm:.1f} kg")
    else:
        # Mifflin-St Jeor 公式
        if gender == "男":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

st.sidebar.divider()

activity_level = st.sidebar.selectbox(
    "日常活動量",
    ("久坐 (BMR x 1.2)", "輕度 (BMR x 1.375)", "中度 (BMR x 1.55)", "高度 (BMR x 1.725)"),
    index=1
)

# 計算 TDEE
multipliers = {"久坐": 1.2, "輕度": 1.375, "中度": 1.55, "高度": 1.725}
act_key = activity_level.split(" ")[0]
tdee = bmr * multipliers[act_key]

# --- 2. 目標設定 (倒推熱量需求) ---
st.title("🥑 素食體態管理 v2.0")

with st.expander("🎯 2. 設定減重目標 (點擊展開)", expanded=True):
    col1, col2 = st.columns(2)
    target_weight = col1.number_input("目標體重 (kg)", 30.0, 200.0, weight - 2.0)
    target_days = col2.number_input("預計達成天數", 7, 365, 30)

    # 計算邏輯
    weight_diff = weight - target_weight
    if weight_diff > 0:
        total_cal_deficit = weight_diff * 7700 # 減去1kg約需消耗7700大卡
        daily_deficit_needed = total_cal_deficit / target_days
        daily_target_calories = tdee - daily_deficit_needed

        st.write(f"為了在 **{target_days}** 天內減去 **{weight_diff:.1f}** 公斤：")
        st.info(f"👉 你每天需要創造 **{int(daily_deficit_needed)}** 大卡的熱量赤字")
    else:
        daily_target_calories = tdee
        st.success("目前目標為維持或增重。")

    # 安全機制
    if daily_target_calories < bmr:
        st.warning(f"⚠️ 注意：建議攝取量 ({int(daily_target_calories)}) 低於基礎代謝 ({int(bmr)})，長期可能影響健康，建議延長天數。")

# 蛋白質目標 (簡單設為體重的 1.5 倍)
protein_goal = weight * 1.5

# --- 顯示今日儀表板 ---
st.divider()
st.subheader("📊 今日儀表板")
col_a, col_b, col_c = st.columns(3)
col_a.metric("每日目標攝取", f"{int(daily_target_calories)} kcal")
col_b.metric("每日蛋白質目標", f"{int(protein_goal)} g")
col_c.metric("基礎代謝 (InBody/公式)", f"{int(bmr)} kcal")

# --- 3. 飲食紀錄 (手動 + 資料庫) ---
st.divider()
st.subheader("🍽️ 飲食紀錄")

# 簡易素食資料庫
food_db = {
    "手動輸入": {"cal": 0, "prot": 0},
    "無糖豆漿 (400ml)": {"cal": 135, "prot": 14},
    "水煮蛋 (1顆)": {"cal": 70, "prot": 7},
    "素食自助餐便當 (少油)": {"cal": 600, "prot": 20},
    "便利商店御飯糰 (肉鬆)": {"cal": 200, "prot": 4},
    "燙青菜 (一盤)": {"cal": 50, "prot": 2},
    "板豆腐 (半盒)": {"cal": 150, "prot": 12},
    "五穀飯 (一碗)": {"cal": 280, "prot": 5},
    "燕麥奶拿鐵 (中杯)": {"cal": 200, "prot": 2},
}

col_food, col_btn = st.columns([3, 1])
with col_food:
    selected_food = st.selectbox("選擇食物 (或選擇手動輸入)", list(food_db.keys()))

cal_input = 0
prot_input = 0

# 如果選資料庫，自動帶入數值；如果是手動，讓用戶輸入
if selected_food == "手動輸入":
    c1, c2 = st.columns(2)
    cal_input = c1.number_input("熱量 (kcal)", 0, 2000, 0)
    prot_input = c2.number_input("蛋白質 (g)", 0, 200, 0)
else:
    data = food_db[selected_food]
    cal_input = data["cal"]
    prot_input = data["prot"]
    st.caption(f"預設數值：熱量 {cal_input} kcal / 蛋白質 {prot_input} g (可手動修改)")
    # 這裡讓使用者可以微調數值
    # cal_input = st.number_input("確認熱量", value=data["cal"])
    # (為了介面簡潔，暫時鎖定直接加入)

if col_btn.button("➕ 加入清單"):
    st.session_state.food_log.append({
        "item": selected_food if selected_food != "手動輸入" else "自訂食物",
        "cal": cal_input,
        "prot": prot_input
    })
    st.success(f"已加入：{selected_food}")

# --- 顯示已吃清單與加總 ---
if len(st.session_state.food_log) > 0:
    st.write("📋 今天吃了：")

    # 轉成表格顯示
    df = pd.DataFrame(st.session_state.food_log)
    st.table(df)

    # 計算總和
    total_eaten = df['cal'].sum()
    total_prot = df['prot'].sum()

    # 刪除按鈕
    if st.button("🗑️ 清空紀錄"):
        st.session_state.food_log = []
        st.rerun()
else:
    total_eaten = 0
    total_prot = 0
    st.info("目前還沒紀錄任何食物，快去吃點東西吧！")

# --- 4. 結算與建議 ---
st.divider()
st.subheader("💡 即時建議")

remaining = daily_target_calories - total_eaten
prot_remaining = protein_goal - total_prot

# 進度條
st.write(f"熱量進度：{int(total_eaten)} / {int(daily_target_calories)}")
st.progress(min(total_eaten / daily_target_calories, 1.0))

if remaining > 0:
    st.success(f"👍 你今天還有 **{int(remaining)} kcal** 的額度！")
    if prot_remaining > 0:
        st.info(f"💪 蛋白質還差 **{int(prot_remaining)} g**，建議補充豆漿、豆腐或高蛋白粉。")
else:
    st.error(f"⚠️ 已超過目標 **{abs(int(remaining))} kcal**，建議下一餐只吃蔬菜或停止進食。")

# --- 針對問題 4 的食譜討論區塊 ---
with st.expander("📖 素食食譜與餐廳建議 (開發中)"):
    st.write("這裡未來會依照你的剩餘熱量，推薦食譜。")
    st.write("目前推薦：")
    st.markdown("""
    * **低卡飽足：** 蒟蒻涼麵 + 溫泉蛋 (約 250 kcal)
    * **高蛋白餐：** 煎板豆腐 + 毛豆炒豆皮 (約 400 kcal, 25g 蛋白)
    * **外食建議：** Subway 素食堡 (不加醬, 乾酪) / 潤餅 (不加糖粉)
    """)
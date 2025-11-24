import streamlit as st
import pandas as pd

# --- 設定網頁基本配置 (分頁標題 icon) ---
st.set_page_config(page_title="植感生活 Diary", page_icon="🌿", layout="centered")

# --- 自定義 CSS 美化標題 ---
st.markdown("""
    <style>
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2E7D32; /* 深綠色 */
        text-align: center;
        font-weight: 700;
        padding-bottom: 20px;
    }
    .sub-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #558B2F; /* 較淺的綠色 */
        text-align: center;
        font-size: 1.2rem;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 顯示美化後的標題 ---
st.markdown('<h1 class="main-header">🌿 植感生活 Diary</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plant-Based Living & Body Balance</p>', unsafe_allow_html=True)


# --- 初始化 Session State (暫存) ---
if 'food_log' not in st.session_state:
    st.session_state.food_log = []

# =========================================
#  核心數據區 (維持 V2.3 的手機友善介面)
# =========================================
with st.expander("⚙️ 設定個人數據 (InBody / 運動量)", expanded=False):
    st.caption("輸入更精準的數據，獲得專屬計算結果")

    col1, col2 = st.columns(2)
    gender = col1.radio("生理性別", ["男", "女"], horizontal=True)
    age = col2.number_input("年齡", 18, 100, 30)

    col3, col4 = st.columns(2)
    height = col3.number_input("身高 (cm)", 100, 250, 170)
    weight = col4.number_input("體重 (kg)", 30.0, 200.0, 60.0)

    # 體脂率輸入
    st.divider()
    use_bodyfat = st.checkbox("我有體脂率數據 (InBody)")

    calculated_bmr = 0
    if use_bodyfat:
        body_fat = st.number_input("輸入體脂率 (%)", 3.0, 50.0, 20.0, step=0.1)
        # Katch-McArdle 公式
        lbm = weight * (1 - (body_fat / 100))
        calculated_bmr = 370 + (21.6 * lbm)
        st.caption(f"✅ 已啟用 Katch公式 (去脂體重 {lbm:.1f} kg)")
    else:
        # Mifflin-St Jeor 公式
        if gender == "男":
            calculated_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            calculated_bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # 手動 BMR 修正
    use_manual_bmr = st.checkbox(f"系統估算 BMR 為 {int(calculated_bmr)}，我要手動修正")
    if use_manual_bmr:
        final_bmr = st.number_input("手動輸入 BMR", 500, 5000, int(calculated_bmr))
    else:
        final_bmr = calculated_bmr

    # 運動頻率
    st.divider()
    activity_option = st.selectbox(
        "每週運動強度",
        ("久坐 (辦公室/無運動)", "輕度 (每週運動 1-3 天)", "中度 (每週運動 3-5 天)", "高度 (每週運動 6-7 天)", "超高度 (勞力/選手)")
    )
    multipliers = {"久坐": 1.2, "輕度": 1.375, "中度": 1.55, "高度": 1.725, "超高度": 1.9}
    act_key = activity_option[:2]
    if "久坐" in activity_option: act_key = "久坐"
    elif "輕度" in activity_option: act_key = "輕度"
    elif "中度" in activity_option: act_key = "中度"
    elif "高度" in activity_option: act_key = "高度"
    else: act_key = "超高度"

    tdee = final_bmr * multipliers[act_key]

# 目標設定
with st.expander("🎯 設定體態目標", expanded=False):
    c1, c2 = st.columns(2)
    target_weight = c1.number_input("目標體重", 30.0, 200.0, weight)
    target_days = c2.number_input("預計天數", 7, 365, 30)

    weight_diff = weight - target_weight
    if weight_diff > 0:
        daily_deficit = (weight_diff * 7700) / target_days
        daily_target = tdee - daily_deficit
    elif weight_diff < 0:
        daily_surplus = (abs(weight_diff) * 7700) / target_days
        daily_target = tdee + daily_surplus
    else:
        daily_target = tdee

protein_goal = weight * 1.5

# =========================================
#  儀表板與紀錄區
# =========================================
st.divider()
# st.subheader("📊 今日概況") # 舊標題
st.markdown("### 📊 今日概況") # 新標題樣式

total_cal = sum([item['熱量'] for item in st.session_state.food_log])
total_prot = sum([item['蛋白質'] for item in st.session_state.food_log])
remaining = daily_target - total_cal

col_a, col_b = st.columns(2)
col_a.metric("剩餘熱量", f"{int(remaining)}", f"目標 {int(daily_target)}")
col_b.metric("蛋白質進度", f"{int(total_prot)}g", f"目標 {int(protein_goal)}g")
st.progress(min(total_cal / daily_target, 1.0) if daily_target > 0 else 0)

# 飲食紀錄按鈕區
st.divider()
st.markdown("### 🍽️ 飲食紀錄")
with st.expander("➕ 新增一筆紀錄", expanded=False):
    # 簡易資料庫
    food_options = {
        "手動輸入": {"cal": 0, "prot": 0},
        "無糖豆漿 (400ml)": {"cal": 135, "prot": 14},
        "茶葉蛋 (1顆)": {"cal": 75, "prot": 7},
        "素食便當 (一般)": {"cal": 700, "prot": 20},
        "素食便當 (減飯/少油)": {"cal": 500, "prot": 18},
        "燙青菜": {"cal": 50, "prot": 2},
        "五穀飯 (一碗)": {"cal": 280, "prot": 5},
        "水果 (一份)": {"cal": 60, "prot": 1},
        "堅果 (一小把)": {"cal": 150, "prot": 4},
    }
    f1, f2 = st.columns([2, 1])
    with f1: choice = st.selectbox("選擇食物", list(food_options.keys()))
    custom_name = ""; add_cal = 0; add_prot = 0
    if choice == "手動輸入":
        custom_name = st.text_input("食物名稱", "自訂食物")
        in1, in2 = st.columns(2)
        add_cal = in1.number_input("熱量 (kcal)", 0, 3000, 0)
        add_prot = in2.number_input("蛋白質 (g)", 0, 200, 0)
    else:
        vals = food_options[choice]
        in1, in2 = st.columns(2)
        add_cal = in1.number_input("熱量", value=vals["cal"])
        add_prot = in2.number_input("蛋白質", value=vals["prot"])
    if st.button("確認加入", use_container_width=True):
        final_name = custom_name if choice == "手動輸入" else choice
        st.session_state.food_log.append({"食物": final_name, "熱量": add_cal, "蛋白質": add_prot})
        st.rerun()

if st.session_state.food_log:
    df = pd.DataFrame(st.session_state.food_log)
    st.dataframe(df, use_container_width=True, hide_index=True)
    d1, d2 = st.columns(2)
    with d1: st.download_button("📥 下載 CSV", data=df.to_csv(index=False).encode('utf-8-sig'), file_name='log.csv', mime='text/csv', use_container_width=True)
    with d2:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.food_log = []
            st.rerun()

# =========================================
#  新增功能：靈感廚房 (三餐建議 + 食譜)
# =========================================
st.divider()
st.markdown("### 🥑 靈感廚房：三餐提案")

# 定義食譜資料庫 (這裡先內建兩個範本)
recipe_book = {
    "低卡輕盈餐 (適合剩餘熱量較少時)": {
        "早餐": {
            "name": "希臘優格燕麥杯",
            "desc": "約 250 kcal / 蛋白質 15g",
            "recipe": """
            * **食材：** 無糖希臘優格 150g、大燕麥片 3匙、奇亞籽 1匙、藍莓/草莓適量。
            * **作法：**
                1. 前一晚將燕麥片與奇亞籽混入優格中，放冰箱冷藏（隔夜燕麥）。
                2. 早上取出，鋪上新鮮水果即可享用。
            """
        },
        "午餐": {
            "name": "涼拌雞絲(素雞)蒟蒻麵",
            "desc": "約 350 kcal / 蛋白質 20g",
            "recipe": """
            * **食材：** 蒟蒻麵一包、素雞絲(或剝皮辣椒口味) 100g、小黃瓜絲、紅蘿蔔絲、和風醬汁。
            * **作法：**
                1. 蒟蒻麵用熱水燙過即撈起冰鎮。
                2. 所有蔬菜切絲。
                3. 將麵、蔬菜絲、素雞絲混合，淋上和風醬汁拌勻。
            """
        },
        "晚餐": {
            "name": "蔬菜豆腐味噌湯 + 燙青菜",
            "desc": "約 200 kcal / 蛋白質 12g",
            "recipe": """
            * **食材：** 板豆腐半塊、海帶芽、綜合蔬菜(高麗菜/菇類)、味噌一匙。
            * **作法：**
                1. 水滾後放入蔬菜與豆腐煮熟。
                2. 關火，將味噌先用一點熱水化開，再倒入鍋中攪拌（避免持續滾煮破壞風味）。
                3. 另外燙一份深綠色蔬菜搭配。
            """
        }
    },
    "均衡活力餐 (適合熱量充足時)": {
        "早餐": {
            "name": "酪梨全麥吐司加蛋",
            "desc": "約 400 kcal / 蛋白質 18g",
            "recipe": """
            * **食材：** 全麥吐司 2片、酪梨半顆、水煮蛋或煎蛋 1顆、黑胡椒。
            * **作法：**
                1. 酪梨壓成泥，抹在烤好的吐司上。
                2. 放上蛋，撒上黑胡椒調味。
            """
        },
        "午餐": {
            "name": "鷹嘴豆藜麥彩虹沙拉",
            "desc": "約 500 kcal / 蛋白質 25g",
            "recipe": """
            * **食材：** 熟藜麥半碗、鷹嘴豆半罐(瀝乾)、甜椒丁、小黃瓜丁、紫洋蔥丁、毛豆仁、橄欖油檸檬醬汁。
            * **作法：**
                1. 將所有食材在一個大碗中混合。
                2. 淋上橄欖油、檸檬汁、少許鹽巴拌勻即可。可一次做多天份冷藏。
            """
        },
        "晚餐": {
            "name": "香煎天貝佐時蔬",
            "desc": "約 450 kcal / 蛋白質 30g",
            "recipe": """
            * **食材：** 天貝 150g、花椰菜、四季豆、醬油膏、蒜末(選用)。
            * **作法：**
                1. 天貝切片，平底鍋少油兩面煎至金黃。加入一點醬油膏燒入味。
                2. 原鍋利用餘油炒熟蔬菜，加鹽調味。
                3. 組合盛盤。
            """
        }
    }
}

# 判斷邏輯：根據剩餘熱量推薦
if remaining < 400 and daily_target > 0:
    recommendation_key = "低卡輕盈餐 (適合剩餘熱量較少時)"
    st.info("💡 今日額度較少，推薦你清爽低負擔的餐點：")
else:
    recommendation_key = "均衡活力餐 (適合熱量充足時)"
    if daily_target > 0:
        st.success("💡 今日熱量充足，來點營養豐富的美味餐點吧！")

# 顯示三餐建議與食譜
selected_plan = recipe_book[recommendation_key]

col_meal1, col_meal2, col_meal3 = st.columns(3)

with col_meal1:
    st.markdown(f"#### ☀️ 早餐")
    meal = selected_plan["早餐"]
    st.write(f"**{meal['name']}**")
    st.caption(meal['desc'])
    with st.expander("👨‍🍳 查看作法"):
        st.markdown(meal['recipe'])

with col_meal2:
    st.markdown(f"#### 🍱 午餐")
    meal = selected_plan["午餐"]
    st.write(f"**{meal['name']}**")
    st.caption(meal['desc'])
    with st.expander("👨‍🍳 查看作法"):
        st.markdown(meal['recipe'])

with col_meal3:
    st.markdown(f"#### 🌙 晚餐")
    meal = selected_plan["晚餐"]
    st.write(f"**{meal['name']}**")
    st.caption(meal['desc'])
    with st.expander("👨‍🍳 查看作法"):
        st.markdown(meal['recipe'])

st.divider()
st.caption("Note: 這是一個基於 Streamlit 構建的個人化素食生活管理工具。V2.4")
import streamlit as st
import pandas as pd

# --- 設定網頁基本配置 ---
st.set_page_config(page_title="植感生活 Diary v2.5", page_icon="🌿", layout="centered")

# --- CSS 美化標題 ---
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2E7D32; text-align: center; font-weight: 700; padding-bottom: 10px; }
    .sub-header { font-family: 'Helvetica Neue', sans-serif; color: #558B2F; text-align: center; font-size: 1.1rem; margin-top: -15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🌿 植感生活 Diary</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plant-Based Living & Body Balance</p>', unsafe_allow_html=True)

if 'food_log' not in st.session_state:
    st.session_state.food_log = []

# =========================================
#  1. 設定區 (加入素食類型選擇)
# =========================================
with st.expander("⚙️ 個人檔案設定 (素食類型 / InBody)", expanded=False):
    # --- 新增：素食類型選擇 ---
    st.subheader("🌱 飲食偏好")
    diet_type = st.radio(
        "你是哪種素食者？(將影響食譜建議)",
        ["全素 (Vegan)", "蛋奶素 (Lacto-Ovo)", "鍋邊素 (方便素)"],
        horizontal=True
    )
    st.divider()

    # --- 身體數據 ---
    col1, col2 = st.columns(2)
    gender = col1.radio("生理性別", ["男", "女"], horizontal=True)
    age = col2.number_input("年齡", 18, 100, 30)

    col3, col4 = st.columns(2)
    height = col3.number_input("身高 (cm)", 100, 250, 170)
    weight = col4.number_input("體重 (kg)", 30.0, 200.0, 60.0)

    # --- InBody / BMR ---
    st.divider()
    use_bodyfat = st.checkbox("我有體脂率數據 (InBody)")
    calculated_bmr = 0
    if use_bodyfat:
        body_fat = st.number_input("輸入體脂率 (%)", 3.0, 60.0, 20.0, step=0.1)
        lbm = weight * (1 - (body_fat / 100))
        calculated_bmr = 370 + (21.6 * lbm)
        st.caption(f"已啟用 Katch公式 (去脂體重 {lbm:.1f} kg)")
    else:
        if gender == "男": calculated_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else: calculated_bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    use_manual_bmr = st.checkbox(f"系統估算 BMR: {int(calculated_bmr)}，我要手動修正")
    final_bmr = st.number_input("BMR 數值", 500, 5000, int(calculated_bmr)) if use_manual_bmr else calculated_bmr

    # --- 運動量 ---
    st.divider()
    activity_option = st.selectbox("每週運動強度",
        ("久坐 (無運動)", "輕度 (1-3天)", "中度 (3-5天)", "高度 (6-7天)", "超高度 (選手)"))
    multipliers = {"久坐": 1.2, "輕度": 1.375, "中度": 1.55, "高度": 1.725, "超高度": 1.9}
    act_key = activity_option[:2]
    tdee = final_bmr * multipliers.get(act_key, 1.2)

# =========================================
#  2. 目標設定
# =========================================
with st.expander("🎯 體態目標設定", expanded=False):
    c1, c2 = st.columns(2)
    target_weight = c1.number_input("目標體重", 30.0, 200.0, weight)
    target_days = c2.number_input("預計天數", 7, 365, 30)

    weight_diff = weight - target_weight
    if weight_diff > 0: daily_target = tdee - ((weight_diff * 7700) / target_days)
    elif weight_diff < 0: daily_target = tdee + ((abs(weight_diff) * 7700) / target_days)
    else: daily_target = tdee

    protein_goal = weight * 1.5

# =========================================
#  3. 儀表板
# =========================================
st.markdown("### 📊 今日概況")
total_cal = sum([item['熱量'] for item in st.session_state.food_log])
total_prot = sum([item['蛋白質'] for item in st.session_state.food_log])
remaining = daily_target - total_cal

col_a, col_b = st.columns(2)
col_a.metric("剩餘熱量", f"{int(remaining)}", f"目標 {int(daily_target)}")
col_b.metric("蛋白質進度", f"{int(total_prot)}g", f"目標 {int(protein_goal)}g")
st.progress(min(total_cal / daily_target, 1.0) if daily_target > 0 else 0)

# =========================================
#  4. 飲食紀錄
# =========================================
st.markdown("### 🍽️ 飲食紀錄")
with st.expander("➕ 新增紀錄", expanded=False):
    food_options = {
        "手動輸入": {"cal": 0, "prot": 0},
        "無糖豆漿 (400ml)": {"cal": 135, "prot": 14},
        "茶葉蛋 (1顆)": {"cal": 75, "prot": 7},
        "素食便當 (一般)": {"cal": 700, "prot": 20},
        "燙青菜": {"cal": 50, "prot": 2},
        "五穀飯 (一碗)": {"cal": 280, "prot": 5},
        "水果 (一份)": {"cal": 60, "prot": 1},
        "堅果 (一小把)": {"cal": 150, "prot": 4},
    }
    f1, f2 = st.columns([2, 1])
    with f1: choice = st.selectbox("選擇食物", list(food_options.keys()))

    custom_name = ""
    if choice == "手動輸入":
        custom_name = st.text_input("食物名稱", "自訂食物")
        in1, in2 = st.columns(2)
        add_cal = in1.number_input("熱量", 0, 3000, 0)
        add_prot = in2.number_input("蛋白質", 0, 200, 0)
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
    if st.button("🗑️ 清空", use_container_width=True):
        st.session_state.food_log = []
        st.rerun()

# =========================================
#  5. 靈感廚房 (依照素食類型與熱量推薦)
# =========================================
st.divider()
st.markdown(f"### 🥑 靈感廚房 ({diet_type})")

# 定義食譜資料庫 (包含三種素食類型的 高/低熱量 菜單)
menus = {
    "全素 (Vegan)": {
        "low": {
            "早": {"n": "奇亞籽豆漿布丁", "d": "250 kcal / 12g 蛋", "r": "豆漿+奇亞籽放隔夜，早起加水果"},
            "午": {"n": "鷹嘴豆藜麥沙拉", "d": "350 kcal / 18g 蛋", "r": "鷹嘴豆、藜麥、甜椒、小黃瓜、檸檬油醋醬"},
            "晚": {"n": "味噌豆腐蔬菜湯", "d": "200 kcal / 12g 蛋", "r": "板豆腐、海帶芽、綜合菇類、味噌湯底"}
        },
        "high": {
            "早": {"n": "酪梨全麥吐司", "d": "400 kcal / 15g 蛋", "r": "全麥吐司、酪梨泥、黑胡椒、堅果"},
            "午": {"n": "天貝炒時蔬", "d": "500 kcal / 25g 蛋", "r": "天貝煎金黃、加入花椰菜與醬油拌炒"},
            "晚": {"n": "紅燒豆腐煲", "d": "450 kcal / 20g 蛋", "r": "板豆腐煎過、加入紅蘿蔔/香菇紅燒燉煮"}
        }
    },
    "蛋奶素 (Lacto-Ovo)": {
        "low": {
            "早": {"n": "希臘優格杯", "d": "250 kcal / 15g 蛋", "r": "無糖優格、藍莓、少量燕麥"},
            "午": {"n": "涼拌雞絲(素)蒟蒻麵", "d": "350 kcal / 20g 蛋", "r": "蒟蒻麵、素雞絲(蛋白製品)、小黃瓜、和風醬"},
            "晚": {"n": "番茄蔬菜蛋花湯", "d": "200 kcal / 12g 蛋", "r": "兩顆蛋、番茄、小白菜、清湯"}
        },
        "high": {
            "早": {"n": "起司蔬菜烘蛋", "d": "400 kcal / 22g 蛋", "r": "兩顆蛋、菠菜、起司片、平底鍋烘烤"},
            "午": {"n": "松露野菇義大利麵", "d": "550 kcal / 18g 蛋", "r": "義大利麵、鮮奶油/牛奶、綜合菇、松露醬"},
            "晚": {"n": "歐姆蛋咖哩飯", "d": "500 kcal / 15g 蛋", "r": "滑嫩歐姆蛋、素食咖哩塊、馬鈴薯紅蘿蔔"}
        }
    },
    "鍋邊素 (方便素)": {
        "low": {
            "早": {"n": "超商地瓜+茶葉蛋", "d": "280 kcal / 10g 蛋", "r": "中型蒸地瓜一顆、茶葉蛋一顆"},
            "午": {"n": "關東煮輕食餐", "d": "350 kcal / 15g 蛋", "r": "白蘿蔔、娃娃菜、滷蛋、蒟蒻絲 (不喝湯)"},
            "晚": {"n": "自助餐夾菜(去肉)", "d": "300 kcal / 10g 蛋", "r": "三樣深色蔬菜、一份豆腐、不淋肉燥"}
        },
        "high": {
            "早": {"n": "蛋餅+無糖豆漿", "d": "400 kcal / 15g 蛋", "r": "起司蛋餅或蔬菜蛋餅、400ml 無糖豆漿"},
            "午": {"n": "素食水餃餐", "d": "550 kcal / 18g 蛋", "r": "素水餃 10 顆、燙青菜一份、皮蛋豆腐"},
            "晚": {"n": "潤餅(微糖)", "d": "450 kcal / 15g 蛋", "r": "多加高麗菜與豆干、不加肥肉、花生粉減半"}
        }
    }
}

# 推薦邏輯
menu_type = "low" if (remaining < 400 and daily_target > 0) else "high"
current_menu = menus[diet_type][menu_type]

if menu_type == "low":
    st.info(f"💡 今日額度較少，推薦 **{diet_type} - 輕盈低卡餐**：")
else:
    st.success(f"💡 今日熱量充足，推薦 **{diet_type} - 營養均衡餐**：")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### ☀️ 早餐")
    st.write(f"**{current_menu['早']['n']}**")
    st.caption(current_menu['早']['d'])
    with st.expander("作法"): st.write(current_menu['早']['r'])

with c2:
    st.markdown("#### 🍱 午餐")
    st.write(f"**{current_menu['午']['n']}**")
    st.caption(current_menu['午']['d'])
    with st.expander("作法"): st.write(current_menu['午']['r'])

with c3:
    st.markdown("#### 🌙 晚餐")
    st.write(f"**{current_menu['晚']['n']}**")
    st.caption(current_menu['晚']['d'])
    with st.expander("作法"): st.write(current_menu['晚']['r'])

st.divider()
st.caption("Note: 素食分類與食譜僅供參考，請依個人過敏源調整。")
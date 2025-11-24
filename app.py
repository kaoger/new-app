import streamlit as st

# --- 設定網頁基本配置 ---
st.set_page_config(page_title="素食體態管理 App", page_icon="🥑")

# --- 側邊欄：使用者資料輸入 ---
st.sidebar.header("⚙️ 個人數值設定")
st.sidebar.write("請輸入你的基本資料以計算代謝：")

gender = st.sidebar.radio("生理性別", ["男", "女"])
age = st.sidebar.number_input("年齡", 18, 100, 30)
height = st.sidebar.number_input("身高 (cm)", 100, 250, 170)
weight = st.sidebar.number_input("目前體重 (kg)", 30, 200, 60)
activity_level = st.sidebar.selectbox(
    "日常活動量",
    ("久坐 (辦公室工作)", "輕度活動 (每週運動1-3天)", "中度活動 (每週運動3-5天)", "高度活動 (每週運動6-7天)")
)
diet_type = st.sidebar.selectbox(
    "🌱 你的素食類型",
    ("全素 (Vegan)", "蛋奶素 (Lacto-Ovo)", "鍋邊/方便素")
)

# --- 核心計算邏輯 (BMR & TDEE) ---
# Mifflin-St Jeor 公式
if gender == "男":
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

# 活動因子轉換
activity_multipliers = {
    "久坐 (辦公室工作)": 1.2,
    "輕度活動 (每週運動1-3天)": 1.375,
    "中度活動 (每週運動3-5天)": 1.55,
    "高度活動 (每週運動6-7天)": 1.725
}
tdee = bmr * activity_multipliers[activity_level]

# 減重目標設定 (創造熱量赤字)
deficit = 400 # 每日少吃 400 大卡
target_calories = tdee - deficit
protein_goal = weight * 1.5 # 減脂期建議高蛋白 (體重x1.5g)

# --- 主畫面設計 ---
st.title("🥑 素食體態管理助手")
st.write("透過科學計算，協助你簡單控制體重。")

st.divider() # 分隔線

# 顯示目標
col1, col2, col3 = st.columns(3)
col1.metric("每日建議熱量", f"{int(target_calories)} kcal")
col2.metric("每日蛋白質量", f"{int(protein_goal)} g")
col3.metric("基礎代謝率 (BMR)", f"{int(bmr)} kcal")

st.divider()

# --- 今日飲食追蹤 ---
st.subheader("📝 今天吃了什麼？")
eaten_calories = st.number_input("目前已攝取熱量 (kcal)", 0, 5000, 0, step=50)

# 計算剩餘熱量
remaining_calories = target_calories - eaten_calories

# 顯示進度條
progress = min(eaten_calories / target_calories, 1.0)
st.progress(progress)

if remaining_calories > 0:
    st.info(f"👉 你今天還有 **{int(remaining_calories)} kcal** 的額度！")
else:
    st.error(f"⚠️ 注意！你已經超過目標 **{abs(int(remaining_calories))} kcal** 了。")

# --- 體重預測 ---
st.subheader("📉 預測成果")
# 7700大卡 = 1公斤脂肪
weekly_loss = (deficit * 7) / 7700
st.write(f"如果你每天都保持這個進度，預計本週可以減輕約 **{weekly_loss:.2f} 公斤**。")

# --- 智慧飲食建議 (依照素食類型) ---
st.divider()
st.subheader("💡 下一餐建議")

if remaining_calories <= 0:
    st.warning("建議停止進食，或僅飲用無糖花草茶、水。")
elif remaining_calories < 300:
    st.success("額度較少，建議選擇低卡高纖的點心：")
    if diet_type == "全素 (Vegan)":
        st.write("- 無糖豆漿 (200ml)")
        st.write("- 涼拌海帶芽")
        st.write("- 一份芭樂或蘋果")
    elif diet_type == "蛋奶素 (Lacto-Ovo)":
        st.write("- 水煮蛋 1 顆")
        st.write("- 希臘優格 (無糖)")
    else:
        st.write("- 茶葉蛋 1 顆")
        st.write("- 蒟蒻果凍")
else:
    st.success("額度充足，可以享用營養均衡的正餐！建議優先補充蛋白質：")
    if diet_type == "全素 (Vegan)":
        st.write("- 煎板豆腐 / 豆干炒芹菜")
        st.write("- 鷹嘴豆沙拉 / 毛豆")
        st.write("- 天貝料理")
    elif diet_type == "蛋奶素 (Lacto-Ovo)":
        st.write("- 番茄炒蛋 (少油)")
        st.write("- 起司蔬菜烘蛋")
        st.write("- 鮮奶燕麥粥")
    else:
        st.write("- 各式蛋料理")
        st.write("- 豆腐鍋 (清湯底)")
        st.write("- 方便素自助餐 (避開炸物與勾芡)")
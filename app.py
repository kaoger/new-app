<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>植感生活 Diary - Mobile UI Concept</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
        body { font-family: 'Noto Sans TC', sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }

        /* 手機外框模擬 */
        .phone-frame {
            width: 375px;
            height: 812px;
            background-color: #ffffff;
            border-radius: 40px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.2);
            border: 12px solid #1a1a1a;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        /* 瀏海 */
        .notch {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 150px;
            height: 30px;
            background-color: #1a1a1a;
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
            z-index: 50;
        }

        /* 內容區域 */
        .app-content {
            flex: 1;
            overflow-y: auto;
            padding-bottom: 80px; /* 避開底部導航 */
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        .app-content::-webkit-scrollbar { display: none; }

        /* 底部導航列 */
        .bottom-nav {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 80px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding-bottom: 20px; /* 適應 iPhone 底部橫條 */
            z-index: 40;
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #9ca3af;
            font-size: 12px;
            cursor: pointer;
            transition: 0.3s;
        }

        .nav-item.active {
            color: #2E7D32;
            font-weight: bold;
        }

        .nav-item i { font-size: 24px; margin-bottom: 4px; }

        /* FAB (新增按鈕) */
        .fab {
            position: absolute;
            bottom: 90px;
            right: 20px;
            width: 56px;
            height: 56px;
            background: #2E7D32;
            color: white;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            box-shadow: 0 4px 10px rgba(46, 125, 50, 0.4);
            cursor: pointer;
            transition: 0.2s;
            z-index: 30;
        }
        .fab:active { transform: scale(0.95); }

        /* 卡片樣式 */
        .card {
            background: white;
            border-radius: 20px;
            padding: 20px;
            margin: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }

        /* 進度環 */
        .progress-ring { transform: rotate(-90deg); transform-origin: 50% 50%; }
        .progress-ring__circle {
            stroke-dasharray: 326;
            stroke-dashoffset: 326; /* Full is 0 */
            transition: stroke-dashoffset 0.35s;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }

        /* 畫面切換 */
        .screen { display: none; animation: fadeIn 0.3s; }
        .screen.active { display: block; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .tag-pill {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        .tag-vegan { background: #E8F5E9; color: #2E7D32; }
    </style>
</head>
<body>

    <div class="phone-frame">
        <div class="notch"></div>

        <!-- 狀態列模擬 -->
        <div class="flex justify-between px-6 pt-3 pb-2 text-xs font-bold text-gray-800 z-10 bg-white">
            <span>09:41</span>
            <div class="flex gap-1">
                <i class="fas fa-signal"></i>
                <i class="fas fa-wifi"></i>
                <i class="fas fa-battery-full"></i>
            </div>
        </div>

        <!-- ================= 畫面 1: 首頁 (Dashboard) ================= -->
        <div id="home-screen" class="app-content screen active">
            <!-- Header -->
            <div class="px-6 pt-4 pb-2 flex justify-between items-center">
                <div>
                    <p class="text-gray-500 text-sm">早安, 小明 👋</p>
                    <h1 class="text-2xl font-bold text-gray-800">今日概況</h1>
                </div>
                <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-700">
                    <i class="fas fa-user"></i>
                </div>
            </div>

            <!-- 熱量大圈圈 (核心視覺) -->
            <div class="card flex flex-col items-center relative">
                <h3 class="text-gray-500 text-sm mb-2 w-full text-left">剩餘熱量</h3>

                <!-- 模擬 SVG 環形進度條 -->
                <div class="relative w-48 h-48 flex items-center justify-center">
                    <svg class="w-full h-full" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="52" fill="none" stroke="#eee" stroke-width="8" />
                        <!-- 這是綠色的進度條 (模擬剩餘) -->
                        <circle cx="60" cy="60" r="52" fill="none" stroke="#2E7D32" stroke-width="8"
                                stroke-dasharray="326" stroke-dashoffset="100" stroke-linecap="round"
                                style="transform: rotate(-90deg); transform-origin: 50% 50%;"/>
                    </svg>
                    <div class="absolute text-center">
                        <!-- 如果超標，這裡文字變紅 -->
                        <span class="text-4xl font-bold text-gray-800 block">885</span>
                        <span class="text-xs text-gray-400">Kcal Left</span>
                    </div>
                </div>

                <div class="flex justify-between w-full mt-6 px-4">
                    <div class="text-center">
                        <p class="text-xs text-gray-400">目標</p>
                        <p class="font-bold text-gray-800">2114</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xs text-gray-400">已攝取</p>
                        <p class="font-bold text-green-600">1229</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xs text-gray-400">燃燒</p>
                        <p class="font-bold text-orange-500">350</p>
                    </div>
                </div>
            </div>

            <!-- 蛋白質進度 -->
            <div class="px-6 mb-2">
                <div class="flex justify-between text-sm mb-1">
                    <span class="font-bold text-gray-700">蛋白質</span>
                    <span class="text-green-600 font-bold">100g / 138g</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div class="bg-green-600 h-2.5 rounded-full" style="width: 72%"></div>
                </div>
                <p class="text-xs text-right text-gray-400 mt-1">加油！還差 38g</p>
            </div>

            <!-- 餐別甜甜圈 (取代折線圖) -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold text-gray-800">熱量來源</h3>
                    <i class="fas fa-ellipsis-h text-gray-400"></i>
                </div>
                <div class="flex items-center gap-4">
                    <div class="w-1/2">
                        <canvas id="mealDoughnutChart"></canvas>
                    </div>
                    <div class="w-1/2 space-y-3">
                        <div class="flex items-center justify-between text-xs">
                            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-green-500"></div>早餐</div>
                            <span class="font-bold">35%</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-green-300"></div>午餐</div>
                            <span class="font-bold">45%</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-green-100"></div>晚餐</div>
                            <span class="font-bold">20%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="h-12"></div> <!-- Spacer -->
        </div>

        <!-- ================= 畫面 2: 飲食紀錄 (Log) ================= -->
        <div id="log-screen" class="app-content screen">
            <div class="px-6 pt-4 pb-4 bg-white sticky top-0 z-20 shadow-sm">
                <h1 class="text-xl font-bold text-gray-800">飲食日記</h1>
                <!-- 日期選擇器 -->
                <div class="flex justify-between items-center mt-4 bg-gray-50 p-2 rounded-xl">
                    <i class="fas fa-chevron-left text-gray-400 p-2"></i>
                    <span class="font-bold text-gray-700">今天, 11月 24日</span>
                    <i class="fas fa-chevron-right text-gray-400 p-2"></i>
                </div>
            </div>

            <div class="p-4 space-y-4">
                <!-- 早餐區塊 -->
                <div class="bg-white rounded-2xl p-4 shadow-sm">
                    <div class="flex justify-between items-center mb-3">
                        <div class="flex items-center gap-2">
                            <div class="bg-yellow-100 p-2 rounded-lg text-yellow-600"><i class="fas fa-sun"></i></div>
                            <span class="font-bold text-gray-800">早餐</span>
                        </div>
                        <span class="text-sm text-gray-500">450 kcal</span>
                    </div>
                    <div class="border-l-2 border-gray-100 pl-3 space-y-3">
                        <div class="flex justify-between text-sm">
                            <span>無糖豆漿</span>
                            <span class="text-gray-500">135 kcal</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span>地瓜 (中)</span>
                            <span class="text-gray-500">315 kcal</span>
                        </div>
                    </div>
                    <button class="w-full mt-3 py-2 text-green-600 text-sm font-bold border border-green-200 rounded-xl hover:bg-green-50">+ 新增早餐</button>
                </div>

                <!-- 午餐區塊 -->
                <div class="bg-white rounded-2xl p-4 shadow-sm">
                    <div class="flex justify-between items-center mb-3">
                        <div class="flex items-center gap-2">
                            <div class="bg-orange-100 p-2 rounded-lg text-orange-600"><i class="fas fa-utensils"></i></div>
                            <span class="font-bold text-gray-800">午餐</span>
                        </div>
                        <span class="text-sm text-gray-500">700 kcal</span>
                    </div>
                    <div class="border-l-2 border-gray-100 pl-3 space-y-3">
                        <div class="flex justify-between text-sm">
                            <span>素食便當 (一般)</span>
                            <span class="text-gray-500">700 kcal</span>
                        </div>
                    </div>
                    <button class="w-full mt-3 py-2 text-green-600 text-sm font-bold border border-green-200 rounded-xl hover:bg-green-50">+ 新增午餐</button>
                </div>
            </div>
        </div>

        <!-- ================= 畫面 3: 體態 (Stats) ================= -->
        <div id="stats-screen" class="app-content screen">
            <div class="px-6 pt-4 pb-2">
                <h1 class="text-xl font-bold text-gray-800">體態追蹤</h1>
            </div>

            <!-- 體重卡片 -->
            <div class="card bg-green-600 text-white">
                <p class="text-green-100 text-sm">目前體重</p>
                <div class="flex items-end gap-2 mt-1">
                    <h2 class="text-4xl font-bold">58.5</h2>
                    <span class="text-lg mb-1">kg</span>
                </div>
                <div class="mt-4 flex gap-2">
                    <span class="bg-white/20 px-3 py-1 rounded-full text-xs">體脂 24.5%</span>
                    <span class="bg-white/20 px-3 py-1 rounded-full text-xs">↓ 1.5kg (本月)</span>
                </div>
            </div>

            <!-- 體重圖表 -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold text-gray-800">變化趨勢</h3>
                    <div class="flex gap-2 text-xs">
                        <span class="px-2 py-1 bg-gray-100 rounded-md text-gray-500">週</span>
                        <span class="px-2 py-1 bg-green-100 rounded-md text-green-700 font-bold">月</span>
                    </div>
                </div>
                <canvas id="weightChart" height="200"></canvas>
            </div>

            <!-- 輸入按鈕 -->
            <div class="px-4">
                <button class="w-full bg-gray-800 text-white py-4 rounded-2xl font-bold shadow-lg hover:bg-gray-900 transition">
                    <i class="fas fa-weight mr-2"></i> 紀錄今日體重
                </button>
            </div>
        </div>

        <!-- ================= 畫面 4: 靈感 (Recipes) ================= -->
        <div id="recipe-screen" class="app-content screen">
            <div class="px-6 pt-4 pb-2">
                <h1 class="text-xl font-bold text-gray-800">靈感廚房</h1>
                <div class="flex gap-3 mt-4 overflow-x-auto pb-2 no-scrollbar">
                    <span class="bg-green-600 text-white px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap">全素推薦</span>
                    <span class="bg-white border border-gray-200 text-gray-600 px-4 py-2 rounded-full text-sm whitespace-nowrap">蛋奶素</span>
                    <span class="bg-white border border-gray-200 text-gray-600 px-4 py-2 rounded-full text-sm whitespace-nowrap">低卡輕食</span>
                </div>
            </div>

            <div class="p-4 grid grid-cols-2 gap-4">
                <!-- 食譜卡片 1 -->
                <div class="bg-white rounded-2xl overflow-hidden shadow-sm">
                    <div class="h-32 bg-gray-200 relative">
                        <img src="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&auto=format&fit=crop&q=60" class="w-full h-full object-cover" alt="Salad">
                        <span class="absolute top-2 left-2 bg-white/90 px-2 py-1 rounded-md text-xs font-bold">早餐</span>
                    </div>
                    <div class="p-3">
                        <h3 class="font-bold text-gray-800 text-sm">酪梨全麥吐司</h3>
                        <div class="flex justify-between mt-2 text-xs text-gray-500">
                            <span>400 kcal</span>
                            <span>15g 蛋白</span>
                        </div>
                    </div>
                </div>

                <!-- 食譜卡片 2 -->
                <div class="bg-white rounded-2xl overflow-hidden shadow-sm">
                    <div class="h-32 bg-gray-200 relative">
                        <img src="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&auto=format&fit=crop&q=60" class="w-full h-full object-cover" alt="Bowl">
                        <span class="absolute top-2 left-2 bg-white/90 px-2 py-1 rounded-md text-xs font-bold">午餐</span>
                    </div>
                    <div class="p-3">
                        <h3 class="font-bold text-gray-800 text-sm">鷹嘴豆藜麥沙拉</h3>
                        <div class="flex justify-between mt-2 text-xs text-gray-500">
                            <span>350 kcal</span>
                            <span>18g 蛋白</span>
                        </div>
                    </div>
                </div>
                 <!-- 食譜卡片 3 -->
                 <div class="bg-white rounded-2xl overflow-hidden shadow-sm">
                    <div class="h-32 bg-gray-200 relative">
                        <img src="https://images.unsplash.com/photo-1547592180-85f173990554?w=400&auto=format&fit=crop&q=60" class="w-full h-full object-cover" alt="Soup">
                        <span class="absolute top-2 left-2 bg-white/90 px-2 py-1 rounded-md text-xs font-bold">晚餐</span>
                    </div>
                    <div class="p-3">
                        <h3 class="font-bold text-gray-800 text-sm">味噌豆腐湯</h3>
                        <div class="flex justify-between mt-2 text-xs text-gray-500">
                            <span>200 kcal</span>
                            <span>12g 蛋白</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FAB 懸浮按鈕 -->
        <div class="fab">
            <i class="fas fa-plus"></i>
        </div>

        <!-- 底部導航 -->
        <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('home')">
                <i class="fas fa-home"></i>
                <span>首頁</span>
            </div>
            <div class="nav-item" onclick="switchTab('log')">
                <i class="fas fa-book-open"></i>
                <span>日記</span>
            </div>
            <div class="nav-item" onclick="switchTab('stats')">
                <i class="fas fa-chart-line"></i>
                <span>追蹤</span>
            </div>
            <div class="nav-item" onclick="switchTab('recipe')">
                <i class="fas fa-utensils"></i>
                <span>靈感</span>
            </div>
        </div>
    </div>

    <script>
        // 簡單的分頁切換邏輯
        function switchTab(tabName) {
            // 隱藏所有畫面
            document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
            // 移除所有 nav active
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

            // 顯示目標畫面
            document.getElementById(tabName + '-screen').classList.add('active');

            // 設定 Nav 狀態 (這裡簡單用 index 對應，實際開發可用 ID)
            const navs = document.querySelectorAll('.nav-item');
            if(tabName === 'home') navs[0].classList.add('active');
            if(tabName === 'log') navs[1].classList.add('active');
            if(tabName === 'stats') navs[2].classList.add('active');
            if(tabName === 'recipe') navs[3].classList.add('active');
        }

        // 繪製圖表 (Chart.js)
        // 1. 甜甜圈圖
        const ctxDoughnut = document.getElementById('mealDoughnutChart').getContext('2d');
        new Chart(ctxDoughnut, {
            type: 'doughnut',
            data: {
                labels: ['早餐', '午餐', '晚餐'],
                datasets: [{
                    data: [35, 45, 20],
                    backgroundColor: ['#22c55e', '#86efac', '#dcfce7'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '70%',
                plugins: { legend: { display: false } }
            }
        });

        // 2. 體重折線圖
        const ctxLine = document.getElementById('weightChart').getContext('2d');
        new Chart(ctxLine, {
            type: 'line',
            data: {
                labels: ['11/01', '11/08', '11/15', '11/22', '11/24'],
                datasets: [{
                    label: '體重',
                    data: [60, 59.5, 59.2, 58.8, 58.5],
                    borderColor: '#16a34a',
                    backgroundColor: 'rgba(22, 163, 74, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#16a34a',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 57, max: 61, grid: { display: false } },
                    x: { grid: { display: false } }
                }
            }
        });
    </script>
</body>
</html>
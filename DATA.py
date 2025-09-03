import requests
import pandas as pd
import time

# 抓取bitcoin api
def fetch_historical_trades(symbol, start_time, end_time, limit=1000):
    url = "https://api.binance.com/api/v3/aggTrades"
    all_trades = []
    
    while start_time < end_time:
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data:  # 如果沒有更多數據，停止抓取
            break

        # 整理數據
        for trade in data:
            all_trades.append({
                "trade_id": trade["a"],        # 成交 ID
                "price": float(trade["p"]),    # 成交價格
                "quantity": float(trade["q"]), # 成交數量
                "timestamp": trade["T"],       # 成交時間戳 (毫秒)
                "is_buyer_maker": trade["m"]   # 是否為主動賣方
            })
        
        
        start_time = data[-1]["T"] + 1
        time.sleep(0.2)  

    return pd.DataFrame(all_trades)
#fomc_dates = ["2024-11-08", "2024-09-19", "2024-05-02", "2023-07-27", "2023-05-04", "2023-03-23", 
#"2023-02-02"(抓不到), "2022-12-15", "2022-11-03", 
    #"2022-09-22", "2022-07-28"

# 日期設定
fomc_date = "2022-12-15"
symbol = "BTCUSDT"  

# 抓取時間：公告前與公告後（）
start_time = pd.Timestamp(fomc_date) - pd.Timedelta(days=1)
end_time = pd.Timestamp(fomc_date) + pd.Timedelta(days=1)

start_time_ms = int(start_time.timestamp() * 1000)
end_time_ms = int(end_time.timestamp() * 1000)

# 抓取數據
print(f"正在抓取 {fomc_date} 的數據...")
trades_data = fetch_historical_trades(symbol, start_time_ms, end_time_ms)

# 將數據保存到 CSV 文件
output_file = f"D:\\NSYSU FIN\\bitcoin\\for_git\\BTC_trades_{fomc_date}.csv"
trades_data['timestamp'] = pd.to_datetime(trades_data['timestamp'], unit='ms')  # 轉換時間戳
trades_data.to_csv(output_file, index=False)
print(f"{fomc_date} 的數據已保存到 {output_file}")

# %%
import pandas as pd
import matplotlib.pyplot as plt

# 讀取資料
file_path = "D:/NSYSU FIN/bitcoin/for_git/BTC_PIN_with_dummies.csv"
data = pd.read_csv(file_path)

# 確保 'interval' 欄位格式正確
# 修改日期格式
data['interval'] = pd.to_datetime(data['interval'], format="%Y/%m/%d %H:%M")


# 排除 PIN 為 0 的資料
data = data[data['PIN'] != 0]

# 提取 FOMC 公告時間的日期與時間
fomc_times = [
    {"date": "2023-03-23", "time": "14:00:00"},
    {"date": "2023-05-04", "time": "14:00:00"},
    {"date": "2023-07-27", "time": "14:00:00"},
    {"date": "2024-05-02", "time": "14:00:00"},
    {"date": "2024-09-19", "time": "14:00:00"},
    {"date": "2024-11-08", "time": "14:00:00"}
]

# 繪製每次 FOMC 公告的圖
for fomc in fomc_times:
    fomc_datetime = pd.Timestamp(f"{fomc['date']} {fomc['time']}")
    
    # 選取前後 15 分鐘的資料
    time_window = data[(data['interval'] >= fomc_datetime - pd.Timedelta(minutes=15)) &
                       (data['interval'] <= fomc_datetime + pd.Timedelta(minutes=15))]
    
    # 繪圖
    plt.figure(figsize=(10, 6))
    plt.plot(time_window['interval'], time_window['PIN'], marker='o', label="PIN", color="blue")
    plt.axvline(fomc_datetime, color='red', linestyle='--', label="FOMC Time")
    plt.title(f"PIN Around FOMC Announcement ({fomc['date']} {fomc['time']})")
    plt.xlabel("Time")
    plt.ylabel("PIN Value")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    
    # 儲存圖片
    output_path = f"D:/NSYSU FIN/bitcoin/pin/PIN_FOMC_{fomc['date']}_{fomc['time'].replace(':', '')}.png"
    plt.savefig(output_path)
    plt.show()

    print(f"圖表已儲存至 {output_path}")
# %%

import pandas as pd
import matplotlib.pyplot as plt

# 加載數據
file_path = "D:/NSYSU FIN/bitcoin/pin/BTC_PIN_with_dummies.csv"
data = pd.read_csv(file_path)

# 確保 interval 格式正確
data['interval'] = pd.to_datetime(data['interval'], format='%Y-%m-%d %H:%M')
data['interval'] = pd.to_datetime(data['interval'], infer_datetime_format=True, errors='coerce')

# 篩選掉 PIN 為 0 的數據
data = data[data['PIN'] != 0]

# 定義每次 FOMC 公告時間
fomc_times = [
    "2023-03-23 14:00:00", 
    "2023-05-04 14:00:00",
    "2023-07-27 14:00:00",
    "2024-09-19 14:00:00", 
    "2024-11-08 14:00:00"
]
fomc_times = pd.to_datetime(fomc_times)

# 遍歷 FOMC 公告時間，繪製每次公告的 PIN 變化
for fomc_time in fomc_times:
    # 篩選時間範圍（公告前後 1 小時）
    time_range = (data['interval'] >= fomc_time - pd.Timedelta(hours=1)) & (data['interval'] <= fomc_time + pd.Timedelta(hours=1))
    subset = data[time_range]

    # 繪圖
    plt.figure(figsize=(10, 6))
    plt.plot(subset['interval'], subset['PIN'], marker='o', label='PIN')
    plt.axvline(fomc_time, color='red', linestyle='--', label='FOMC Time')
    plt.title(f"PIN Around FOMC Announcement ({fomc_time})")
    plt.xlabel("Time")
    plt.ylabel("PIN Value")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
# %%

import pandas as pd
import matplotlib.pyplot as plt

# 載入資料
file_path = "D:/NSYSU FIN/bitcoin/pin/BTC_PIN_with_dummies.csv"
data = pd.read_csv(file_path)

# 格式化時間
data['interval'] = pd.to_datetime(data['interval'], infer_datetime_format=True, errors='coerce')

# 定義 FOMC 公告時間
fomc_times = [
    "2023-03-23 14:00:00",
    "2023-05-04 14:00:00",
    "2023-07-27 14:00:00",
    "2024-09-19 14:00:00",
    "2024-11-08 14:00:00"
]
fomc_times = pd.to_datetime(fomc_times)

# 過濾 PIN 不為 0 的數據
data = data[data['PIN'] != 0]

for date in fomc_times:
    fomc_time = pd.Timestamp(date)
    start_time = fomc_time - pd.Timedelta(hours=24)
    end_time = fomc_time + pd.Timedelta(hours=24)

    # 篩選目標時間範圍內的數據
    subset = data[(data['interval'] >= start_time) & (data['interval'] <= end_time) & (data['PIN'] != 0)]

    plt.figure(figsize=(14, 7))
    plt.plot(subset['interval'], subset['PIN'], linestyle='-', linewidth=2, color='navy', label='PIN')  # 平滑曲線，移除點
    plt.axvline(x=fomc_time, color='red', linestyle='--', linewidth=2, label='FOMC Time')  # FOMC 時間垂直線

    # 設定圖表標題與標籤
    plt.title(f"PIN Around FOMC Announcement ({fomc_time})", fontsize=16,weight='bold')
    plt.xlabel("Time", fontsize=14)
    plt.ylabel("PIN Value", fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(visible=True, linestyle='--', linewidth=0.5)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
    
    # 儲存圖表
    output_path = f"D:/NSYSU FIN/bitcoin/pin/PIN_FOMC_{fomc_time.date()}.png"
    plt.savefig(output_path)
    plt.show()

# %%

import requests
import pandas as pd
from datetime import datetime, timedelta

# API Key
api_key = "MY"

# 定義前 10 大加密貨幣和權重（假設均等權重）
cryptos = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "AVAX", "MATIC"]
weights = [0.1] * 10  # 均等權重

# 定義研究時間區間（根據你的研究需求）
study_periods = [
    {"start": "2023-03-22 00:00:00", "end": "2023-03-23 23:59:59"},
    {"start": "2023-05-03 00:00:00", "end": "2023-05-04 23:59:59"},
    {"start": "2023-07-25 00:00:00", "end": "2023-07-26 23:59:59"},
    {"start": "2024-05-01 00:00:00", "end": "2024-05-02 23:59:59"},
    {"start": "2024-09-18 00:00:00", "end": "2024-09-19 23:59:59"},
    {"start": "2024-11-07 00:00:00", "end": "2024-11-08 23:59:59"}
]

# 初始化結果 DataFrame
final_data = []

# 抓取數據並計算 CMI10 指數
for period in study_periods:
    start_time = datetime.strptime(period["start"], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(period["end"], "%Y-%m-%d %H:%M:%S")
    current_time = start_time

    while current_time <= end_time:
        prices = []
        # 從 API 抓取每個加密貨幣的價格
        for coin in cryptos:
            url = f"https://min-api.cryptocompare.com/data/v2/histominute"
            params = {
                "fsym": coin,
                "tsym": "USD",
                "limit": 1,
                "toTs": int(current_time.timestamp()),
                "api_key": api_key
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data["Response"] == "Success":
                price = data["Data"]["Data"][-1]["close"]
                prices.append(price)
            else:
                print(f"Error fetching {coin} at {current_time}: {data['Message']}")
                prices.append(None)

        # 計算 CMI10 指數
        if None not in prices:
# %%
            cmi10_value = sum(price * weight for price, weight in zip(prices, weights))

            final_data.append({"timestamp": current_time, "CMI10": cmi10_value})
        else:
            print(f"Missing data for {current_time}, skipping...")

        current_time += timedelta(minutes=15)  # 每 15 分鐘更新

# 將結果存入 DataFrame 並輸出 CSV
result_df = pd.DataFrame(final_data)
result_df.to_csv("CMI10_index_results.csv", index=False)
print("CMI10 指數數據已儲存至 CMI10_index_results.csv")

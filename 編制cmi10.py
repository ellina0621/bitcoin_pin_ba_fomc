import requests
import pandas as pd
from datetime import datetime, timedelta

# API Key
api_key = "MY"

# 定義前 10 大加密貨幣和權重，這裡假設等權
cryptos = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "AVAX", "MATIC"]
weights = [0.1] * 10  # 均等權重

# 定義研究時間區間
study_periods = [
    {"start": "2023-03-22 00:00:00", "end": "2023-03-23 23:59:59"},
    {"start": "2023-05-03 00:00:00", "end": "2023-05-04 23:59:59"},
    {"start": "2023-07-25 00:00:00", "end": "2023-07-26 23:59:59"},
    {"start": "2024-05-01 00:00:00", "end": "2024-05-02 23:59:59"},
    {"start": "2024-09-18 00:00:00", "end": "2024-09-19 23:59:59"},
    {"start": "2024-11-07 00:00:00", "end": "2024-11-08 23:59:59"}
]

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
            cmi10_value = sum(price * weight for price, weight in zip(prices, weights))

            final_data.append({"timestamp": current_time, "CMI10": cmi10_value})
        else:
            print(f"Missing data for {current_time}, skipping...")

        current_time += timedelta(minutes=15)  # 每 15 分鐘更新

result_df = pd.DataFrame(final_data)
result_df.to_csv("D:/NSYSU FIN/bitcoin/for_git/CMI10_index_results.csv", index=False)
print("finish")

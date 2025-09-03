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

# 抓取時間：公告前與公告後（等於公告前一日00:00:00到公告日23:59:00）
start_time = pd.Timestamp(fomc_date) - pd.Timedelta(days=1)
end_time = pd.Timestamp(fomc_date) + pd.Timedelta(days=1)

start_time_ms = int(start_time.timestamp() * 1000)
end_time_ms = int(end_time.timestamp() * 1000)

# 抓取數據
print(f"正在抓取 {fomc_date} 的數據...")
trades_data = fetch_historical_trades(symbol, start_time_ms, end_time_ms)

output_file = f"D:\\NSYSU FIN\\bitcoin\\for_git\\BTC_trades_{fomc_date}.csv"
trades_data['timestamp'] = pd.to_datetime(trades_data['timestamp'], unit='ms')  # 轉換時間戳
trades_data.to_csv(output_file, index=False)
print(f"{fomc_date} 的數據已保存到 {output_file}")


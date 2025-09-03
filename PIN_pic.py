import pandas as pd
import matplotlib.pyplot as plt

file_path = "D:/NSYSU FIN/bitcoin/for_git/BTC_PIN_with_dummies.csv"
data = pd.read_csv(file_path)
data['interval'] = pd.to_datetime(data['interval'], format="%Y/%m/%d %H:%M")
data = data[data['PIN'] != 0]# 排除 PIN 為 0 的資料

#print(data.head())

# 抓取FOMC 公告時間的日期與時間
fomc_times = [
    {"date": "2023-03-23", "time": "14:00:00"},
    {"date": "2023-05-04", "time": "14:00:00"},
    {"date": "2023-07-27", "time": "14:00:00"},
    {"date": "2024-05-02", "time": "14:00:00"},
    {"date": "2024-09-19", "time": "14:00:00"},
    {"date": "2024-11-08", "time": "14:00:00"}
]
### (1) 15 min前後，繪製 FOMC 公告的圖###
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
    output_path = f"D:/NSYSU FIN/bitcoin/for_git/PIN_FOMC_15min_{fomc['date']}_{fomc['time'].replace(':', '')}.png"
    plt.savefig(output_path)
    plt.show()

    print(f"圖表已儲存至 {output_path}")

### (2) 1hr 前後，繪製 FOMC 公告的圖###
for fomc in fomc_times:
    fomc_datetime = pd.Timestamp(f"{fomc['date']} {fomc['time']}")
    
    # 選取前後 15 分鐘的資料
    time_window = data[(data['interval'] >= fomc_datetime - pd.Timedelta(minutes=60)) &
                       (data['interval'] <= fomc_datetime + pd.Timedelta(minutes=60))]
    
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
    output_path = f"D:/NSYSU FIN/bitcoin/for_git/PIN_FOMC_60min_{fomc['date']}_{fomc['time'].replace(':', '')}.png"
    plt.savefig(output_path)
    plt.show()

    print(f"圖表已儲存至 {output_path}")



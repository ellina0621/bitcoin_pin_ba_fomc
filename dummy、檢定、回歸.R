########報酬率與pin計算#############
library(dplyr)
library(lubridate)

#這個當初是手動更改日期，已將所有檔案放入資料夾#

file_path <- "D:\\NSYSU FIN\\bitcoin\\for_git\\BTC_trades_2024-05-02.csv"
data <- read.csv(file_path)
data$timestamp <- as.POSIXct(data$timestamp, format = "%Y-%m-%d %H:%M:%OS", tz = "UTC")

# 按 15 分鐘區間分組
data <- data %>%
  mutate(interval = floor_date(timestamp, "15 minutes"))  # 將時間戳分為 15 分鐘區間

# 根據 is_buyer_maker 更新 direction 欄位
data <- data %>%
  mutate(
    is_buyer_maker = as.logical(is_buyer_maker),  # 將字串轉為布林值
    direction = ifelse(is_buyer_maker == TRUE, "Sell", "Buy")  # 買方掛單被吃掉，因此true 為sell
  )

# 計算每個區間的價格加權平均價（VWAP）
interval_data <- data %>%
  group_by(interval) %>%
  summarize(
    BuyVolume = sum(quantity[direction == "Buy"], na.rm = TRUE),
    SellVolume = sum(quantity[direction == "Sell"], na.rm = TRUE),
    VWAP = sum(price * quantity, na.rm = TRUE) / sum(quantity, na.rm = TRUE)  # 計算加權平均價
  )

# 計算報酬率
interval_data <- interval_data %>%
  arrange(interval) %>%
  mutate(
    Return = (VWAP - lag(VWAP)) / lag(VWAP) 
  )

# 定義 PIN 的最大似然估計函數
estimate_pin <- function(BuyVolume, SellVolume) {
  # 設定最低交易量以避免 NA
  BuyVolume <- ifelse(BuyVolume < 5, 5, BuyVolume)
  SellVolume <- ifelse(SellVolume < 5, 5, SellVolume)
  
  # 動態初始參數
  initial_params <- c(
    alpha = 0.5,
    mu = max(10, mean(c(BuyVolume, SellVolume)) / 2),
    epsilon = max(1, mean(c(BuyVolume, SellVolume)) / 10)
  )
  
  # 邊界
  lower_bounds <- c(0.05, 1, 0.1)
  upper_bounds <- c(0.95, 100, 50)
  
  # 定義似然函數
  likelihood <- function(params) {
    alpha <- params[1]
    mu <- params[2]
    epsilon <- params[3]
    
    if (alpha <= 0 || alpha >= 1 || mu <= 0 || epsilon <= 0) {
      return(Inf)
    }
    
    informed_buy <- dgamma(BuyVolume, shape = (mu + epsilon)^2 / (mu + epsilon), scale = mu + epsilon)
    uninformed_buy <- dgamma(BuyVolume, shape = epsilon^2 / epsilon, scale = epsilon)
    informed_sell <- dgamma(SellVolume, shape = epsilon^2 / epsilon, scale = epsilon)
    uninformed_sell <- dgamma(SellVolume, shape = epsilon^2 / epsilon, scale = epsilon)
    
    informed <- alpha * informed_buy * informed_sell
    uninformed <- (1 - alpha) * uninformed_buy * uninformed_sell
    total_probability <- informed + uninformed
    
    if (any(is.nan(total_probability)) || any(total_probability <= 0, na.rm = TRUE)) {
      return(Inf)
    }
    
    return(-sum(log(total_probability), na.rm = TRUE))
  }
  
  # 捕獲優化過程中的錯誤
  result <- tryCatch(
    {
      optim(
        par = initial_params,
        fn = likelihood,
        method = "L-BFGS-B",
        lower = lower_bounds,
        upper = upper_bounds,
        control = list(maxit = 500)
      )
    },
    error = function(e) {
      return(NULL)
    }
  )
  
  # 返回結果
  if (is.null(result) || result$convergence != 0) {
    return(0)  # 用 0 填補失敗的情況
  }
  
  alpha <- result$par[1]
  mu <- result$par[2]
  epsilon <- result$par[3]
  pin <- alpha * mu / (alpha * mu + 2 * epsilon)
  
  return(pin)
}


# 計算每個區間的 PIN
interval_data <- interval_data %>%
  rowwise() %>%
  mutate(
    PIN = ifelse(
      BuyVolume > 0 & SellVolume > 0,
      estimate_pin(BuyVolume, SellVolume),
      NA
    )
  )

# 保存結果
output_file <- "D:\\NSYSU FIN\\bitcoin\\for_git\\BTC_PIN_results_20240502.csv"
write.csv(interval_data, output_file, row.names = FALSE)
print(paste("結果已保存到檔案:", output_file))




###########合併檔案###################
setwd("D:/NSYSU FIN/bitcoin/for_git")

file_paths <- list.files(pattern = "BTC_PIN_results_.*\\.csv")

combined_data <- file_paths %>%
  lapply(read.csv) %>%
  bind_rows(.id = "source_file") 

output_file <- "BTC_PIN_combined_results.csv"
write.csv(combined_data, output_file, row.names = FALSE)

#######dummy############
file_path <- "D:/NSYSU FIN/bitcoin/for_git/BTC_PIN_combined_results.csv"
data <- read.csv(file_path)

# 定義 FOMC 公告日期和時間
fomc_dates <- data.frame(
  date = as.Date(c("2023-03-23", "2023-05-04", "2023-07-27", "2024-05-02", "2024-09-19", "2024-11-08")),
  time = "14:00:00"
)

fomc_dates$datetime <- as.POSIXct(paste(fomc_dates$date, fomc_dates$time), format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
data <- data %>%
  mutate(
    interval = ymd_hms(interval),       
    date = as.Date(interval),           
    time = format(interval, "%H:%M:%S") 
  )


#head(data[, c("interval", "date", "time")])

#這裡都設置一小時作為觀察
data <- data %>%
  mutate(
    # 公告前一天 (前一天整天)
    FOMC_PreviousDay = ifelse(date %in% (fomc_dates$date - 1), 1, 0),
    
    # 公告前 (公告日 00:00 到 14:00)
    FOMC_Before = ifelse(date %in% fomc_dates$date & time < "14:00:00", 1, 0),
    
    # 公告中 (公告日 14:00 到 15:00)
    FOMC_During = ifelse(date %in% fomc_dates$date & time >= "14:00:00" & time < "15:00:00", 1, 0),
    
    # 公告後 (公告日 15:00 到 23:59)
    FOMC_After = ifelse(date %in% fomc_dates$date & time >= "15:00:00", 1, 0)
  )

# 確認結果
table(data$FOMC_PreviousDay)
table(data$FOMC_Before)
table(data$FOMC_During)
table(data$FOMC_After)
write.csv(data, "D:\\NSYSU FIN\\bitcoin\\for_git\\BTC_PIN_with_dummies.csv", row.names = FALSE)


#######回歸1##########
filtered_data <- data %>%
  filter(PIN != 0)

print(paste("篩選後剩餘觀測值數量:", nrow(filtered_data)))

#  以FOMC_After 為基準
filtered_data <- filtered_data %>%
  mutate(
    FOMC_PreviousDay = as.factor(FOMC_PreviousDay),
    FOMC_Before = as.factor(FOMC_Before),
    FOMC_During = as.factor(FOMC_During),
    FOMC_After = as.factor(FOMC_After)
  ) %>%
  mutate(FOMC_After = relevel(FOMC_After, ref = "0"))  # 設定 FOMC_After = 0 為基準類別

# 建立回歸模型 (PIN 為因變數，移除 FOMC_After 作為基準)
model <- lm(PIN ~ FOMC_PreviousDay + FOMC_Before + FOMC_During, data = filtered_data)

# 檢視回歸結果
summary(model)

############回歸式2############

hike_days <- as.Date(c("2023-03-23", "2023-05-04", "2023-07-27"))

#05/02放緩縮表，維持利率，視為未來可能降息
cut_days  <- as.Date(c("2024-05-02", "2024-09-19", "2024-11-08"))

data <- data %>%
  mutate(Rate = case_when(
    date %in% c(hike_days, hike_days - 1) ~ 1,   # 升息日 & 前一天 = 1
    date %in% c(cut_days,  cut_days  - 1) ~ 0,   # 降息日 & 前一天 = 0
    TRUE ~ NA_real_                           # 其他日 NA
  ))
# 篩選掉 Return 為 NA 並加入前一期pin，看是否仍顯著
filtered_data <- data %>%
  filter(!is.na(Return), PIN != 0) %>%
  arrange(interval) %>%
  mutate(
    PIN_Lag1 = lag(PIN, 1)  # 計算 PIN 的一階滯後
  )

# 回歸分析
model <- lm(Return ~ PIN * FOMC_Before + PIN * FOMC_During + PIN * FOMC_After +
              Rate + PIN + PIN_Lag1, data = filtered_data)

# 檢視回歸結果
summary(model)

####增加波動####
#最後記得沒用XD
data$Return <- as.numeric(data$Return)

window <- 4 #要滾多少

data <- data %>%
  mutate(Volatility = zoo::rollapply(Return, width = window, FUN = sd, fill = NA, align = "right"))

data <- data %>%
  mutate(volume = BuyVolume + SellVolume)

#head(data)

write.csv(data, "D:/NSYSU FIN/bitcoin/for_git/BTC_PIN_with_dummies.csv", row.names = FALSE)

##########穩健性########
library(dplyr)
library(lmtest)       # 自相關檢定
library(car)          # 異質性檢定與VIF檢查
library(sandwich)     # 穩健標準誤
library(stargazer)    # 輸出回歸結果
library(tseries)      # 單位根檢定
library(plm)
filtered_data <- data %>%
  filter(!is.na(Return), PIN != 0) %>%
  arrange(interval) %>%
  mutate(
    PIN_Lag1 = lag(PIN, 1),      # 計算 PIN 的一階滯後
    Return_Lag1 = lag(Return, 1) # 計算 Return 的一階滯後
  )

# 檢查資料清潔後的前幾筆數據
head(filtered_data)

############ 回歸式2 ############
# 模型 1: 基本回歸
model1 <- lm(Return ~ PIN + Rate + PIN_Lag1 + Return_Lag1, data = filtered_data)

# 模型 2: 加入 FOMC Dummy 變數
model2 <- lm(Return ~ PIN + FOMC_Before + FOMC_During +
               Rate + PIN_Lag1 + Return_Lag1, data = filtered_data)

# 模型 3: 加入 PIN 與 FOMC 交乘項
model3 <- lm(Return ~ PIN * FOMC_Before + PIN * FOMC_During +
               Rate + PIN_Lag1 + Return_Lag1, data = filtered_data)

# 查看回歸結果
summary(model1)
summary(model2)
summary(model3)

############ 穩定性檢定 ############

# 1. 異質性檢定 (Breusch-Pagan Test)
bptest(model3)

# 2. 多重共線性檢定 (VIF)，dummy有共線性問題
vif(model3, type = "predictor") 

# 3. 殘差自相關檢定 (Durbin-Watson Test)，時間序列上沒問題
dwtest(model3)

# 4. 單位根檢定 (ADF Test) - 檢查 Return 是否穩定
adf.test(filtered_data$Return, alternative = "stationary")

# 5.用Newey–West 修正標準誤
model3 <- lm(Return ~ PIN*FOMC_Before + PIN*FOMC_During + 
               Rate + PIN + PIN_Lag1 + Return_Lag1, data = filtered_data)

nw <- NeweyWest(model3, lag = 4, prewhite = FALSE, adjust = TRUE)
coeftest(model3, vcov. = nw)


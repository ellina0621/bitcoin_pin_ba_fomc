# 載入必要套件
library(ggplot2)
library(dplyr)
library(readr)

data <- read_csv("D:/NSYSU FIN/bitcoin/for_git/BTC_PIN_with_dummies.csv")


data$interval <- as.POSIXct(data$interval, format = "%Y/%m/%d %H:%M", tz = "UTC")


event_times <- list(
  "Event 1" = as.POSIXct("2023-03-23 14:15", tz = "UTC"),
  "Event 2" = as.POSIXct("2023-05-04 14:15", tz = "UTC"),
  "Event 3" = as.POSIXct("2023-07-27 14:15", tz = "UTC"),
  "Event 4" = as.POSIXct("2024-05-02 14:15", tz = "UTC"),
  "Event 5" = as.POSIXct("2024-09-19 14:15", tz = "UTC"),
  "Event 6" = as.POSIXct("2024-11-08 14:15", tz = "UTC")
)

standardize <- function(x) {
  (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)
}


for (i in seq_along(event_times)) {
  event_name <- names(event_times)[i]
  t0_time <- event_times[[i]]
  

  data_filtered <- data %>%
    mutate(t_relative = as.numeric(difftime(interval, t0_time, units = "mins") / 15)) %>%
    filter(t_relative >= -30 & t_relative <= 30) %>% # 保留 T=-10 到 T=10 的數據
    mutate(CAR_std = standardize(CAR),  # 標準化 CAR
           PIN_std = standardize(PIN))  # 標準化 PIN
  
  plot <- ggplot(data_filtered, aes(x = t_relative)) +
    geom_line(aes(y = CAR_std, color = "CAR (Standardized)"), size = 1) +
    geom_line(aes(y = PIN_std, color = "PIN (Standardized)"), linetype = "dashed", size = 1) +
    geom_vline(xintercept = 0, color = "black", linetype = "dashed") +
    labs(title = paste("Standardized CAR and PIN for", event_name, "on", format(t0_time, "%Y-%m-%d")),
         x = "Relative Time (T=0 at 14:15)", 
         y = "Standardized Values",
         color = "") +
    theme_minimal() +
    theme(legend.position = "bottom")
  

  print(plot)
  

  ggsave(
    filename = paste0("D:/NSYSU FIN/bitcoin/for_git/Standardized_CAR_PIN_", event_name, ".png"),
    plot = plot,
    width = 8,
    height = 6
  )
}


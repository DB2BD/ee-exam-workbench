#!/bin/bash
# 設置 macOS 本機 Crontab 每日上午 08:30 自動執行爬蟲與情報庫更新

PROJECT_DIR="/Users/a/技師考試/歷屆試題_104-114年"
CRAWLER_SCRIPT="$PROJECT_DIR/scripts/au_job_radar_crawler.py"
LOG_FILE="$PROJECT_DIR/scripts/au_job_crawler.log"

CRON_JOB="30 8 * * * /usr/bin/python3 $CRAWLER_SCRIPT >> $LOG_FILE 2>&1"

# 檢查是否已有相同排程
crontab -l 2>/dev/null | grep -F "$CRAWLER_SCRIPT" >/dev/null

if [ $? -eq 0 ]; then
    echo "ℹ️ macOS 本機 Crontab 每日自動爬蟲排程已存在，無需重複新增。"
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ 成功新增 macOS Crontab 每日 08:30 AM 自動爬蟲排程！"
    echo "📄 執行日誌將自動記錄於: $LOG_FILE"
fi

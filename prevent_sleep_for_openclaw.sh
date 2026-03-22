#!/bin/bash

# 脚本：当 OpenClaw 运行时阻止 Mac 睡眠
# 使用方法：./prevent_sleep_for_openclaw.sh start|stop

PID_FILE="/tmp/openclaw_caffeinate.pid"
LOG_FILE="/tmp/openclaw_caffeinate.log"

case "$1" in
    start)
        echo "$(date): 开始阻止睡眠，因为 OpenClaw 正在运行" >> "$LOG_FILE"
        
        # 使用 caffeinate 阻止系统睡眠
        # -i 阻止空闲睡眠
        # -s 阻止系统睡眠
        # -w 等待进程结束
        caffeinate -i -s -w $$ &
        CAFFEINATE_PID=$!
        
        echo "$CAFFEINATE_PID" > "$PID_FILE"
        echo "$(date): caffeinate 进程已启动，PID: $CAFFEINATE_PID" >> "$LOG_FILE"
        echo "已启动 caffeinate 进程 (PID: $CAFFEINATE_PID) 来阻止睡眠"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            CAFFEINATE_PID=$(cat "$PID_FILE")
            echo "$(date): 停止 caffeinate 进程 (PID: $CAFFEINATE_PID)" >> "$LOG_FILE"
            
            if kill "$CAFFEINATE_PID" 2>/dev/null; then
                echo "已停止 caffeinate 进程 (PID: $CAFFEINATE_PID)"
                rm "$PID_FILE"
            else
                echo "无法停止进程 $CAFFEINATE_PID，可能已终止"
                rm "$PID_FILE"
            fi
        else
            echo "没有找到运行的 caffeinate 进程"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ]; then
            CAFFEINATE_PID=$(cat "$PID_FILE")
            if ps -p "$CAFFEINATE_PID" > /dev/null; then
                echo "caffeinate 正在运行 (PID: $CAFFEINATE_PID)"
                echo "查看日志: $LOG_FILE"
            else
                echo "caffeinate 进程文件存在但进程未运行"
                rm "$PID_FILE"
            fi
        else
            echo "caffeinate 未运行"
        fi
        ;;
        
    *)
        echo "使用方法: $0 {start|stop|status}"
        exit 1
        ;;
esac
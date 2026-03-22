#!/bin/bash

# 当 OpenClaw 运行时保持 Mac 唤醒
# 这个脚本会持续运行，当检测到 OpenClaw 网关进程时阻止睡眠

echo "=== OpenClaw 睡眠阻止器 ==="
echo "当 OpenClaw 运行时，此脚本会阻止 Mac 进入睡眠模式"
echo "按 Ctrl+C 停止"

# 检查 caffeinate 是否可用
if ! command -v caffeinate &> /dev/null; then
    echo "错误: caffeinate 命令不可用"
    exit 1
fi

# 创建日志文件
LOG_FILE="/tmp/openclaw_keep_awake.log"
echo "$(date): 脚本启动" >> "$LOG_FILE"

# 主循环
while true; do
    # 检查 OpenClaw 网关是否在运行
    if pgrep -f "openclaw-gateway" > /dev/null; then
        # OpenClaw 在运行，检查是否已经有 caffeinate 进程
        if ! pgrep -f "caffeinate.*openclaw" > /dev/null; then
            echo "$(date): OpenClaw 正在运行，启动 caffeinate 阻止睡眠" >> "$LOG_FILE"
            echo "检测到 OpenClaw 正在运行，开始阻止睡眠..."
            
            # 启动 caffeinate
            # -i: 阻止空闲睡眠
            # -s: 阻止系统睡眠  
            # -d: 阻止显示器睡眠
            # 在后台运行，并标记为 openclaw 相关
            caffeinate -i -s -d &
            CAFFEINATE_PID=$!
            echo "$CAFFEINATE_PID" > /tmp/openclaw_caffeinate.pid
            echo "caffeinate 已启动 (PID: $CAFFEINATE_PID)"
        fi
    else
        # OpenClaw 不在运行，检查是否有 caffeinate 进程需要停止
        if [ -f /tmp/openclaw_caffeinate.pid ]; then
            CAFFEINATE_PID=$(cat /tmp/openclaw_caffeinate.pid)
            if kill -0 "$CAFFEINATE_PID" 2>/dev/null; then
                echo "$(date): OpenClaw 已停止，停止 caffeinate" >> "$LOG_FILE"
                echo "OpenClaw 已停止，允许睡眠..."
                kill "$CAFFEINATE_PID"
                rm /tmp/openclaw_caffeinate.pid
            fi
        fi
    fi
    
    # 等待10秒后再次检查
    sleep 10
done
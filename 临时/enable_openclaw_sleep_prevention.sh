#!/bin/bash

# OpenClaw 睡眠阻止启用脚本
# 一键启用/禁用 OpenClaw 运行时的睡眠阻止

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/openclaw_sleep_prevent.pid"
LOG_FILE="/tmp/openclaw_sleep_prevent.log"

function log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

function start_prevention() {
    log "=== 启动 OpenClaw 睡眠阻止 ==="
    
    # 检查是否已经在运行
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "睡眠阻止已经在运行 (PID: $PID)"
            return 0
        fi
    fi
    
    # 启动 caffeinate
    log "启动 caffeinate 进程..."
    caffeinate -i -s -d &
    CAFFEINATE_PID=$!
    
    echo "$CAFFEINATE_PID" > "$PID_FILE"
    log "caffeinate 已启动 (PID: $CAFFEINATE_PID)"
    log "Mac 现在不会进入睡眠模式"
    
    # 显示状态
    echo ""
    echo "✅ 睡眠阻止已启用"
    echo "   进程ID: $CAFFEINATE_PID"
    echo "   日志文件: $LOG_FILE"
    echo ""
    echo "要停止，运行: $0 stop"
}

function stop_prevention() {
    log "=== 停止 OpenClaw 睡眠阻止 ==="
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log "已停止 caffeinate 进程 (PID: $PID)"
            echo "✅ 睡眠阻止已禁用"
        else
            log "进程 $PID 不存在"
            echo "⚠️  进程不存在，但清理了 PID 文件"
        fi
        rm -f "$PID_FILE"
    else
        log "没有找到运行的进程"
        echo "ℹ️  没有找到运行的睡眠阻止进程"
    fi
    
    # 也停止任何其他 caffeinate 进程
    pkill -f "caffeinate.*openclaw" 2>/dev/null || true
}

function status() {
    echo "=== OpenClaw 睡眠阻止状态 ==="
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✅ 正在运行 (PID: $PID)"
            echo "   日志: $LOG_FILE"
            echo "   启动时间: $(ps -p "$PID" -o lstart= 2>/dev/null || echo '未知')"
        else
            echo "❌ 进程文件存在但进程未运行"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ 未运行"
    fi
    
    # 检查系统断言
    echo ""
    echo "系统电源管理断言:"
    pmset -g assertions | grep -A2 caffeinate || echo "   没有 caffeinate 断言"
}

function install_service() {
    echo "=== 安装 LaunchAgent 服务 ==="
    
    SERVICE_PLIST="$HOME/Library/LaunchAgents/com.niejq.openclaw.prevent-sleep.plist"
    
    cat > "$SERVICE_PLIST" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.niejq.openclaw.prevent-sleep</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>while pgrep -f "openclaw-gateway" > /dev/null; do caffeinate -i -s -d; sleep 30; done</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw-sleep-prevent-service.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-sleep-prevent-service.err</string>
</dict>
</plist>
EOF
    
    echo "服务配置文件已创建: $SERVICE_PLIST"
    
    # 加载服务
    launchctl load "$SERVICE_PLIST" 2>/dev/null || true
    launchctl start com.niejq.openclaw.prevent-sleep 2>/dev/null || true
    
    echo "✅ LaunchAgent 服务已安装并启动"
    echo "   日志: /tmp/openclaw-sleep-prevent-service.log"
}

function uninstall_service() {
    echo "=== 卸载 LaunchAgent 服务 ==="
    
    SERVICE_PLIST="$HOME/Library/LaunchAgents/com.niejq.openclaw.prevent-sleep.plist"
    
    if [ -f "$SERVICE_PLIST" ]; then
        launchctl stop com.niejq.openclaw.prevent-sleep 2>/dev/null || true
        launchctl unload "$SERVICE_PLIST" 2>/dev/null || true
        rm -f "$SERVICE_PLIST"
        echo "✅ 服务已卸载"
    else
        echo "ℹ️  服务未安装"
    fi
}

# 主逻辑
case "${1:-}" in
    start)
        start_prevention
        ;;
    stop)
        stop_prevention
        ;;
    status)
        status
        ;;
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    *)
        echo "OpenClaw 睡眠阻止管理器"
        echo ""
        echo "使用方法: $0 {start|stop|status|install|uninstall}"
        echo ""
        echo "命令:"
        echo "  start     启动睡眠阻止"
        echo "  stop      停止睡眠阻止"
        echo "  status    查看当前状态"
        echo "  install   安装自动启动服务"
        echo "  uninstall 卸载自动启动服务"
        echo ""
        echo "当前状态:"
        status
        exit 1
        ;;
esac
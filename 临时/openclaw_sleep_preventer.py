#!/usr/bin/env python3
"""
OpenClaw 睡眠阻止器
当 OpenClaw 网关运行时阻止 Mac 进入睡眠
"""

import subprocess
import time
import os
import signal
import sys
from datetime import datetime

LOG_FILE = "/tmp/openclaw_sleep_preventer.log"
PID_FILE = "/tmp/openclaw_sleep_preventer.pid"

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def is_openclaw_running():
    """检查 OpenClaw 网关是否在运行"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "openclaw-gateway"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except Exception as e:
        log_message(f"检查 OpenClaw 状态时出错: {e}")
        return False

def start_caffeinate():
    """启动 caffeinate 进程"""
    try:
        # 启动 caffeinate 阻止所有睡眠
        # -i: 阻止空闲睡眠
        # -s: 阻止系统睡眠
        # -d: 阻止显示器睡眠
        process = subprocess.Popen(
            ["caffeinate", "-i", "-s", "-d"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        
        log_message(f"已启动 caffeinate 进程 (PID: {process.pid})")
        return process
    except Exception as e:
        log_message(f"启动 caffeinate 失败: {e}")
        return None

def stop_caffeinate():
    """停止 caffeinate 进程"""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pid = f.read().strip()
            
            if pid:
                subprocess.run(["kill", pid], capture_output=True)
                log_message(f"已停止 caffeinate 进程 (PID: {pid})")
            
            os.remove(PID_FILE)
    except Exception as e:
        log_message(f"停止 caffeinate 时出错: {e}")

def main():
    """主函数"""
    log_message("=" * 50)
    log_message("OpenClaw 睡眠阻止器启动")
    
    caffeinate_process = None
    openclaw_was_running = False
    
    try:
        while True:
            openclaw_running = is_openclaw_running()
            
            if openclaw_running and not openclaw_was_running:
                log_message("检测到 OpenClaw 正在运行，开始阻止睡眠")
                caffeinate_process = start_caffeinate()
                openclaw_was_running = True
                
            elif not openclaw_running and openclaw_was_running:
                log_message("OpenClaw 已停止，允许睡眠")
                stop_caffeinate()
                caffeinate_process = None
                openclaw_was_running = False
            
            # 每30秒检查一次
            time.sleep(30)
            
    except KeyboardInterrupt:
        log_message("收到中断信号，正在清理...")
    except Exception as e:
        log_message(f"发生错误: {e}")
    finally:
        stop_caffeinate()
        log_message("OpenClaw 睡眠阻止器已停止")
        log_message("=" * 50)

if __name__ == "__main__":
    main()
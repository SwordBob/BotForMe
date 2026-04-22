# OpenClaw 防止 Mac 睡眠指南

## 当前状态 ✅
**caffeinate 进程已在运行**，正在阻止 Mac 进入睡眠模式。

### 验证命令：
```bash
# 检查 caffeinate 进程
pgrep -f caffeinate

# 检查电源管理断言
pmset -g assertions | grep caffeinate
```

## 手动控制方法

### 1. 启动阻止睡眠
```bash
# 简单启动（后台运行）
caffeinate -i -s -d &

# 详细启动（带日志）
caffeinate -i -s -d -t 86400 &  # 24小时
```

### 2. 停止阻止睡眠
```bash
# 停止所有 caffeinate 进程
pkill caffeinate

# 或停止特定进程
kill [PID]
```

### 3. 检查状态
```bash
# 查看所有阻止睡眠的进程
pmset -g assertions

# 查看 caffeinate 进程
ps aux | grep caffeinate | grep -v grep
```

## 自动化脚本

### 方案一：简单监控脚本
我已经创建了 `keep_mac_awake_with_openclaw.sh`，可以自动检测 OpenClaw 运行状态：

```bash
# 启动监控
./keep_mac_awake_with_openclaw.sh

# 后台运行
nohup ./keep_mac_awake_with_openclaw.sh > /tmp/openclaw_awake.log 2>&1 &
```

### 方案二：Python 守护进程
更智能的解决方案 `openclaw_sleep_preventer.py`：
- 自动检测 OpenClaw 网关进程
- 只在 OpenClaw 运行时阻止睡眠
- 完整的日志记录

```bash
# 运行 Python 守护进程
python3 openclaw_sleep_preventer.py
```

## LaunchAgent 方案（推荐）

创建系统级自动启动服务：

### 1. 创建 LaunchAgent 配置文件
```bash
cat > ~/Library/LaunchAgents/com.user.openclaw.prevent-sleep.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.openclaw.prevent-sleep</string>
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
    <string>/tmp/openclaw-caffeinate.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-caffeinate.err</string>
</dict>
</plist>
EOF
```

### 2. 加载 LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.user.openclaw.prevent-sleep.plist
```

### 3. 管理服务
```bash
# 启动
launchctl start com.user.openclaw.prevent-sleep

# 停止
launchctl stop com.user.openclaw.prevent-sleep

# 查看状态
launchctl list | grep openclaw
```

## 验证效果

### 测试睡眠阻止：
```bash
# 1. 查看当前断言
pmset -g assertions

# 2. 尝试让系统睡眠（应该被阻止）
# 等待10分钟，检查系统是否保持唤醒

# 3. 停止 OpenClaw 后检查
openclaw gateway stop
# 等待30秒，caffeinate 应该自动停止
```

## 故障排除

### 常见问题：
1. **caffeinate 不工作**
   ```bash
   # 检查权限
   ls -la /usr/bin/caffeinate
   
   # 重新安装命令行工具
   xcode-select --install
   ```

2. **LaunchAgent 不启动**
   ```bash
   # 查看日志
   tail -f /tmp/openclaw-caffeinate.log
   
   # 重新加载
   launchctl unload ~/Library/LaunchAgents/com.user.openclaw.prevent-sleep.plist
   launchctl load ~/Library/LaunchAgents/com.user.openclaw.prevent-sleep.plist
   ```

3. **电池模式下的行为**
   ```bash
   # 查看当前电源模式
   pmset -g
   
   # 在电池模式下也阻止睡眠
   caffeinate -i -s -d -u &
   ```

## 注意事项

1. **电池消耗**：阻止睡眠会增加电池消耗
2. **过热风险**：长时间运行可能使设备温度升高
3. **自动恢复**：重启后需要重新启用
4. **与其他应用的兼容性**：某些应用可能有自己的电源管理

## 快速命令参考

```bash
# 一键启用
alias openclaw-keep-awake='caffeinate -i -s -d & echo "睡眠阻止已启用 (PID: $!)"'

# 一键禁用
alias openclaw-allow-sleep='pkill caffeinate && echo "睡眠阻止已禁用"'

# 状态检查
alias openclaw-sleep-status='pmset -g assertions | grep -A2 caffeinate'
```

---

**当前已启用**：caffeinate 正在运行，阻止 Mac 睡眠。要停止，运行 `pkill caffeinate`。
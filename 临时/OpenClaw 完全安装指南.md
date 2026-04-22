# OpenClaw 完全安装指南：打造你的 AI 助手

> 让 AI 真正融入你的生活，从 OpenClaw 开始

---

## 📌 目录

1. [什么是 OpenClaw？](#一什么是-openclaw)
2. [系统要求](#二系统要求)
3. [安装前准备](#三安装前准备)
4. [Mac 安装教程](#四 mac-安装教程)
5. [Windows 安装教程](#五 windows-安装教程)
6. [Linux 安装教程](#六 linux-安装教程)
7. [配置指南](#七配置指南)
8. [模型配置](#八模型配置)
9. [消息渠道配置](#九消息渠道配置)
10. [常见问题](#十常见问题)
11. [进阶使用](#十一进阶使用)

---

## 一、什么是 OpenClaw？

### 简介

**OpenClaw** 是一个开源的 AI 助手框架，让你能够：

- 🤖 **拥有个人 AI 助手** - 24/7 在线，理解你的习惯和偏好
- 📱 **多渠道接入** - WhatsApp、Telegram、Discord、微信等
- 🧠 **多模型支持** - DeepSeek、Qwen、Kimi、Claude 等任意切换
- 📂 **文件操作** - 读写文件、管理文档、自动化任务
- 🌐 **网络搜索** - 实时获取最新信息
- 🤖 **子代理系统** - 多任务并行处理
- 📅 **定时任务** - Cron 调度、提醒、自动化

### 核心特性

| 特性 | 说明 |
|------|------|
| **本地运行** | 数据本地存储，隐私安全 |
| **多模型支持** | 支持主流大模型 API |
| **消息集成** | WhatsApp/Telegram/Discord 等 |
| **文件操作** | 读写、搜索、管理本地文件 |
| **浏览器控制** | 自动化网页操作 |
| **子代理系统** | 多任务并行处理 |
| **定时任务** | Cron 调度、提醒系统 |
| **记忆系统** | 长期记忆 + 短期记忆 |

### 适用场景

```
✓ 个人助理 - 日程管理、提醒、信息整理
✓ 学习助手 - 文档分析、知识整理、答疑解惑
✓ 工作效率 - 文件管理、自动化任务、信息检索
✓ 开发辅助 - 代码审查、文档编写、问题排查
✓ 生活助手 - 天气查询、新闻摘要、音乐推荐
```

---

## 二、系统要求

### 最低配置

| 项目 | 要求 |
|------|------|
| **操作系统** | macOS 10.15+ / Windows 10+ / Linux (Ubuntu 20.04+) |
| **CPU** | 双核处理器 |
| **内存** | 4GB RAM |
| **硬盘** | 2GB 可用空间 |
| **网络** | 稳定的互联网连接 |

### 推荐配置

| 项目 | 要求 |
|------|------|
| **操作系统** | macOS 12+ / Windows 11+ / Linux (Ubuntu 22.04+) |
| **CPU** | 四核处理器 |
| **内存** | 8GB RAM |
| **硬盘** | 10GB 可用空间 (SSD 更佳) |
| **网络** | 宽带连接 |

### 必需软件

```
□ Node.js 18+ (推荐 20+)
□ npm 或 yarn
□ Git (可选，用于克隆仓库)
```

---

## 三、安装前准备

### 步骤 1：安装 Node.js

#### Mac

```bash
# 方法 1：使用 Homebrew (推荐)
brew install node@20

# 验证安装
node --version
npm --version
```

#### Windows

1. 访问 https://nodejs.org
2. 下载 LTS 版本 (推荐 v20.x)
3. 运行安装程序，按提示安装
4. 验证安装：
   ```cmd
   node --version
   npm --version
   ```

#### Linux

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 步骤 2：准备模型 API

OpenClaw 支持多种大模型，选择你需要的：

| 模型 | 提供商 | 申请地址 | 价格参考 |
|------|--------|----------|----------|
| **DeepSeek V3** | DeepSeek | https://platform.deepseek.com | ¥0.5/百万 tokens |
| **Qwen Coder** | 阿里云 | https://dashscope.aliyun.com | ¥2.4/百万 tokens |
| **Kimi** | 月之暗面 | https://platform.moonshot.cn | ¥4.0/百万 tokens |
| **Claude** | Anthropic | https://console.anthropic.com | $3-15/百万 tokens |
| **GPT-4** | OpenAI | https://platform.openai.com | $10-30/百万 tokens |

**建议：** 初学者推荐 DeepSeek V3，性价比最高

### 步骤 3：准备消息渠道（可选）

| 渠道 | 难度 | 说明 |
|------|------|------|
| **Web 界面** | ⭐ | 内置，无需配置 |
| **Telegram** | ⭐⭐ | 需要 Bot Token |
| **Discord** | ⭐⭐ | 需要 Bot Token |
| **WhatsApp** | ⭐⭐⭐ | 需要 Meta 开发者账号 |
| **微信** | ⭐⭐⭐⭐ | 需要第三方服务 |

---

## 四、Mac 安装教程

### 方法 1：使用 npm（推荐）

```bash
# 1. 全局安装 OpenClaw
npm install -g openclaw

# 2. 验证安装
openclaw --version

# 3. 初始化工作空间
openclaw init ~/openclaw-workspace

# 4. 进入工作空间
cd ~/openclaw-workspace

# 5. 启动 OpenClaw
openclaw gateway start
```

### 方法 2：使用 Homebrew

```bash
# 1. 添加 OpenClaw tap
brew tap openclaw/openclaw

# 2. 安装 OpenClaw
brew install openclaw

# 3. 验证安装
openclaw --version

# 4. 初始化工作空间
openclaw init ~/openclaw-workspace

# 5. 启动
openclaw gateway start
```

### 方法 3：从源码安装

```bash
# 1. 克隆仓库
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 2. 安装依赖
npm install

# 3. 全局链接
npm link

# 4. 验证安装
openclaw --version

# 5. 初始化工作空间
openclaw init ~/openclaw-workspace

# 6. 启动
openclaw gateway start
```

### 验证安装成功

```bash
# 查看状态
openclaw status

# 应该看到类似输出：
# 🦞 OpenClaw 2026.x.x
# 🟢 Gateway: running
# 📂 Workspace: /Users/yourname/openclaw-workspace
```

---

## 五、Windows 安装教程

### 方法 1：使用 npm（推荐）

```cmd
# 1. 以管理员身份打开 PowerShell 或 CMD

# 2. 全局安装 OpenClaw
npm install -g openclaw

# 3. 验证安装
openclaw --version

# 4. 初始化工作空间
openclaw init C:\openclaw-workspace

# 5. 进入工作空间
cd C:\openclaw-workspace

# 6. 启动 OpenClaw
openclaw gateway start
```

### 方法 2：使用 WSL2（推荐开发者）

```bash
# 1. 安装 WSL2
wsl --install

# 2. 重启电脑后，进入 Ubuntu

# 3. 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. 安装 OpenClaw
sudo npm install -g openclaw

# 5. 初始化工作空间
openclaw init ~/openclaw-workspace

# 6. 启动
openclaw gateway start
```

### 验证安装成功

```cmd
# 查看状态
openclaw status
```

---

## 六、Linux 安装教程

### Ubuntu/Debian

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 3. 安装 OpenClaw
sudo npm install -g openclaw

# 4. 验证安装
openclaw --version

# 5. 初始化工作空间
openclaw init ~/openclaw-workspace

# 6. 启动
openclaw gateway start
```

### CentOS/RHEL

```bash
# 1. 安装 Node.js
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# 2. 安装 OpenClaw
sudo npm install -g openclaw

# 3. 验证安装
openclaw --version

# 4. 初始化工作空间
openclaw init ~/openclaw-workspace

# 5. 启动
openclaw gateway start
```

### 设置开机自启（Systemd）

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/openclaw.service

# 2. 添加以下内容（修改路径）
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/openclaw-workspace
ExecStart=/usr/bin/openclaw gateway start
Restart=always

[Install]
WantedBy=multi-user.target

# 3. 启用服务
sudo systemctl daemon-reload
sudo systemctl enable openclaw
sudo systemctl start openclaw

# 4. 查看状态
sudo systemctl status openclaw
```

---

## 七、配置指南

### 配置文件位置

```
~/.openclaw/openclaw.json    # 主配置文件
~/openclaw-workspace/        # 工作空间目录
```

### 基本配置

```bash
# 1. 打开配置
openclaw configure

# 或手动编辑
nano ~/.openclaw/openclaw.json
```

### 配置示例

```json
{
  "gateway": {
    "port": 8080,
    "host": "127.0.0.1"
  },
  "models": {
    "default": "deepseek",
    "providers": {
      "deepseek": {
        "type": "openai-compatible",
        "baseUrl": "https://api.deepseek.com",
        "apiKey": "YOUR_DEEPSEEK_API_KEY",
        "model": "deepseek-chat"
      },
      "qwen": {
        "type": "dashscope",
        "apiKey": "YOUR_QWEN_API_KEY",
        "model": "qwen-max"
      }
    }
  },
  "workspace": {
    "path": "~/openclaw-workspace",
    "autoSave": true
  },
  "memory": {
    "enabled": true,
    "maxSize": 1000
  }
}
```

### 配置命令

```bash
# 设置默认模型
openclaw config set models.default deepseek

# 设置 API Key
openclaw config set models.providers.deepseek.apiKey sk-xxxxx

# 查看配置
openclaw config get

# 重置配置
openclaw config reset
```

---

## 八、模型配置

### DeepSeek 配置

```bash
# 1. 获取 API Key
# 访问 https://platform.deepseek.com 注册并获取

# 2. 配置
openclaw configure --section models

# 3. 或使用命令
openclaw config set models.providers.deepseek.apiKey "sk-xxxxxxxxxxxxx"
openclaw config set models.providers.deepseek.baseUrl "https://api.deepseek.com"
openclaw config set models.providers.deepseek.model "deepseek-chat"
openclaw config set models.default "deepseek"
```

### Qwen（通义千问）配置

```bash
# 1. 获取 API Key
# 访问 https://dashscope.aliyun.com 注册并获取

# 2. 配置
openclaw config set models.providers.qwen.apiKey "sk-xxxxxxxxxxxxx"
openclaw config set models.providers.qwen.type "dashscope"
openclaw config set models.providers.qwen.model "qwen-max"
```

### Kimi 配置

```bash
# 1. 获取 API Key
# 访问 https://platform.moonshot.cn 注册并获取

# 2. 配置
openclaw config set models.providers.kimi.apiKey "sk-xxxxxxxxxxxxx"
openclaw config set models.providers.kimi.baseUrl "https://api.moonshot.cn/v1"
openclaw config set models.providers.kimi.model "moonshot-v1-8k"
```

### 切换模型

```bash
# 查看可用模型
openclaw models list

# 切换模型
openclaw models use deepseek
openclaw models use qwen
openclaw models use kimi
```

---

## 九、消息渠道配置

### Telegram 配置

```bash
# 1. 创建 Bot
# 在 Telegram 搜索 @BotFather
# 发送 /newbot 创建机器人
# 获取 Bot Token

# 2. 配置
openclaw configure --section messaging

# 3. 添加 Telegram
openclaw channel add telegram --token "YOUR_BOT_TOKEN"

# 4. 启动
openclaw gateway restart
```

### Discord 配置

```bash
# 1. 创建 Bot
# 访问 https://discord.com/developers/applications
# 创建应用，获取 Bot Token
# 邀请 Bot 到你的服务器

# 2. 配置
openclaw channel add discord --token "YOUR_BOT_TOKEN" --guild "SERVER_ID"

# 3. 启动
openclaw gateway restart
```

### Web 界面

```bash
# Web 界面默认开启
# 访问 http://localhost:8080
```

---

## 十、常见问题

### Q1: 安装时提示权限错误

**问题：**
```
npm ERR! Error: EACCES: permission denied
```

**解决：**

Mac/Linux:
```bash
# 方法 1：使用 sudo
sudo npm install -g openclaw

# 方法 2：修复 npm 权限（推荐）
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g openclaw
```

Windows:
```cmd
# 以管理员身份运行 CMD 或 PowerShell
npm install -g openclaw
```

---

### Q2: Gateway 启动失败

**问题：**
```
Error: Port 8080 is already in use
```

**解决：**

```bash
# 方法 1：更改端口
openclaw config set gateway.port 8081
openclaw gateway restart

# 方法 2：关闭占用端口的进程
# Mac/Linux
lsof -i :8080
kill -9 <PID>

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

### Q3: 模型 API 调用失败

**问题：**
```
Error: API key is invalid
```

**解决：**

```bash
# 1. 检查 API Key 是否正确
openclaw config get models.providers

# 2. 重新设置
openclaw config set models.providers.deepseek.apiKey "sk-xxxxx"

# 3. 测试连接
openclaw models test deepseek

# 4. 检查网络
# 确保能访问 API 服务器
curl https://api.deepseek.com
```

---

### Q4: 工作空间无法创建

**问题：**
```
Error: Cannot create workspace directory
```

**解决：**

```bash
# 1. 检查磁盘空间
df -h

# 2. 检查权限
ls -la ~/

# 3. 手动创建工作空间
mkdir -p ~/openclaw-workspace
chmod 755 ~/openclaw-workspace

# 4. 重新初始化
openclaw init ~/openclaw-workspace
```

---

### Q5: 中文乱码问题

**问题：**
```
终端显示中文乱码
```

**解决：**

Mac:
```bash
# 设置终端编码
defaults write com.apple.terminal StringEncodings -array 4
```

Linux:
```bash
# 设置 locale
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

Windows:
```cmd
# 更改代码页
chcp 65001
```

---

### Q6: 内存占用过高

**问题：**
```
OpenClaw 占用内存过高
```

**解决：**

```bash
# 1. 检查记忆系统配置
openclaw config get memory

# 2. 限制记忆大小
openclaw config set memory.maxSize 500

# 3. 重启 Gateway
openclaw gateway restart

# 4. 清理缓存
openclaw cache clear
```

---

### Q7: 无法连接消息渠道

**问题：**
```
Error: Cannot connect to Telegram/Discord
```

**解决：**

```bash
# 1. 检查 Token 是否正确
openclaw config get messaging

# 2. 检查网络
# 确保能访问 Telegram/Discord API

# 3. 重新添加渠道
openclaw channel remove telegram
openclaw channel add telegram --token "YOUR_TOKEN"

# 4. 查看日志
openclaw logs --tail 100
```

---

## 十一、进阶使用

### 子代理系统

```bash
# 查看可用子代理
openclaw agents list

#  spawn 子代理
openclaw spawn --agent deepseek --task "分析这个文档"

# 查看子代理状态
openclaw agents status
```

### 定时任务

```bash
# 添加定时任务
openclaw cron add --schedule "0 9 * * *" --command "提醒我开会"

# 查看任务
openclaw cron list

# 删除任务
openclaw cron remove <job-id>
```

### 文件操作

```bash
# 工作空间内文件操作
cd ~/openclaw-workspace

# 让 AI 帮你处理文件
openclaw ask "帮我整理这个文件夹的文件"
```

### 浏览器自动化

```bash
# 启动浏览器
openclaw browser start

# 截图
openclaw browser screenshot --url "https://example.com"

# 自动化操作
openclaw browser automate --script "script.js"
```

### 记忆系统

```bash
# 查看记忆
openclaw memory search "关键词"

# 添加记忆
openclaw memory add "重要信息"

# 清理记忆
openclaw memory clear
```

---

## 附录 A：常用命令速查

```bash
# 安装
npm install -g openclaw

# 初始化
openclaw init ~/workspace

# 启动/停止
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 状态
openclaw status
openclaw gateway status

# 配置
openclaw configure
openclaw config get
openclaw config set <key> <value>

# 模型
openclaw models list
openclaw models use <model>
openclaw models test <model>

# 渠道
openclaw channel list
openclaw channel add <channel> --token <token>
openclaw channel remove <channel>

# 日志
openclaw logs
openclaw logs --tail 100
openclaw logs --follow

# 帮助
openclaw --help
openclaw <command> --help
```

---

## 附录 B：资源链接

| 资源 | 链接 |
|------|------|
| **官方网站** | https://openclaw.ai |
| **GitHub** | https://github.com/openclaw/openclaw |
| **文档** | https://docs.openclaw.ai |
| **Discord 社区** | https://discord.com/invite/clawd |
| **技能市场** | https://clawhub.com |
| **问题反馈** | https://github.com/openclaw/openclaw/issues |

---

## 附录 C：版本历史

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| 2026.3.12 | 2026-03 | 最新稳定版 |
| 2026.2.0 | 2026-02 | 子代理系统优化 |
| 2026.1.0 | 2026-01 | 多模型支持 |
| 2025.12.0 | 2025-12 | 消息渠道扩展 |

---

## 结语

恭喜你完成 OpenClaw 的安装！🎉

现在你可以：

1. ✅ 开始与你的 AI 助手对话
2. ✅ 配置喜欢的模型
3. ✅ 连接消息渠道
4. ✅ 探索更多功能

**下一步建议：**

- 阅读官方文档：https://docs.openclaw.ai
- 加入社区 Discord：https://discord.com/invite/clawd
- 探索技能市场：https://clawhub.com
- 创建工作空间文件：SOUL.md, USER.md, MEMORY.md

---

*最后更新：2026-03-16*
*作者：OpenClaw 社区*
*许可证：MIT*

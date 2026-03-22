# GitHub 上传手动指南

## 🎯 目标
将 OpenClaw 工作空间上传到 GitHub 仓库 `BotForMe`

## 📋 准备工作

### 1. 检查当前状态
```bash
# 进入工作空间
cd ~/.openclaw/workspace

# 检查 Git 状态
git status
git log --oneline -5
```

### 2. 确保 GitHub 账户
- 已有 GitHub 账户：https://github.com
- 如果没有，请先注册

## 🚀 方法一：使用 GitHub CLI（推荐）

### 步骤 1：登录 GitHub CLI
```bash
# 如果未登录
gh auth login

# 选择：
# 1. GitHub.com
# 2. HTTPS
# 3. 是（通过浏览器登录）
```

### 步骤 2：创建仓库
```bash
# 创建名为 BotForMe 的仓库
gh repo create BotForMe \
  --description "OpenClaw workspace - AI assistant knowledge base and tools" \
  --public \
  --confirm
```

### 步骤 3：配置并推送
```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/BotForMe.git

# 重命名分支为 main（如果需要）
git branch -M main

# 推送代码
git push -u origin main
```

## 🚀 方法二：手动创建仓库

### 步骤 1：在 GitHub 创建仓库
1. 访问：https://github.com/new
2. 填写信息：
   - **Repository name**: `BotForMe`
   - **Description**: `OpenClaw workspace - AI assistant knowledge base and tools`
   - **Public**（选择公开）
   - **不要**初始化 README、.gitignore、license
3. 点击 "Create repository"

### 步骤 2：获取仓库 URL
创建后，你会看到类似这样的指令：
```bash
git remote add origin https://github.com/YOUR_USERNAME/BotForMe.git
git branch -M main
git push -u origin main
```

### 步骤 3：执行推送命令
```bash
# 在工作空间执行这些命令
cd ~/.openclaw/workspace

# 添加远程仓库（使用你的用户名）
git remote add origin https://github.com/YOUR_USERNAME/BotForMe.git

# 确保分支名为 main
git branch -M main

# 推送代码
git push -u origin main
```

## 🚀 方法三：使用 SSH 密钥

### 步骤 1：检查 SSH 密钥
```bash
# 检查现有密钥
ls -la ~/.ssh/

# 如果没有密钥，生成新的
ssh-keygen -t ed25519 -C "your-email@example.com"
```

### 步骤 2：添加密钥到 GitHub
1. 复制公钥：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 或
   cat ~/.ssh/id_rsa.pub
   ```

2. 添加到 GitHub：
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容

### 步骤 3：使用 SSH URL
```bash
# 使用 SSH URL 添加远程仓库
git remote add origin git@github.com:YOUR_USERNAME/BotForMe.git

# 推送
git push -u origin main
```

## 🔧 自动化脚本

我已经创建了自动化脚本，可以一键完成所有步骤：

```bash
# 运行上传脚本
./upload-to-github.sh
```

脚本会自动：
1. ✅ 检查 Git 状态
2. ✅ 检测 GitHub CLI 登录状态
3. ✅ 创建仓库（如果需要）
4. ✅ 配置远程仓库
5. ✅ 推送代码
6. ✅ 生成详细报告

## 📊 仓库内容概览

### 主要目录和文件
```
📁 .obsidian/              # Obsidian 笔记配置
📁 scripts/                # 自动化脚本
📁 skills/                 # AI 技能库
📁 memory/                 # 每日记忆存档
📁 knowledge-*/            # 知识演化跟踪系统
📄 *.md                    # 各种文档和指南
📄 *.py                    # Python 脚本
📄 *.sh                    # Shell 脚本
```

### 核心功能
1. **知识演化跟踪系统** - 每周自动分析知识变化
2. **Obsidian + Git 集成** - 专业笔记管理
3. **关系图谱可视化** - 知识网络分析
4. **自动化维护脚本** - 系统健康管理

## ⚠️ 注意事项

### 1. 文件大小
- 检查是否有大文件（>100MB）
- GitHub 限制单个文件 100MB
- 如果有大文件，考虑使用 Git LFS 或排除

### 2. 敏感信息
确保没有上传：
- 密码、API 密钥
- 个人隐私信息
- 配置文件中的敏感数据

### 3. .gitignore 检查
当前 `.gitignore` 已配置排除：
- 系统文件（.DS_Store）
- Python 缓存（__pycache__）
- 临时文件
- 大型 PDF 文件

## 🛠️ 故障排除

### 问题 1：认证失败
```bash
# 如果提示认证失败
git config --global credential.helper osxkeychain  # macOS
# 或
git config --global credential.helper cache
```

### 问题 2：仓库已存在
```bash
# 如果远程仓库已配置
git remote -v
git remote remove origin  # 删除现有配置
git remote add origin NEW_URL  # 重新添加
```

### 问题 3：推送被拒绝
```bash
# 如果提示 "non-fast-forward"
git pull origin main --allow-unrelated-histories
git push origin main
```

### 问题 4：网络问题
```bash
# 使用 SSH 替代 HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/BotForMe.git
```

## 📈 成功标志

推送成功后，你应该看到：
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
Delta compression using up to 8 threads
Compressing objects: 100% (Y/Y), done.
Writing objects: 100% (Z/Z), 1.23 MiB | 1.45 MiB/s, done.
Total Z (delta W), reused 0 (delta 0)
remote: Resolving deltas: 100% (W/W), done.
To https://github.com/YOUR_USERNAME/BotForMe.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

## 🌐 验证上传

1. **访问仓库**：https://github.com/YOUR_USERNAME/BotForMe
2. **检查文件**：确认所有重要文件都已上传
3. **查看提交**：确认提交历史完整

## 🔄 后续维护

### 定期推送更新
```bash
# 添加新文件
git add .

# 提交更改
git commit -m "更新描述"

# 推送到 GitHub
git push origin main
```

### 从其他设备克隆
```bash
# 在其他设备上获取代码
git clone https://github.com/YOUR_USERNAME/BotForMe.git
cd BotForMe
```

## 🎉 完成！

成功上传后，你的 OpenClaw 工作空间将：
- ✅ 拥有 GitHub 备份
- ✅ 支持多设备同步
- ✅ 具备版本控制历史
- ✅ 可公开分享（如果设为公开）

现在你可以：
1. 在 GitHub 上查看仓库
2. 添加 README.md 介绍项目
3. 设置合适的开源许可证
4. 邀请其他人协作

**💡 提示**：定期使用 `git push` 保持 GitHub 仓库更新！
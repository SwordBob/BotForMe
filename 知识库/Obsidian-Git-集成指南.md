# Obsidian + Git 集成指南

## 📋 概述

本指南帮助你使用 Obsidian 和 Git 来管理 OpenClaw 生成的 Markdown 文件。通过这个集成，你可以：

1. **版本控制** - 跟踪所有文件的更改历史
2. **备份** - 自动备份重要文档
3. **同步** - 在多设备间同步笔记
4. **组织** - 使用 Obsidian 的强大功能组织笔记

## 🚀 快速开始

### 1. 安装 Obsidian

如果你还没有安装 Obsidian，请访问 [obsidian.md](https://obsidian.md) 下载并安装。

### 2. 打开仓库作为 Obsidian Vault

1. 打开 Obsidian
2. 点击 "打开其他仓库"
3. 选择 `/Users/niejq/.openclaw/workspace` 目录
4. Obsidian 会自动加载所有配置

### 3. 配置 Git（可选）

如果你想要远程备份，可以配置 Git 远程仓库：

```bash
# 添加远程仓库（例如 GitHub）
git remote add origin https://github.com/你的用户名/你的仓库.git

# 推送到远程
git push -u origin master
```

## 🔧 自动化脚本

我已经创建了几个自动化脚本来简化工作流程：

### 自动提交新的 Markdown 文件

```bash
# 运行自动提交脚本
./scripts/auto-commit-md.sh "添加新的学习笔记"

# 或使用默认提交信息
./scripts/auto-commit-md.sh
```

### 每日自动备份

```bash
# 运行每日备份
./scripts/daily-git-backup.sh
```

你可以设置定时任务（cron）来自动运行每日备份：

```bash
# 编辑 crontab
crontab -e

# 添加以下行，每天凌晨2点运行备份
0 2 * * * /Users/niejq/.openclaw/workspace/scripts/daily-git-backup.sh
```

## 📁 文件结构说明

```
./
├── .obsidian/              # Obsidian 配置文件
│   ├── core-plugins.json   # 核心插件配置
│   ├── app.json           # 应用设置
│   ├── editor.json        # 编辑器设置
│   └── git.json           # Git 插件配置
├── scripts/               # 自动化脚本
│   ├── auto-commit-md.sh  # 自动提交脚本
│   └── daily-git-backup.sh # 每日备份脚本
├── memory/                # 每日记忆文件
├── *.md                   # 各种 Markdown 文档
└── .gitignore             # Git 忽略文件
```

## 🔌 Obsidian 插件推荐

### 内置插件（已启用）
- **文件浏览器** - 浏览所有文件
- **图形视图** - 可视化笔记关系
- **反向链接** - 查看引用关系
- **大纲** - 快速导航文档结构
- **每日笔记** - 创建每日笔记

### 社区插件（可选）
1. **Git** - 已预配置，用于版本控制
2. **Dataview** - 高级查询和表格
3. **Templater** - 强大的模板系统
4. **Calendar** - 日历视图
5. **Excalidraw** - 绘图工具

## 📝 最佳实践

### 1. 文件命名
- 使用有意义的文件名
- 避免特殊字符
- 使用中文或英文，保持一致性

### 2. 提交频率
- 每次完成重要修改后运行自动提交
- 设置每日自动备份
- 重要更改立即提交

### 3. 备份策略
- 本地 Git 仓库提供完整历史
- 配置远程仓库（GitHub/GitLab）进行云备份
- 定期检查备份状态

### 4. Obsidian 使用技巧
- 使用 `[[链接]]` 连接相关笔记
- 添加标签 `#标签` 进行分类
- 利用反向链接发现关联内容
- 使用图形视图探索知识网络

## 🛠️ 故障排除

### Git 相关问题

**问题：** 提交时出现身份错误
**解决：**
```bash
git config user.email "你的邮箱"
git config user.name "你的名字"
```

**问题：** 文件权限错误
**解决：**
```bash
chmod +x scripts/*.sh
```

### Obsidian 相关问题

**问题：** Obsidian 无法识别配置
**解决：** 确保 `.obsidian` 目录存在且包含配置文件

**问题：** 插件不工作
**解决：** 检查 `.obsidian/core-plugins.json` 配置

## 📈 高级功能

### 1. 自定义工作流
你可以修改脚本以适应你的工作流程：
- 添加文件类型过滤
- 自定义提交信息格式
- 集成其他自动化工具

### 2. 多设备同步
如果你有多台设备：
1. 在所有设备上配置相同的远程仓库
2. 使用 `git pull` 同步更改
3. 解决可能的冲突

### 3. 版本恢复
如果需要恢复旧版本：
```bash
# 查看历史
git log --oneline

# 恢复到特定版本
git checkout <commit-hash> -- <file-path>

# 或恢复整个仓库到某个时间点
git checkout <commit-hash>
```

## 🎯 下一步

1. **立即尝试**：打开 Obsidian 并浏览你的笔记
2. **运行测试**：执行 `./scripts/auto-commit-md.sh` 测试自动提交
3. **配置远程**：设置 GitHub 仓库进行云备份
4. **探索插件**：安装感兴趣的 Obsidian 社区插件

## 📞 支持

如果你遇到问题：
1. 检查本指南的相关部分
2. 查看脚本中的注释
3. 联系我获取帮助

---

*最后更新: $(date '+%Y-%m-%d %H:%M:%S')*
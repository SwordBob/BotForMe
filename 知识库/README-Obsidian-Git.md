# OpenClaw + Obsidian + Git 集成

## 🎯 一句话说明

**用 Obsidian 管理 OpenClaw 生成的笔记，用 Git 进行版本控制和备份。**

## 🚀 快速开始

### 第一步：安装 Obsidian
1. 访问 [obsidian.md](https://obsidian.md)
2. 下载并安装 Obsidian

### 第二步：打开工作区
1. 打开 Obsidian
2. 选择 "打开其他仓库"
3. 选择 `/Users/niejq/.openclaw/workspace`
4. 开始使用！

### 第三步：日常使用
```bash
# 1. 我生成新的 .md 文件后
./scripts/auto-commit-md.sh

# 2. 每日自动备份（可选）
./scripts/daily-git-backup.sh

# 3. 测试一切是否正常
./scripts/test-obsidian-git.sh
```

## 📁 核心文件

- `.obsidian/` - Obsidian 配置文件
- `scripts/` - 自动化脚本
- `memory/` - 每日记忆文件
- `*.md` - 所有笔记文档

## 🔧 自动化脚本

| 脚本 | 用途 | 使用频率 |
|------|------|----------|
| `auto-commit-md.sh` | 自动提交新的 .md 文件 | 每次生成新文件后 |
| `daily-git-backup.sh` | 每日自动备份 | 每天一次 |
| `test-obsidian-git.sh` | 测试集成功能 | 初次设置时 |

## 💡 小贴士

### Obsidian 技巧
- 使用 `[[文件名]]` 创建内部链接
- 使用 `#标签` 进行分类
- 点击右上角图标打开图形视图
- 使用反向链接查看引用关系

### Git 技巧
```bash
# 查看历史
git log --oneline

# 查看更改
git diff

# 恢复文件
git checkout -- 文件名.md
```

## ⚙️ 配置远程备份（推荐）

1. 在 GitHub/GitLab 创建新仓库
2. 添加远程仓库：
   ```bash
   git remote add origin https://github.com/你的用户名/仓库名.git
   ```
3. 推送到远程：
   ```bash
   git push -u origin master
   ```

## 🆘 常见问题

**Q: Obsidian 打不开文件？**
A: 确保使用 "打开其他仓库" 而不是 "打开文件夹"

**Q: 脚本没有权限？**
A: 运行 `chmod +x scripts/*.sh`

**Q: Git 提交失败？**
A: 检查用户配置：`git config user.name` 和 `git config user.email`

## 📞 需要帮助？

1. 查看详细指南：`Obsidian-Git-集成指南.md`
2. 运行测试脚本：`./scripts/test-obsidian-git.sh`
3. 联系我获取支持

---

*让知识管理变得简单高效！*
#!/bin/bash

# 上传工作空间到 GitHub 仓库 BotForMe

set -e

echo "========================================"
echo "🚀 上传到 GitHub: BotForMe"
echo "========================================"
echo ""

WORKSPACE_DIR="/Users/niejq/.openclaw/workspace"
REPO_NAME="BotForMe"
GITHUB_USER=""  # 将自动检测或询问

cd "$WORKSPACE_DIR"

# 函数：检查 Git 状态
check_git_status() {
    echo "🔍 检查 Git 状态..."
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  有未提交的更改:"
        git status --short
        echo ""
        read -p "是否先提交这些更改？ (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "Auto commit before pushing to GitHub"
            echo "✅ 更改已提交"
        fi
    else
        echo "✅ Git 工作区干净"
    fi
    
    # 显示当前分支
    CURRENT_BRANCH=$(git branch --show-current)
    echo "   当前分支: $CURRENT_BRANCH"
    echo "   提交数: $(git rev-list --count HEAD)"
}

# 函数：检查 GitHub CLI 登录状态
check_github_cli() {
    echo ""
    echo "🔐 检查 GitHub CLI..."
    
    if command -v gh &> /dev/null; then
        if gh auth status &> /dev/null; then
            GITHUB_USER=$(gh api user --jq .login 2>/dev/null)
            if [ -n "$GITHUB_USER" ]; then
                echo "✅ 已登录 GitHub CLI"
                echo "   用户名: $GITHUB_USER"
                return 0
            fi
        fi
    fi
    
    echo "❌ GitHub CLI 未登录或未安装"
    return 1
}

# 函数：检查 SSH 密钥
check_ssh_keys() {
    echo ""
    echo "🔑 检查 SSH 密钥..."
    
    if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
        echo "✅ 找到 SSH 密钥"
        
        # 测试 GitHub SSH 连接
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            echo "✅ SSH 密钥已配置到 GitHub"
            return 0
        else
            echo "⚠️  SSH 密钥未配置到 GitHub 或需要验证"
            return 1
        fi
    else
        echo "❌ 未找到 SSH 密钥"
        return 1
    fi
}

# 函数：创建 GitHub 仓库（使用 GitHub CLI）
create_github_repo_cli() {
    echo ""
    echo "🏗️  使用 GitHub CLI 创建仓库..."
    
    # 检查仓库是否已存在
    if gh repo view "$GITHUB_USER/$REPO_NAME" &> /dev/null; then
        echo "⚠️  仓库已存在: $GITHUB_USER/$REPO_NAME"
        return 0
    fi
    
    # 创建新仓库
    echo "正在创建仓库: $REPO_NAME"
    gh repo create "$REPO_NAME" \
        --description "OpenClaw workspace - AI assistant knowledge base and tools" \
        --public \
        --confirm
    
    if [ $? -eq 0 ]; then
        echo "✅ 仓库创建成功: https://github.com/$GITHUB_USER/$REPO_NAME"
        return 0
    else
        echo "❌ 仓库创建失败"
        return 1
    fi
}

# 函数：手动创建 GitHub 仓库说明
create_github_repo_manual() {
    echo ""
    echo "📝 手动创建 GitHub 仓库步骤:"
    echo ""
    echo "1. 访问: https://github.com/new"
    echo "2. 填写仓库信息:"
    echo "   - Repository name: BotForMe"
    echo "   - Description: OpenClaw workspace - AI assistant knowledge base and tools"
    echo "   - Public (推荐)"
    echo "   - 不要初始化 README, .gitignore, license"
    echo "3. 点击 'Create repository'"
    echo ""
    echo "创建后，你会看到推送现有仓库的指令，类似:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/BotForMe.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
    
    read -p "是否已创建仓库？ (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入你的 GitHub 用户名: " GITHUB_USER
        return 0
    else
        return 1
    fi
}

# 函数：配置远程仓库
setup_remote() {
    echo ""
    echo "🌐 配置远程仓库..."
    
    # 检查是否已配置远程仓库
    if git remote | grep -q "origin"; then
        echo "⚠️  已配置远程仓库:"
        git remote -v
        read -p "是否覆盖？ (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote remove origin
        else
            return 0
        fi
    fi
    
    # 选择远程仓库 URL 类型
    echo ""
    echo "选择远程仓库 URL 类型:"
    echo "1) HTTPS (推荐，无需 SSH 密钥)"
    echo "2) SSH (需要配置 SSH 密钥)"
    read -p "选择 [1-2]: " -n 1 -r
    echo ""
    
    if [ -z "$GITHUB_USER" ]; then
        read -p "请输入你的 GitHub 用户名: " GITHUB_USER
    fi
    
    case $REPLY in
        2)
            # SSH URL
            REMOTE_URL="git@github.com:$GITHUB_USER/$REPO_NAME.git"
            ;;
        *)
            # HTTPS URL (默认)
            REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
            ;;
    esac
    
    # 添加远程仓库
    git remote add origin "$REMOTE_URL"
    echo "✅ 远程仓库已配置: $REMOTE_URL"
}

# 函数：推送到 GitHub
push_to_github() {
    echo ""
    echo "🚀 推送到 GitHub..."
    
    # 确保分支名称为 main
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo "将分支重命名为 main..."
        git branch -M main
    fi
    
    # 推送代码
    echo "正在推送代码..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ 代码推送成功!"
        echo ""
        echo "🌐 仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
        return 0
    else
        echo "❌ 推送失败"
        echo "可能的原因:"
        echo "1. 网络问题"
        echo "2. 认证失败"
        echo "3. 仓库不存在或无权访问"
        return 1
    fi
}

# 函数：生成仓库报告
generate_repo_report() {
    echo ""
    echo "📊 生成仓库报告..."
    
    REPORT_FILE="github-repo-info.md"
    
    cat > "$REPORT_FILE" << EOF
# GitHub 仓库信息 - BotForMe

## 📅 上传时间
$(date '+%Y-%m-%d %H:%M:%S')

## 📁 仓库内容概览

### 文件统计
- **总文件数**: $(git ls-files | wc -l)
- **Markdown 文件**: $(git ls-files "*.md" | wc -l)
- **脚本文件**: $(git ls-files "*.sh" "*.py" | wc -l)
- **配置文件**: $(git ls-files "*.json" "*.plist" | wc -l)

### 目录结构
\`\`\`
$(find . -type f -name "*.md" -o -name "*.sh" -o -name "*.py" | sort | head -20)
... 更多文件
\`\`\`

### 提交历史
\`\`\`
$(git log --oneline -10)
\`\`\`

## 🔗 重要文件

### 核心文档
1. **MEMORY.md** - AI 助手长期记忆
2. **SOUL.md** - AI 助手身份定义
3. **USER.md** - 用户信息
4. **AGENTS.md** - 工作空间指南

### 工具脚本
1. **知识演化跟踪系统** - 自动化知识维护
   - \`scripts/weekly-knowledge-evolution.py\`
   - \`scripts/weekly-knowledge-maintenance.sh\`
   - \`setup-knowledge-maintenance.sh\`

2. **Obsidian + Git 集成** - 笔记管理
   - \`.obsidian/\` - Obsidian 配置
   - \`Obsidian-Git-集成指南.md\`

3. **关系图谱工具** - 知识可视化
   - \`scripts/create-obsidian-graph.py\`
   - \`obsidian-graph-visualizer.html\`

### 技能库
- \`skills/knowledge-evolution-tracker/\` - 知识演化跟踪技能

## 🚀 使用说明

### 克隆仓库
\`\`\`bash
git clone https://github.com/$GITHUB_USER/BotForMe.git
cd BotForMe
\`\`\`

### 主要功能
1. **知识管理**: 使用 Obsidian 打开工作空间
2. **自动化维护**: 运行知识演化跟踪系统
3. **关系图谱**: 查看知识网络可视化
4. **版本控制**: 所有更改自动跟踪

### 快速开始
\`\`\`bash
# 安装知识维护系统
./setup-knowledge-maintenance.sh

# 查看关系图谱
open obsidian-graph-visualizer.html

# 使用 Obsidian
open -a Obsidian .
\`\`\`

## 📞 维护信息

### 自动化任务
- **知识演化跟踪**: 每周日 09:00 自动运行
- **数据备份**: 每周自动备份重要文件
- **报告生成**: 自动生成演化报告

### 安全说明
- 所有脚本为只读操作，不会删除源文件
- 使用 Git 版本控制，可随时恢复
- 定期备份到 GitHub

---

**仓库创建时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**最后提交**: $(git log -1 --pretty=format:"%h - %s (%ad)" --date=short)
EOF
    
    echo "✅ 报告已生成: $REPORT_FILE"
}

# 主执行流程
main() {
    echo "开始上传流程..."
    echo ""
    
    # 1. 检查 Git 状态
    check_git_status
    
    # 2. 尝试使用 GitHub CLI
    if check_github_cli; then
        echo ""
        echo "🎯 使用 GitHub CLI 方案"
        # 创建仓库
        if create_github_repo_cli; then
            setup_remote
            push_to_github
        fi
    else
        echo ""
        echo "🎯 使用手动方案"
        # 检查 SSH 密钥
        if check_ssh_keys; then
            echo "✅ 可以使用 SSH 方式"
        else
            echo "⚠️  建议使用 HTTPS 方式"
        fi
        
        # 手动创建仓库
        if create_github_repo_manual; then
            setup_remote
            push_to_github
        else
            echo "❌ 需要先创建 GitHub 仓库"
            echo ""
            echo "📋 请先完成:"
            echo "1. 创建 GitHub 仓库: https://github.com/new"
            echo "2. 仓库名: BotForMe"
            echo "3. 然后重新运行此脚本"
            exit 1
        fi
    fi
    
    # 生成报告
    generate_repo_report
    
    echo ""
    echo "========================================"
    echo "🎉 上传完成！"
    echo "========================================"
    echo ""
    echo "📋 完成的项目:"
    echo "✅ Git 仓库检查"
    echo "✅ 远程仓库配置"
    echo "✅ 代码推送"
    echo "✅ 报告生成"
    echo ""
    echo "🌐 访问你的仓库:"
    echo "   https://github.com/$GITHUB_USER/BotForMe"
    echo ""
    echo "🚀 下一步建议:"
    echo "1. 在浏览器中打开仓库页面"
    echo "2. 添加 README.md 文件"
    echo "3. 设置仓库描述和主题"
    echo "4. 定期推送更新"
}

# 执行主函数
main "$@"
#!/bin/bash

# 最简单的一键上传脚本
# 专为 SwordBob 优化

echo "🚀 GitHub 一键上传脚本 (SwordBob 专用)"
echo "========================================"
echo ""

# 检查是否在正确目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误: 请在 OpenClaw 工作空间运行此脚本"
    echo "当前目录: $(pwd)"
    echo "正确目录: ~/.openclaw/workspace"
    exit 1
fi

# 使用你的 GitHub 用户名
GITHUB_USER="SwordBob"
REPO_NAME="BotForMe"
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "👤 GitHub 用户: $GITHUB_USER"
echo "📦 仓库名称: $REPO_NAME"
echo "🌐 远程地址: $REMOTE_URL"
echo ""

echo ""
echo "📋 上传信息:"
echo "   用户名: $GITHUB_USER"
echo "   仓库名: $REPO_NAME"
echo "   远程地址: $REMOTE_URL"
echo ""

# 智能检查 GitHub 仓库
echo "🔍 检查 GitHub 仓库状态..."
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"

# 尝试多种方式检查仓库
if curl -s -I "$REPO_URL" 2>/dev/null | grep -q "200 OK"; then
    echo "✅ 仓库已存在: $REPO_URL"
    REPO_EXISTS=true
else
    echo "❌ 仓库不存在或无法访问"
    echo ""
    echo "📝 自动创建选项:"
    echo "   1. 手动创建（推荐第一次使用）"
    echo "   2. 使用 GitHub CLI 创建（如果已登录）"
    echo "   3. 跳过检查直接尝试上传"
    echo ""
    read -p "请选择 (1/2/3): " -n 1 -r
    echo ""
    
    case $REPLY in
        1)
            echo "📋 手动创建步骤:"
            echo "   1. 访问: https://github.com/new"
            echo "   2. 仓库名: BotForMe"
            echo "   3. 描述: OpenClaw workspace - AI assistant knowledge base and tools"
            echo "   4. 选择: Public"
            echo "   5. 不要初始化 README, .gitignore, license"
            echo "   6. 点击 'Create repository'"
            echo ""
            read -p "是否已创建仓库？ (y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "请先创建仓库，然后重新运行此脚本"
                exit 1
            fi
            REPO_EXISTS=true
            ;;
        2)
            echo "尝试使用 GitHub CLI 创建仓库..."
            if command -v gh &> /dev/null && gh auth status &> /dev/null; then
                gh repo create "$REPO_NAME" --public --confirm
                if [ $? -eq 0 ]; then
                    echo "✅ 仓库创建成功"
                    REPO_EXISTS=true
                else
                    echo "❌ 仓库创建失败，请手动创建"
                    exit 1
                fi
            else
                echo "❌ GitHub CLI 未安装或未登录"
                echo "请使用选项1手动创建"
                exit 1
            fi
            ;;
        *)
            echo "⚠️  跳过仓库检查，直接尝试上传..."
            REPO_EXISTS=false
            ;;
    esac
fi

# 智能 Git 配置
echo ""
echo "⚙️ 配置 Git 远程仓库..."

# 检查是否已配置
if git remote | grep -q origin; then
    CURRENT_URL=$(git remote get-url origin)
    if [ "$CURRENT_URL" = "$REMOTE_URL" ]; then
        echo "✅ 远程仓库已正确配置: $CURRENT_URL"
    else
        echo "🔄 更新远程仓库:"
        echo "   从: $CURRENT_URL"
        echo "   到: $REMOTE_URL"
        git remote set-url origin "$REMOTE_URL"
    fi
else
    echo "➕ 添加远程仓库: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
fi

# 确保分支为 main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 重命名分支: $CURRENT_BRANCH -> main"
    git branch -M main
else
    echo "✅ 当前分支: main"
fi

echo "✅ Git 配置完成"

# 显示上传摘要
echo ""
echo "📦 上传内容摘要:"
echo "   提交历史: $(git rev-list --count HEAD) 次提交"
echo "   文件总数: $(git ls-files | wc -l) 个文件"
echo "   目录大小: $(du -sh . | cut -f1)"
echo "   Markdown 文件: $(git ls-files "*.md" | wc -l) 个"
echo "   脚本文件: $(git ls-files "*.sh" "*.py" | wc -l) 个"
echo "   配置文件: $(git ls-files "*.json" "*.plist" | wc -l) 个"

# 显示最近提交
echo ""
echo "📝 最近提交:"
git log --oneline -3

# 智能确认
echo ""
echo "========================================"
echo "🚀 准备上传到 GitHub"
echo "========================================"
echo ""
echo "目标仓库: https://github.com/SwordBob/BotForMe"
echo ""
echo "选项:"
echo "   1. 立即上传（默认）"
echo "   2. 先查看差异"
echo "   3. 取消上传"
echo ""
read -p "请选择 (1/2/3) [默认1]: " -n 1 -r
echo ""

case $REPLY in
    2)
        echo "📊 显示上传差异..."
        echo "本地与远程差异:"
        git log --oneline origin/main..main 2>/dev/null || echo "（首次上传，无远程分支）"
        echo ""
        read -p "是否继续上传？ (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "上传取消"
            exit 0
        fi
        ;;
    3)
        echo "上传取消"
        exit 0
        ;;
esac

# 执行上传
echo ""
echo "🚀 正在上传到 GitHub..."
echo "这可能需要几秒钟，请稍候..."
echo ""

START_TIME=$(date +%s)

if git push -u origin main; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo "🎉🎉🎉 上传成功！ 🎉🎉🎉"
    echo ""
    echo "⏱️  用时: ${DURATION} 秒"
    echo "📦 上传大小: $(git count-objects -vH | grep size-pack | cut -d: -f2)"
    echo ""
    echo "🌐 重要链接:"
    echo "   仓库主页: https://github.com/SwordBob/BotForMe"
    echo "   提交历史: https://github.com/SwordBob/BotForMe/commits/main"
    echo "   文件浏览: https://github.com/SwordBob/BotForMe"
    echo "   README: https://github.com/SwordBob/BotForMe#readme"
    echo ""
    echo "✨ 恭喜！你的 OpenClaw 工作空间已成功上传到 GitHub。"
    echo ""
    echo "💡 下一步建议:"
    echo "   1. 访问仓库页面查看效果"
    echo "   2. 添加仓库描述和主题标签"
    echo "   3. 考虑启用 GitHub Pages"
    echo "   4. 定期使用 'git push' 更新"
    
    # 保存成功信息
    cat > "GITHUB_UPLOAD_SUCCESS.md" << EOF
# 🎉 GitHub 上传成功报告

## 基本信息
- **用户名**: SwordBob
- **仓库名**: BotForMe
- **上传时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **用时**: ${DURATION} 秒

## 仓库链接
- 主页: https://github.com/SwordBob/BotForMe
- 提交: https://github.com/SwordBob/BotForMe/commits/main
- 文件: https://github.com/SwordBob/BotForMe

## 统计信息
- 总提交数: $(git rev-list --count HEAD)
- 总文件数: $(git ls-files | wc -l)
- 仓库大小: $(git count-objects -vH | grep size-pack | cut -d: -f2)

## 验证命令
\`\`\`bash
# 克隆验证
cd /tmp
git clone https://github.com/SwordBob/BotForMe.git
cd BotForMe
ls -la
\`\`\`

## 后续操作
1. 完善仓库信息（描述、主题）
2. 设置 GitHub Pages（可选）
3. 定期推送更新
4. 分享给他人

---
**上传完成时间**: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    echo "✅ 详细报告已生成: GITHUB_UPLOAD_SUCCESS.md"
    echo "🔗 仓库地址已保存: https://github.com/SwordBob/BotForMe"
    
else
    echo ""
    echo "❌ 上传失败"
    echo ""
    echo "🔧 故障排除:"
    echo ""
    
    # 检查具体错误
    echo "1. 检查仓库是否存在:"
    echo "   访问: https://github.com/SwordBob/BotForMe"
    echo ""
    
    echo "2. 检查网络连接:"
    ping -c 2 github.com 2>/dev/null && echo "   ✅ GitHub 可访问" || echo "   ❌ 无法访问 GitHub"
    echo ""
    
    echo "3. 尝试 SSH 方式:"
    echo "   git remote set-url origin git@github.com:SwordBob/BotForMe.git"
    echo "   git push -u origin main"
    echo ""
    
    echo "4. 检查 Git 配置:"
    echo "   用户名: $(git config user.name)"
    echo "   邮箱: $(git config user.email)"
    echo ""
    
    echo "5. 手动创建仓库后重试:"
    echo "   访问: https://github.com/new"
    echo "   仓库名: BotForMe"
    echo "   描述: OpenClaw workspace - AI assistant knowledge base and tools"
    echo "   公开仓库，不要初始化文件"
    
    # 保存错误信息
    echo "上传失败，请检查以上问题" > UPLOAD_FAILED.txt
fi

echo ""
echo "========================================"
echo "脚本执行完成"
echo "========================================"
echo ""
echo "📞 如需帮助:"
echo "   1. 查看报告文件: GITHUB_UPLOAD_SUCCESS.md 或 UPLOAD_FAILED.txt"
echo "   2. 检查错误信息"
echo "   3. 重新运行此脚本"
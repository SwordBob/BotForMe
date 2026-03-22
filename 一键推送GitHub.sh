#!/bin/bash

# 最简单的一键推送脚本
# 只需运行此脚本，按照提示操作

echo "🚀 GitHub 一键推送"
echo "========================"
echo ""

# 检查是否在正确目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误: 请在 OpenClaw 工作空间运行"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo "📋 推送信息:"
echo "   用户: SwordBob"
echo "   仓库: BotForMe"
echo "   地址: https://github.com/SwordBob/BotForMe"
echo ""

# 检查仓库是否存在
echo "🔍 检查 GitHub 仓库..."
if curl -s -I "https://github.com/SwordBob/BotForMe" | grep -q "200 OK"; then
    echo "✅ 仓库已存在"
else
    echo "❌ 仓库不存在"
    echo ""
    echo "📝 需要先创建仓库:"
    echo "   访问: https://github.com/new"
    echo "   仓库名: BotForMe"
    echo "   描述: OpenClaw workspace - AI assistant knowledge base and tools"
    echo "   选择: Public"
    echo "   不要初始化 README, .gitignore, license"
    echo ""
    read -p "是否已创建仓库？ (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先创建仓库，然后重新运行此脚本"
        exit 1
    fi
fi

# 配置 Git
echo ""
echo "⚙️ 配置 Git..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/SwordBob/BotForMe.git"
git branch -M main 2>/dev/null

echo "✅ Git 配置完成"

# 显示内容
echo ""
echo "📦 推送内容:"
echo "   提交: $(git rev-list --count HEAD) 次"
echo "   文件: $(git ls-files | wc -l) 个"
echo "   大小: $(du -sh . | cut -f1)"

# 确认
echo ""
read -p "是否开始推送？ (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "推送取消"
    exit 0
fi

# 执行推送
echo ""
echo "🚀 正在推送到 GitHub..."
echo "请稍候..."
echo ""

if git push -u origin main; then
    echo ""
    echo "🎉🎉🎉 推送成功！ 🎉🎉🎉"
    echo ""
    echo "🌐 访问你的仓库:"
    echo "   https://github.com/SwordBob/BotForMe"
    echo ""
    echo "✨ 恭喜！你的工作空间已成功推送到 GitHub。"
    
    # 保存链接
    echo "https://github.com/SwordBob/BotForMe" > GITHUB_SUCCESS.txt
    echo "✅ 仓库地址已保存: GITHUB_SUCCESS.txt"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "请尝试:"
    echo "1. 确认仓库名称正确"
    echo "2. 检查网络"
    echo "3. 使用 SSH:"
    echo "   git remote set-url origin git@github.com:SwordBob/BotForMe.git"
    echo "   git push -u origin main"
fi

echo ""
echo "========================"
echo "完成"
echo "========================"
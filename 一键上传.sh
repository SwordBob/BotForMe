#!/bin/bash

# 最简单的一键上传脚本
# 只需运行并输入 GitHub 用户名

echo "🚀 GitHub 一键上传脚本"
echo "========================"
echo ""

# 检查是否在正确目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误: 请在 OpenClaw 工作空间运行此脚本"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 获取 GitHub 用户名
echo "请输入你的 GitHub 用户名:"
echo "（例如: niejq, johnsmith, alice123）"
read -r GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ 错误: 用户名不能为空"
    exit 1
fi

REPO_NAME="BotForMe"
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo ""
echo "📋 上传信息:"
echo "   用户名: $GITHUB_USER"
echo "   仓库名: $REPO_NAME"
echo "   远程地址: $REMOTE_URL"
echo ""

# 检查仓库是否已存在
echo "🔍 检查 GitHub 仓库..."
if curl -s -I "https://github.com/$GITHUB_USER/$REPO_NAME" | grep -q "200 OK"; then
    echo "✅ 仓库已存在"
else
    echo "❌ 仓库不存在"
    echo ""
    echo "📝 需要先创建仓库:"
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
fi

# 配置 Git
echo ""
echo "⚙️ 配置 Git..."
git remote remove origin 2>/dev/null
git remote add origin "$REMOTE_URL"
git branch -M main 2>/dev/null

echo "✅ Git 配置完成"

# 显示上传内容
echo ""
echo "📦 上传内容:"
echo "   提交数: $(git rev-list --count HEAD)"
echo "   文件数: $(git ls-files | wc -l)"
echo "   大小: $(du -sh . | cut -f1)"

# 确认上传
echo ""
read -p "是否开始上传？ (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "上传取消"
    exit 0
fi

# 执行上传
echo ""
echo "🚀 正在上传到 GitHub..."
echo "这可能需要几秒钟..."
echo ""

if git push -u origin main; then
    echo ""
    echo "🎉🎉🎉 上传成功！ 🎉🎉🎉"
    echo ""
    echo "🌐 访问你的仓库:"
    echo "   https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "📊 查看提交:"
    echo "   https://github.com/$GITHUB_USER/$REPO_NAME/commits/main"
    echo ""
    echo "📁 浏览文件:"
    echo "   https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "✨ 恭喜！你的 OpenClaw 工作空间已成功上传到 GitHub。"
    
    # 保存成功信息
    echo "https://github.com/$GITHUB_USER/$REPO_NAME" > GITHUB_REPO_URL.txt
    echo "✅ 仓库地址已保存到: GITHUB_REPO_URL.txt"
else
    echo ""
    echo "❌ 上传失败"
    echo ""
    echo "请尝试以下解决方案:"
    echo "1. 确认仓库名称正确: BotForMe"
    echo "2. 确认用户名正确: $GITHUB_USER"
    echo "3. 检查网络连接"
    echo "4. 使用 SSH 方式:"
    echo "   git remote set-url origin git@github.com:$GITHUB_USER/BotForMe.git"
    echo "   git push -u origin main"
fi

echo ""
echo "========================"
echo "脚本执行完成"
echo "========================"
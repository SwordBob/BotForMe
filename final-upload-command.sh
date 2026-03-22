#!/bin/bash

# 最终上传命令脚本
# 只需替换 YOUR_USERNAME 为你的 GitHub 用户名

set -e

echo "========================================"
echo "🚀 GitHub 最终上传命令"
echo "========================================"
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 需要提供 GitHub 用户名"
    echo ""
    echo "使用方法:"
    echo "  ./final-upload-command.sh YOUR_GITHUB_USERNAME"
    echo ""
    echo "例如:"
    echo "  ./final-upload-command.sh niejq"
    echo ""
    echo "或者直接设置用户名:"
    echo "  GITHUB_USER=\"niejq\" ./final-upload-command.sh"
    exit 1
fi

GITHUB_USER="$1"
REPO_NAME="BotForMe"
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "📋 上传配置:"
echo "   用户名: $GITHUB_USER"
echo "   仓库名: $REPO_NAME"
echo "   远程地址: $REMOTE_URL"
echo ""

# 检查是否已配置远程仓库
if git remote | grep -q origin; then
    CURRENT_URL=$(git remote get-url origin)
    echo "当前远程仓库: $CURRENT_URL"
    echo "更新为: $REMOTE_URL"
    git remote set-url origin "$REMOTE_URL"
else
    echo "添加远程仓库: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
fi

# 确保分支为 main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "重命名分支: $CURRENT_BRANCH -> main"
    git branch -M main
fi

echo ""
echo "📊 准备上传:"
echo "   分支: main"
echo "   提交数: $(git rev-list --count HEAD)"
echo "   文件数: $(git ls-files | wc -l)"
echo ""

# 确认
read -p "是否开始上传到 GitHub？ (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "上传取消"
    exit 0
fi

echo ""
echo "🚀 开始上传..."
echo "执行: git push -u origin main"
echo ""

# 执行上传
if git push -u origin main; then
    echo ""
    echo "🎉 上传成功！"
    echo ""
    echo "🌐 仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo "📊 提交查看: https://github.com/$GITHUB_USER/$REPO_NAME/commits/main"
    echo "📁 文件浏览: https://github.com/$GITHUB_USER/$REPO_NAME"
    
    # 生成成功文件
    cat > "UPLOAD_SUCCESS.md" << EOF
# 🎉 GitHub 上传成功！

## 上传信息
- **时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **仓库**: https://github.com/$GITHUB_USER/$REPO_NAME
- **用户**: $GITHUB_USER
- **分支**: main

## 统计信息
- 总提交数: $(git rev-list --count HEAD)
- 总文件数: $(git ls-files | wc -l)
- Markdown 文件: $(git ls-files "*.md" | wc -l)
- 脚本文件: $(git ls-files "*.sh" "*.py" | wc -l)

## 验证命令
\`\`\`bash
# 克隆验证
cd /tmp
git clone https://github.com/$GITHUB_USER/$REPO_NAME.git
cd $REPO_NAME
ls -la
\`\`\`

## 后续操作
1. 访问仓库主页完善信息
2. 添加仓库描述和主题
3. 定期推送更新
4. 考虑启用 GitHub Pages

---
**上传完成时间**: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    echo ""
    echo "✅ 成功报告已生成: UPLOAD_SUCCESS.md"
else
    echo ""
    echo "❌ 上传失败"
    echo ""
    echo "可能的原因:"
    echo "1. 仓库不存在: 请确认 https://github.com/$GITHUB_USER/$REPO_NAME 存在"
    echo "2. 用户名错误: 请确认 GitHub 用户名正确"
    echo "3. 网络问题: 检查网络连接"
    echo "4. 权限问题: 确认你有推送权限"
    echo ""
    echo "解决方案:"
    echo "1. 创建仓库: https://github.com/new"
    echo "2. 检查用户名: 访问 https://github.com 查看右上角"
    echo "3. 使用 SSH: git remote set-url origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
fi

echo ""
echo "========================================"
echo "上传流程完成"
echo "========================================"
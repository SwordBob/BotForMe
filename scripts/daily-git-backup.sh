#!/bin/bash

# 每日 Git 备份脚本
# 自动提交所有更改并推送到远程仓库（如果配置了）

set -e

echo "🔄 开始每日 Git 备份..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 检查是否有更改
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ 没有需要提交的更改"
    exit 0
fi

echo "📊 当前更改状态:"
git status --short

# 添加所有更改
echo "📤 添加所有更改..."
git add .

# 提交
COMMIT_MSG="Daily backup: $(date '+%Y-%m-%d %H:%M:%S')"
echo "💾 提交更改: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# 检查是否有远程仓库
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$REMOTE_URL" ]; then
    echo "🚀 推送到远程仓库..."
    git push origin master
    echo "✅ 已推送到远程仓库"
else
    echo "ℹ️  未配置远程仓库，跳过推送"
    echo "提示: 使用 'git remote add origin <url>' 添加远程仓库"
fi

echo "✅ 每日备份完成！"
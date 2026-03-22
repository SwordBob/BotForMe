#!/bin/bash

# 自动提交新的 Markdown 文件到 Git
# 用法: ./scripts/auto-commit-md.sh [提交信息]

set -e

# 获取提交信息，默认为当前时间
COMMIT_MSG="${1:-"Auto commit: $(date '+%Y-%m-%d %H:%M:%S')"}"

echo "🔍 检查新的 Markdown 文件..."

# 查找所有 .md 文件
MD_FILES=$(find . -name "*.md" -type f | grep -v ".git" | grep -v ".obsidian/workspace")

# 检查是否有未跟踪的 .md 文件
UNTRACKED_MD_FILES=""
for file in $MD_FILES; do
    if ! git ls-files "$file" > /dev/null 2>&1; then
        UNTRACKED_MD_FILES="$UNTRACKED_MD_FILES $file"
    fi
done

if [ -z "$UNTRACKED_MD_FILES" ]; then
    echo "✅ 没有发现新的 Markdown 文件"
    exit 0
fi

echo "📝 发现新的 Markdown 文件:"
echo "$UNTRACKED_MD_FILES" | tr ' ' '\n' | sed 's/^/  /'

# 添加文件到 Git
echo "📤 添加到 Git..."
for file in $UNTRACKED_MD_FILES; do
    git add "$file"
done

# 提交
echo "💾 提交更改..."
git commit -m "$COMMIT_MSG"

echo "✅ 完成！已提交 $(echo "$UNTRACKED_MD_FILES" | wc -w) 个文件"

# 显示 Git 状态
echo ""
echo "📊 当前 Git 状态:"
git status --short
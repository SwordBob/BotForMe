#!/bin/bash
# 自动存档脚本 v0.1
# 用于 DeepSeek V3 + 存档系统

set -e

# 配置
WORKSPACE="/Users/niejq/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
ARCHIVE_FILE="$MEMORY_DIR/$TODAY.md"
MEMORY_FILE="$WORKSPACE/MEMORY.md"

# 创建目录
mkdir -p "$MEMORY_DIR"
mkdir -p "$WORKSPACE/scripts"

# 检查今日存档是否存在，不存在则创建
if [ ! -f "$ARCHIVE_FILE" ]; then
    cat > "$ARCHIVE_FILE" << EOF
# $TODAY 对话存档

## 📅 日期
$TODAY

## 📝 今日摘要

## 🔧 技术讨论

## 📁 文件操作

## 🎯 任务完成

## 💡 重要决策

---
*本文件由 auto_archive.sh 自动创建*
EOF
    echo "✅ 创建今日存档文件: $ARCHIVE_FILE"
else
    echo "📁 今日存档已存在: $ARCHIVE_FILE"
fi

# 检查内存目录中的文件数量
FILE_COUNT=$(find "$MEMORY_DIR" -name "*.md" -type f | wc -l)
echo "📊 内存目录现有 $FILE_COUNT 个存档文件"

# 建议：保留最近7天的存档，压缩更早的
if [ $FILE_COUNT -gt 10 ]; then
    echo "⚠️  存档文件较多，建议整理"
    echo "   最近文件:"
    find "$MEMORY_DIR" -name "*.md" -type f -exec ls -la {} \; | sort -k6,7 | tail -5
fi

# 更新长期记忆文件的修改时间（保持活跃）
touch "$MEMORY_FILE"

echo "✅ 自动存档检查完成"
echo "📁 今日存档: $ARCHIVE_FILE"
echo "🧠 长期记忆: $MEMORY_FILE"
#!/bin/bash
# 手动执行知识维护

cd "$(dirname "$0")"
echo "🚀 手动执行知识维护..."
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

./scripts/weekly-knowledge-maintenance.sh

echo ""
echo "✅ 手动执行完成"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"

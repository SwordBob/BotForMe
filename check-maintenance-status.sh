#!/bin/bash
# 检查知识维护系统状态

cd "$(dirname "$0")"
echo "🔍 知识维护系统状态检查"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

echo "📁 目录结构:"
ls -la knowledge-maintenance-logs/ 2>/dev/null | head -5
echo "..."

echo ""
echo "📊 日志文件:"
find knowledge-maintenance-logs/ -name "*.log" -type f 2>/dev/null | sort -r | head -3 | while read log; do
    echo "  $(basename "$log"): $(stat -f %Sm -t "%Y-%m-%d %H:%M" "$log" 2>/dev/null || echo "未知时间")"
done

echo ""
echo "📈 演化报告:"
find knowledge-evolution-reports/ -name "*.md" -type f 2>/dev/null | sort -r | head -3 | while read report; do
    echo "  $(basename "$report"): $(stat -f %Sm -t "%Y-%m-%d %H:%M" "$report" 2>/dev/null || echo "未知时间")"
done

echo ""
echo "💾 数据备份:"
find knowledge-backups/ -name "*.tar.gz" -type f 2>/dev/null | sort -r | head -3 | while read backup; do
    size=$(du -h "$backup" 2>/dev/null | cut -f1)
    echo "  $(basename "$backup"): $size ($(stat -f %Sm -t "%Y-%m-%d" "$backup" 2>/dev/null || echo "未知时间"))"
done

echo ""
echo "🔄 关系图谱:"
if [ -f "obsidian-graph-data.json" ]; then
    mtime=$(stat -f %Sm -t "%Y-%m-%d %H:%M" "obsidian-graph-data.json" 2>/dev/null)
    age_days=$(( ($(date +%s) - $(stat -f %m "obsidian-graph-data.json" 2>/dev/null)) / 86400 ))
    echo "  最后更新: $mtime ($age_days 天前)"
    
    node_count=$(python3 -c "
import json
try:
    with open('obsidian-graph-data.json', 'r') as f:
        data = json.load(f)
    print(len(data.get('nodes', [])))
except:
    print('无法读取')
" 2>/dev/null || echo "未知")
    echo "  节点数量: $node_count"
else
    echo "  ❌ 未找到关系图谱数据"
fi

echo ""
echo "🚀 LaunchAgent 状态:"
if launchctl list | grep -q "niejq.knowledge"; then
    echo "  ✅ 服务已加载"
else
    echo "  ⚠️  服务未加载"
    echo "    执行: launchctl load $HOME/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist"
fi

echo ""
echo "🎯 建议操作:"
echo "  1. 立即执行维护: ./knowledge-maintenance-now.sh"
echo "  2. 查看最新报告: ls -lt knowledge-evolution-reports/"
echo "  3. 检查系统日志: tail -f knowledge-maintenance-logs/launchd.log"
echo "  4. 验证自动化: launchctl list | grep knowledge"

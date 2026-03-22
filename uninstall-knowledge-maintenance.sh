#!/bin/bash
# 卸载知识维护系统

echo "🗑️  卸载知识维护系统..."
echo ""

# 停止并卸载 LaunchAgent
echo "🛑 停止 LaunchAgent..."
launchctl unload "$HOME/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist" 2>/dev/null || true

echo "📁 删除 plist 文件..."
rm -f "$HOME/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist"

echo "📝 删除脚本文件..."
rm -f knowledge-maintenance-now.sh
rm -f check-maintenance-status.sh
rm -f uninstall-knowledge-maintenance.sh

echo ""
echo "⚠️  注意: 以下目录和数据将被保留:"
echo "  knowledge-maintenance-logs/     # 日志文件"
echo "  knowledge-evolution-reports/    # 演化报告"
echo "  knowledge-evolution-data/       # 历史数据"
echo "  knowledge-backups/              # 备份文件"
echo ""
echo "✅ 卸载完成"
echo ""
echo "如果需要完全清理，请手动删除上述目录。"

#!/bin/bash

# 知识维护系统安装脚本

set -e

echo "========================================"
echo "🔧 知识维护系统安装脚本"
echo "========================================"
echo ""

WORKSPACE_DIR="/Users/niejq/.openclaw/workspace"
PLIST_FILE="com.niejq.knowledge-maintenance.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# 检查工作空间
echo "📁 检查工作空间..."
if [ ! -d "$WORKSPACE_DIR" ]; then
    echo "❌ 工作空间不存在: $WORKSPACE_DIR"
    exit 1
fi

cd "$WORKSPACE_DIR"
echo "✅ 工作空间: $(pwd)"

# 检查必要文件
echo ""
echo "🔍 检查必要文件..."

REQUIRED_FILES=(
    "scripts/weekly-knowledge-evolution.py"
    "scripts/weekly-knowledge-maintenance.sh"
    "scripts/create-obsidian-graph.py"
    "$PLIST_FILE"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ 缺少文件: $file"
        exit 1
    fi
done

# 检查 Python 依赖
echo ""
echo "🐍 检查 Python 依赖..."
python3 -c "import jieba, json, hashlib, datetime" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python 依赖已安装"
else
    echo "⚠️  安装 Python 依赖..."
    pip3 install jieba
fi

# 设置脚本权限
echo ""
echo "🔐 设置脚本权限..."
chmod +x scripts/*.sh
chmod +x scripts/*.py 2>/dev/null || true
echo "✅ 脚本权限已设置"

# 创建必要目录
echo ""
echo "📂 创建必要目录..."
mkdir -p knowledge-maintenance-logs
mkdir -p knowledge-evolution-reports
mkdir -p knowledge-evolution-data
mkdir -p knowledge-backups
echo "✅ 目录已创建"

# 测试脚本
echo ""
echo "🧪 测试维护脚本..."
if ./scripts/weekly-knowledge-maintenance.sh --help 2>/dev/null; then
    echo "✅ 维护脚本测试通过"
else
    echo "⚠️  维护脚本可能需要调整"
fi

# 安装 LaunchAgent
echo ""
echo "🚀 安装 LaunchAgent..."

# 复制 plist 文件到 LaunchAgents 目录
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"
echo "✅ 复制 plist 文件到: $LAUNCH_AGENTS_DIR/"

# 加载 LaunchAgent
echo "📥 加载 LaunchAgent..."
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ LaunchAgent 加载成功"
else
    echo "❌ LaunchAgent 加载失败"
    echo "  请手动执行: launchctl load $LAUNCH_AGENTS_DIR/$PLIST_FILE"
fi

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
launchctl list | grep -i "niejq.knowledge" || echo "⚠️  服务未在运行列表中找到（可能正常）"

# 显示下次执行时间
echo ""
echo "⏰ 计划执行时间:"
echo "  每周日 09:00"
echo "  下次大约: $(date -v nextSunday -v 9H -v 0M '+%Y-%m-%d %H:%M')"

# 创建手动执行脚本
echo ""
echo "📝 创建手动执行脚本..."
cat > knowledge-maintenance-now.sh << 'EOF'
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
EOF

chmod +x knowledge-maintenance-now.sh
echo "✅ 手动执行脚本: ./knowledge-maintenance-now.sh"

# 创建状态检查脚本
cat > check-maintenance-status.sh << 'EOF'
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
EOF

chmod +x check-maintenance-status.sh
echo "✅ 状态检查脚本: ./check-maintenance-status.sh"

# 创建卸载脚本
cat > uninstall-knowledge-maintenance.sh << 'EOF'
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
EOF

chmod +x uninstall-knowledge-maintenance.sh
echo "✅ 卸载脚本: ./uninstall-knowledge-maintenance.sh"

# 显示安装摘要
echo ""
echo "========================================"
echo "🎉 知识维护系统安装完成！"
echo "========================================"
echo ""
echo "📋 安装摘要:"
echo "  ✅ 工作空间: $WORKSPACE_DIR"
echo "  ✅ LaunchAgent: 每周日 09:00 自动执行"
echo "  ✅ 必要目录: 已创建"
echo "  ✅ 脚本权限: 已设置"
echo ""
echo "🚀 可用命令:"
echo "  ./knowledge-maintenance-now.sh      # 手动执行维护"
echo "  ./check-maintenance-status.sh       # 检查系统状态"
echo "  ./uninstall-knowledge-maintenance.sh # 卸载系统"
echo ""
echo "📊 首次执行建议:"
echo "  1. 运行手动维护: ./knowledge-maintenance-now.sh"
echo "  2. 检查状态: ./check-maintenance-status.sh"
echo "  3. 查看报告: open knowledge-evolution-reports/"
echo ""
echo "🔧 配置说明:"
echo "  编辑 scripts/weekly-knowledge-maintenance.sh 调整配置"
echo "  编辑 com.niejq.knowledge-maintenance.plist 调整计划"
echo ""
echo "📞 技术支持:"
echo "  查看日志: tail -f knowledge-maintenance-logs/*.log"
echo "  检查状态: launchctl list | grep knowledge"
echo ""
echo "========================================"
echo "💡 系统将在每周日早上9点自动运行，跟踪知识演化"
echo "========================================"
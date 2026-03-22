#!/bin/bash

# 每周知识维护脚本
# 自动执行知识演化跟踪和关系图谱更新

set -e  # 遇到错误时退出

echo "========================================"
echo "📅 每周知识维护脚本"
echo "========================================"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 配置
LOG_DIR="knowledge-maintenance-logs"
REPORT_DIR="knowledge-evolution-reports"
BACKUP_DIR="knowledge-backups"
WEEKLY_BACKUP=true
SEND_NOTIFICATION=false  # 设置为 true 可启用通知

# 创建目录
mkdir -p "$LOG_DIR" "$REPORT_DIR" "$BACKUP_DIR"

# 日志文件
LOG_FILE="$LOG_DIR/weekly-$(date '+%Y-%m-%d').log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "📝 日志文件: $LOG_FILE"

# 函数：发送通知
send_notification() {
    local title="$1"
    local message="$2"
    
    if [ "$SEND_NOTIFICATION" = true ]; then
        # 这里可以集成各种通知方式
        # 例如：邮件、Slack、Telegram 等
        echo "📧 发送通知: $title"
        echo "  内容: $message"
    fi
}

# 函数：备份重要数据
backup_important_data() {
    if [ "$WEEKLY_BACKUP" = true ]; then
        echo "💾 备份重要数据..."
        
        local backup_file="$BACKUP_DIR/knowledge-backup-$(date '+%Y-%m-%d').tar.gz"
        
        # 备份关键文件
        tar -czf "$backup_file" \
            "MEMORY.md" \
            "knowledge-evolution-data/" \
            "obsidian-graph-data.json" \
            "scripts/" \
            "*.md" 2>/dev/null || true
        
        echo "  备份文件: $backup_file"
        echo "  大小: $(du -h "$backup_file" | cut -f1)"
    fi
}

# 函数：检查 Git 状态
check_git_status() {
    echo "🔍 检查 Git 状态..."
    
    if git status --porcelain | grep -q "^[ MADRC]"; then
        local changes=$(git status --porcelain | wc -l)
        echo "⚠️  有未提交的更改: $changes 个文件"
        
        # 显示主要更改
        echo "  主要更改:"
        git status --porcelain | head -5 | while read line; do
            echo "    $line"
        done
        
        return 1
    else
        echo "✅ Git 工作区干净"
        return 0
    fi
}

# 函数：执行知识演化跟踪
run_evolution_tracking() {
    echo "📈 执行知识演化跟踪..."
    
    # 运行 Python 脚本
    python3 scripts/weekly-knowledge-evolution.py
    
    # 检查报告文件
    local latest_report=$(ls -t "$REPORT_DIR/knowledge-evolution-"*.md 2>/dev/null | head -1)
    
    if [ -n "$latest_report" ]; then
        echo "📄 最新报告: $latest_report"
        
        # 提取关键指标
        local file_count=$(grep -oP '总文件数.*?\|\s*\K\d+' "$latest_report" | head -1)
        local change_rate=$(grep -oP '总变化率.*?\|\s*\K[0-9.]+' "$latest_report" | head -1)
        
        echo "  文件总数: $file_count"
        echo "  变化率: ${change_rate}%"
        
        # 如果有显著变化，发送通知
        if [ -n "$change_rate" ] && [ $(echo "$change_rate > 5" | bc) -eq 1 ]; then
            send_notification "知识库显著变化" "检测到 ${change_rate}% 的变化，建议查看详细报告"
        fi
    fi
}

# 函数：更新关系图谱
update_relationship_graph() {
    echo "🔄 更新关系图谱..."
    
    # 检查是否需要更新
    local graph_age_days=0
    if [ -f "obsidian-graph-data.json" ]; then
        local graph_mtime=$(stat -f %m "obsidian-graph-data.json")
        local now=$(date +%s)
        graph_age_days=$(( (now - graph_mtime) / 86400 ))
    fi
    
    # 如果图谱超过7天或检测到显著变化，则更新
    if [ $graph_age_days -ge 7 ]; then
        echo "  图谱已过期 ($graph_age_days 天)，正在更新..."
        python3 scripts/create-obsidian-graph.py
        
        # 检查是否成功
        if [ -f "obsidian-graph-data.json" ]; then
            local node_count=$(python3 -c "
import json
with open('obsidian-graph-data.json', 'r') as f:
    data = json.load(f)
print(len(data['nodes']))
" 2>/dev/null || echo "0")
            
            echo "✅ 图谱更新完成"
            echo "  节点数: $node_count"
            
            send_notification "关系图谱已更新" "知识图谱已更新，包含 $node_count 个节点"
        else
            echo "❌ 图谱更新失败"
        fi
    else
        echo "✅ 图谱仍新鲜 ($graph_age_days 天)，跳过更新"
    fi
}

# 函数：清理旧文件
cleanup_old_files() {
    echo "🧹 清理旧文件..."
    
    # 保留最近4周的日志
    find "$LOG_DIR" -name "weekly-*.log" -mtime +28 -delete 2>/dev/null || true
    echo "  清理旧日志文件"
    
    # 保留最近12周的备份
    find "$BACKUP_DIR" -name "knowledge-backup-*.tar.gz" -mtime +84 -delete 2>/dev/null || true
    echo "  清理旧备份文件"
    
    # 清理临时文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "  清理 Python 缓存文件"
}

# 函数：生成维护摘要
generate_maintenance_summary() {
    echo "📋 生成维护摘要..."
    
    local summary_file="$LOG_DIR/maintenance-summary-$(date '+%Y-%m-%d').md"
    
    cat > "$summary_file" << EOF
# 每周知识维护摘要 - $(date '+%Y-%m-%d')

## 📊 执行结果

### 1. 知识演化跟踪
- **执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **日志文件**: $LOG_FILE
$(if [ -n "$latest_report" ]; then echo "- **演化报告**: $(basename "$latest_report")"; fi)

### 2. 关系图谱状态
- **图谱年龄**: $graph_age_days 天
- **是否需要更新**: $([ $graph_age_days -ge 7 ] && echo "是" || echo "否")

### 3. 数据备份
- **备份执行**: $([ "$WEEKLY_BACKUP" = true ] && echo "是" || echo "否")
$(if [ "$WEEKLY_BACKUP" = true ] && [ -n "$backup_file" ]; then echo "- **备份文件**: $(basename "$backup_file")"; fi)

### 4. 清理工作
- **清理完成**: 是
- **保留策略**: 日志(4周)、备份(12周)

## 🎯 建议操作

### 立即执行
1. 查看演化报告: $([ -n "$latest_report" ] && echo "open \"$latest_report\"" || echo "无新报告")
2. 检查知识图谱: $([ $graph_age_days -ge 7 ] && echo "open obsidian-graph-visualizer.html" || echo "图谱已最新")

### 本周计划
1. 整理新增的知识内容
2. 优化文件之间的链接
3. 删除或归档过时内容

## 📈 长期趋势

### 文件增长
$(if [ -f "knowledge-evolution-data/knowledge-snapshots.json" ]; then
    python3 -c "
import json, datetime
try:
    with open('knowledge-evolution-data/knowledge-snapshots.json', 'r') as f:
        data = json.load(f)
    
    if data['snapshots']:
        print('最近4周文件数量变化:')
        for snap in data['snapshots'][-4:]:
            date = snap['id']
            count = snap['file_count']
            size_mb = snap['total_size'] / (1024*1024)
            print(f'- {date}: {count} 个文件 ({size_mb:.1f} MB)')
except:
    print('无法加载历史数据')
")
fi)

## 🔧 系统状态

### 脚本健康度
- 演化跟踪脚本: $(python3 -c "import sys; sys.path.append('.'); from scripts.weekly_knowledge_evolution import main; print('正常')" 2>/dev/null || echo "需要检查")
- 图谱生成脚本: $(python3 -c "import sys; sys.path.append('.'); from scripts.create_obsidian_graph import main; print('正常')" 2>/dev/null || echo "需要检查")

### 存储使用
$(df -h . | tail -1 | awk '{print "- 总空间: "$2"\n- 已用: "$3" ("$5")\n- 可用: "$4}')

---

**维护完成时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**下次维护计划**: $(date -v+7d '+%Y-%m-%d')

> 提示：定期维护有助于保持知识库的健康和可用性。
EOF
    
    echo "  摘要文件: $summary_file"
}

# 主执行流程
main() {
    echo "🚀 开始每周知识维护..."
    echo ""
    
    # 1. 检查 Git 状态
    check_git_status
    echo ""
    
    # 2. 备份重要数据
    backup_important_data
    echo ""
    
    # 3. 执行知识演化跟踪
    run_evolution_tracking
    echo ""
    
    # 4. 更新关系图谱
    update_relationship_graph
    echo ""
    
    # 5. 清理旧文件
    cleanup_old_files
    echo ""
    
    # 6. 生成维护摘要
    generate_maintenance_summary
    echo ""
    
    echo "========================================"
    echo "✅ 每周知识维护完成！"
    echo "========================================"
    echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "📋 输出文件:"
    echo "  日志: $LOG_FILE"
    [ -n "$summary_file" ] && echo "  摘要: $summary_file"
    [ -n "$latest_report" ] && echo "  报告: $latest_report"
    [ -n "$backup_file" ] && echo "  备份: $backup_file"
    echo ""
    echo "🎯 下一步:"
    echo "  1. 查看维护摘要了解详情"
    echo "  2. 根据报告优化知识库"
    echo "  3. 探索更新后的关系图谱"
    echo ""
    
    # 发送完成通知
    send_notification "每周知识维护完成" "知识库维护已完成，请查看摘要和报告"
    
    return 0
}

# 执行主函数
main "$@"
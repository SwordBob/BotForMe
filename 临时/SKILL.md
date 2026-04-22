# 知识演化跟踪器技能

## 描述
自动化知识演化跟踪系统，用于定期分析 Markdown 文件变化、生成演化报告、更新关系图谱，并提供数据驱动的维护建议。

## 适用场景
- 用户需要定期跟踪知识库变化
- 用户想要可视化知识增长趋势
- 用户需要自动化维护知识库
- 用户想要基于数据的优化建议

## 核心功能
1. **📈 自动演化分析** - 每周分析文件变化
2. **📊 智能报告生成** - 生成详细演化报告
3. **🔄 关系图谱更新** - 自动更新知识网络
4. **💾 数据备份保护** - 定期备份重要文件
5. **🧹 系统自动维护** - 清理旧文件，保持系统健康

## 安装与配置

### 前提条件
- macOS 系统（使用 LaunchAgent 自动化）
- Python 3.x 环境
- OpenClaw 工作空间已初始化

### 快速安装
```bash
# 在工作空间根目录执行
./setup-knowledge-maintenance.sh
```

### 手动安装步骤
1. **设置脚本权限**：
   ```bash
   chmod +x scripts/*.sh
   chmod +x scripts/*.py
   ```

2. **创建必要目录**：
   ```bash
   mkdir -p knowledge-maintenance-logs \
            knowledge-evolution-reports \
            knowledge-evolution-data \
            knowledge-backups
   ```

3. **安装 LaunchAgent**：
   ```bash
   cp com.niejq.knowledge-maintenance.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist
   ```

## 使用方法

### 基本命令
```bash
# 立即执行知识维护
./knowledge-maintenance-now.sh

# 检查系统状态
./check-maintenance-status.sh

# 查看最新报告
open knowledge-evolution-reports/$(ls -t knowledge-evolution-reports/ | head -1)

# 卸载系统
./uninstall-knowledge-maintenance.sh
```

### 自动化计划
系统配置为 **每周日早上9点自动执行**，包含：
1. 📸 创建知识快照
2. 📊 分析文件变化
3. 📈 生成演化报告
4. 🔄 更新关系图谱（如变化显著）
5. 💾 自动备份
6. 🧹 清理旧文件

### 输出文件说明

#### 1. 演化报告 (`knowledge-evolution-reports/`)
每周生成的 Markdown 报告，包含：
- **变化分析**：新增/修改/删除的文件统计
- **趋势图表**：文件数量增长可视化
- **维护建议**：基于数据的优化建议
- **系统状态**：技术详情和健康度

#### 2. 执行日志 (`knowledge-maintenance-logs/`)
详细的执行记录：
- `weekly-YYYY-MM-DD.log` - 每周执行日志
- `maintenance-summary-YYYY-MM-DD.md` - 维护摘要
- `launchd.log` - 系统服务日志

#### 3. 历史数据 (`knowledge-evolution-data/`)
保存12周的历史快照：
- `knowledge-snapshots.json` - 文件快照元数据

#### 4. 自动备份 (`knowledge-backups/`)
每周备份重要文件：
- `knowledge-backup-YYYY-MM-DD.tar.gz` - 压缩备份包

## 配置调整

### 调整执行时间
编辑 `com.niejq.knowledge-maintenance.plist`：
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>   <!-- 0=周日, 1=周一, ..., 6=周六 -->
    <integer>0</integer>
    <key>Hour</key>      <!-- 0-23 -->
    <integer>9</integer>
    <key>Minute</key>    <!-- 0-59 -->
    <integer>0</integer>
</dict>
```

重新加载配置：
```bash
launchctl unload ~/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist
launchctl load ~/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist
```

### 调整维护参数
编辑 `scripts/weekly-knowledge-maintenance.sh`：
```bash
# 主要配置参数
LOG_DIR="knowledge-maintenance-logs"
REPORT_DIR="knowledge-evolution-reports"
BACKUP_DIR="knowledge-backups"
WEEKLY_BACKUP=true
SEND_NOTIFICATION=false  # 设置为 true 可启用通知
```

### 调整分析参数
编辑 `scripts/weekly-knowledge-evolution.py`：
```python
CONFIG = {
    "data_dir": "knowledge-evolution-data",
    "snapshot_file": "knowledge-snapshots.json",
    "report_dir": "knowledge-evolution-reports",
    "weeks_to_keep": 12,           # 保留12周数据
    "min_change_threshold": 0.01,  # 1% 变化阈值
}
```

## 故障排除

### 常见问题

#### 1. 系统未自动执行
```bash
# 检查服务状态
launchctl list | grep knowledge

# 重新加载服务
launchctl unload ~/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist
launchctl load ~/Library/LaunchAgents/com.niejq.knowledge-maintenance.plist

# 查看系统日志
tail -f knowledge-maintenance-logs/launchd.log
```

#### 2. 脚本执行失败
```bash
# 检查权限
ls -la scripts/

# 测试脚本
./scripts/weekly-knowledge-maintenance.sh --help

# 查看详细错误
bash -x ./scripts/weekly-knowledge-maintenance.sh 2>&1 | head -50
```

#### 3. Python 依赖问题
```bash
# 安装依赖
pip3 install jieba

# 检查 Python 环境
python3 --version
python3 -c "import jieba; print('✅ jieba 正常')"
```

#### 4. 磁盘空间不足
```bash
# 检查磁盘使用
df -h .

# 清理旧文件
find knowledge-backups/ -name "*.tar.gz" -mtime +84 -delete
find knowledge-maintenance-logs/ -name "*.log" -mtime +28 -delete
```

### 日志位置
- **系统服务日志**: `knowledge-maintenance-logs/launchd.log`
- **每周执行日志**: `knowledge-maintenance-logs/weekly-YYYY-MM-DD.log`
- **错误日志**: `knowledge-maintenance-logs/launchd-error.log`

## 安全说明

### 重要安全特性
1. **只读操作**：系统对 `.md` 文件执行只读分析，不会修改或删除源文件
2. **文件指纹**：使用 SHA256 哈希进行变化检测，不依赖文件名
3. **数据隔离**：所有生成的文件都在专用目录中
4. **备份保护**：定期备份重要数据，支持恢复

### 不会执行的操作
- ❌ 不会删除工作空间中的 `.md` 文件
- ❌ 不会修改源文件内容
- ❌ 不会重命名或移动文件
- ❌ 不会执行任何破坏性操作

## 集成建议

### 与 Obsidian 集成
1. 将演化报告目录添加到 Obsidian 仓库
2. 使用 Dataview 插件显示统计信息
3. 创建索引文件链接所有报告

### 与 Git 集成
```bash
# 将报告添加到 Git（可选）
git add knowledge-evolution-reports/
git commit -m "添加每周知识演化报告"

# 或添加到 .gitignore（如果不想版本控制）
echo "knowledge-evolution-reports/" >> .gitignore
```

### 添加通知功能
编辑 `scripts/weekly-knowledge-maintenance.sh`：
```bash
SEND_NOTIFICATION=true

send_notification() {
    local title="$1"
    local message="$2"
    
    # 邮件通知
    echo "$message" | mail -s "$title" your-email@example.com
    
    # 或系统通知
    osascript -e "display notification \"$message\" with title \"$title\""
}
```

## 最佳实践

### 1. 定期检查
- 每周一查看演化报告
- 每月回顾趋势变化
- 每季度评估系统效果

### 2. 主动维护
- 根据报告建议优化知识库
- 及时处理警告信息
- 保持系统更新

### 3. 数据驱动
- 基于报告做决策
- 关注关键指标（变化率、文件分布等）
- 调整维护策略

### 4. 知识管理
- 从枢纽文件开始学习
- 沿着关联路径探索
- 发现隐藏的知识联系

## 扩展功能

### 计划扩展
1. **智能分类** - 自动识别知识领域
2. **质量评分** - 评估内容质量
3. **关联分析** - 发现隐藏的知识联系
4. **预测模型** - 预测知识增长趋势

### 自定义分析
可以修改 `scripts/weekly-knowledge-evolution.py` 添加：
- 自定义文件分类规则
- 特定的分析指标
- 个性化的报告格式

## 技术支持

### 获取帮助
1. **查看日志**: `tail -f knowledge-maintenance-logs/*.log`
2. **检查状态**: `./check-maintenance-status.sh`
3. **手动测试**: `./knowledge-maintenance-now.sh`

### 报告问题
如果遇到问题，请提供：
1. 错误日志内容
2. 系统环境信息
3. 复现步骤

### 更新系统
定期检查脚本更新，确保系统稳定运行。

---

## 技能触发关键词
- "知识演化跟踪"
- "知识维护系统"
- "演化报告"
- "知识图谱更新"
- "自动化知识管理"
- "检查知识状态"
- "生成演化分析"
- "维护知识库"

## 相关文件
- `知识演化跟踪系统指南.md` - 完整用户指南
- `关系图谱工具汇总.md` - 关系图谱工具说明
- `Obsidian-图谱增强指南.md` - Obsidian 集成指南

## 版本信息
- **版本**: 1.0.0
- **创建日期**: 2026-03-22
- **最后更新**: 2026-03-22
- **作者**: OpenClaw AI Assistant
- **依赖**: Python 3.x, jieba, macOS LaunchAgent
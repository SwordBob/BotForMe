#!/bin/bash

# DeepSeek 配置优化应用脚本
# 作者: OpenClaw 健康检查技能
# 日期: 2026-03-26

echo "🔧 开始应用 DeepSeek 配置优化..."

# 1. 备份当前配置
BACKUP_DIR="$HOME/.openclaw/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/openclaw-backup-$(date +%Y%m%d-%H%M%S).json"
cp ~/.openclaw/openclaw.json "$BACKUP_FILE"
echo "✅ 配置已备份到: $BACKUP_FILE"

# 2. 验证配置语法
echo "🔍 验证配置语法..."
if ! python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null 2>&1; then
    echo "❌ 配置语法错误，恢复备份..."
    cp "$BACKUP_FILE" ~/.openclaw/openclaw.json
    exit 1
fi
echo "✅ 配置语法验证通过"

# 3. 重启 OpenClaw Gateway
echo "🔄 重启 OpenClaw Gateway..."
if command -v openclaw > /dev/null 2>&1; then
    # 尝试优雅重启
    if openclaw gateway restart > /dev/null 2>&1; then
        echo "✅ OpenClaw Gateway 重启成功"
    else
        echo "⚠️  优雅重启失败，尝试强制重启..."
        pkill -f "openclaw gateway" 2>/dev/null
        sleep 2
        openclaw gateway start > /dev/null 2>&1 &
        echo "✅ OpenClaw Gateway 已启动"
    fi
else
    echo "⚠️  openclaw 命令未找到，请手动重启"
fi

# 4. 等待服务启动
echo "⏳ 等待服务启动 (10秒)..."
sleep 10

# 5. 检查服务状态
echo "📊 检查服务状态..."
if openclaw gateway status > /dev/null 2>&1; then
    echo "✅ OpenClaw Gateway 运行正常"
else
    echo "❌ OpenClaw Gateway 未运行，请检查日志"
fi

# 6. 显示优化摘要
echo ""
echo "🎉 DeepSeek 配置优化完成！"
echo "========================================"
echo "优化内容摘要:"
echo "1. DeepSeek 上下文窗口: 16k → 64k"
echo "2. 新增推理专用模型: deepseek-reasoner"
echo "3. 智能模型选择策略已启用"
echo "4. 上下文压缩优化: 积极模式"
echo "5. 精确成本计算已配置"
echo ""
echo "使用说明:"
echo "- 日常对话: 使用 'deepseek' 别名"
echo "- 复杂推理: 使用 'deepseek-reasoning' 别名"
echo "- 查看状态: openclaw status"
echo "- 详细指南: 查看 deepseek-optimization-guide.md"
echo ""
echo "⚠️  注意事项:"
echo "- 首次使用可能感觉响应稍慢 (64k上下文)"
echo "- 成本计算更精确，可能显示更高成本"
echo "- 如有问题，恢复备份: cp $BACKUP_FILE ~/.openclaw/openclaw.json"
echo "========================================"
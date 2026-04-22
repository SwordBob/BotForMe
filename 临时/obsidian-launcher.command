#!/bin/bash

# Obsidian 启动器 - 双击运行

cd "$(dirname "$0")"
WORKSPACE_PATH="$HOME/.openclaw/workspace"

echo "========================================"
echo "   OpenClaw + Obsidian 工作空间启动器"
echo "========================================"
echo ""
echo "工作空间: $WORKSPACE_PATH"
echo ""

# 检查目录是否存在
if [ ! -d "$WORKSPACE_PATH" ]; then
    echo "❌ 错误: 工作空间目录不存在"
    echo "请确保 OpenClaw 已正确安装"
    exit 1
fi

# 尝试用 Obsidian 打开
echo "🚀 正在启动 Obsidian..."
if [ -d "/Applications/Obsidian.app" ]; then
    open -a Obsidian "$WORKSPACE_PATH"
    echo "✅ 已请求打开 Obsidian"
else
    echo "⚠️  未找到 Obsidian.app"
    echo ""
    echo "📋 手动操作步骤:"
    echo "1. 打开 Obsidian"
    echo "2. 点击左下角 '打开其他仓库'"
    echo "3. 选择路径: $WORKSPACE_PATH"
    echo "4. 或选择: $HOME/openclaw-workspace (符号链接)"
fi

echo ""
echo "📁 目录内容:"
ls -la "$WORKSPACE_PATH" | head -10
echo "..."

# 保持窗口打开
echo ""
read -p "按回车键退出..."
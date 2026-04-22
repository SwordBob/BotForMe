#!/bin/bash

# 用 Obsidian 打开 OpenClaw 工作空间

WORKSPACE_PATH="$HOME/.openclaw/workspace"

echo "🚀 正在用 Obsidian 打开工作空间..."
echo "路径: $WORKSPACE_PATH"

# 检查 Obsidian 是否安装
if [ -d "/Applications/Obsidian.app" ]; then
    echo "✅ 检测到 Obsidian.app"
    
    # 方法1: 使用 open 命令
    echo "📂 使用方法1: open 命令"
    open -a Obsidian "$WORKSPACE_PATH"
    
    # 方法2: 使用 Obsidian URI 协议
    echo "🔗 使用方法2: Obsidian URI"
    open "obsidian://open?vault=$(echo -n "$WORKSPACE_PATH" | base64)"
    
elif command -v obsidian &> /dev/null; then
    echo "✅ 检测到 obsidian 命令行工具"
    obsidian "$WORKSPACE_PATH"
else
    echo "❌ 未找到 Obsidian"
    echo "请先安装 Obsidian: https://obsidian.md"
    
    # 创建符号链接作为备用方案
    echo "🔗 创建符号链接备用..."
    ln -sf "$WORKSPACE_PATH" "$HOME/openclaw-workspace"
    echo "✅ 已创建: $HOME/openclaw-workspace"
    echo "📝 你可以手动用 Obsidian 打开这个目录"
fi

echo ""
echo "💡 提示:"
echo "1. 如果 Obsidian 没有自动打开，请手动打开并选择 '打开其他仓库'"
echo "2. 选择路径: $WORKSPACE_PATH"
echo "3. 或使用符号链接: $HOME/openclaw-workspace"
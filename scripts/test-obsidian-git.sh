#!/bin/bash

# 测试 Obsidian + Git 集成

echo "🧪 测试 Obsidian + Git 集成..."
echo "========================================"

# 1. 检查 Git 配置
echo "1. 检查 Git 配置..."
git config --list | grep -E "(user\.name|user\.email)" || echo "⚠️  Git 用户配置未找到"

# 2. 检查 Obsidian 配置
echo ""
echo "2. 检查 Obsidian 配置..."
if [ -d ".obsidian" ]; then
    echo "✅ .obsidian 目录存在"
    ls -la .obsidian/*.json | wc -l | xargs echo "  配置文件数量:"
else
    echo "❌ .obsidian 目录不存在"
fi

# 3. 检查脚本权限
echo ""
echo "3. 检查脚本权限..."
SCRIPTS=("scripts/auto-commit-md.sh" "scripts/daily-git-backup.sh" "scripts/test-obsidian-git.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script 可执行"
    else
        echo "❌ $script 不可执行"
    fi
done

# 4. 检查 Git 状态
echo ""
echo "4. 检查 Git 状态..."
git status --short

# 5. 创建测试文件
echo ""
echo "5. 创建测试文件..."
TEST_FILE="测试-Obsidian-Git-集成-$(date +%s).md"
cat > "$TEST_FILE" << EOF
# 测试文件

这是一个测试文件，用于验证 Obsidian + Git 集成。

- 创建时间: $(date '+%Y-%m-%d %H:%M:%S')
- 目的: 测试自动提交功能

## 测试步骤

1. 创建测试文件
2. 运行自动提交脚本
3. 验证文件是否被正确提交

## 预期结果

- 文件应该被添加到 Git
- 应该有一个新的提交
- 文件应该出现在 Git 历史中
EOF

echo "✅ 创建测试文件: $TEST_FILE"

# 6. 测试自动提交脚本
echo ""
echo "6. 测试自动提交脚本..."
./scripts/auto-commit-md.sh "测试: 添加测试文件"

# 7. 显示结果
echo ""
echo "7. 测试结果:"
echo "========================================"
git log --oneline -3
echo ""
echo "📁 测试文件: $TEST_FILE"
echo "📊 Git 状态:"
git status --short

# 8. 清理（可选）
echo ""
read -p "是否删除测试文件？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$TEST_FILE"
    git add "$TEST_FILE"
    git commit -m "清理: 删除测试文件"
    echo "✅ 已删除测试文件"
fi

echo ""
echo "🎉 测试完成！"
echo "========================================"
echo "下一步:"
echo "1. 打开 Obsidian 并加载这个目录"
echo "2. 探索你的笔记"
echo "3. 尝试使用图形视图和反向链接"
echo "4. 考虑设置远程仓库进行备份"
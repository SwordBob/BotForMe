#!/bin/bash

# GitHub 完整推送脚本
# 专为 SwordBob 的 BotForMe 仓库设计

set -e

echo "========================================"
echo "🚀 GitHub 完整推送脚本"
echo "========================================"
echo ""

# 配置
GITHUB_USER="SwordBob"
REPO_NAME="BotForMe"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 推送配置:${NC}"
echo "   用户: $GITHUB_USER"
echo "   仓库: $REPO_NAME"
echo "   地址: $REPO_URL"
echo ""

# 步骤1: 检查仓库是否存在
echo -e "${YELLOW}步骤1: 检查 GitHub 仓库...${NC}"
if curl -s -I "$REPO_URL" | grep -q "200 OK"; then
    echo -e "${GREEN}✅ 仓库已存在${NC}"
    REPO_EXISTS=true
else
    echo -e "${RED}❌ 仓库不存在${NC}"
    echo ""
    echo "请先创建 GitHub 仓库:"
    echo "1. 访问: https://github.com/new"
    echo "2. 仓库名: BotForMe"
    echo "3. 描述: OpenClaw workspace - AI assistant knowledge base and tools"
    echo "4. 选择: Public"
    echo "5. 不要初始化 README, .gitignore, license"
    echo ""
    read -p "是否已创建仓库？ (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先创建仓库，然后重新运行此脚本"
        exit 1
    fi
    REPO_EXISTS=true
fi

# 步骤2: 配置 Git 远程仓库
echo ""
echo -e "${YELLOW}步骤2: 配置 Git 远程仓库...${NC}"
if git remote | grep -q origin; then
    CURRENT_URL=$(git remote get-url origin)
    echo "当前远程仓库: $CURRENT_URL"
    
    if [ "$CURRENT_URL" != "$REMOTE_URL" ]; then
        echo "更新为: $REMOTE_URL"
        git remote set-url origin "$REMOTE_URL"
    fi
else
    echo "添加远程仓库: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
fi

# 步骤3: 确保分支为 main
echo ""
echo -e "${YELLOW}步骤3: 检查分支...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "重命名分支: $CURRENT_BRANCH -> main"
    git branch -M main
else
    echo "当前分支: main"
fi

# 步骤4: 显示推送摘要
echo ""
echo -e "${YELLOW}步骤4: 推送摘要${NC}"
echo "   提交数: $(git rev-list --count HEAD)"
echo "   文件数: $(git ls-files | wc -l)"
echo "   大小: $(git count-objects -vH | grep size-pack | cut -d: -f2)"
echo ""

# 步骤5: 确认推送
echo -e "${YELLOW}步骤5: 确认推送${NC}"
echo "即将推送到: $REPO_URL"
echo ""
read -p "是否继续？ (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "推送取消"
    exit 0
fi

# 步骤6: 执行推送
echo ""
echo -e "${YELLOW}步骤6: 执行推送...${NC}"
START_TIME=$(date +%s)

if git push -u origin main; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo -e "${GREEN}🎉 推送成功！${NC}"
    echo ""
    echo "⏱️  用时: ${DURATION} 秒"
    echo "🌐 仓库: $REPO_URL"
    echo ""
    echo "✅ 完成！"
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    echo ""
    echo "请尝试:"
    echo "1. 确认仓库名称正确"
    echo "2. 检查网络连接"
    echo "3. 使用 SSH 方式:"
    echo "   git remote set-url origin git@github.com:SwordBob/BotForMe.git"
    echo "   git push -u origin main"
fi

echo ""
echo "========================================"
echo "脚本执行完成"
echo "========================================"

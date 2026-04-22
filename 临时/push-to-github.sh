#!/bin/bash

# 简化版 GitHub 上传脚本
# 无需 GitHub CLI 登录

set -e

echo "========================================"
echo "🚀 简化版 GitHub 上传"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 主函数
main() {
    print_info "开始 GitHub 上传流程..."
    
    # 1. 检查 Git 状态
    print_info "1. 检查 Git 状态..."
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "发现未提交的更改"
        git status --short
        echo ""
        read -p "是否先提交这些更改？ (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "准备上传到 GitHub - $(date '+%Y-%m-%d %H:%M:%S')"
            print_success "更改已提交"
        else
            print_warning "继续使用当前未提交状态"
        fi
    else
        print_success "Git 工作区干净"
    fi
    
    # 2. 获取 GitHub 用户名
    print_info "2. 获取 GitHub 信息..."
    echo ""
    echo "请输入你的 GitHub 用户名（例如：niejq）："
    read -r GITHUB_USER
    
    if [ -z "$GITHUB_USER" ]; then
        print_error "用户名不能为空"
        exit 1
    fi
    
    # 3. 检查远程仓库
    print_info "3. 配置远程仓库..."
    REPO_NAME="BotForMe"
    REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
    
    if git remote | grep -q "origin"; then
        CURRENT_URL=$(git remote get-url origin)
        print_warning "已配置远程仓库: $CURRENT_URL"
        read -p "是否覆盖？ (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote remove origin
            git remote add origin "$REMOTE_URL"
            print_success "远程仓库已更新: $REMOTE_URL"
        else
            print_info "使用现有远程仓库"
        fi
    else
        git remote add origin "$REMOTE_URL"
        print_success "远程仓库已添加: $REMOTE_URL"
    fi
    
    # 4. 确保分支名为 main
    print_info "4. 检查分支..."
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_warning "当前分支为 '$CURRENT_BRANCH'，重命名为 'main'"
        git branch -M main
        print_success "分支已重命名为 main"
    else
        print_success "当前分支为 main"
    fi
    
    # 5. 显示上传摘要
    print_info "5. 上传摘要:"
    echo ""
    echo "   仓库名称: $REPO_NAME"
    echo "   GitHub 用户: $GITHUB_USER"
    echo "   远程地址: $REMOTE_URL"
    echo "   分支: main"
    echo "   提交数: $(git rev-list --count HEAD)"
    echo "   文件数: $(git ls-files | wc -l)"
    echo ""
    
    # 6. 确认上传
    print_warning "重要：请确保你已经在 GitHub 上创建了仓库 '$REPO_NAME'"
    echo ""
    echo "创建仓库步骤:"
    echo "1. 访问: https://github.com/new"
    echo "2. 仓库名: BotForMe"
    echo "3. 描述: OpenClaw workspace - AI assistant knowledge base and tools"
    echo "4. 选择: Public"
    echo "5. 不要初始化 README, .gitignore, license"
    echo "6. 点击 'Create repository'"
    echo ""
    
    read -p "是否已在 GitHub 上创建了仓库？ (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "请先创建 GitHub 仓库"
        echo ""
        echo "创建后重新运行此脚本"
        exit 1
    fi
    
    # 7. 执行推送
    print_info "6. 开始推送代码到 GitHub..."
    echo ""
    
    print_info "执行: git push -u origin main"
    echo ""
    
    # 尝试推送
    if git push -u origin main; then
        print_success "🎉 代码推送成功！"
        echo ""
        echo "🌐 仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
        echo "📊 提交查看: https://github.com/$GITHUB_USER/$REPO_NAME/commits/main"
        echo "📁 文件浏览: https://github.com/$GITHUB_USER/$REPO_NAME"
        
        # 生成成功报告
        echo ""
        print_info "生成上传报告..."
        cat > "github-upload-success.md" << EOF
# GitHub 上传成功报告

## 🎉 上传成功！
- **时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **仓库**: https://github.com/$GITHUB_USER/$REPO_NAME
- **分支**: main
- **用户**: $GITHUB_USER

## 📊 上传统计
- 总提交数: $(git rev-list --count HEAD)
- 总文件数: $(git ls-files | wc -l)
- Markdown 文件: $(git ls-files "*.md" | wc -l)
- 脚本文件: $(git ls-files "*.sh" "*.py" | wc -l)

## 🚀 下一步操作
1. **访问仓库**: https://github.com/$GITHUB_USER/$REPO_NAME
2. **添加描述**: 在仓库页面添加项目描述
3. **设置主题**: 添加相关主题标签
4. **查看代码**: 浏览上传的文件

## 🔗 重要链接
- 仓库主页: https://github.com/$GITHUB_USER/$REPO_NAME
- 提交历史: https://github.com/$GITHUB_USER/$REPO_NAME/commits/main
- 文件浏览: https://github.com/$GITHUB_USER/$REPO_NAME

## 📞 验证上传
运行以下命令验证：
\`\`\`bash
# 克隆仓库到新位置验证
cd /tmp
git clone https://github.com/$GITHUB_USER/$REPO_NAME.git
cd $REPO_NAME
ls -la
\`\`\`
EOF
        
        print_success "报告已生成: github-upload-success.md"
        
    else
        print_error "推送失败"
        echo ""
        echo "可能的原因:"
        echo "1. 仓库不存在或名称错误"
        echo "2. 网络连接问题"
        echo "3. 认证失败"
        echo "4. 权限不足"
        echo ""
        echo "解决方案:"
        echo "1. 确认仓库名称: BotForMe"
        echo "2. 确认 GitHub 用户名: $GITHUB_USER"
        echo "3. 检查网络连接"
        echo "4. 使用 SSH 方式（如果需要）"
        echo ""
        echo "SSH 方式命令:"
        echo "  git remote set-url origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
        echo "  git push -u origin main"
    fi
    
    echo ""
    echo "========================================"
    print_success "上传流程完成"
    echo "========================================"
}

# 执行主函数
main "$@"
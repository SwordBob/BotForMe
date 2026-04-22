#!/bin/bash

# SwordBob 专用 GitHub 上传脚本
# 一键上传 OpenClaw 工作空间到 GitHub

set -e

echo "╔══════════════════════════════════════════╗"
echo "║    🚀 SwordBob GitHub 上传工具           ║"
echo "║    📦 仓库: SwordBob/BotForMe            ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
GITHUB_USER="SwordBob"
REPO_NAME="BotForMe"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
SSH_URL="git@github.com:$GITHUB_USER/$REPO_NAME.git"

# 函数：打印带颜色的消息
print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║    $1${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 检查环境
check_environment() {
    print_header "🔍 环境检查"
    
    # 检查目录
    if [ ! -f "README.md" ]; then
        print_error "错误：不在 OpenClaw 工作空间"
        echo "当前目录: $(pwd)"
        echo "请切换到: ~/.openclaw/workspace"
        exit 1
    fi
    
    print_success "工作空间: $(pwd)"
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        print_error "Git 未安装"
        exit 1
    fi
    
    print_success "Git 版本: $(git --version | cut -d' ' -f3)"
    
    # 检查网络
    print_step "检查网络连接..."
    if ping -c 1 github.com &> /dev/null; then
        print_success "GitHub 可访问"
    else
        print_warning "GitHub 访问可能有问题，继续尝试..."
    fi
}

# 检查仓库状态
check_repository() {
    print_header "📦 仓库状态检查"
    
    # 检查本地仓库
    print_step "检查本地 Git 仓库..."
    if [ -d ".git" ]; then
        print_success "Git 仓库已初始化"
        echo "   分支: $(git branch --show-current)"
        echo "   提交: $(git rev-list --count HEAD)"
        echo "   文件: $(git ls-files | wc -l)"
    else
        print_error "不是 Git 仓库"
        exit 1
    fi
    
    # 检查远程仓库
    print_step "检查远程仓库..."
    if git remote | grep -q origin; then
        CURRENT_URL=$(git remote get-url origin)
        print_success "已配置远程仓库:"
        echo "   $CURRENT_URL"
        
        if [ "$CURRENT_URL" = "$REMOTE_URL" ] || [ "$CURRENT_URL" = "$SSH_URL" ]; then
            print_success "远程仓库配置正确"
        else
            print_warning "远程仓库配置不同，将更新"
        fi
    else
        print_warning "未配置远程仓库，将添加"
    fi
    
    # 检查 GitHub 仓库是否存在
    print_step "检查 GitHub 仓库..."
    if curl -s -I "$REPO_URL" 2>/dev/null | grep -q "200 OK"; then
        print_success "GitHub 仓库已存在: $REPO_URL"
        REPO_EXISTS=true
    else
        print_warning "GitHub 仓库不存在或无法访问"
        REPO_EXISTS=false
    fi
}

# 配置 Git
configure_git() {
    print_header "⚙️  Git 配置"
    
    # 更新远程仓库
    print_step "配置远程仓库..."
    git remote remove origin 2>/dev/null || true
    
    # 选择 URL 类型
    echo ""
    echo "选择远程仓库类型:"
    echo "  1) HTTPS (推荐，简单)"
    echo "  2) SSH (需要配置 SSH 密钥)"
    read -p "请选择 [1/2，默认1]: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[2]$ ]]; then
        SELECTED_URL="$SSH_URL"
        print_success "使用 SSH 地址: $SELECTED_URL"
    else
        SELECTED_URL="$REMOTE_URL"
        print_success "使用 HTTPS 地址: $SELECTED_URL"
    fi
    
    git remote add origin "$SELECTED_URL"
    print_success "远程仓库已配置"
    
    # 确保分支为 main
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_step "重命名分支: $CURRENT_BRANCH -> main"
        git branch -M main
        print_success "分支已重命名"
    else
        print_success "当前分支: main"
    fi
}

# 显示上传摘要
show_summary() {
    print_header "📊 上传摘要"
    
    echo "📋 基本信息:"
    echo "   用户: $GITHUB_USER"
    echo "   仓库: $REPO_NAME"
    echo "   地址: $REPO_URL"
    echo ""
    
    echo "📦 内容统计:"
    echo "   提交数: $(git rev-list --count HEAD)"
    echo "   文件数: $(git ls-files | wc -l)"
    echo "   总大小: $(du -sh . | cut -f1)"
    echo ""
    
    echo "📁 文件分类:"
    echo "   📝 Markdown: $(git ls-files "*.md" | wc -l)"
    echo "   🐍 Python: $(git ls-files "*.py" | wc -l)"
    echo "   🐚 Shell: $(git ls-files "*.sh" | wc -l)"
    echo "   ⚙️ 配置: $(git ls-files "*.json" "*.plist" | wc -l)"
    echo ""
    
    echo "📝 最近提交:"
    git log --oneline -3 | while read line; do
        echo "   $line"
    done
}

# 执行上传
perform_upload() {
    print_header "🚀 开始上传"
    
    # 确认
    echo ""
    print_warning "即将上传到: $REPO_URL"
    echo ""
    read -p "是否继续？ (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "上传取消"
        exit 0
    fi
    
    # 开始上传
    print_step "正在上传到 GitHub..."
    echo "这可能需要几秒钟，请稍候..."
    echo ""
    
    START_TIME=$(date +%s)
    
    # 执行上传
    if git push -u origin main; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        print_header "🎉 上传成功！"
        
        echo "⏱️  用时: ${DURATION} 秒"
        echo "📦 大小: $(git count-objects -vH | grep size-pack | cut -d: -f2)"
        echo ""
        
        echo "🌐 重要链接:"
        echo "   主页: $REPO_URL"
        echo "   提交: $REPO_URL/commits/main"
        echo "   文件: $REPO_URL"
        echo "   README: $REPO_URL#readme"
        echo ""
        
        # 生成成功报告
        generate_success_report "$DURATION"
        
    else
        print_header "❌ 上传失败"
        
        echo "可能的原因:"
        echo "  1. 仓库不存在"
        echo "  2. 权限不足"
        echo "  3. 网络问题"
        echo "  4. 认证失败"
        echo ""
        
        echo "解决方案:"
        echo "  1. 创建仓库: https://github.com/new"
        echo "  2. 检查权限"
        echo "  3. 使用不同 URL 类型"
        echo ""
        
        # 保存错误信息
        echo "上传失败时间: $(date '+%Y-%m-%d %H:%M:%S')" > UPLOAD_ERROR.txt
        echo "用户: $GITHUB_USER" >> UPLOAD_ERROR.txt
        echo "仓库: $REPO_NAME" >> UPLOAD_ERROR.txt
        print_warning "错误信息已保存到: UPLOAD_ERROR.txt"
    fi
}

# 生成成功报告
generate_success_report() {
    local duration=$1
    
    cat > "GITHUB_UPLOAD_REPORT.md" << EOF
# 🎉 GitHub 上传成功报告

## 基本信息
- **用户**: $GITHUB_USER
- **仓库**: $REPO_NAME
- **时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **用时**: ${duration} 秒

## 仓库链接
- 🏠 主页: $REPO_URL
- 📝 提交: $REPO_URL/commits/main
- 📁 文件: $REPO_URL
- 📖 README: $REPO_URL#readme

## 统计信息
- 总提交数: $(git rev-list --count HEAD)
- 总文件数: $(git ls-files | wc -l)
- 仓库大小: $(git count-objects -vH | grep size-pack | cut -d: -f2)

## 内容概览
\`\`\`
$(find . -type f -name "*.md" -o -name "*.sh" -o -name "*.py" | sort | head -15)
... 更多文件
\`\`\`

## 验证命令
\`\`\`bash
# 克隆验证
git clone $REPO_URL
cd $REPO_NAME
ls -la
\`\`\`

## 后续操作
1. ✅ 访问仓库页面
2. 📝 添加仓库描述
3. 🏷️  设置主题标签
4. 🌐 考虑启用 GitHub Pages
5. 🔄 定期推送更新

## 自动化脚本
已安装的自动化系统:
- 📈 知识演化跟踪（每周日 09:00 自动运行）
- 🔄 自动备份和清理
- 📊 智能报告生成

---
**报告生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    print_success "详细报告已生成: GITHUB_UPLOAD_REPORT.md"
}

# 显示完成信息
show_completion() {
    print_header "✨ 完成"
    
    echo "✅ 上传流程执行完成"
    echo ""
    echo "📞 后续操作:"
    echo "  1. 查看报告: GITHUB_UPLOAD_REPORT.md"
    echo "  2. 访问仓库: $REPO_URL"
    echo "  3. 完善信息: 添加描述和主题"
    echo "  4. 定期更新: 使用 'git push'"
    echo ""
    echo "💡 提示: 你的知识演化跟踪系统已配置为"
    echo "       每周日 09:00 自动运行"
    echo ""
    echo "感谢使用！ 🚀"
}

# 主函数
main() {
    clear
    check_environment
    check_repository
    configure_git
    show_summary
    perform_upload
    show_completion
}

# 执行主函数
main "$@"
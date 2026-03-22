#!/bin/bash

# 打开 Obsidian 关系图谱可视化

echo "🚀 正在打开关系图谱可视化..."
echo "========================================"

# 检查是否生成了数据文件
if [ ! -f "obsidian-graph-data.json" ]; then
    echo "❌ 未找到图形数据文件"
    echo "正在生成数据..."
    python3 scripts/create-obsidian-graph.py
fi

if [ ! -f "obsidian-graph-visualizer.html" ]; then
    echo "❌ 未找到可视化文件"
    exit 1
fi

# 获取本地 IP 地址（用于网络访问）
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "127.0.0.1")

echo "📊 数据统计:"
python3 -c "
import json
try:
    with open('obsidian-graph-data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'   节点数: {len(data[\"nodes\"])}')
    print(f'   连接数: {len(data[\"links\"])}')
    print(f'   分类数: {len(set(n[\"category\"] for n in data[\"nodes\"]))}')
except:
    print('   无法读取数据文件')
"

echo ""
echo "🌐 打开方式:"
echo ""
echo "1. 🔗 直接打开 (推荐):"
echo "   open obsidian-graph-visualizer.html"
echo ""
echo "2. 🌍 网络共享 (多设备访问):"
echo "   python3 -m http.server 8080"
echo "   然后在浏览器打开: http://${LOCAL_IP}:8080/obsidian-graph-visualizer.html"
echo ""
echo "3. 📱 二维码访问 (手机扫描):"
echo "   http://${LOCAL_IP}:8080/obsidian-graph-visualizer.html"
echo ""

# 询问用户选择
echo "请选择打开方式:"
echo "1) 直接打开 (默认)"
echo "2) 启动 HTTP 服务器"
echo "3) 生成二维码"
read -p "选择 [1-3]: " choice

case $choice in
    2)
        echo "🚀 启动 HTTP 服务器..."
        echo "访问地址: http://${LOCAL_IP}:8080/obsidian-graph-visualizer.html"
        echo "按 Ctrl+C 停止服务器"
        python3 -m http.server 8080
        ;;
    3)
        echo "📱 生成二维码..."
        # 检查是否安装了 qrcode 库
        python3 -c "import qrcode" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "安装 qrcode 库..."
            pip3 install qrcode[pil]
        fi
        
        URL="http://${LOCAL_IP}:8080/obsidian-graph-visualizer.html"
        python3 -c "
import qrcode
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data('$URL')
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')
img.save('graph-qrcode.png')
print('✅ 二维码已保存: graph-qrcode.png')
        "
        
        echo "🚀 启动 HTTP 服务器..."
        echo "扫描二维码访问: $URL"
        echo "按 Ctrl+C 停止服务器"
        python3 -m http.server 8080
        ;;
    *)
        echo "🔗 直接打开..."
        open obsidian-graph-visualizer.html
        ;;
esac

echo ""
echo "🎯 使用提示:"
echo "1. 拖动节点重新布局"
echo "2. 鼠标悬停查看详情"
echo "3. 点击节点查看详细信息"
echo "4. 使用右侧面板筛选和调整"
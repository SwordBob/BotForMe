#!/bin/bash

# 直接使用qpdf拆分PDF

PDF_FILE="信息系统项目管理师教程（第四版）-带目录可搜索.pdf"
OUTPUT_DIR="教程拆分结果"
PAGES_PER_FILE=30

echo "开始拆分PDF: $PDF_FILE"
echo "每$PAGES_PER_FILE页一个文件"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 获取总页数
TOTAL_PAGES=$(qpdf --show-npages "$PDF_FILE")
echo "总页数: $TOTAL_PAGES"

# 计算需要拆分成多少部分
NUM_PARTS=$(( (TOTAL_PAGES + PAGES_PER_FILE - 1) / PAGES_PER_FILE ))
echo "将拆分为 $NUM_PARTS 个文件"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 开始拆分
SUCCESS_COUNT=0
for ((i=0; i<NUM_PARTS; i++)); do
    START=$((i * PAGES_PER_FILE + 1))
    END=$(( (i + 1) * PAGES_PER_FILE ))
    if (( END > TOTAL_PAGES )); then
        END=$TOTAL_PAGES
    fi
    
    OUTPUT_FILE="$OUTPUT_DIR/第$((i+1))部分_第${START}-${END}页.pdf"
    
    echo "拆分 $((i+1))/$NUM_PARTS: 第${START}-${END}页"
    
    # 使用qpdf拆分
    if qpdf "$PDF_FILE" --pages . "$START-$END" -- "$OUTPUT_FILE" 2>/dev/null; then
        FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
        FILE_SIZE_MB=$(echo "scale=1; $FILE_SIZE / 1024 / 1024" | bc)
        echo "  ✅ 成功: $(basename "$OUTPUT_FILE") (${FILE_SIZE_MB} MB)"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  ❌ 失败"
    fi
    echo ""
done

echo "=" * 60
echo "拆分完成!"
echo "成功: $SUCCESS_COUNT/$NUM_PARTS 个文件"
echo "输出目录: $OUTPUT_DIR"

# 创建文件列表
echo "创建文件列表..."
ls -lh "$OUTPUT_DIR"/*.pdf > "$OUTPUT_DIR/文件列表.txt" 2>/dev/null

echo ""
echo "文件列表:"
ls -la "$OUTPUT_DIR"/*.pdf | head -10
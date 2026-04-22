#!/bin/bash

echo "=== 重新拆分PDF文件 ==="
echo ""

# 清理旧目录
rm -rf "教程拆分结果_new"
mkdir -p "教程拆分结果_new"

# 获取总页数
TOTAL_PAGES=$(qpdf --show-npages "信息系统项目管理师教程（第四版）-带目录可搜索.pdf")
echo "总页数: $TOTAL_PAGES"
echo "按每30页拆分"
echo ""

# 计算需要拆分成多少部分
NUM_PARTS=$(( (TOTAL_PAGES + 30 - 1) / 30 ))
echo "将拆分为 $NUM_PARTS 个文件"
echo ""

# 开始拆分
for ((i=0; i<NUM_PARTS; i++)); do
    START=$((i * 30 + 1))
    END=$(( (i + 1) * 30 ))
    if (( END > TOTAL_PAGES )); then
        END=$TOTAL_PAGES
    fi
    
    OUTPUT_FILE="教程拆分结果_new/第$((i+1))部分_第${START}-${END}页.pdf"
    
    echo "拆分 $((i+1))/$NUM_PARTS: 第${START}-${END}页"
    
    # 使用qpdf拆分
    if qpdf "信息系统项目管理师教程（第四版）-带目录可搜索.pdf" --pages . "$START-$END" -- "$OUTPUT_FILE"; then
        FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
        FILE_SIZE_MB=$(echo "scale=1; $FILE_SIZE / 1024 / 1024" | bc)
        echo "  ✅ 成功: $(basename "$OUTPUT_FILE") (${FILE_SIZE_MB} MB)"
    else
        echo "  ❌ 失败"
    fi
    echo ""
done

echo "=== 拆分完成 ==="
echo "输出目录: 教程拆分结果_new"
echo "文件列表:"
ls -lh "教程拆分结果_new/"
#!/bin/bash

# 软考高项第8章考题批改脚本
# 使用方法：./批改考题_第08章.sh <答题卡文件>

echo "========================================="
echo "   软考高项第8章《项目整合管理》批改系统"
echo "========================================="
echo ""

if [ $# -eq 0 ]; then
    echo "使用方法：$0 <答题卡文件>"
    echo "示例：$0 我的答题卡.txt"
    exit 1
fi

ANSWER_FILE="$1"
if [ ! -f "$ANSWER_FILE" ]; then
    echo "错误：找不到答题卡文件 '$ANSWER_FILE'"
    exit 1
fi

echo "正在批改答题卡：$ANSWER_FILE"
echo ""

# 创建临时文件存储批改结果
TEMP_RESULT=$(mktemp)
TEMP_SCORE=$(mktemp)

# 正确答案
# 单选题答案 (20题)
SINGLE_ANSWERS=("B" "B" "B" "B" "C" "A" "B" "C" "B" "B" "D" "D" "D" "C" "A" "A" "A" "C" "C" "C")

# 多选题答案 (10题)
MULTI_ANSWERS=(
    "ABCDEFG"
    "ABCD"
    "ABCDE"
    "ABC"
    "ABC"
    "ABCD"
    "ABC"
    "ABCDE"
    "ABC"
    "ABC"
)

# 判断题答案 (10题)
JUDGE_ANSWERS=("×" "×" "×" "√" "×" "√" "×" "×" "√" "×")

echo "批改结果：" > "$TEMP_RESULT"
echo "==========" >> "$TEMP_RESULT"

# 初始化分数
TOTAL_SCORE=0
SINGLE_SCORE=0
MULTI_SCORE=0
JUDGE_SCORE=0
CASE_SCORE=0

echo "一、单选题批改结果：" >> "$TEMP_RESULT"
echo "-------------------" >> "$TEMP_RESULT"

# 这里需要根据实际答题卡格式解析答案
# 由于答题卡格式可能不同，这里只提供框架
# 实际使用时需要根据答题卡格式调整解析逻辑

echo "提示：请手动对照参考答案批改单选题"
echo "单选题参考答案："
for i in {1..20}; do
    echo "第${i}题: ${SINGLE_ANSWERS[$((i-1))]}"
done
echo ""

echo "二、多选题批改结果：" >> "$TEMP_RESULT"
echo "-------------------" >> "$TEMP_RESULT"
echo "多选题参考答案："
for i in {1..10}; do
    echo "第$((20+i))题: ${MULTI_ANSWERS[$((i-1))]}"
done
echo ""

echo "三、判断题批改结果：" >> "$TEMP_RESULT"
echo "-------------------" >> "$TEMP_RESULT"
echo "判断题参考答案："
for i in {1..10}; do
    echo "第$((30+i))题: ${JUDGE_ANSWERS[$((i-1))]}"
done
echo ""

echo "四、案例分析题批改要点：" >> "$TEMP_RESULT"
echo "------------------------" >> "$TEMP_RESULT"
echo "案例分析题参考答案要点："
echo ""
echo "案例一："
echo "1. 制定项目章程过程"
echo "2. 项目章程和假设日志"
echo "3. 专家判断、数据收集、人际关系与团队技能、会议"
echo "4. 项目目的、目标、需求、风险、里程碑、预算、干系人等"
echo ""
echo "案例二："
echo "1. 实施整体变更控制过程"
echo "2. 范围变更"
echo "3. 建立变更流程、收集请求、分析影响、CCB审批、实施变更、更新文件"
echo "4. 评审变更、评估影响、批准/拒绝变更、维护基准完整性"
echo ""

# 询问用户输入得分
echo "请输入各题型得分："
read -p "单选题得分（0-40）：" SINGLE_SCORE
read -p "多选题得分（0-30）：" MULTI_SCORE
read -p "判断题得分（0-20）：" JUDGE_SCORE
read -p "案例分析题得分（0-30）：" CASE_SCORE

TOTAL_SCORE=$((SINGLE_SCORE + MULTI_SCORE + JUDGE_SCORE + CASE_SCORE))

echo "" >> "$TEMP_RESULT"
echo "得分统计：" >> "$TEMP_RESULT"
echo "---------" >> "$TEMP_RESULT"
echo "单选题：$SINGLE_SCORE/40" >> "$TEMP_RESULT"
echo "多选题：$MULTI_SCORE/30" >> "$TEMP_RESULT"
echo "判断题：$JUDGE_SCORE/20" >> "$TEMP_RESULT"
echo "案例分析：$CASE_SCORE/30" >> "$TEMP_RESULT"
echo "总分：$TOTAL_SCORE/120" >> "$TEMP_RESULT"

# 计算正确率
if [ $TOTAL_SCORE -gt 0 ]; then
    PERCENTAGE=$((TOTAL_SCORE * 100 / 120))
else
    PERCENTAGE=0
fi

echo "正确率：$PERCENTAGE%" >> "$TEMP_RESULT"
echo "" >> "$TEMP_RESULT"

# 给出评价
echo "学习评价：" >> "$TEMP_RESULT"
echo "---------" >> "$TEMP_RESULT"

if [ $TOTAL_SCORE -ge 100 ]; then
    echo "优秀！掌握扎实，可以进入下一章学习。" >> "$TEMP_RESULT"
    echo "建议：继续保持，适当复习巩固。" >> "$TEMP_RESULT"
elif [ $TOTAL_SCORE -ge 80 ]; then
    echo "良好！基本掌握，需要巩固薄弱点。" >> "$TEMP_RESULT"
    echo "建议：重点复习错题，加强理解。" >> "$TEMP_RESULT"
elif [ $TOTAL_SCORE -ge 60 ]; then
    echo "及格！需要重点复习。" >> "$TEMP_RESULT"
    echo "建议：重新学习本章内容，多做练习。" >> "$TEMP_RESULT"
else
    echo "不及格！需要重新学习本章内容。" >> "$TEMP_RESULT"
    echo "建议：系统学习第8章，理解基本概念。" >> "$TEMP_RESULT"
fi

echo "" >> "$TEMP_RESULT"
echo "批改完成时间：$(date '+%Y-%m-%d %H:%M:%S')" >> "$TEMP_RESULT"

# 显示批改结果
echo ""
echo "========================================="
cat "$TEMP_RESULT"
echo "========================================="

# 保存批改结果
RESULT_FILE="批改结果_第08章_$(date '+%Y%m%d_%H%M%S').txt"
cp "$TEMP_RESULT" "$RESULT_FILE"
echo ""
echo "批改结果已保存到：$RESULT_FILE"

# 提示更新错题本
echo ""
echo "下一步建议："
echo "1. 对照参考答案分析错题"
echo "2. 更新错题本：软考高项_第08章_错题本.md"
echo "3. 针对薄弱知识点进行专项复习"

# 清理临时文件
rm -f "$TEMP_RESULT" "$TEMP_SCORE"

exit 0
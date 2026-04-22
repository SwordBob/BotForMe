#!/usr/bin/env python3
# 软考高项第06章考题批改脚本

# 标准答案
standard_answers = {
    # 单选题
    "single_choice": ["C", "D", "B", "C", "B", "D", "B", "C", "D", "B"],
    
    # 多选题
    "multi_choice": [
        ["A", "B", "D", "E"],  # 1
        ["A", "B", "C", "D"],  # 2
        ["A", "B", "C", "D"],  # 3
        ["A", "B", "D"],       # 4
        ["A", "B", "C", "D"],  # 5
        ["A", "B", "C"],       # 6
        ["A", "B", "C"],       # 7
        ["A", "B", "C", "D", "E"],  # 8
        ["A", "B", "C"],       # 9
        ["A", "B", "C", "D", "E"]   # 10
    ],
    
    # 判断题
    "true_false": ["×", "×", "√", "×", "×", "×", "√", "√", "×", "√"]
}

# 考生答案（从答题卡提取）
student_answers = {
    # 单选题
    "single_choice": ["C", "D", "B", "C", "B", "D", "B", "C", "D", "B"],
    
    # 多选题
    "multi_choice": [
        ["D", "E"],           # 1 - 缺少A,B
        ["A", "B", "C", "D"], # 2 - 正确
        ["A", "B", "D"],      # 3 - 缺少C
        ["A", "B", "D"],      # 4 - 正确
        ["A", "B", "C", "D"], # 5 - 正确
        ["A", "B", "C"],      # 6 - 正确
        ["A", "B", "C"],      # 7 - 正确
        ["A", "B", "C", "D", "E"], # 8 - 正确
        ["A", "B"],           # 9 - 缺少C
        ["A", "B", "C", "D", "E"]  # 10 - 正确
    ],
    
    # 判断题
    "true_false": ["T", "F", "T", "F", "F", "F", "T", "T", "F", "T"]  # 注意：T=√, F=×
}

# 转换判断题格式
def convert_tf(answer):
    if answer.upper() == "T":
        return "√"
    elif answer.upper() == "F":
        return "×"
    return answer

student_answers["true_false"] = [convert_tf(ans) for ans in student_answers["true_false"]]

# 批改函数
def grade_single_choice():
    correct = 0
    wrong_questions = []
    
    for i in range(10):
        if student_answers["single_choice"][i].upper() == standard_answers["single_choice"][i]:
            correct += 1
        else:
            wrong_questions.append({
                "question_no": i + 1,
                "student_answer": student_answers["single_choice"][i],
                "correct_answer": standard_answers["single_choice"][i]
            })
    
    return correct, wrong_questions

def grade_multi_choice():
    correct = 0
    wrong_questions = []
    
    for i in range(10):
        student_set = set(student_answers["multi_choice"][i])
        standard_set = set(standard_answers["multi_choice"][i])
        
        if student_set == standard_set:
            correct += 1
        else:
            wrong_questions.append({
                "question_no": i + 1,
                "student_answer": ", ".join(sorted(student_answers["multi_choice"][i])),
                "correct_answer": ", ".join(sorted(standard_answers["multi_choice"][i]))
            })
    
    return correct, wrong_questions

def grade_true_false():
    correct = 0
    wrong_questions = []
    
    for i in range(10):
        if student_answers["true_false"][i] == standard_answers["true_false"][i]:
            correct += 1
        else:
            wrong_questions.append({
                "question_no": i + 1,
                "student_answer": student_answers["true_false"][i],
                "correct_answer": standard_answers["true_false"][i]
            })
    
    return correct, wrong_questions

# 执行批改
single_correct, single_wrong = grade_single_choice()
multi_correct, multi_wrong = grade_multi_choice()
tf_correct, tf_wrong = grade_true_false()

# 计算总分
total_score = (single_correct * 2) + (multi_correct * 3) + (tf_correct * 2)

# 输出结果
print("=" * 60)
print("软考高项《第06章 项目管理概论》批改结果")
print("=" * 60)
print()

print("📊 成绩统计：")
print(f"  单选题：{single_correct}/10 题正确，得分：{single_correct * 2}/20")
print(f"  多选题：{multi_correct}/10 题正确，得分：{multi_correct * 3}/30")
print(f"  判断题：{tf_correct}/10 题正确，得分：{tf_correct * 2}/20")
print(f"  客观题总分：{total_score}/70")
print()

# 等级评定
if total_score >= 63:  # 90%正确率
    grade = "优秀 🎉"
elif total_score >= 56:  # 80%正确率
    grade = "良好 👍"
elif total_score >= 42:  # 60%正确率
    grade = "及格 ✅"
else:
    grade = "不及格 ❌"

print(f"  等级：{grade}")
print()

# 错题分析
all_wrong = single_wrong + multi_wrong + tf_wrong
if all_wrong:
    print("🔍 错题分析：")
    print("-" * 40)
    
    for wrong in all_wrong:
        q_type = ""
        if wrong in single_wrong:
            q_type = "单选题"
        elif wrong in multi_wrong:
            q_type = "多选题"
        else:
            q_type = "判断题"
        
        print(f"{q_type} 第{wrong['question_no']}题：")
        print(f"  你的答案：{wrong['student_answer']}")
        print(f"  正确答案：{wrong['correct_answer']}")
        print()
else:
    print("🎯 恭喜！客观题全部正确！")

print("=" * 60)
print("💡 学习建议：")
print("1. 仔细阅读错题对应的知识点")
print("2. 多选题注意要选全所有正确选项")
print("3. 判断题要准确理解概念定义")
print("4. 简答题部分需要补充完成")
print("=" * 60)
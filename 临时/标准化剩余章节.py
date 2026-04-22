#!/usr/bin/env python3
"""
标准化剩余章节（第16-24章）文件命名
"""

import os
import re

def main():
    directory = "剩余章节拆分结果"
    
    print("=" * 80)
    print("📚 标准化剩余章节（第16-24章）文件命名")
    print("=" * 80)
    
    # 官方教材第16-24章标准名称
    official_names = {
        16: "项目变更管理",
        17: "战略管理",
        18: "组织级项目管理",
        19: "流程管理",
        20: "项目集管理",
        21: "项目组合管理",
        22: "信息系统安全管理",
        23: "信息系统综合测试与管理",
        24: "项目管理成熟度模型"
    }
    
    # 检查目录
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    # 收集文件信息
    pdf_files = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            # 尝试匹配不同模式
            patterns = [
                r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf',
                r'第(\d+)部分_第(\d+)-(\d+)页\.pdf',
                r'第(\d+)章_([^_]+)\.pdf'
            ]
            
            matched = False
            for pattern in patterns:
                match = re.match(pattern, filename)
                if match:
                    if '章' in pattern:
                        chapter_num = int(match.group(1))
                        chapter_name = match.group(2)
                        if len(match.groups()) >= 4:
                            start_page = int(match.group(3))
                            end_page = int(match.group(4))
                        else:
                            start_page = end_page = None
                    else:
                        # 对于"第X部分"模式，需要映射到章节
                        part_num = int(match.group(1))
                        start_page = int(match.group(2))
                        end_page = int(match.group(3))
                        # 假设部分编号对应章节编号
                        chapter_num = part_num
                        chapter_name = f"第{part_num}部分"
                    
                    pdf_files.append({
                        'filename': filename,
                        'chapter_num': chapter_num,
                        'current_name': chapter_name,
                        'start_page': start_page,
                        'end_page': end_page,
                        'pages': end_page - start_page + 1 if start_page and end_page else None
                    })
                    matched = True
                    break
            
            if not matched:
                pdf_files.append({
                    'filename': filename,
                    'chapter_num': None,
                    'current_name': None,
                    'start_page': None,
                    'end_page': None,
                    'pages': None
                })
    
    # 按章节编号排序
    pdf_files.sort(key=lambda x: x['chapter_num'] if x['chapter_num'] is not None else 999)
    
    print(f"📁 发现 {len(pdf_files)} 个PDF文件")
    
    # 显示当前文件
    print("\n📋 当前文件列表:")
    for pdf in pdf_files:
        if pdf['chapter_num']:
            print(f"  第{pdf['chapter_num']:02d}章: {pdf['filename']}")
        else:
            print(f"  其他: {pdf['filename']}")
    
    # 创建标准化重命名计划
    print("\n🔄 创建标准化重命名计划...")
    
    rename_plan = []
    
    for pdf in pdf_files:
        if pdf['chapter_num'] and pdf['chapter_num'] in official_names:
            chapter_num = pdf['chapter_num']
            official_name = official_names[chapter_num]
            
            # 构建新文件名
            if pdf['start_page'] and pdf['end_page']:
                new_filename = f"第{chapter_num:02d}章_{official_name}_第{pdf['start_page']}-{pdf['end_page']}页.pdf"
            else:
                new_filename = f"第{chapter_num:02d}章_{official_name}.pdf"
            
            old_path = os.path.join(directory, pdf['filename'])
            new_path = os.path.join(directory, new_filename)
            
            # 检查是否需要重命名
            if pdf['filename'] != new_filename:
                rename_plan.append({
                    'old': pdf['filename'],
                    'new': new_filename,
                    'old_path': old_path,
                    'new_path': new_path,
                    'chapter': chapter_num,
                    'action': '重命名'
                })
            else:
                rename_plan.append({
                    'old': pdf['filename'],
                    'new': new_filename,
                    'old_path': old_path,
                    'new_path': new_path,
                    'chapter': chapter_num,
                    'action': '保持'
                })
    
    # 显示重命名计划
    if rename_plan:
        print("\n📊 重命名计划:")
        print("-" * 80)
        for plan in rename_plan:
            print(f"  {plan['old']} → {plan['new']} ({plan['action']})")
        print("-" * 80)
        
        # 执行重命名
        print("\n❓ 确认执行重命名？(y/n): ", end='')
        confirm = input().strip().lower()
        
        if confirm == 'y':
            import shutil
            success = 0
            
            print("\n🔄 执行重命名...")
            for plan in rename_plan:
                if plan['action'] == '重命名':
                    try:
                        # 如果目标文件已存在，先备份
                        if os.path.exists(plan['new_path']):
                            backup_name = plan['new_path'] + '.backup'
                            shutil.move(plan['new_path'], backup_name)
                            print(f"  📦 备份: {plan['new']} → {os.path.basename(backup_name)}")
                        
                        # 执行重命名
                        shutil.move(plan['old_path'], plan['new_path'])
                        print(f"  ✅ 重命名: {plan['old']} → {plan['new']}")
                        success += 1
                        
                    except Exception as e:
                        print(f"  ❌ 失败 {plan['old']}: {e}")
                else:
                    print(f"  ✓ 保持: {plan['old']}")
                    success += 1
            
            print(f"\n📊 重命名结果: {success}/{len(rename_plan)} 成功")
        else:
            print("❌ 取消重命名")
    else:
        print("✅ 所有文件已符合标准格式")
    
    # 创建章节索引
    print("\n📝 创建剩余章节索引...")
    
    index_file = os.path.join(directory, "剩余章节索引.md")
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📚 信息系统项目管理师教程 - 剩余章节索引（第16-24章）\n\n")
        f.write("## 高级项目管理专题\n\n")
        f.write("| 章节 | 章节名称 | 页码范围 | 页数 | 说明 |\n")
        f.write("|------|----------|----------|------|------|\n")
        
        # 重新收集文件信息（重命名后）
        pdf_files = []
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pdf'):
                match = re.match(r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf', filename)
                if match:
                    chapter_num = int(match.group(1))
                    chapter_name = match.group(2)
                    start_page = int(match.group(3))
                    end_page = int(match.group(4))
                    pages = end_page - start_page + 1
                    
                    pdf_files.append({
                        'num': chapter_num,
                        'name': chapter_name,
                        'start': start_page,
                        'end': end_page,
                        'pages': pages,
                        'filename': filename
                    })
        
        # 按章节编号排序
        pdf_files.sort(key=lambda x: x['num'])
        
        # 写入表格
        for pdf in pdf_files:
            # 添加说明
            if pdf['num'] == 16:
                description = "变更控制流程、变更管理计划"
            elif pdf['num'] == 17:
                description = "战略规划、战略实施"
            elif pdf['num'] == 18:
                description = "组织级项目管理体系"
            elif pdf['num'] == 19:
                description = "流程设计、优化、管理"
            elif pdf['num'] == 20:
                description = "项目集规划、治理"
            elif pdf['num'] == 21:
                description = "项目组合选择、平衡"
            elif pdf['num'] == 22:
                description = "安全策略、风险管理"
            elif pdf['num'] == 23:
                description = "测试管理、综合管理"
            elif pdf['num'] == 24:
                description = "成熟度评估、改进"
            else:
                description = "-"
            
            f.write(f"| 第{pdf['num']:02d}章 | {pdf['name']} | 第{pdf['start']}-{pdf['end']}页 | {pdf['pages']}页 | {description} |\n")
        
        # 统计
        if pdf_files:
            total_pages = sum(p['pages'] for p in pdf_files)
            f.write(f"| **总计** | **{len(pdf_files)}章** | **-** | **{total_pages}页** | **高级项目管理专题** |\n")
        
        f.write("\n## 章节分类\n\n")
        f.write("### 1. 组织级管理（第16-19章）\n")
        f.write("- 项目变更管理：变更控制流程\n")
        f.write("- 战略管理：组织战略与项目对齐\n")
        f.write("- 组织级项目管理：PMO、管理体系\n")
        f.write("- 流程管理：标准化、优化\n")
        
        f.write("\n### 2. 多项目管理（第20-21章）\n")
        f.write("- 项目集管理：相关项目的协调管理\n")
        f.write("- 项目组合管理：战略目标下的项目选择\n")
        
        f.write("\n### 3. 专项管理（第22-24章）\n")
        f.write("- 信息系统安全管理：安全策略、控制\n")
        f.write("- 信息系统综合测试与管理：测试体系\n")
        f.write("- 项目管理成熟度模型：能力评估、改进\n")
        
        f.write("\n## 学习重点\n\n")
        f.write("### 考试重点\n")
        f.write("1. **变更管理流程**（第16章）：变更请求、评估、实施\n")
        f.write("2. **战略管理**（第17章）：战略与项目对齐\n")
        f.write("3. **组织级项目管理**（第18章）：PMO职能、OPM3\n")
        
        f.write("\n### 理解难点\n")
        f.write("1. 项目集 vs 项目组合的区别\n")
        f.write("2. 成熟度模型的五个等级\n")
        f.write("3. 安全管理体系的建立\n")
        
        f.write("\n## 与基础章节的关系\n\n")
        f.write("这些高级专题建立在基础项目管理知识之上：\n")
        f.write("- 变更管理基于整体变更控制（第4章）\n")
        f.write("- 战略管理基于项目立项（第3章）\n")
        f.write("- 多项目管理基于单个项目管理知识\n")
        
        f.write("\n## 文件列表\n\n")
        f.write("```\n")
        for pdf in sorted([f for f in os.listdir(directory) if f.endswith('.pdf')]):
            f.write(f"{pdf}\n")
        f.write("```\n")
    
    print(f"✅ 剩余章节索引已创建: {index_file}")
    
    # 显示最终文件列表
    print("\n📋 最终文件列表:")
    print("-" * 80)
    
    final_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
    for file in final_files:
        print(file)
    
    print("-" * 80)
    print(f"总计: {len(final_files)} 个文件")
    
    print("\n" + "=" * 80)
    print("🎉 剩余章节标准化完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
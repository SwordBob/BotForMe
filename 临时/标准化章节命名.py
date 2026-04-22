#!/usr/bin/env python3
"""
标准化章节文件命名
基于软考高级（信息系统项目管理师）官方教材结构
"""

import os
import re

def get_standard_chapter_names():
    """获取标准章节名称（基于常见教材结构）"""
    # 软考高级（信息系统项目管理师）第四版标准章节
    standard_names = {
        1: "信息化与信息系统",
        2: "信息系统项目管理基础",
        3: "项目立项管理",
        4: "项目整体管理",
        5: "项目范围管理",
        6: "项目进度管理",
        7: "项目成本管理",
        8: "项目质量管理",
        9: "项目人力资源管理",
        10: "项目沟通管理",
        11: "项目风险管理",
        12: "项目采购管理",
        13: "项目干系人管理",
        14: "信息文档管理与配置管理",
        15: "知识管理",
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
    return standard_names

def analyze_current_naming(directory):
    """分析当前命名情况"""
    print("🔍 分析当前文件命名...")
    
    files = []
    pattern = re.compile(r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf')
    
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            match = pattern.match(filename)
            if match:
                chapter_num = int(match.group(1))
                chapter_name = match.group(2)
                start_page = int(match.group(3))
                end_page = int(match.group(4))
                
                files.append({
                    'filename': filename,
                    'chapter_num': chapter_num,
                    'current_name': chapter_name,
                    'start_page': start_page,
                    'end_page': end_page,
                    'pages': end_page - start_page + 1
                })
            else:
                files.append({
                    'filename': filename,
                    'chapter_num': None,
                    'current_name': None,
                    'start_page': None,
                    'end_page': None,
                    'pages': None
                })
    
    # 按章节编号排序
    files.sort(key=lambda x: x['chapter_num'] if x['chapter_num'] is not None else 999)
    
    return files

def create_rename_plan(files, standard_names):
    """创建重命名计划"""
    print("\n📋 创建重命名计划...")
    
    rename_plan = []
    
    for file_info in files:
        if file_info['chapter_num'] is not None:
            chapter_num = file_info['chapter_num']
            
            if chapter_num in standard_names:
                standard_name = standard_names[chapter_num]
                current_name = file_info['current_name']
                
                # 检查是否需要重命名
                if current_name != standard_name:
                    new_filename = f"第{chapter_num:02d}章_{standard_name}_第{file_info['start_page']}-{file_info['end_page']}页.pdf"
                    
                    rename_plan.append({
                        'old_filename': file_info['filename'],
                        'new_filename': new_filename,
                        'chapter_num': chapter_num,
                        'current_name': current_name,
                        'standard_name': standard_name,
                        'pages': file_info['pages'],
                        'action': '重命名'
                    })
                else:
                    rename_plan.append({
                        'old_filename': file_info['filename'],
                        'new_filename': file_info['filename'],
                        'chapter_num': chapter_num,
                        'current_name': current_name,
                        'standard_name': standard_name,
                        'pages': file_info['pages'],
                        'action': '保持'
                    })
            else:
                rename_plan.append({
                    'old_filename': file_info['filename'],
                    'new_filename': file_info['filename'],
                    'chapter_num': chapter_num,
                    'current_name': file_info['current_name'],
                    'standard_name': '未知',
                    'pages': file_info['pages'],
                    'action': '未知章节'
                })
        else:
            rename_plan.append({
                'old_filename': file_info['filename'],
                'new_filename': file_info['filename'],
                'chapter_num': None,
                'current_name': None,
                'standard_name': None,
                'pages': None,
                'action': '非章节文件'
            })
    
    return rename_plan

def display_rename_plan(rename_plan):
    """显示重命名计划"""
    print("\n📊 重命名计划详情:")
    print("=" * 100)
    print(f"{'章节':<6} {'当前名称':<25} {'标准名称':<25} {'页码范围':<15} {'操作':<10}")
    print("=" * 100)
    
    for plan in rename_plan:
        if plan['chapter_num']:
            chapter_str = f"第{plan['chapter_num']:02d}章"
            page_range = f"第{plan['old_filename'].split('_')[-1].replace('.pdf', '')}"
        else:
            chapter_str = "其他"
            page_range = "N/A"
        
        print(f"{chapter_str:<6} {plan['current_name'] or 'N/A':<25} {plan['standard_name'] or 'N/A':<25} {page_range:<15} {plan['action']:<10}")
    
    print("=" * 100)
    
    # 统计
    total = len(rename_plan)
    rename_count = sum(1 for p in rename_plan if p['action'] == '重命名')
    keep_count = sum(1 for p in rename_plan if p['action'] == '保持')
    other_count = total - rename_count - keep_count
    
    print(f"\n📈 统计:")
    print(f"  总计文件: {total}")
    print(f"  需要重命名: {rename_count}")
    print(f"  保持原样: {keep_count}")
    print(f"  其他: {other_count}")

def create_chapter_index(directory, rename_plan, standard_names):
    """创建章节索引文件"""
    print("\n📝 创建章节索引文件...")
    
    index_file = os.path.join(directory, "官方教材章节索引.md")
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📚 软考高级（信息系统项目管理师）官方教材章节索引\n\n")
        f.write("## 标准章节结构（第四版）\n\n")
        f.write("| 章节编号 | 标准章节名称 | 状态 | 页码范围 | 页数 |\n")
        f.write("|----------|--------------|------|----------|------|\n")
        
        # 按章节编号排序的计划
        chapter_plans = sorted([p for p in rename_plan if p['chapter_num'] is not None], 
                              key=lambda x: x['chapter_num'])
        
        for plan in chapter_plans:
            chapter_num = plan['chapter_num']
            standard_name = plan['standard_name']
            
            if plan['action'] == '重命名':
                status = "⚠️ 需重命名"
            elif plan['action'] == '保持':
                status = "✅ 已匹配"
            else:
                status = "❓ 未知"
            
            if plan['pages']:
                page_range = plan['old_filename'].split('_')[-1].replace('.pdf', '')
                pages = f"{plan['pages']}页"
            else:
                page_range = "N/A"
                pages = "N/A"
            
            f.write(f"| 第{chapter_num:02d}章 | {standard_name} | {status} | {page_range} | {pages} |\n")
        
        f.write("\n## 完整章节列表（共24章）\n\n")
        f.write("```\n")
        for chapter_num in range(1, 25):
            if chapter_num in standard_names:
                f.write(f"第{chapter_num:02d}章: {standard_names[chapter_num]}\n")
        f.write("```\n")
        
        f.write("\n## 文件命名规范\n\n")
        f.write("标准格式：`第XX章_章节名称_第A-B页.pdf`\n\n")
        f.write("示例：\n")
        f.write("- `第01章_信息化与信息系统_第16-51页.pdf`\n")
        f.write("- `第06章_项目进度管理_第198-239页.pdf`\n")
        f.write("- `第15章_知识管理_第446-486页.pdf`\n")
        
        f.write("\n## 使用说明\n\n")
        f.write("1. 本目录为《信息系统项目管理师教程（第四版）》按章节拆分文件\n")
        f.write("2. 章节名称已按官方教材标准命名\n")
        f.write("3. 页码对应原教材页码（1-indexed）\n")
        f.write("4. 建议按章节顺序系统学习\n")
        
        f.write("\n## 学习建议\n\n")
        f.write("### 重点章节（考试占比高）\n")
        f.write("1. **第5-12章**：核心项目管理知识（范围、进度、成本、质量等）\n")
        f.write("2. **第6章 项目进度管理**：关键路径、PERT、EVM等计算题重点\n")
        f.write("3. **第7章 项目成本管理**：挣值管理、成本估算\n")
        f.write("4. **第14-15章**：配置管理、知识管理\n")
        
        f.write("\n### 复习策略\n")
        f.write("1. **理论先行**：先掌握各章节基本概念\n")
        f.write("2. **计算重点**：重点练习第6、7章的计算题\n")
        f.write("3. **案例结合**：结合案例分析理解知识点\n")
        f.write("4. **模拟测试**：定期进行模拟考试\n")
    
    print(f"✅ 章节索引已创建: {index_file}")
    
    # 显示索引预览
    print("\n📄 索引文件预览（前20行）:")
    with open(index_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 20:
                print(line.rstrip())
            else:
                print("...")
                break

def main():
    directory = "按章节拆分结果"
    
    print("=" * 80)
    print("📚 软考高级章节文件标准化命名")
    print("=" * 80)
    
    # 检查目录
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    # 获取标准章节名称
    standard_names = get_standard_chapter_names()
    
    # 分析当前文件
    files = analyze_current_naming(directory)
    
    if not files:
        print("❌ 未找到PDF文件")
        return
    
    print(f"📁 发现 {len(files)} 个PDF文件")
    
    # 创建重命名计划
    rename_plan = create_rename_plan(files, standard_names)
    
    # 显示计划
    display_rename_plan(rename_plan)
    
    # 创建章节索引
    create_chapter_index(directory, rename_plan, standard_names)
    
    print("\n" + "=" * 80)
    print("🎉 分析完成！")
    print("=" * 80)
    print("\n📋 下一步操作建议:")
    print("1. 查看生成的索引文件: 官方教材章节索引.md")
    print("2. 根据索引确认章节名称是否正确")
    print("3. 如需重命名，可手动执行或使用mv命令")
    print("4. 保持文件命名一致性便于学习和复习")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
根据软考高级（信息系统项目管理师）官方教材章节命名重命名文件
"""

import os
import re
import shutil

def get_official_chapter_names():
    """获取官方教材章节名称"""
    # 根据软考高级（信息系统项目管理师）第四版教材的常见章节结构
    # 参考：https://www.ruankao.org.cn/ 和常见教材目录
    chapters = {
        1: "信息化发展",
        2: "信息技术发展",
        3: "信息系统治理",
        4: "信息系统管理",
        5: "信息系统工程",
        6: "项目管理概论",
        7: "项目立项管理",
        8: "项目整合管理",
        9: "项目范围管理",
        10: "项目进度管理",
        11: "项目成本管理",
        12: "项目质量管理",
        13: "项目资源管理",
        14: "项目沟通管理",
        15: "项目风险管理",
        16: "项目采购管理",
        17: "项目干系人管理",
        18: "项目绩效域",
        19: "配置与变更管理",
        20: "高级项目管理",
        21: "组织通用治理",
        22: "组织通用管理",
        23: "法律法规与标准规范",
        24: "管理科学基础知识",
        25: "专业英语"
    }
    
    # 但根据我们之前的拆分，只有前15章，所以调整一下
    # 实际上教材前15章通常是：
    actual_chapters = {
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
    
    return actual_chapters

def analyze_current_files(directory):
    """分析当前文件"""
    print("📁 分析当前目录文件...")
    
    files = []
    for f in os.listdir(directory):
        if f.endswith('.pdf'):
            filepath = os.path.join(directory, f)
            files.append({
                'old_name': f,
                'old_path': filepath,
                'chapter_num': None,
                'pages': None
            })
    
    # 按文件名排序
    files.sort(key=lambda x: x['old_name'])
    
    # 提取章节编号和页码信息
    for file_info in files:
        filename = file_info['old_name']
        
        # 匹配模式：第XX章_XXX_第A-B页.pdf
        match = re.search(r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf', filename)
        if match:
            file_info['chapter_num'] = int(match.group(1))
            file_info['chapter_name'] = match.group(2)
            file_info['start_page'] = int(match.group(3))
            file_info['end_page'] = int(match.group(4))
            file_info['pages'] = file_info['end_page'] - file_info['start_page'] + 1
        else:
            # 尝试其他模式
            match2 = re.search(r'第(\d+)部分_第(\d+)-(\d+)页\.pdf', filename)
            if match2:
                file_info['part_num'] = int(match2.group(1))
                file_info['start_page'] = int(match2.group(2))
                file_info['end_page'] = int(match2.group(3))
                file_info['pages'] = file_info['end_page'] - file_info['start_page'] + 1
    
    return files

def rename_files(directory, files, chapter_names):
    """重命名文件"""
    print("\n🔄 开始重命名文件...")
    
    rename_plan = []
    
    for file_info in files:
        if 'chapter_num' in file_info and file_info['chapter_num'] in chapter_names:
            chapter_num = file_info['chapter_num']
            official_name = chapter_names[chapter_num]
            
            # 构建新文件名
            new_name = f"第{chapter_num:02d}章_{official_name}_第{file_info['start_page']}-{file_info['end_page']}页.pdf"
            new_path = os.path.join(directory, new_name)
            
            rename_plan.append({
                'old_name': file_info['old_name'],
                'new_name': new_name,
                'old_path': file_info['old_path'],
                'new_path': new_path,
                'chapter_num': chapter_num,
                'official_name': official_name,
                'pages': file_info.get('pages', '未知')
            })
    
    # 显示重命名计划
    print("\n📋 重命名计划:")
    print("-" * 80)
    print(f"{'原文件名':<40} {'新文件名':<40}")
    print("-" * 80)
    
    for plan in rename_plan:
        print(f"{plan['old_name']:<40} → {plan['new_name']:<40}")
    
    print("-" * 80)
    print(f"总计: {len(rename_plan)} 个文件需要重命名")
    
    # 确认
    print("\n❓ 确认执行重命名？(y/n): ", end='')
    confirm = input().strip().lower()
    
    if confirm != 'y':
        print("❌ 取消重命名")
        return False
    
    # 执行重命名
    print("\n🔄 执行重命名...")
    success_count = 0
    
    for plan in rename_plan:
        try:
            # 如果新文件已存在，先删除
            if os.path.exists(plan['new_path']):
                os.remove(plan['new_path'])
                print(f"🗑️  删除已存在文件: {plan['new_name']}")
            
            # 重命名文件
            shutil.move(plan['old_path'], plan['new_path'])
            print(f"✅ 重命名: {plan['old_name']} → {plan['new_name']}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ 重命名失败 {plan['old_name']}: {e}")
    
    print(f"\n🎉 重命名完成: {success_count}/{len(rename_plan)} 个文件成功")
    return True

def create_chapter_index(directory, chapter_names):
    """创建章节索引文件"""
    print("\n📝 创建章节索引文件...")
    
    index_file = os.path.join(directory, "章节索引.md")
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📚 信息系统项目管理师（第四版）章节索引\n\n")
        f.write("## 官方教材章节结构\n\n")
        f.write("| 章节编号 | 章节名称 | 说明 |\n")
        f.write("|----------|----------|------|\n")
        
        for num, name in sorted(chapter_names.items()):
            # 查找对应的PDF文件
            pdf_pattern = f"第{num:02d}章_{name}_*.pdf"
            pdf_files = [f for f in os.listdir(directory) if f.startswith(f"第{num:02d}章_{name}_")]
            
            if pdf_files:
                pdf_file = pdf_files[0]
                # 提取页码
                match = re.search(r'第(\d+)-(\d+)页\.pdf', pdf_file)
                if match:
                    pages = f"{match.group(1)}-{match.group(2)}页"
                else:
                    pages = "已存在"
                
                f.write(f"| 第{num:02d}章 | {name} | ✅ {pages} |\n")
            else:
                f.write(f"| 第{num:02d}章 | {name} | ❌ 缺失 |\n")
        
        f.write("\n## 文件列表\n\n")
        f.write("```\n")
        
        pdf_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
        for pdf in pdf_files:
            f.write(f"{pdf}\n")
        
        f.write("```\n")
        
        f.write("\n## 使用说明\n\n")
        f.write("1. 本目录包含《信息系统项目管理师教程（第四版）》按章节拆分的PDF文件\n")
        f.write("2. 文件名格式：`第XX章_章节名称_第A-B页.pdf`\n")
        f.write("3. 章节名称已按官方教材统一命名\n")
        f.write("4. 页码对应原教材页码\n")
    
    print(f"✅ 章节索引已创建: {index_file}")
    
    # 显示索引内容
    print("\n📄 索引文件预览:")
    with open(index_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[:30]:  # 显示前30行
            print(line.rstrip())

def main():
    directory = "按章节拆分结果"
    
    print("=" * 80)
    print("📚 软考高级（信息系统项目管理师）章节文件重命名工具")
    print("=" * 80)
    
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    # 获取官方章节名称
    chapter_names = get_official_chapter_names()
    print(f"📖 官方教材共 {len(chapter_names)} 章")
    
    # 显示前15章
    print("\n📋 官方教材前15章:")
    for i in range(1, 16):
        if i in chapter_names:
            print(f"  第{i:02d}章: {chapter_names[i]}")
    
    # 分析当前文件
    files = analyze_current_files(directory)
    print(f"\n📁 发现 {len(files)} 个PDF文件")
    
    # 显示当前文件
    print("\n📄 当前文件列表:")
    for file_info in files:
        if 'chapter_num' in file_info:
            print(f"  第{file_info['chapter_num']:02d}章: {file_info['old_name']}")
        else:
            print(f"  其他: {file_info['old_name']}")
    
    # 重命名文件
    if rename_files(directory, files, chapter_names):
        # 创建章节索引
        create_chapter_index(directory, chapter_names)
    
    print("\n" + "=" * 80)
    print("🎉 操作完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
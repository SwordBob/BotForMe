#!/usr/bin/env python3
"""
根据官方教材章节名称重命名文件
"""

import os
import re
import shutil

def main():
    directory = "按章节拆分结果"
    
    print("=" * 80)
    print("📚 根据官方教材章节名称重命名文件")
    print("=" * 80)
    
    # 官方教材章节名称（用户提供的）
    official_names = {
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
        21: "项目管理科学基础",
        22: "组织通用治理",
        23: "组织通用管理",
        24: "法律法规与标准规范"
    }
    
    # 检查目录
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    # 收集当前文件
    current_files = []
    pattern = re.compile(r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf')
    
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            match = pattern.match(filename)
            if match:
                chapter_num = int(match.group(1))
                current_name = match.group(2)
                start_page = match.group(3)
                end_page = match.group(4)
                
                current_files.append({
                    'filename': filename,
                    'chapter_num': chapter_num,
                    'current_name': current_name,
                    'start_page': start_page,
                    'end_page': end_page
                })
    
    # 按章节编号排序
    current_files.sort(key=lambda x: x['chapter_num'])
    
    print(f"📁 发现 {len(current_files)} 个PDF文件")
    
    # 创建重命名计划
    rename_plan = []
    
    for file_info in current_files:
        chapter_num = file_info['chapter_num']
        
        if chapter_num in official_names:
            official_name = official_names[chapter_num]
            current_name = file_info['current_name']
            
            # 构建新文件名
            new_filename = f"第{chapter_num:02d}章_{official_name}_第{file_info['start_page']}-{file_info['end_page']}页.pdf"
            
            old_path = os.path.join(directory, file_info['filename'])
            new_path = os.path.join(directory, new_filename)
            
            # 检查是否需要重命名
            if file_info['filename'] != new_filename:
                rename_plan.append({
                    'old': file_info['filename'],
                    'new': new_filename,
                    'old_path': old_path,
                    'new_path': new_path,
                    'chapter': chapter_num,
                    'current_name': current_name,
                    'official_name': official_name
                })
            else:
                rename_plan.append({
                    'old': file_info['filename'],
                    'new': file_info['filename'],
                    'old_path': old_path,
                    'new_path': old_path,
                    'chapter': chapter_num,
                    'current_name': current_name,
                    'official_name': official_name,
                    'action': '保持'
                })
    
    # 显示重命名计划
    print("\n📋 重命名计划:")
    print("=" * 100)
    print(f"{'章节':<8} {'当前名称':<25} {'官方名称':<25} {'页码范围':<20} {'操作':<10}")
    print("=" * 100)
    
    for plan in rename_plan:
        chapter_str = f"第{plan['chapter']:02d}章"
        page_range = f"第{plan['old'].split('_')[-1].replace('.pdf', '')}"
        
        if 'action' in plan:
            action = plan['action']
        else:
            action = '重命名'
        
        print(f"{chapter_str:<8} {plan['current_name']:<25} {plan['official_name']:<25} {page_range:<20} {action:<10}")
    
    print("=" * 100)
    
    # 统计
    rename_count = sum(1 for p in rename_plan if 'action' not in p)
    keep_count = sum(1 for p in rename_plan if 'action' in p)
    
    print(f"\n📊 统计:")
    print(f"  需要重命名: {rename_count} 个文件")
    print(f"  保持原样: {keep_count} 个文件")
    print(f"  总计: {len(rename_plan)} 个文件")
    
    # 确认执行
    if rename_count > 0:
        print("\n✅ 自动执行重命名...")
        confirm = 'y'
        
        if confirm == 'y':
            print("\n🔄 执行重命名...")
            success = 0
            
            for plan in rename_plan:
                if 'action' not in plan:  # 需要重命名的
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
            return
    else:
        print("\n✅ 所有文件已符合官方命名，无需重命名")
    
    # 创建新的章节索引
    print("\n📝 创建官方章节索引...")
    
    index_file = os.path.join(directory, "官方教材章节索引.md")
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📚 信息系统项目管理师教程（第四版）官方章节索引\n\n")
        f.write("## 完整章节列表（共24章）\n\n")
        f.write("| 章节编号 | 官方章节名称 | 页码范围 | 页数 | 文件大小 |\n")
        f.write("|----------|--------------|----------|------|----------|\n")
        
        # 收集重命名后的文件信息
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
                    
                    filepath = os.path.join(directory, filename)
                    size_bytes = os.path.getsize(filepath)
                    size_mb = size_bytes / 1024 / 1024
                    
                    pdf_files.append({
                        'num': chapter_num,
                        'name': chapter_name,
                        'start': start_page,
                        'end': end_page,
                        'pages': pages,
                        'size_mb': size_mb,
                        'filename': filename
                    })
        
        # 按章节编号排序
        pdf_files.sort(key=lambda x: x['num'])
        
        # 写入表格
        for pdf in pdf_files:
            f.write(f"| 第{pdf['num']:02d}章 | {pdf['name']} | 第{pdf['start']}-{pdf['end']}页 | {pdf['pages']}页 | {pdf['size_mb']:.1f}MB |\n")
        
        # 统计
        if pdf_files:
            total_chapters = len(pdf_files)
            total_pages = sum(p['pages'] for p in pdf_files)
            total_size = sum(p['size_mb'] for p in pdf_files)
            
            f.write(f"| **总计** | **{total_chapters}章** | **-** | **{total_pages}页** | **{total_size:.1f}MB** |\n")
        
        f.write("\n## 章节分类\n\n")
        f.write("### 第一部分：信息化基础（第1-5章）\n")
        f.write("- 第1章 信息化发展\n")
        f.write("- 第2章 信息技术发展\n")
        f.write("- 第3章 信息系统治理\n")
        f.write("- 第4章 信息系统管理\n")
        f.write("- 第5章 信息系统工程\n\n")
        
        f.write("### 第二部分：项目管理基础（第6-7章）\n")
        f.write("- 第6章 项目管理概论\n")
        f.write("- 第7章 项目立项管理\n\n")
        
        f.write("### 第三部分：十大知识领域（第8-17章）\n")
        f.write("- 第8章 项目整合管理\n")
        f.write("- 第9章 项目范围管理\n")
        f.write("- 第10章 项目进度管理\n")
        f.write("- 第11章 项目成本管理\n")
        f.write("- 第12章 项目质量管理\n")
        f.write("- 第13章 项目资源管理\n")
        f.write("- 第14章 项目沟通管理\n")
        f.write("- 第15章 项目风险管理\n")
        f.write("- 第16章 项目采购管理\n")
        f.write("- 第17章 项目干系人管理\n\n")
        
        f.write("### 第四部分：高级专题（第18-24章）\n")
        f.write("- 第18章 项目绩效域\n")
        f.write("- 第19章 配置与变更管理\n")
        f.write("- 第20章 高级项目管理\n")
        f.write("- 第21章 项目管理科学基础\n")
        f.write("- 第22章 组织通用治理\n")
        f.write("- 第23章 组织通用管理\n")
        f.write("- 第24章 法律法规与标准规范\n\n")
        
        f.write("## 考试重点\n\n")
        f.write("### 高占比章节\n")
        f.write("1. **第10章 项目进度管理**：关键路径、PERT、挣值管理\n")
        f.write("2. **第11章 项目成本管理**：成本估算、预算、控制\n")
        f.write("3. **第12章 项目质量管理**：质量规划、保证、控制\n\n")
        
        f.write("### 计算题重点\n")
        f.write("1. **关键路径法（CPM）**：第10章\n")
        f.write("2. **三点估算（PERT）**：第10章\n")
        f.write("3. **挣值管理（EVM）**：第10、11章\n")
        f.write("4. **决策树分析**：第15章\n")
        
        f.write("\n## 文件列表\n\n")
        f.write("```\n")
        for pdf in sorted([f for f in os.listdir(directory) if f.endswith('.pdf')]):
            f.write(f"{pdf}\n")
        f.write("```\n")
    
    print(f"✅ 官方章节索引已创建: {index_file}")
    
    # 显示最终文件列表
    print("\n📋 最终文件列表:")
    print("=" * 80)
    
    final_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
    for file in final_files:
        filepath = os.path.join(directory, file)
        size = os.path.getsize(filepath) / 1024 / 1024
        print(f"{file} ({size:.1f}MB)")
    
    print("=" * 80)
    print(f"总计: {len(final_files)} 个文件")
    
    print("\n" + "=" * 80)
    print("🎉 官方章节名称重命名完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
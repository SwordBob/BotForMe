#!/usr/bin/env python3
"""
执行最终重命名 - 将文件名标准化为官方教材章节名称
"""

import os
import re
import shutil

def main():
    directory = "按章节拆分结果"
    
    print("=" * 80)
    print("📚 执行最终重命名 - 标准化为官方教材章节名称")
    print("=" * 80)
    
    # 官方教材标准章节名称（软考高级第四版）
    # 注意：根据实际文件内容，我们可能需要调整
    official_names = {
        1: "信息化与信息系统",           # 原"项目管理概论"
        2: "信息系统项目管理基础",       # 原"项目立项管理"  
        3: "项目立项管理",              # 原"项目整体管理"
        4: "项目整体管理",              # 原"项目范围管理"
        5: "项目范围管理",              # 原"项目进度管理"
        6: "项目进度管理",              # 原"项目成本管理"
        7: "项目成本管理",              # 原"项目质量管理"
        8: "项目质量管理",              # 原"项目资源管理"
        9: "项目资源管理",              # 原"项目沟通管理"
        10: "项目沟通管理",             # 原"项目风险管理"
        11: "项目风险管理",             # 原"项目采购管理"
        12: "项目采购管理",             # 原"项目干系人管理"
        13: "项目干系人管理",           # 原"项目合同管理"
        14: "信息文档管理与配置管理",   # 原"信息文档与配置管理"
        15: "知识管理"                  # 原"知识管理"
    }
    
    # 但根据实际内容，可能保持原样更准确
    # 让我们保持原章节名称，但确保格式统一
    keep_original_names = {
        1: "项目管理概论",
        2: "项目立项管理", 
        3: "项目整体管理",
        4: "项目范围管理",
        5: "项目进度管理",
        6: "项目成本管理",
        7: "项目质量管理",
        8: "项目资源管理",
        9: "项目沟通管理",
        10: "项目风险管理",
        11: "项目采购管理",
        12: "项目干系人管理",
        13: "项目合同管理",
        14: "信息文档与配置管理",
        15: "知识管理"
    }
    
    print("📋 重命名方案:")
    print("-" * 80)
    print(f"{'章节':<6} {'原名称':<20} {'新名称':<20} {'操作':<10}")
    print("-" * 80)
    
    for chapter_num in range(1, 16):
        old_name = keep_original_names.get(chapter_num, f"第{chapter_num:02d}章")
        new_name = old_name  # 保持原名称，只确保格式统一
        
        print(f"第{chapter_num:02d}章 {old_name:<20} {new_name:<20} {'保持原样':<10}")
    
    print("-" * 80)
    
    # 收集需要重命名的文件
    rename_list = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            # 匹配模式：第XX章_XXX_第A-B页.pdf
            match = re.match(r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf', filename)
            if match:
                chapter_num = int(match.group(1))
                current_name = match.group(2)
                start_page = match.group(3)
                end_page = match.group(4)
                
                if 1 <= chapter_num <= 15:
                    # 构建新文件名（确保格式统一）
                    new_name = keep_original_names[chapter_num]
                    new_filename = f"第{chapter_num:02d}章_{new_name}_第{start_page}-{end_page}页.pdf"
                    
                    old_path = os.path.join(directory, filename)
                    new_path = os.path.join(directory, new_filename)
                    
                    # 只有名称不同时才需要重命名
                    if filename != new_filename:
                        rename_list.append({
                            'old': filename,
                            'new': new_filename,
                            'old_path': old_path,
                            'new_path': new_path,
                            'chapter': chapter_num
                        })
    
    if not rename_list:
        print("\n✅ 所有文件已符合标准格式，无需重命名")
    else:
        print(f"\n🔄 需要重命名 {len(rename_list)} 个文件:")
        for item in rename_list:
            print(f"  {item['old']} → {item['new']}")
        
        print("\n❓ 确认执行重命名？(y/n): ", end='')
        confirm = input().strip().lower()
        
        if confirm == 'y':
            print("\n🔄 执行重命名...")
            success = 0
            
            for item in rename_list:
                try:
                    # 如果目标文件已存在，先备份
                    if os.path.exists(item['new_path']):
                        backup_name = item['new_path'] + '.backup'
                        shutil.move(item['new_path'], backup_name)
                        print(f"  📦 备份: {item['new']} → {os.path.basename(backup_name)}")
                    
                    # 执行重命名
                    shutil.move(item['old_path'], item['new_path'])
                    print(f"  ✅ 重命名: {item['old']} → {item['new']}")
                    success += 1
                    
                except Exception as e:
                    print(f"  ❌ 失败 {item['old']}: {e}")
            
            print(f"\n📊 重命名结果: {success}/{len(rename_list)} 成功")
        else:
            print("❌ 取消重命名")
    
    # 创建最终索引文件
    print("\n📝 创建最终章节索引...")
    
    index_file = os.path.join(directory, "最终章节索引.md")
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📚 信息系统项目管理师教程 - 章节索引\n\n")
        f.write("## 文件列表\n\n")
        f.write("| 章节 | 章节名称 | 页码范围 | 页数 | 文件大小 |\n")
        f.write("|------|----------|----------|------|----------|\n")
        
        # 收集所有PDF文件信息
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
        
        # 统计信息
        total_pages = sum(p['pages'] for p in pdf_files)
        total_size = sum(p['size_mb'] for p in pdf_files)
        
        f.write(f"| **总计** | **{len(pdf_files)}章** | **-** | **{total_pages}页** | **{total_size:.1f}MB** |\n")
        
        f.write("\n## 章节结构说明\n\n")
        f.write("1. **基础理论**（第1-2章）：信息化基础、项目管理概论\n")
        f.write("2. **项目管理过程**（第3-13章）：十大知识领域\n")
        f.write("3. **支持过程**（第14-15章）：配置管理、知识管理\n")
        
        f.write("\n## 重点章节（考试占比）\n\n")
        f.write("### 高占比章节（建议重点学习）\n")
        f.write("- **第5章 项目进度管理**：关键路径、PERT、挣值管理\n")
        f.write("- **第6章 项目成本管理**：成本估算、预算、控制\n")
        f.write("- **第7章 项目质量管理**：质量规划、保证、控制\n")
        
        f.write("\n### 中占比章节\n")
        f.write("- 第4章 项目范围管理\n")
        f.write("- 第8章 项目资源管理\n")
        f.write("- 第10章 项目风险管理\n")
        
        f.write("\n### 计算题重点\n")
        f.write("1. **关键路径法（CPM）**：第5章\n")
        f.write("2. **三点估算（PERT）**：第5章\n")
        f.write("3. **挣值管理（EVM）**：第5、6章\n")
        f.write("4. **决策树分析**：第10章\n")
        
        f.write("\n## 学习建议\n\n")
        f.write("1. **系统学习**：按章节顺序，建立知识体系\n")
        f.write("2. **重点突破**：针对高占比章节深入理解\n")
        f.write("3. **计算练习**：多做计算题，掌握公式应用\n")
        f.write("4. **案例结合**：结合实际案例理解理论知识\n")
        f.write("5. **模拟测试**：定期进行模拟考试\n")
        
        f.write("\n## 文件命名规范\n\n")
        f.write("所有文件已统一为标准格式：\n")
        f.write("```\n")
        f.write("第XX章_章节名称_第A-B页.pdf\n")
        f.write("```\n")
        f.write("\n示例：\n")
        f.write("- `第05章_项目进度管理_第144-197页.pdf`\n")
        f.write("- `第10章_项目风险管理_第312-348页.pdf`\n")
        f.write("- `第15章_知识管理_第446-486页.pdf`\n")
    
    print(f"✅ 最终索引已创建: {index_file}")
    
    # 显示最终文件列表
    print("\n📋 最终文件列表:")
    print("-" * 80)
    
    pdf_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
    for pdf in pdf_files:
        filepath = os.path.join(directory, pdf)
        size = os.path.getsize(filepath) / 1024 / 1024
        print(f"{pdf} ({size:.1f}MB)")
    
    print("-" * 80)
    print(f"总计: {len(pdf_files)} 个文件")
    
    print("\n" + "=" * 80)
    print("🎉 标准化完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
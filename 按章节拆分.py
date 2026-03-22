#!/usr/bin/env python3
"""
按章节拆分PDF
根据用户提供的章节页码进行拆分
"""

import os
from PyPDF2 import PdfReader, PdfWriter

def split_by_chapters(input_file, chapter_ranges):
    """按章节拆分PDF"""
    print("=" * 60)
    print("📚 按章节拆分PDF")
    print("=" * 60)
    
    # 创建输出目录
    output_dir = "按章节拆分结果"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 输入文件: {input_file}")
    print(f"📁 输出目录: {output_dir}")
    print()
    
    try:
        # 读取PDF
        print("📖 读取PDF文件...")
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        print(f"   总页数: {total_pages}")
        print()
        
        success_count = 0
        
        # 按章节拆分
        for i, (chapter_name, start_page, end_page) in enumerate(chapter_ranges, 1):
            # 调整页码（用户提供的是1-indexed，PyPDF2使用0-indexed）
            start_idx = start_page - 1
            end_idx = end_page  # 因为range是[start, end)，所以end_page就是结束索引
            
            # 验证页码范围
            if start_idx < 0 or end_idx > total_pages:
                print(f"❌ 第{i}章: 页码范围无效 ({start_page}-{end_page})")
                continue
            
            output_file = os.path.join(output_dir, f"第{i:02d}章_{chapter_name}_第{start_page}-{end_page}页.pdf")
            
            print(f"🔄 拆分 第{i:02d}章: {chapter_name} (第{start_page}-{end_page}页)")
            
            try:
                writer = PdfWriter()
                
                # 添加页面
                for page_idx in range(start_idx, end_idx):
                    writer.add_page(reader.pages[page_idx])
                
                # 写入文件
                with open(output_file, 'wb') as f:
                    writer.write(f)
                
                # 检查文件
                if os.path.exists(output_file):
                    size = os.path.getsize(output_file)
                    size_mb = size / 1024 / 1024
                    pages = end_page - start_page + 1
                    print(f"  ✅ 成功: {pages}页 ({size_mb:.1f} MB)")
                    success_count += 1
                else:
                    print(f"  ❌ 失败: 文件未创建")
                    
            except Exception as e:
                print(f"  ❌ 错误: {e}")
            
            print()
        
        # 创建章节列表文件
        create_chapter_list(output_dir, chapter_ranges)
        
        # 结果统计
        print("=" * 60)
        print(f"🎉 拆分完成!")
        print(f"✅ 成功: {success_count}/{len(chapter_ranges)} 个章节")
        print(f"📁 输出目录: {output_dir}")
        print()
        
        # 显示文件列表
        print("📋 生成的文件:")
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
        for f in files:
            filepath = os.path.join(output_dir, f)
            size = os.path.getsize(filepath) / 1024 / 1024
            print(f"  {f} ({size:.1f} MB)")
        
        return success_count, output_dir
        
    except Exception as e:
        print(f"❌ 读取PDF文件失败: {e}")
        import traceback
        traceback.print_exc()
        return 0, None

def create_chapter_list(output_dir, chapter_ranges):
    """创建章节列表文件"""
    list_file = os.path.join(output_dir, "章节列表.txt")
    
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write("=== PDF按章节拆分列表 ===\n\n")
        f.write("章节编号 | 章节名称 | 页码范围 | 页数\n")
        f.write("-" * 50 + "\n")
        
        for i, (chapter_name, start_page, end_page) in enumerate(chapter_ranges, 1):
            pages = end_page - start_page + 1
            f.write(f"第{i:02d}章 | {chapter_name} | 第{start_page}-{end_page}页 | {pages}页\n")
        
        f.write("\n" + "=" * 50 + "\n")
        
        # 统计信息
        total_pages = sum(end_page - start_page + 1 for _, start_page, end_page in chapter_ranges)
        f.write(f"总章节数: {len(chapter_ranges)}\n")
        f.write(f"总页数: {total_pages}页\n")
        f.write(f"平均每章页数: {total_pages/len(chapter_ranges):.1f}页\n")
    
    print(f"📝 章节列表: {list_file}")

def main():
    # 章节定义（根据用户提供的数据）
    # 格式: (章节名称, 起始页码, 结束页码)
    chapters = [
        ("项目管理概论", 16, 51),      # 第一章
        ("项目立项管理", 52, 81),      # 第二章
        ("项目整体管理", 82, 107),     # 第三章
        ("项目范围管理", 108, 143),    # 第四章
        ("项目进度管理", 144, 197),    # 第五章
        ("项目成本管理", 198, 239),    # 第六章
        ("项目质量管理", 240, 251),    # 第七章
        ("项目资源管理", 252, 286),    # 第八章
        ("项目沟通管理", 287, 311),    # 第九章
        ("项目风险管理", 312, 348),    # 第十章
        ("项目采购管理", 349, 372),    # 第十一章
        ("项目干系人管理", 373, 394),  # 第十二章
        ("项目合同管理", 395, 428),    # 第十三章
        ("信息文档与配置管理", 429, 445), # 第十四章
        ("知识管理", 446, 486),        # 第十五章
    ]
    
    input_file = "信息系统项目管理师教程（第四版）-带目录可搜索.pdf"
    
    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return
    
    # 显示章节信息
    print("📚 章节信息:")
    for i, (name, start, end) in enumerate(chapters, 1):
        pages = end - start + 1
        print(f"  第{i:02d}章: {name} (第{start}-{end}页, {pages}页)")
    print()
    
    # 确认
    total_pages = sum(end - start + 1 for _, start, end in chapters)
    print(f"📊 统计: 共{len(chapters)}章, {total_pages}页")
    print()
    
    # 开始拆分
    success, output_dir = split_by_chapters(input_file, chapters)
    
    if success > 0 and output_dir:
        print()
        print("🔍 快速操作:")
        print(f"cd \"{output_dir}\"")
        print("ls -lh *.pdf")
        print()
        print("📖 打开第一章:")
        print(f"open \"{output_dir}/第01章_项目管理概论_第16-51页.pdf\"")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
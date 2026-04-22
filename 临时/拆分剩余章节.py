#!/usr/bin/env python3
"""
拆分PDF剩余章节（第16-24章）
"""

import os
from PyPDF2 import PdfReader, PdfWriter

def split_remaining_chapters(input_file, chapter_ranges):
    """拆分剩余章节"""
    print("=" * 60)
    print("📚 拆分PDF剩余章节（第16-24章）")
    print("=" * 60)
    
    # 创建输出目录
    output_dir = "剩余章节拆分结果"
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
        for i, (chapter_num, chapter_name, start_page, end_page) in enumerate(chapter_ranges, 16):
            # 调整页码（用户提供的是1-indexed，PyPDF2使用0-indexed）
            start_idx = start_page - 1
            end_idx = end_page  # 因为range是[start, end)，所以end_page就是结束索引
            
            # 验证页码范围
            if start_idx < 0 or end_idx > total_pages:
                print(f"❌ 第{chapter_num}章: 页码范围无效 ({start_page}-{end_page})")
                continue
            
            output_file = os.path.join(output_dir, f"第{chapter_num:02d}章_{chapter_name}_第{start_page}-{end_page}页.pdf")
            
            print(f"🔄 拆分 第{chapter_num:02d}章: {chapter_name} (第{start_page}-{end_page}页)")
            
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
        create_chapter_list(output_dir, chapter_ranges, total_pages)
        
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

def create_chapter_list(output_dir, chapter_ranges, total_pages):
    """创建章节列表文件"""
    list_file = os.path.join(output_dir, "章节列表.txt")
    
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write("=== PDF剩余章节拆分列表（第16-24章）===\n\n")
        f.write("章节编号 | 章节名称 | 页码范围 | 页数\n")
        f.write("-" * 50 + "\n")
        
        for chapter_num, chapter_name, start_page, end_page in chapter_ranges:
            pages = end_page - start_page + 1
            f.write(f"第{chapter_num:02d}章 | {chapter_name} | 第{start_page}-{end_page}页 | {pages}页\n")
        
        f.write("\n" + "=" * 50 + "\n")
        
        # 统计信息
        total_chapter_pages = sum(end_page - start_page + 1 for _, _, start_page, end_page in chapter_ranges)
        f.write(f"总章节数: {len(chapter_ranges)}\n")
        f.write(f"本章节总页数: {total_chapter_pages}页\n")
        f.write(f"PDF总页数: {total_pages}页\n")
        f.write(f"剩余未分配页数: {total_pages - total_chapter_pages}页\n")
        f.write(f"平均每章页数: {total_chapter_pages/len(chapter_ranges):.1f}页\n")
    
    print(f"📝 章节列表: {list_file}")

def main():
    # 剩余章节定义（根据用户提供的数据）
    # 格式: (章节编号, 章节名称, 起始页码, 结束页码)
    chapters = [
        (16, "项目变更管理", 472, 517),      # 第十六章
        (17, "战略管理", 518, 534),         # 第十七章
        (18, "组织级项目管理", 535, 569),   # 第十八章
        (19, "流程管理", 570, 586),         # 第十九章
        (20, "项目集管理", 587, 621),       # 第20章
        (21, "项目组合管理", 622, 655),     # 第21章
        (22, "信息系统安全管理", 656, 677), # 第22章
        (23, "信息系统综合测试与管理", 678, 731), # 第23章
        (24, "项目管理成熟度模型", 732, 752), # 第24章（到PDF最后）
    ]
    
    input_file = "信息系统项目管理师教程（第四版）-带目录可搜索.pdf"
    
    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return
    
    # 显示章节信息
    print("📚 剩余章节信息（第16-24章）:")
    for chapter_num, name, start, end in chapters:
        pages = end - start + 1
        print(f"  第{chapter_num:02d}章: {name} (第{start}-{end}页, {pages}页)")
    print()
    
    # 确认
    total_chapter_pages = sum(end - start + 1 for _, _, start, end in chapters)
    print(f"📊 统计: 共{len(chapters)}章, {total_chapter_pages}页")
    print()
    
    # 开始拆分
    success, output_dir = split_remaining_chapters(input_file, chapters)
    
    if success > 0 and output_dir:
        print()
        print("🔍 快速操作:")
        print(f"cd \"{output_dir}\"")
        print("ls -lh *.pdf")
        print()
        print("📖 打开第十六章:")
        print(f"open \"{output_dir}/第16章_项目变更管理_第472-517页.pdf\"")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
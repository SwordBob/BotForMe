#!/usr/bin/env python3
"""
重新拆分第十六章（页码487-517）
"""

import os
from PyPDF2 import PdfReader, PdfWriter

def main():
    print("=" * 60)
    print("🔄 重新拆分第十六章")
    print("=" * 60)
    
    input_file = "信息系统项目管理师教程（第四版）-带目录可搜索.pdf"
    output_dir = "剩余章节拆分结果"
    
    # 新页码范围
    chapter_num = 16
    chapter_name = "项目变更管理"
    start_page = 487  # 1-indexed
    end_page = 517    # 1-indexed
    
    print(f"📄 输入文件: {input_file}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📚 章节: 第{chapter_num}章 - {chapter_name}")
    print(f"📖 页码范围: 第{start_page}-{end_page}页")
    print(f"📊 页数: {end_page - start_page + 1}页")
    print()
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 删除原文件（如果存在）
    old_files = [
        "第16章_项目变更管理_第472-517页.pdf",
        "第16章_项目变更管理_第487-517页.pdf"
    ]
    
    for old_file in old_files:
        old_path = os.path.join(output_dir, old_file)
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"🗑️ 已删除旧文件: {old_file}")
    
    print()
    
    try:
        # 读取PDF
        print("📖 读取PDF文件...")
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        print(f"   总页数: {total_pages}")
        print()
        
        # 调整页码（用户提供的是1-indexed，PyPDF2使用0-indexed）
        start_idx = start_page - 1
        end_idx = end_page  # 因为range是[start, end)，所以end_page就是结束索引
        
        # 验证页码范围
        if start_idx < 0:
            print(f"❌ 起始页码无效: {start_page}")
            return
        if end_idx > total_pages:
            print(f"❌ 结束页码无效: {end_page} (PDF只有{total_pages}页)")
            return
        
        output_file = os.path.join(output_dir, f"第{chapter_num:02d}章_{chapter_name}_第{start_page}-{end_page}页.pdf")
        
        print(f"🔄 开始拆分...")
        
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
            
            print(f"✅ 文件创建成功!")
            print(f"   📄 文件名: {os.path.basename(output_file)}")
            print(f"   📖 页数: {pages}页")
            print(f"   💾 大小: {size_mb:.1f} MB")
            print(f"   📁 路径: {output_file}")
            
            # 验证页数
            new_reader = PdfReader(output_file)
            actual_pages = len(new_reader.pages)
            
            if actual_pages == pages:
                print(f"✅ 验证通过: 实际{actual_pages}页 = 预期{pages}页")
            else:
                print(f"⚠️ 验证警告: 实际{actual_pages}页 ≠ 预期{pages}页")
            
            # 检查内容
            try:
                text = new_reader.pages[0].extract_text()
                print(f"📄 第一页内容前50字符:")
                print(f"   {text[:50]}")
            except:
                print("📄 无法提取文本内容（可能是扫描版）")
            
        else:
            print(f"❌ 文件未创建")
            
        print()
        
        # 更新章节列表文件
        update_chapter_list(output_dir, chapter_num, chapter_name, start_page, end_page)
        
        # 显示当前目录文件
        print("📋 当前目录文件列表:")
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
        for f in files:
            filepath = os.path.join(output_dir, f)
            size = os.path.getsize(filepath) / 1024 / 1024
            print(f"  {f} ({size:.1f} MB)")
        
        print()
        print("=" * 60)
        print(f"🎉 第十六章重新拆分完成!")
        print(f"📖 现在可以打开: {output_file}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def update_chapter_list(output_dir, chapter_num, chapter_name, start_page, end_page):
    """更新章节列表文件"""
    list_file = os.path.join(output_dir, "章节列表.txt")
    
    if not os.path.exists(list_file):
        print(f"⚠️ 章节列表文件不存在: {list_file}")
        return
    
    # 读取原内容
    with open(list_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到第十六章行并更新
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"第{chapter_num:02d}章"):
            pages = end_page - start_page + 1
            lines[i] = f"第{chapter_num:02d}章 | {chapter_name} | 第{start_page}-{end_page}页 | {pages}页\n"
            updated = True
            break
    
    if updated:
        # 重新计算统计信息
        total_chapter_pages = 0
        for line in lines:
            if "|" in line and "第" in line and "章" in line:
                # 提取页数
                parts = line.split("|")
                if len(parts) >= 4:
                    page_info = parts[3].strip()
                    if "页" in page_info:
                        try:
                            pages = int(page_info.replace("页", ""))
                            total_chapter_pages += pages
                        except:
                            pass
        
        # 更新统计信息部分
        for i, line in enumerate(lines):
            if "本章节总页数:" in line:
                lines[i] = f"本章节总页数: {total_chapter_pages}页\n"
                break
        
        # 写入更新后的内容
        with open(list_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"📝 已更新章节列表: {list_file}")
    else:
        print(f"⚠️ 未找到第{chapter_num}章在章节列表中")

if __name__ == "__main__":
    main()
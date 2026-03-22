#!/usr/bin/env python3
"""
从PDF目录中提取所有章节信息
"""

import sys
import os
import re
from PyPDF2 import PdfReader

def extract_chapters_from_toc(pdf_path):
    """从目录页提取章节信息"""
    reader = PdfReader(pdf_path)
    
    # 收集所有目录页内容
    all_toc_text = ""
    toc_page_numbers = []
    
    # 查找目录页（前30页）
    for page_idx in range(min(30, len(reader.pages))):
        page = reader.pages[page_idx]
        text = page.extract_text()
        
        if "目录" in text or "目  录" in text or "CONTENTS" in text.upper():
            toc_page_numbers.append(page_idx + 1)
            all_toc_text += text + "\n"
    
    print(f"找到目录页: {toc_page_numbers}")
    print("=" * 80)
    
    # 解析章节信息
    chapters = []
    
    # 模式1: 第X章 标题 页码
    pattern1 = r'第([一二三四五六七八九十零\d]+)章\s+([^\d]+?)\s+(\d+)'
    matches1 = re.findall(pattern1, all_toc_text)
    
    # 模式2: 数字.数字 标题 页码 (如 1.1, 1.2)
    pattern2 = r'(\d+\.\d+(?:\.\d+)?)\s+([^\d]+?)\s+(\d+)'
    matches2 = re.findall(pattern2, all_toc_text)
    
    # 模式3: 第X部分 标题 页码
    pattern3 = r'第([一二三四五六七八九十零\d]+)部分\s+([^\d]+?)\s+(\d+)'
    matches3 = re.findall(pattern3, all_toc_text)
    
    print(f"找到章节模式1: {len(matches1)} 个")
    print(f"找到小节模式2: {len(matches2)} 个")
    print(f"找到部分模式3: {len(matches3)} 个")
    print("-" * 80)
    
    # 处理章节
    if matches1:
        print("章节列表:")
        for chap_num, chap_title, page_num in matches1:
            print(f"  第{chap_num}章: {chap_title.strip()} (第{page_num}页)")
            chapters.append({
                'type': 'chapter',
                'number': chap_num,
                'title': chap_title.strip(),
                'page': int(page_num)
            })
    
    # 处理部分
    if matches3:
        print("\n部分列表:")
        for part_num, part_title, page_num in matches3:
            print(f"  第{part_num}部分: {part_title.strip()} (第{page_num}页)")
            chapters.append({
                'type': 'part',
                'number': part_num,
                'title': part_title.strip(),
                'page': int(page_num)
            })
    
    # 处理小节（按章分组）
    if matches2:
        print(f"\n小节总数: {len(matches2)}")
        
        # 按章分组
        chapter_sections = {}
        for section_num, section_title, page_num in matches2:
            # 提取章号
            chapter_num = section_num.split('.')[0]
            
            if chapter_num not in chapter_sections:
                chapter_sections[chapter_num] = []
            
            chapter_sections[chapter_num].append({
                'section': section_num,
                'title': section_title.strip(),
                'page': int(page_num)
            })
        
        # 显示每章的小节数
        print("各章小节分布:")
        for chap_num in sorted(chapter_sections.keys(), key=lambda x: int(x)):
            sections = chapter_sections[chap_num]
            print(f"  第{chap_num}章: {len(sections)} 个小节")
            
            # 显示前3个小节
            for i, sec in enumerate(sections[:3]):
                print(f"    {sec['section']} {sec['title']}")
            if len(sections) > 3:
                print(f"    ... 还有{len(sections)-3}个小节")
    
    return chapters, matches2

def create_split_plan(chapters, sections, total_pages=752):
    """创建拆分计划"""
    print("\n" + "=" * 80)
    print("PDF拆分计划")
    print("=" * 80)
    
    if not chapters and not sections:
        print("未找到章节信息，使用默认拆分方案")
        # 默认按每50页拆分
        num_parts = (total_pages + 49) // 50
        print(f"将{total_pages}页拆分为{num_parts}个部分，每部分约50页")
        
        split_points = []
        for i in range(num_parts):
            start = i * 50 + 1
            end = min((i + 1) * 50, total_pages)
            split_points.append((start, end))
            print(f"  部分{i+1}: 第{start}-{end}页")
        
        return split_points
    
    # 如果有章节信息，按章节拆分
    if chapters:
        print("按章节拆分:")
        split_points = []
        
        # 按页码排序
        sorted_chapters = sorted(chapters, key=lambda x: x['page'])
        
        for i, chap in enumerate(sorted_chapters):
            start_page = chap['page']
            
            # 确定结束页码（下一个章节的开始页-1，或者总页数）
            if i < len(sorted_chapters) - 1:
                end_page = sorted_chapters[i + 1]['page'] - 1
            else:
                end_page = total_pages
            
            chap_type = "章" if chap['type'] == 'chapter' else "部分"
            print(f"  第{chap['number']}{chap_type}: {chap['title']}")
            print(f"    页码: 第{start_page}-{end_page}页 ({end_page - start_page + 1}页)")
            
            split_points.append((start_page, end_page))
        
        return split_points
    
    return []

def main():
    if len(sys.argv) < 2:
        print("使用方法: python extract_all_chapters.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    # 提取章节信息
    chapters, sections = extract_chapters_from_toc(pdf_path)
    
    # 创建拆分计划
    split_plan = create_split_plan(chapters, sections)
    
    # 生成拆分命令
    if split_plan:
        print("\n" + "=" * 80)
        print("拆分命令生成:")
        print("=" * 80)
        
        # 检查是否安装了qpdf
        print("检查工具...")
        os.system("which qpdf")
        os.system("which pdftk")
        
        print("\n使用qpdf拆分的命令:")
        for i, (start, end) in enumerate(split_plan):
            output_name = f"第{i+1:02d}部分_第{start}-{end}页.pdf"
            print(f"qpdf \"{pdf_path}\" --pages . {start}-{end} -- \"{output_name}\"")
        
        print("\n使用pdftk拆分的命令:")
        for i, (start, end) in enumerate(split_plan):
            output_name = f"第{i+1:02d}部分_第{start}-{end}页.pdf"
            print(f"pdftk \"{pdf_path}\" cat {start}-{end} output \"{output_name}\"")

if __name__ == "__main__":
    main()
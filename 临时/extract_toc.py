#!/usr/bin/env python3
"""
提取PDF目录页内容，分析章节结构
"""

import sys
import os
import re
from PyPDF2 import PdfReader

def extract_toc_details(pdf_path, toc_page_numbers):
    """提取目录页的详细内容"""
    reader = PdfReader(pdf_path)
    
    all_toc_text = ""
    for page_num in toc_page_numbers:
        # 页码从0开始
        page_idx = page_num - 1
        if page_idx < len(reader.pages):
            page = reader.pages[page_idx]
            text = page.extract_text()
            all_toc_text += text + "\n"
    
    return all_toc_text

def parse_toc_text(toc_text):
    """解析目录文本，提取章节信息"""
    print("正在解析目录内容...")
    print("=" * 80)
    
    # 清理文本
    lines = toc_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # 移除过多的空格
            line = re.sub(r'\s+', ' ', line)
            cleaned_lines.append(line)
    
    # 查找章节模式
    chapter_patterns = [
        # 中文章节：第X章
        (r'第[一二三四五六七八九十零]+章\s+[^\d]+?\s+(\d+)', '第X章'),
        # 数字章节：第1章
        (r'第\d+章\s+[^\d]+?\s+(\d+)', '第数字章'),
        # 带点的章节：1.1, 1.2
        (r'(\d+\.\d+)\s+[^\d]+?\s+(\d+)', '数字.数字'),
        # 中文序号：一、二、
        (r'^[一二三四五六七八九十]、\s+[^\d]+?\s+(\d+)', '中文序号'),
    ]
    
    chapters = []
    section_pattern = r'(\d+\.\d+(?:\.\d+)?)\s+([^\d]+?)\s+(\d+)'
    sections = re.findall(section_pattern, toc_text)
    
    if sections:
        print(f"找到 {len(sections)} 个小节:")
        print("-" * 80)
        
        # 按章节分组
        chapter_dict = {}
        for section_num, section_title, page_num in sections:
            # 提取章号（第一个数字）
            chapter_num = section_num.split('.')[0]
            
            if chapter_num not in chapter_dict:
                chapter_dict[chapter_num] = {
                    'sections': [],
                    'start_page': int(page_num),
                    'end_page': int(page_num)
                }
            
            chapter_dict[chapter_num]['sections'].append({
                'number': section_num,
                'title': section_title.strip(),
                'page': int(page_num)
            })
            
            # 更新结束页码
            if int(page_num) > chapter_dict[chapter_num]['end_page']:
                chapter_dict[chapter_num]['end_page'] = int(page_num)
        
        # 输出章节信息
        for chap_num in sorted(chapter_dict.keys(), key=lambda x: int(x)):
            chap_info = chapter_dict[chap_num]
            section_count = len(chap_info['sections'])
            
            print(f"第{chap_num}章:")
            print(f"  起始页: {chap_info['start_page']}")
            print(f"  结束页: {chap_info['end_page']}")
            print(f"  小节数: {section_count}")
            print(f"  页数范围: {chap_info['end_page'] - chap_info['start_page'] + 1}页")
            
            # 显示前3个小节作为示例
            print(f"  示例小节:")
            for i, section in enumerate(chap_info['sections'][:3]):
                print(f"    {section['number']} {section['title']} (第{section['page']}页)")
            if section_count > 3:
                print(f"    ... 还有{section_count-3}个小节")
            print()
            
            # 添加到章节列表
            chapters.append({
                'chapter': chap_num,
                'start_page': chap_info['start_page'],
                'end_page': chap_info['end_page'],
                'section_count': section_count
            })
    
    else:
        print("未找到标准的小节格式，尝试其他模式...")
        # 显示目录文本的前1000字符
        print("目录内容预览:")
        print("-" * 80)
        print(toc_text[:1000])
        print("..." if len(toc_text) > 1000 else "")
    
    return chapters

def main():
    if len(sys.argv) < 2:
        print("使用方法: python extract_toc.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    # 从之前的分析我们知道目录页是第10、12、14页
    toc_pages = [10, 12, 14]
    
    print(f"分析文件: {os.path.basename(pdf_path)}")
    print(f"提取目录页: {toc_pages}")
    print("=" * 80)
    
    # 提取目录内容
    toc_text = extract_toc_details(pdf_path, toc_pages)
    
    # 解析目录
    chapters = parse_toc_text(toc_text)
    
    # 输出拆分建议
    if chapters:
        print("=" * 80)
        print("拆分建议:")
        print("=" * 80)
        
        for i, chap in enumerate(chapters, 1):
            chap_num = chap['chapter']
            start = chap['start_page']
            end = chap['end_page']
            page_count = end - start + 1
            
            print(f"{i:2d}. 第{chap_num}章: 第{start:3d}-{end:3d}页 ({page_count:3d}页)")
        
        print("=" * 80)
        print(f"总计: {len(chapters)} 章")
        total_pages = sum(ch['end_page'] - ch['start_page'] + 1 for ch in chapters)
        print(f"总页数: {total_pages} 页")

if __name__ == "__main__":
    main()
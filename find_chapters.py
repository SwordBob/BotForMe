#!/usr/bin/env python3
"""
在PDF中查找章节标题
"""

import sys
import re
from PyPDF2 import PdfReader

def find_chapter_headings(pdf_path, sample_pages=50):
    """在PDF中查找章节标题"""
    reader = PdfReader(pdf_path)
    
    print(f"在PDF中查找章节标题...")
    print(f"采样前{sample_pages}页")
    print("=" * 60)
    
    chapter_patterns = [
        r'^第[一二三四五六七八九十\d]+章\s+',
        r'^\d+\.\d+\s+',
        r'^CHAPTER\s+\d+',
        r'^[一二三四五六七八九十]、\s+',
    ]
    
    found_headings = []
    
    for page_idx in range(min(sample_pages, len(reader.pages))):
        page = reader.pages[page_idx]
        text = page.extract_text()
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines[:20]):  # 只检查前20行
            line = line.strip()
            if any(re.search(pattern, line) for pattern in chapter_patterns):
                found_headings.append({
                    'page': page_idx + 1,
                    'line': line_num + 1,
                    'text': line[:100]
                })
    
    if found_headings:
        print(f"找到 {len(found_headings)} 个可能的章节标题:")
        print("-" * 60)
        
        # 按页码分组
        page_groups = {}
        for heading in found_headings:
            page = heading['page']
            if page not in page_groups:
                page_groups[page] = []
            page_groups[page].append(heading)
        
        for page in sorted(page_groups.keys()):
            print(f"第{page}页:")
            for heading in page_groups[page]:
                print(f"  行{heading['line']}: {heading['text']}")
            print()
    else:
        print("未找到明显的章节标题")
        
        # 显示一些页面内容作为参考
        print("\n前5页内容示例:")
        print("-" * 60)
        for page_idx in range(5):
            page = reader.pages[page_idx]
            text = page.extract_text()
            print(f"第{page_idx+1}页 (前200字符):")
            print(text[:200])
            print()
    
    return found_headings

def main():
    if len(sys.argv) < 2:
        print("使用方法: python find_chapters.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    find_chapter_headings(pdf_path)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
直接查看目录页内容
"""

import sys
import os
from PyPDF2 import PdfReader

def view_toc_pages(pdf_path, page_numbers):
    """查看指定页码的内容"""
    reader = PdfReader(pdf_path)
    
    for page_num in page_numbers:
        page_idx = page_num - 1
        if page_idx < len(reader.pages):
            print(f"\n{'='*80}")
            print(f"第 {page_num} 页内容:")
            print(f"{'='*80}")
            
            page = reader.pages[page_idx]
            text = page.extract_text()
            
            # 按行显示
            lines = text.split('\n')
            for i, line in enumerate(lines[:100]):  # 只显示前100行
                if line.strip():
                    print(f"{i+1:3d}: {line}")
            
            if len(lines) > 100:
                print(f"... 还有 {len(lines)-100} 行")

def main():
    if len(sys.argv) < 2:
        print("使用方法: python view_toc_pages.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    # 查看目录页（第10、12、14页）
    toc_pages = [10, 12, 14]
    view_toc_pages(pdf_path, toc_pages)
    
    # 也查看前几页，看看是否有完整的目录
    print(f"\n{'='*80}")
    print("查看前20页，寻找完整目录:")
    print(f"{'='*80}")
    
    reader = PdfReader(pdf_path)
    for page_idx in range(min(20, len(reader.pages))):
        page = reader.pages[page_idx]
        text = page.extract_text()
        
        # 检查是否是目录页
        if "目录" in text or "目  录" in text or "CONTENTS" in text.upper():
            print(f"\n在第 {page_idx+1} 页找到目录:")
            print("-" * 60)
            
            # 显示前20行
            lines = text.split('\n')
            for i, line in enumerate(lines[:20]):
                if line.strip():
                    print(f"{line}")
            
            # 检查是否有章节编号
            import re
            chapter_lines = []
            for line in lines:
                if re.search(r'第[一二三四五六七八九十\d]+章', line) or re.search(r'\d+\.\d+', line):
                    chapter_lines.append(line.strip())
            
            if chapter_lines:
                print(f"\n找到 {len(chapter_lines)} 个章节行:")
                for line in chapter_lines[:10]:
                    print(f"  {line}")
                if len(chapter_lines) > 10:
                    print(f"  ... 还有 {len(chapter_lines)-10} 个")

if __name__ == "__main__":
    main()
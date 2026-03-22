#!/usr/bin/env python3
"""
分析PDF文件，提取目录和章节信息
"""

import sys
import os
import re
from PyPDF2 import PdfReader

def analyze_pdf(pdf_path):
    """分析PDF文件"""
    print(f"分析文件: {pdf_path}")
    print("=" * 60)
    
    try:
        # 打开PDF文件
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"总页数: {total_pages}")
        print("=" * 60)
        
        # 提取目录（通常在前几页）
        print("正在分析目录页...")
        print("-" * 60)
        
        # 检查前20页中的目录
        toc_pages = []
        for i in range(min(20, total_pages)):
            page = reader.pages[i]
            text = page.extract_text()
            
            # 查找目录关键词
            if "目录" in text or "CONTENTS" in text.upper() or "目  录" in text:
                toc_pages.append(i + 1)  # 页码从1开始
                print(f"找到目录页: 第 {i+1} 页")
                
                # 显示目录内容的前500字符
                preview = text[:500].replace('\n', ' ')
                print(f"预览: {preview}...")
                print("-" * 60)
        
        if not toc_pages:
            print("未找到明显的目录页")
            print("尝试分析章节标题模式...")
            print("-" * 60)
            
            # 分析前50页，查找章节标题
            chapter_patterns = [
                r'第[一二三四五六七八九十]+章',
                r'第\d+章',
                r'CHAPTER\s+\d+',
                r'\d+\.\d+\s+',
                r'^[一二三四五六七八九十]、',
            ]
            
            chapters = []
            for i in range(min(50, total_pages)):
                page = reader.pages[i]
                text = page.extract_text()
                lines = text.split('\n')
                
                for line_num, line in enumerate(lines[:20]):  # 只检查前20行
                    line = line.strip()
                    if any(re.search(pattern, line) for pattern in chapter_patterns):
                        chapters.append({
                            'page': i + 1,
                            'text': line[:100],
                            'line': line_num + 1
                        })
            
            if chapters:
                print(f"找到 {len(chapters)} 个可能的章节标题:")
                for chap in chapters[:10]:  # 只显示前10个
                    print(f"  第 {chap['page']} 页: {chap['text']}")
            else:
                print("未找到章节标题模式")
        
        # 尝试获取元数据
        metadata = reader.metadata
        if metadata:
            print("\nPDF元数据:")
            print("-" * 60)
            for key, value in metadata.items():
                if value:
                    print(f"  {key}: {value}")
        
        # 估计文件结构
        print("\n文件结构估计:")
        print("-" * 60)
        if total_pages > 0:
            print(f"1. 封面/前言: 第1-10页左右")
            print(f"2. 目录: 第{toc_pages[0] if toc_pages else '11-20'}页左右")
            print(f"3. 正文: 第{max(toc_pages) + 1 if toc_pages else 21}页到第{total_pages}页")
            print(f"4. 附录/索引: 第{total_pages - 20}页到第{total_pages}页")
        
        return total_pages, toc_pages
        
    except Exception as e:
        print(f"分析PDF时出错: {e}")
        return None, None

def main():
    if len(sys.argv) < 2:
        print("使用方法: python analyze_pdf.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    analyze_pdf(pdf_path)

if __name__ == "__main__":
    main()
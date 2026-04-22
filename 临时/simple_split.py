#!/usr/bin/env python3
"""
简单按页数拆分PDF
"""

import sys
import os
import subprocess
from PyPDF2 import PdfReader

def split_by_fixed_pages(pdf_path, pages_per_chapter=50):
    """按固定页数拆分PDF"""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    print(f"PDF总页数: {total_pages}")
    print(f"按每{pages_per_chapter}页拆分")
    
    # 计算需要拆分成多少部分
    num_parts = (total_pages + pages_per_chapter - 1) // pages_per_chapter
    
    # 创建输出目录
    output_dir = f"{os.path.splitext(pdf_path)[0]}_拆分"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"输出目录: {output_dir}")
    print(f"将拆分为 {num_parts} 个文件")
    print("-" * 60)
    
    success_count = 0
    
    for i in range(num_parts):
        start_page = i * pages_per_chapter + 1
        end_page = min((i + 1) * pages_per_chapter, total_pages)
        
        output_name = f"第{i+1:02d}部分_第{start_page}-{end_page}页.pdf"
        output_path = os.path.join(output_dir, output_name)
        
        print(f"拆分 {i+1}/{num_parts}: 第{start_page}-{end_page}页 ({end_page-start_page+1}页)")
        
        try:
            # 使用qpdf拆分
            cmd = [
                'qpdf',
                '--empty',
                '--pages',
                pdf_path,
                f'{start_page}-{end_page}',
                '--',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 检查文件大小
                file_size = os.path.getsize(output_path)
                print(f"  ✅ 成功: {output_name} ({file_size/1024/1024:.1f} MB)")
                success_count += 1
            else:
                print(f"  ❌ 失败: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        
        print()
    
    return success_count, num_parts, output_dir

def main():
    if len(sys.argv) < 2:
        print("使用方法: python simple_split.py <pdf文件路径> [每部分页数]")
        print("示例: python simple_split.py 文件.pdf 50")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    pages_per_chapter = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    print(f"处理文件: {os.path.basename(pdf_path)}")
    print("=" * 60)
    
    success, total, output_dir = split_by_fixed_pages(pdf_path, pages_per_chapter)
    
    print("=" * 60)
    print(f"拆分完成!")
    print(f"成功: {success}/{total} 个文件")
    print(f"输出目录: {output_dir}")
    
    # 创建简单的说明文件
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"# {os.path.basename(pdf_path)} 拆分结果\n\n")
        f.write(f"- 原文件: {os.path.basename(pdf_path)}\n")
        f.write(f"- 总页数: {PdfReader(pdf_path).metadata.get('/Pages', '未知')}\n")
        f.write(f"- 拆分方式: 每{pages_per_chapter}页一个文件\n")
        f.write(f"- 生成时间: {subprocess.check_output(['date']).decode().strip()}\n\n")
        
        f.write("## 文件列表\n")
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
        for file in files:
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            f.write(f"- `{file}` ({size/1024/1024:.1f} MB)\n")
    
    print(f"说明文件: {readme_path}")

if __name__ == "__main__":
    main()
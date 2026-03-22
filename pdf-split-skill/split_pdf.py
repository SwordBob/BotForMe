#!/usr/bin/env python3
"""
PDF Split Tool - Split large PDF files into smaller parts

Usage:
    python split_pdf.py <input_pdf> [pages_per_part]
    python split_pdf.py <input_pdf> --range <start>-<end>
    python split_pdf.py <input_pdf> --custom <page_ranges>

Examples:
    python split_pdf.py "document.pdf" 30
    python split_pdf.py "document.pdf" --range 1-100
    python split_pdf.py "document.pdf" --custom "1-30,31-60,61-90"
"""

import os
import sys
import argparse
from PyPDF2 import PdfReader, PdfWriter

def check_dependencies():
    """Check if PyPDF2 is installed, install if missing"""
    try:
        from PyPDF2 import PdfReader, PdfWriter
        return True
    except ImportError:
        print("PyPDF2 not found. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
            print("✅ PyPDF2 installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install PyPDF2: {e}")
            return False

def split_by_page_count(input_file, pages_per_part=30, output_dir=None):
    """Split PDF by fixed page count"""
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = f"{base_name}_拆分结果"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 输入文件: {input_file}")
    print(f"📊 每部分页数: {pages_per_part}")
    print(f"📁 输出目录: {output_dir}")
    print()
    
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        print(f"📖 总页数: {total_pages}")
        
        num_parts = (total_pages + pages_per_part - 1) // pages_per_part
        print(f"🔢 将拆分为 {num_parts} 个文件")
        print()
        
        success_count = 0
        
        for part_num in range(num_parts):
            start_page = part_num * pages_per_part
            end_page = min((part_num + 1) * pages_per_part, total_pages)
            
            output_file = os.path.join(output_dir, f"第{part_num+1:02d}部分_第{start_page+1}-{end_page}页.pdf")
            
            print(f"🔄 拆分 {part_num+1}/{num_parts}: 第{start_page+1}-{end_page}页")
            
            try:
                writer = PdfWriter()
                for page_idx in range(start_page, end_page):
                    writer.add_page(reader.pages[page_idx])
                
                with open(output_file, 'wb') as f:
                    writer.write(f)
                
                if os.path.exists(output_file):
                    size = os.path.getsize(output_file)
                    size_mb = size / 1024 / 1024
                    print(f"  ✅ 成功: {os.path.basename(output_file)} ({size_mb:.1f} MB)")
                    success_count += 1
                else:
                    print(f"  ❌ 失败: 文件未创建")
                    
            except Exception as e:
                print(f"  ❌ 错误: {e}")
            
            print()
        
        # Create file list
        create_file_list(output_dir)
        
        print("=" * 50)
        print(f"🎉 拆分完成!")
        print(f"✅ 成功: {success_count}/{num_parts} 个文件")
        print(f"📁 输出目录: {output_dir}")
        
        return success_count, output_dir
        
    except Exception as e:
        print(f"❌ 读取PDF文件失败: {e}")
        return 0, None

def split_by_range(input_file, page_range, output_dir=None):
    """Split PDF by specific page range"""
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = f"{base_name}_范围拆分"
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        start, end = map(int, page_range.split('-'))
        start = max(1, start)
        
        print(f"📄 输入文件: {input_file}")
        print(f"🎯 页面范围: 第{start}-{end}页")
        print(f"📁 输出目录: {output_dir}")
        print()
        
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        
        end = min(end, total_pages)
        
        if start > end:
            print("❌ 起始页不能大于结束页")
            return 0, None
        
        output_file = os.path.join(output_dir, f"第{start}-{end}页.pdf")
        
        print(f"🔄 提取第{start}-{end}页...")
        
        writer = PdfWriter()
        for page_idx in range(start-1, end):
            writer.add_page(reader.pages[page_idx])
        
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            size_mb = size / 1024 / 1024
            print(f"✅ 成功: {os.path.basename(output_file)} ({size_mb:.1f} MB)")
            
            # Validate
            try:
                test_reader = PdfReader(output_file)
                print(f"📄 验证: 包含 {len(test_reader.pages)} 页")
            except:
                print("⚠️  警告: 文件验证失败")
            
            return 1, output_dir
        else:
            print("❌ 文件未创建")
            return 0, None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 0, None

def create_file_list(output_dir):
    """Create a file list with validation info"""
    list_file = os.path.join(output_dir, "文件列表.txt")
    
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write("=== PDF拆分文件列表 ===\n\n")
        
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
        
        for filename in files:
            filepath = os.path.join(output_dir, filename)
            size = os.path.getsize(filepath)
            size_mb = size / 1024 / 1024
            
            # Validate PDF
            try:
                reader = PdfReader(filepath)
                pages = len(reader.pages)
                status = f"✅ 有效 ({pages}页)"
            except:
                status = "❌ 无效"
            
            f.write(f"{filename}\n")
            f.write(f"  大小: {size_mb:.1f} MB\n")
            f.write(f"  状态: {status}\n\n")
    
    print(f"📝 文件列表: {list_file}")

def main():
    parser = argparse.ArgumentParser(description='Split PDF files into smaller parts')
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('pages', nargs='?', type=int, default=30, 
                       help='Pages per part (default: 30)')
    parser.add_argument('--range', dest='page_range', 
                       help='Extract specific page range (e.g., 1-100)')
    parser.add_argument('--custom', dest='custom_ranges',
                       help='Custom page ranges (e.g., "1-30,31-60,61-90")')
    parser.add_argument('--output', dest='output_dir',
                       help='Custom output directory')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ 无法继续，请手动安装PyPDF2: pip install PyPDF2")
        sys.exit(1)
    
    # Check input file
    if not os.path.exists(args.input):
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)
    
    print("=" * 50)
    print("📚 PDF Split Tool")
    print("=" * 50)
    
    if args.page_range:
        # Split by range
        success, output_dir = split_by_range(args.input, args.page_range, args.output_dir)
    elif args.custom_ranges:
        # TODO: Implement custom ranges
        print("❌ 自定义范围功能尚未实现")
        sys.exit(1)
    else:
        # Split by page count
        success, output_dir = split_by_page_count(args.input, args.pages, args.output_dir)
    
    if success > 0 and output_dir:
        print()
        print("📋 快速查看:")
        print(f"cd \"{output_dir}\"")
        print("ls -lh *.pdf")
        print()
        print("🔍 验证文件:")
        print(f"open \"{output_dir}/第01部分_第1-{min(args.pages, 30)}页.pdf\"")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
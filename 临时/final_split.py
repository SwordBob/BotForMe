#!/usr/bin/env python3
"""
使用PyPDF2拆分PDF文件
"""

import os
import sys
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_file, pages_per_part=30):
    """拆分PDF文件"""
    print(f"=== 拆分PDF文件 ===")
    print(f"输入文件: {input_file}")
    print(f"每部分页数: {pages_per_part}")
    print()
    
    # 创建输出目录
    output_dir = "最终拆分结果"
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")
    print()
    
    try:
        # 读取PDF
        print("读取PDF文件...")
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        print(f"总页数: {total_pages}")
        
        # 计算需要拆分成多少部分
        num_parts = (total_pages + pages_per_part - 1) // pages_per_part
        print(f"将拆分为 {num_parts} 个文件")
        print()
        
        success_count = 0
        
        # 拆分PDF
        for part_num in range(num_parts):
            start_page = part_num * pages_per_part
            end_page = min((part_num + 1) * pages_per_part, total_pages)
            
            output_file = os.path.join(output_dir, f"第{part_num+1:02d}部分_第{start_page+1}-{end_page}页.pdf")
            
            print(f"拆分 {part_num+1}/{num_parts}: 第{start_page+1}-{end_page}页")
            
            try:
                writer = PdfWriter()
                
                # 添加页面
                for page_idx in range(start_page, end_page):
                    writer.add_page(reader.pages[page_idx])
                
                # 写入文件
                with open(output_file, 'wb') as f:
                    writer.write(f)
                
                # 验证文件
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
        
        # 结果统计
        print("=" * 50)
        print(f"拆分完成!")
        print(f"成功: {success_count}/{num_parts} 个文件")
        print(f"输出目录: {output_dir}")
        print()
        
        # 创建文件列表
        create_file_list(output_dir)
        
        return success_count, num_parts, output_dir
        
    except Exception as e:
        print(f"❌ 读取PDF文件失败: {e}")
        return 0, 0, None

def create_file_list(output_dir):
    """创建文件列表"""
    list_file = os.path.join(output_dir, "文件列表.txt")
    
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write("=== PDF拆分文件列表 ===\n\n")
        
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
        
        for filename in files:
            filepath = os.path.join(output_dir, filename)
            size = os.path.getsize(filepath)
            size_mb = size / 1024 / 1024
            
            # 验证PDF
            try:
                reader = PdfReader(filepath)
                pages = len(reader.pages)
                status = f"✅ 有效 ({pages}页)"
            except:
                status = "❌ 无效"
            
            f.write(f"{filename}\n")
            f.write(f"  大小: {size_mb:.1f} MB\n")
            f.write(f"  状态: {status}\n\n")
    
    print(f"文件列表: {list_file}")

def main():
    if len(sys.argv) < 2:
        print("使用方法: python final_split.py <pdf文件路径> [每部分页数]")
        print("示例: python final_split.py 文件.pdf 30")
        sys.exit(1)
    
    input_file = sys.argv[1]
    pages_per_part = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
        sys.exit(1)
    
    success, total, output_dir = split_pdf(input_file, pages_per_part)
    
    if success > 0:
        print("✅ 拆分成功完成!")
        print(f"请查看目录: {output_dir}")
        
        # 显示前几个文件
        print("\n前5个文件:")
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.pdf')])
        for f in files[:5]:
            print(f"  {f}")
        
        if len(files) > 5:
            print(f"  ... 还有{len(files)-5}个文件")
    else:
        print("❌ 拆分失败")

if __name__ == "__main__":
    main()
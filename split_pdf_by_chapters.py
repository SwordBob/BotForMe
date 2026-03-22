#!/usr/bin/env python3
"""
将PDF按章节拆分为单独的文件
"""

import sys
import os
import re
import subprocess
from PyPDF2 import PdfReader

def get_chapter_boundaries(pdf_path):
    """获取章节边界"""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    print(f"PDF总页数: {total_pages}")
    
    # 提取目录页内容
    toc_text = ""
    for page_idx in range(min(30, total_pages)):
        page = reader.pages[page_idx]
        text = page.extract_text()
        if "目录" in text or "目  录" in text:
            toc_text += text + "\n"
    
    # 查找章节
    # 模式: 第X章 标题 页码
    chapter_pattern = r'第([一二三四五六七八九十零\d]+)章\s+([^\d]+?)\s+(\d+)'
    chapters = re.findall(chapter_pattern, toc_text)
    
    if not chapters:
        print("未找到标准章节格式，尝试其他模式...")
        # 尝试数字章节
        chapter_pattern2 = r'第(\d+)章\s+([^\d]+?)\s+(\d+)'
        chapters = re.findall(chapter_pattern2, toc_text)
    
    if not chapters:
        print("无法找到章节信息，将按固定页数拆分")
        return None
    
    print(f"找到 {len(chapters)} 个章节")
    
    # 转换为数字页码并排序
    chapter_list = []
    for chap_num, chap_title, page_num in chapters:
        # 将中文数字转换为阿拉伯数字
        if chap_num.isdigit():
            chap_num_int = int(chap_num)
        else:
            # 简单的中文数字转换
            cn_num_map = {'一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10}
            chap_num_int = cn_num_map.get(chap_num, 0)
        
        chapter_list.append({
            'number': chap_num_int,
            'title': chap_title.strip(),
            'page': int(page_num)
        })
    
    # 按页码排序
    chapter_list.sort(key=lambda x: x['page'])
    
    # 确定每个章节的结束页码
    boundaries = []
    for i, chap in enumerate(chapter_list):
        start_page = chap['page']
        
        if i < len(chapter_list) - 1:
            end_page = chapter_list[i + 1]['page'] - 1
        else:
            end_page = total_pages
        
        # 确保页码有效
        if start_page <= end_page:
            boundaries.append({
                'chapter': chap['number'],
                'title': chap['title'],
                'start': start_page,
                'end': end_page,
                'pages': end_page - start_page + 1
            })
    
    return boundaries

def split_with_qpdf(pdf_path, boundaries):
    """使用qpdf拆分PDF"""
    print("\n使用qpdf拆分PDF...")
    
    # 创建输出目录
    output_dir = "split_chapters"
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    
    for boundary in boundaries:
        chap_num = boundary['chapter']
        start = boundary['start']
        end = boundary['end']
        title = boundary['title']
        
        # 清理文件名中的非法字符
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        output_name = f"第{chap_num:02d}章_{safe_title[:50]}.pdf"
        output_path = os.path.join(output_dir, output_name)
        
        print(f"正在拆分: 第{chap_num}章 {title}")
        print(f"  页码: {start}-{end} ({end-start+1}页)")
        print(f"  输出: {output_path}")
        
        try:
            # 使用qpdf拆分
            cmd = [
                'qpdf',
                '--empty',
                '--pages',
                pdf_path,
                f'{start}-{end}',
                '--',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ 成功")
                success_count += 1
            else:
                print(f"  ❌ 失败: {result.stderr[:100]}")
                failed_count += 1
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            failed_count += 1
        
        print()
    
    return success_count, failed_count

def split_with_pypdf2(pdf_path, boundaries):
    """使用PyPDF2拆分PDF（备用方案）"""
    print("\n使用PyPDF2拆分PDF...")
    
    from PyPDF2 import PdfReader, PdfWriter
    
    # 创建输出目录
    output_dir = "split_chapters_pypdf2"
    os.makedirs(output_dir, exist_ok=True)
    
    reader = PdfReader(pdf_path)
    success_count = 0
    failed_count = 0
    
    for boundary in boundaries:
        chap_num = boundary['chapter']
        start = boundary['start']
        end = boundary['end']
        title = boundary['title']
        
        # 清理文件名中的非法字符
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        output_name = f"第{chap_num:02d}章_{safe_title[:50]}.pdf"
        output_path = os.path.join(output_dir, output_name)
        
        print(f"正在拆分: 第{chap_num}章 {title}")
        print(f"  页码: {start}-{end} ({end-start+1}页)")
        
        try:
            writer = PdfWriter()
            
            # PDF页码从0开始
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"  ✅ 成功: {output_path}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed_count += 1
        
        print()
    
    return success_count, failed_count

def main():
    if len(sys.argv) < 2:
        print("使用方法: python split_pdf_by_chapters.py <pdf文件路径>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    print(f"处理文件: {os.path.basename(pdf_path)}")
    print("=" * 80)
    
    # 获取章节边界
    boundaries = get_chapter_boundaries(pdf_path)
    
    if not boundaries:
        print("无法确定章节边界，退出")
        sys.exit(1)
    
    # 显示拆分计划
    print("\n拆分计划:")
    print("-" * 80)
    total_pages = 0
    for boundary in boundaries:
        print(f"第{boundary['chapter']:2d}章: {boundary['title'][:40]}...")
        print(f"  页码: {boundary['start']:4d}-{boundary['end']:4d} ({boundary['pages']:3d}页)")
        total_pages += boundary['pages']
    
    print(f"\n总计: {len(boundaries)} 章, {total_pages} 页")
    print("=" * 80)
    
    # 确认
    response = input("\n是否开始拆分？(y/n): ").strip().lower()
    if response != 'y':
        print("取消拆分")
        sys.exit(0)
    
    # 尝试使用qpdf拆分
    qpdf_available = subprocess.run(['which', 'qpdf'], capture_output=True).returncode == 0
    
    if qpdf_available:
        print("检测到qpdf，使用qpdf拆分...")
        success, failed = split_with_qpdf(pdf_path, boundaries)
    else:
        print("qpdf未安装，使用PyPDF2拆分...")
        success, failed = split_with_pypdf2(pdf_path, boundaries)
    
    # 结果统计
    print("=" * 80)
    print(f"拆分完成!")
    print(f"成功: {success} 个文件")
    print(f"失败: {failed} 个文件")
    
    if success > 0:
        print(f"\n输出目录: {'split_chapters' if qpdf_available else 'split_chapters_pypdf2'}")
        print("建议使用专业的PDF查看器验证拆分结果。")

if __name__ == "__main__":
    main()
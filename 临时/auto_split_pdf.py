#!/usr/bin/env python3
"""
自动将PDF按章节拆分为单独的文件
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
        print("无法找到章节信息")
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
            cn_num_map = {'一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10,
                         '十一':11, '十二':12, '十三':13, '十四':14, '十五':15, '十六':16, '十七':17, '十八':18, '十九':19,
                         '二十':20, '二十一':21, '二十二':22, '二十三':23, '二十四':24}
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
    output_dir = "信息系统项目管理师教程_拆分章节"
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    results = []
    
    for boundary in boundaries:
        chap_num = boundary['chapter']
        start = boundary['start']
        end = boundary['end']
        title = boundary['title']
        
        # 清理文件名中的非法字符
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        # 缩短文件名
        if len(safe_title) > 30:
            safe_title = safe_title[:30] + "..."
        
        output_name = f"第{chap_num:02d}章_{safe_title}.pdf"
        output_path = os.path.join(output_dir, output_name)
        
        print(f"正在拆分: 第{chap_num}章 {title[:40]}...")
        print(f"  页码: {start}-{end} ({end-start+1}页)")
        
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
                print(f"  ✅ 成功: {output_name}")
                success_count += 1
                results.append({
                    'chapter': chap_num,
                    'title': title,
                    'file': output_path,
                    'pages': end-start+1,
                    'status': 'success'
                })
            else:
                error_msg = result.stderr[:100] if result.stderr else "未知错误"
                print(f"  ❌ 失败: {error_msg}")
                failed_count += 1
                results.append({
                    'chapter': chap_num,
                    'title': title,
                    'file': output_path,
                    'pages': end-start+1,
                    'status': 'failed',
                    'error': error_msg
                })
                
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"  ❌ 异常: {error_msg}")
            failed_count += 1
            results.append({
                'chapter': chap_num,
                'title': title,
                'file': output_path,
                'pages': end-start+1,
                'status': 'failed',
                'error': error_msg
            })
        
        print()
    
    return success_count, failed_count, results, output_dir

def create_summary(results, output_dir):
    """创建拆分结果摘要"""
    summary_file = os.path.join(output_dir, "拆分结果摘要.md")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# 信息系统项目管理师教程（第四版）拆分结果\n\n")
        f.write("## 基本信息\n")
        f.write(f"- 原文件: 信息系统项目管理师教程（第四版）-带目录可搜索.pdf\n")
        f.write(f"- 拆分时间: {subprocess.check_output(['date']).decode().strip()}\n")
        f.write(f"- 输出目录: {output_dir}\n\n")
        
        f.write("## 章节拆分结果\n\n")
        f.write("| 章节 | 标题 | 页数 | 状态 | 文件名 |\n")
        f.write("|------|------|------|------|--------|\n")
        
        success_count = 0
        total_pages = 0
        
        for result in sorted(results, key=lambda x: x['chapter']):
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            filename = os.path.basename(result['file'])
            
            f.write(f"| 第{result['chapter']}章 | {result['title'][:30]}... | {result['pages']} | {status_emoji} | {filename} |\n")
            
            if result['status'] == 'success':
                success_count += 1
                total_pages += result['pages']
        
        f.write(f"\n## 统计\n")
        f.write(f"- 总章节数: {len(results)}\n")
        f.write(f"- 成功拆分: {success_count}\n")
        f.write(f"- 失败: {len(results) - success_count}\n")
        f.write(f"- 总页数: {total_pages}\n")
    
    print(f"摘要文件已创建: {summary_file}")
    return summary_file

def main():
    if len(sys.argv) < 2:
        print("使用方法: python auto_split_pdf.py <pdf文件路径>")
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
    
    # 自动开始拆分
    print("\n开始自动拆分...")
    success, failed, results, output_dir = split_with_qpdf(pdf_path, boundaries)
    
    # 创建摘要
    summary_file = create_summary(results, output_dir)
    
    # 结果统计
    print("\n" + "=" * 80)
    print("拆分完成!")
    print(f"成功: {success} 个文件")
    print(f"失败: {failed} 个文件")
    print(f"输出目录: {output_dir}")
    print(f"摘要文件: {summary_file}")
    
    # 显示输出目录内容
    print("\n输出文件列表:")
    print("-" * 80)
    try:
        files = os.listdir(output_dir)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        for pdf in sorted(pdf_files):
            size = os.path.getsize(os.path.join(output_dir, pdf))
            print(f"  {pdf} ({size/1024/1024:.1f} MB)")
    except Exception as e:
        print(f"  无法列出文件: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
提取《第05章_项目进度管理_第144-197页》的文本内容
"""

from PyPDF2 import PdfReader
import re

def extract_pdf_content(pdf_path):
    """提取PDF文本内容"""
    print("📖 正在提取PDF内容...")
    
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"📄 文件: {pdf_path}")
        print(f"📊 总页数: {total_pages}")
        print()
        
        all_text = ""
        
        # 提取每一页的文本
        for i, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                if text:
                    all_text += f"=== 第{i}页 ===\n{text}\n\n"
                else:
                    all_text += f"=== 第{i}页 ===\n[无文本内容或为扫描版]\n\n"
            except Exception as e:
                all_text += f"=== 第{i}页 ===\n[提取错误: {e}]\n\n"
        
        # 保存到文件
        output_file = "项目进度管理_原始内容.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(all_text)
        
        print(f"✅ 内容已保存到: {output_file}")
        print(f"📝 总字符数: {len(all_text)}")
        
        # 分析章节结构
        analyze_chapter_structure(all_text)
        
        return all_text
        
    except Exception as e:
        print(f"❌ 读取PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_chapter_structure(text):
    """分析章节结构"""
    print("\n🔍 分析章节结构...")
    
    # 查找标题和子标题
    titles = []
    
    # 常见标题模式
    patterns = [
        r'第[一二三四五六七八九十\d]+节\s+[^\n]+',  # 第X节
        r'\d+\.\d+\s+[^\n]+',  # 数字标题如 5.1
        r'[一二三四五六七八九十]+、\s*[^\n]+',  # 中文数字标题
        r'\d+、\s*[^\n]+',  # 数字标题
        r'[A-Z]\.\s*[^\n]+',  # 字母标题
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            titles.extend(matches)
    
    # 去重并排序
    unique_titles = []
    seen = set()
    for title in titles:
        if title not in seen:
            seen.add(title)
            unique_titles.append(title)
    
    print(f"📚 发现 {len(unique_titles)} 个标题:")
    for i, title in enumerate(unique_titles[:20], 1):  # 只显示前20个
        print(f"  {i:2d}. {title}")
    
    if len(unique_titles) > 20:
        print(f"  ... 还有 {len(unique_titles)-20} 个标题")
    
    # 查找关键词
    keywords = [
        '进度计划', '关键路径', 'CPM', 'PERT', '甘特图', '里程碑',
        '进度控制', '进度压缩', '赶工', '快速跟进', '资源平衡',
        '进度基准', '浮动时间', '总浮动时间', '自由浮动时间',
        '进度绩效', 'SPI', 'SV', '进度偏差', '进度绩效指数',
        '进度变更', '进度管理计划', '工作分解结构', 'WBS',
        '活动定义', '活动排序', '活动历时估算', '进度计划编制',
        '进度网络图', '前导图法', '箭线图法', '计划评审技术',
        '三点估算', '最可能时间', '乐观时间', '悲观时间',
        '蒙特卡洛分析', '关键链法', '资源日历', '进度数据',
        '进度报告', '进度预测', '挣值管理', 'EVM'
    ]
    
    print("\n🔑 关键词出现频率:")
    keyword_counts = {}
    for keyword in keywords:
        count = text.count(keyword)
        if count > 0:
            keyword_counts[keyword] = count
    
    # 按频率排序
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    
    for keyword, count in sorted_keywords[:15]:  # 只显示前15个
        print(f"  {keyword}: {count}次")
    
    if len(sorted_keywords) > 15:
        print(f"  ... 还有 {len(sorted_keywords)-15} 个关键词")

def main():
    pdf_path = "按章节拆分结果/第05章_项目进度管理_第144-197页.pdf"
    
    print("=" * 60)
    print("📚 项目进度管理章节内容提取")
    print("=" * 60)
    
    content = extract_pdf_content(pdf_path)
    
    if content:
        print("\n" + "=" * 60)
        print("✅ 提取完成！")
        print("=" * 60)
        
        # 显示部分内容预览
        print("\n📄 内容预览（前1000字符）:")
        print(content[:1000])
        print("...")
        
        print(f"\n📁 完整内容已保存到: 项目进度管理_原始内容.txt")
        
    else:
        print("❌ 提取失败")

if __name__ == "__main__":
    main()
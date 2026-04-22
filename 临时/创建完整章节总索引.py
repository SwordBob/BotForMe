#!/usr/bin/env python3
"""
创建完整的章节总索引，合并两个目录的信息
"""

import os
import re

def main():
    print("=" * 80)
    print("📚 创建完整章节总索引")
    print("=" * 80)
    
    # 两个目录
    dir1 = "按章节拆分结果"
    dir2 = "剩余章节拆分结果"
    
    # 检查目录
    if not os.path.exists(dir1):
        print(f"❌ 目录不存在: {dir1}")
        return
    
    if not os.path.exists(dir2):
        print(f"❌ 目录不存在: {dir2}")
        return
    
    # 收集所有章节文件
    all_chapters = []
    
    for directory in [dir1, dir2]:
        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):
                match = re.match(r'第(\d+)章_([^_]+)_第(\d+)-(\d+)页\.pdf', filename)
                if match:
                    chapter_num = int(match.group(1))
                    chapter_name = match.group(2)
                    start_page = int(match.group(3))
                    end_page = int(match.group(4))
                    pages = end_page - start_page + 1
                    
                    filepath = os.path.join(directory, filename)
                    size_bytes = os.path.getsize(filepath)
                    size_mb = size_bytes / 1024 / 1024
                    
                    all_chapters.append({
                        'num': chapter_num,
                        'name': chapter_name,
                        'start': start_page,
                        'end': end_page,
                        'pages': pages,
                        'size_mb': size_mb,
                        'filename': filename,
                        'directory': directory
                    })
    
    # 按章节编号排序
    all_chapters.sort(key=lambda x: x['num'])
    
    print(f"📚 总计发现 {len(all_chapters)} 个章节文件")
    print(f"📖 覆盖第 {min(c['num'] for c in all_chapters)} 章到第 {max(c['num'] for c in all_chapters)} 章")
    
    # 创建完整索引
    index_file = "完整章节总索引.md"
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📚 信息系统项目管理师教程（第四版）完整章节索引\n\n")
        f.write("## 教材完整结构（共24章）\n\n")
        
        # 章节分类
        f.write("### 第一部分：基础理论（第1-2章）\n")
        f.write("- 信息化与信息系统基础\n")
        f.write("- 项目管理基本概念\n\n")
        
        f.write("### 第二部分：十大知识领域（第3-13章）\n")
        f.write("- 项目立项、整体、范围管理\n")
        f.write("- 项目进度、成本、质量管理\n")
        f.write("- 项目资源、沟通、风险管理\n")
        f.write("- 项目采购、干系人管理\n\n")
        
        f.write("### 第三部分：支持过程（第14-15章）\n")
        f.write("- 信息文档管理与配置管理\n")
        f.write("- 知识管理\n\n")
        
        f.write("### 第四部分：高级专题（第16-24章）\n")
        f.write("- 组织级与战略管理\n")
        f.write("- 多项目管理\n")
        f.write("- 专项管理领域\n\n")
        
        f.write("## 完整章节列表\n\n")
        f.write("| 章节 | 章节名称 | 页码范围 | 页数 | 文件大小 | 目录 |\n")
        f.write("|------|----------|----------|------|----------|------|\n")
        
        # 写入所有章节
        for chapter in all_chapters:
            dir_display = "基础" if chapter['directory'] == dir1 else "高级"
            f.write(f"| 第{chapter['num']:02d}章 | {chapter['name']} | 第{chapter['start']}-{chapter['end']}页 | {chapter['pages']}页 | {chapter['size_mb']:.1f}MB | {dir_display} |\n")
        
        # 统计信息
        total_chapters = len(all_chapters)
        total_pages = sum(c['pages'] for c in all_chapters)
        total_size = sum(c['size_mb'] for c in all_chapters)
        
        f.write(f"| **总计** | **{total_chapters}章** | **-** | **{total_pages}页** | **{total_size:.1f}MB** | **完整教材** |\n")
        
        f.write("\n## 考试重点分布\n\n")
        f.write("### 高占比章节（建议重点学习）\n")
        f.write("1. **第5章 项目进度管理**（15-20%）\n")
        f.write("   - 关键路径法（CPM）\n")
        f.write("   - 计划评审技术（PERT）\n")
        f.write("   - 挣值管理（EVM）\n\n")
        
        f.write("2. **第6章 项目成本管理**（10-15%）\n")
        f.write("   - 成本估算技术\n")
        f.write("   - 成本预算\n")
        f.write("   - 成本控制\n\n")
        
        f.write("3. **第7章 项目质量管理**（8-12%）\n")
        f.write("   - 质量规划\n")
        f.write("   - 质量保证\n")
        f.write("   - 质量控制\n\n")
        
        f.write("### 中占比章节\n")
        f.write("- 第4章 项目范围管理（8-10%）\n")
        f.write("- 第8章 项目资源管理（6-8%）\n")
        f.write("- 第10章 项目风险管理（8-10%）\n")
        f.write("- 第16章 项目变更管理（5-8%）\n\n")
        
        f.write("### 计算题重点\n")
        f.write("| 章节 | 计算内容 | 公式 |\n")
        f.write("|------|----------|------|\n")
        f.write("| 第5章 | 关键路径 | ES/EF, LS/LF, 浮动时间 |\n")
        f.write("| 第5章 | 三点估算 | (O+4M+P)/6, 标准差 |\n")
        f.write("| 第5章 | 挣值管理 | PV, EV, AC, SV, SPI |\n")
        f.write("| 第6章 | 成本估算 | 类比、参数、三点估算 |\n")
        f.write("| 第10章 | 决策树 | 期望货币值（EMV） |\n")
        
        f.write("\n## 学习路径建议\n\n")
        f.write("### 第一阶段：基础建立（1-2周）\n")
        f.write("1. 学习第1-2章：建立基础概念\n")
        f.write("2. 理解项目管理框架\n")
        f.write("3. 掌握专业术语\n\n")
        
        f.write("### 第二阶段：核心知识（3-4周）\n")
        f.write("1. 重点学习第3-13章（十大知识领域）\n")
        f.write("2. 掌握每个过程的输入、工具、输出\n")
        f.write("3. 练习计算题（第5、6章）\n\n")
        
        f.write("### 第三阶段：高级专题（1-2周）\n")
        f.write("1. 学习第14-24章\n")
        f.write("2. 理解组织级项目管理\n")
        f.write("3. 掌握专项管理知识\n\n")
        
        f.write("### 第四阶段：复习冲刺（1-2周）\n")
        f.write("1. 做模拟试题\n")
        f.write("2. 复习错题\n")
        f.write("3. 重点公式记忆\n\n")
        
        f.write("## 文件目录结构\n\n")
        f.write("```\n")
        f.write("信息系统项目管理师教程拆分/\n")
        f.write("├── 按章节拆分结果/          # 第1-15章（基础部分）\n")
        f.write("│   ├── 第01章_信息化与信息系统_第16-51页.pdf\n")
        f.write("│   ├── 第02章_信息系统项目管理基础_第52-81页.pdf\n")
        f.write("│   ├── ...\n")
        f.write("│   ├── 第15章_知识管理_第446-486页.pdf\n")
        f.write("│   └── 最终章节索引.md\n")
        f.write("│\n")
        f.write("├── 剩余章节拆分结果/        # 第16-24章（高级部分）\n")
        f.write("│   ├── 第16章_项目变更管理_第487-517页.pdf\n")
        f.write("│   ├── 第17章_战略管理_第518-534页.pdf\n")
        f.write("│   ├── ...\n")
        f.write("│   ├── 第24章_项目管理成熟度模型_第732-752页.pdf\n")
        f.write("│   └── 剩余章节索引.md\n")
        f.write("│\n")
        f.write("└── 完整章节总索引.md        # 本文件\n")
        f.write("```\n")
        
        f.write("\n## 使用说明\n\n")
        f.write("1. **按需学习**：根据考试重点选择章节\n")
        f.write("2. **系统学习**：建议按章节顺序建立知识体系\n")
        f.write("3. **重点突破**：针对计算题和高占比章节重点学习\n")
        f.write("4. **结合实践**：理论知识结合实际案例理解\n")
        f.write("5. **定期复习**：制定复习计划，定期回顾\n")
        
        f.write("\n## 资源链接\n\n")
        f.write("- **官方教材**：《信息系统项目管理师教程（第四版）》\n")
        f.write("- **考试大纲**：中国计算机技术职业资格网\n")
        f.write("- **模拟试题**：历年真题、模拟题库\n")
        f.write("- **学习社区**：软考论坛、备考群\n")
        
        f.write("\n---\n")
        f.write("\n**祝您学习顺利，考试成功！** 🎯\n")
    
    print(f"✅ 完整章节总索引已创建: {index_file}")
    
    # 显示索引摘要
    print("\n📊 索引摘要:")
    print("-" * 80)
    
    # 按目录统计
    dir1_count = sum(1 for c in all_chapters if c['directory'] == dir1)
    dir2_count = sum(1 for c in all_chapters if c['directory'] == dir2)
    
    dir1_pages = sum(c['pages'] for c in all_chapters if c['directory'] == dir1)
    dir2_pages = sum(c['pages'] for c in all_chapters if c['directory'] == dir2)
    
    print(f"📁 {dir1}: {dir1_count}章, {dir1_pages}页")
    print(f"📁 {dir2}: {dir2_count}章, {dir2_pages}页")
    print(f"📚 总计: {len(all_chapters)}章, {total_pages}页")
    
    # 显示章节范围
    if all_chapters:
        chapter_nums = [c['num'] for c in all_chapters]
        missing = [i for i in range(1, 25) if i not in chapter_nums]
        
        if missing:
            print(f"⚠️  缺失章节: {missing}")
        else:
            print("✅ 完整覆盖第1-24章")
    
    print("-" * 80)
    
    # 显示前10个章节
    print("\n📖 前10个章节:")
    for chapter in all_chapters[:10]:
        print(f"  第{chapter['num']:02d}章: {chapter['name']} ({chapter['pages']}页)")
    
    if len(all_chapters) > 10:
        print(f"  ... 还有 {len(all_chapters)-10} 个章节")
    
    print("\n" + "=" * 80)
    print("🎉 完整章节索引创建完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
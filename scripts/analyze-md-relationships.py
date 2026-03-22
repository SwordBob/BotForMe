#!/usr/bin/env python3
"""
分析 Markdown 文件关系并生成 Obsidian 关系图谱数据
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

def find_md_files(root_dir="."):
    """查找所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        # 跳过 .git 目录
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                md_files.append(full_path)
    return sorted(md_files)

def extract_links(content, current_file):
    """从 Markdown 内容中提取链接"""
    # 内部链接格式: [[文件名]] 或 [[文件名|显示文本]]
    internal_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    
    # 清理链接，移除显示文本部分
    cleaned_links = []
    for link in internal_links:
        # 分割文件名和显示文本
        if '|' in link:
            filename = link.split('|')[0].strip()
        else:
            filename = link.strip()
        cleaned_links.append(filename)
    
    return cleaned_links

def extract_tags(content):
    """从内容中提取标签"""
    tags = re.findall(r'#([a-zA-Z0-9\u4e00-\u9fff_-]+)', content)
    return list(set(tags))  # 去重

def analyze_file(filepath):
    """分析单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {"links": [], "tags": [], "word_count": 0}
    
    filename = os.path.basename(filepath)
    dirname = os.path.dirname(filepath)
    
    links = extract_links(content, filepath)
    tags = extract_tags(content)
    word_count = len(content.split())
    
    return {
        "file": filename,
        "path": filepath,
        "dirname": dirname,
        "links": links,
        "tags": tags,
        "word_count": word_count
    }

def categorize_file(filename, content):
    """根据文件名和内容分类文件"""
    filename_lower = filename.lower()
    
    categories = []
    
    # 根据文件名判断
    if "软考" in filename or "高项" in filename:
        categories.append("软考备考")
    if "项目" in filename or "管理" in filename:
        categories.append("项目管理")
    if "禅宗" in filename or "坐法" in filename:
        categories.append("禅修实践")
    if "obsidian" in filename_lower or "git" in filename_lower:
        categories.append("工具配置")
    if "指南" in filename or "说明" in filename:
        categories.append("使用指南")
    if "memory" in filename_lower or "记忆" in filename:
        categories.append("记忆存档")
    if "skill" in filename_lower:
        categories.append("技能文档")
    if "章节" in filename or "第" in filename and "章" in filename:
        categories.append("学习资料")
    
    # 根据内容关键词判断
    content_lower = content.lower()
    if "openclaw" in content_lower:
        categories.append("OpenClaw相关")
    if "python" in content_lower or "脚本" in content:
        categories.append("技术脚本")
    if "git" in content_lower:
        categories.append("版本控制")
    if "obsidian" in content_lower:
        categories.append("笔记工具")
    
    return list(set(categories))  # 去重

def build_relationship_graph(md_files):
    """构建关系图谱"""
    graph = {
        "nodes": [],
        "links": [],
        "categories": defaultdict(list)
    }
    
    file_data = {}
    
    # 分析所有文件
    for filepath in md_files:
        data = analyze_file(filepath)
        filename = data["file"]
        
        # 读取内容用于分类
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""
        
        categories = categorize_file(filename, content)
        
        # 创建节点
        node = {
            "id": filename.replace(".md", ""),
            "name": filename.replace(".md", ""),
            "path": filepath,
            "category": categories[0] if categories else "未分类",
            "all_categories": categories,
            "size": min(50, max(10, data["word_count"] // 100)),  # 根据字数决定节点大小
            "word_count": data["word_count"],
            "link_count": len(data["links"])
        }
        
        graph["nodes"].append(node)
        file_data[filename] = data
        
        # 记录分类
        for category in categories:
            graph["categories"][category].append(filename)
    
    # 创建链接
    for source_file, data in file_data.items():
        source_id = source_file.replace(".md", "")
        
        for link in data["links"]:
            # 查找目标文件
            target_file = None
            for filename in file_data.keys():
                if link in filename or filename.replace(".md", "") == link:
                    target_file = filename
                    break
            
            if target_file:
                target_id = target_file.replace(".md", "")
                
                # 避免自引用
                if source_id != target_id:
                    graph["links"].append({
                        "source": source_id,
                        "target": target_id,
                        "value": 1
                    })
    
    return graph

def generate_obsidian_graph_view(graph):
    """生成 Obsidian 图形视图的说明"""
    categories = graph["categories"]
    
    output = "# Obsidian 关系图谱分析\n\n"
    output += "## 📊 文件统计\n\n"
    output += f"- 总文件数: {len(graph['nodes'])}\n"
    output += f"- 总链接数: {len(graph['links'])}\n"
    output += f"- 平均每个文件链接数: {len(graph['links']) / max(1, len(graph['nodes'])):.1f}\n\n"
    
    output += "## 🏷️ 文件分类\n\n"
    for category, files in sorted(categories.items()):
        output += f"### {category} ({len(files)}个文件)\n"
        for file in sorted(files)[:10]:  # 只显示前10个
            output += f"- [[{file}]]\n"
        if len(files) > 10:
            output += f"- ... 还有 {len(files) - 10} 个文件\n"
        output += "\n"
    
    output += "## 🔗 关键连接\n\n"
    
    # 找出连接最多的文件
    link_counts = defaultdict(int)
    for link in graph["links"]:
        link_counts[link["source"]] += 1
        link_counts[link["target"]] += 1
    
    top_files = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    output += "### 连接最多的文件（枢纽文件）\n"
    for file_id, count in top_files:
        output += f"- **[[{file_id}.md]]**: {count} 个连接\n"
    
    output += "\n### 重要连接关系\n"
    
    # 找出最强的连接（按出现次数）
    connection_counts = defaultdict(int)
    for link in graph["links"]:
        key = tuple(sorted([link["source"], link["target"]]))
        connection_counts[key] += 1
    
    top_connections = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for (file1, file2), count in top_connections:
        output += f"- [[{file1}.md]] ↔ [[{file2}.md]] ({count}个引用)\n"
    
    output += "\n## 🎯 使用建议\n\n"
    output += "1. **打开 Obsidian 图形视图**：点击右上角的网格图标\n"
    output += "2. **按分类筛选**：在图形视图中右键选择分组\n"
    output += "3. **探索枢纽文件**：从连接最多的文件开始浏览\n"
    output += "4. **创建新连接**：使用 `[[文件名]]` 语法链接相关文件\n"
    output += "5. **添加标签**：使用 `#标签` 进行分类\n\n"
    
    output += "## 🔧 增强建议\n\n"
    output += "1. **创建索引文件**：如 `00-索引.md` 链接所有重要文件\n"
    output += "2. **使用 Dataview 插件**：自动生成文件列表和统计\n"
    output += "3. **添加更多内部链接**：增强文件之间的关联性\n"
    output += "4. **定期更新图谱**：随着文件增加，关系会自然演化\n"
    
    return output

def main():
    print("🔍 正在分析 Markdown 文件关系...")
    
    # 查找所有 .md 文件
    md_files = find_md_files()
    print(f"📁 找到 {len(md_files)} 个 Markdown 文件")
    
    # 构建关系图谱
    graph = build_relationship_graph(md_files)
    
    # 生成分析报告
    report = generate_obsidian_graph_view(graph)
    
    # 保存报告
    output_file = "Obsidian-关系图谱分析报告.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 分析完成！报告已保存到: {output_file}")
    
    # 输出关键统计
    print(f"\n📊 关键统计:")
    print(f"   节点数: {len(graph['nodes'])}")
    print(f"   连接数: {len(graph['links'])}")
    print(f"   分类数: {len(graph['categories'])}")
    
    # 显示主要分类
    print(f"\n🏷️ 主要分类:")
    for category, files in sorted(graph['categories'].items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"   {category}: {len(files)}个文件")
    
    # 显示枢纽文件
    print(f"\n🔗 枢纽文件（连接最多）:")
    link_counts = defaultdict(int)
    for link in graph["links"]:
        link_counts[link["source"]] += 1
        link_counts[link["target"]] += 1
    
    for file_id, count in sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"   {file_id}.md: {count}个连接")

if __name__ == "__main__":
    main()
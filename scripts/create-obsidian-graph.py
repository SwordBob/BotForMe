#!/usr/bin/env python3
"""
为 Obsidian 创建关系图谱和增强链接
"""

import os
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
import jieba  # 中文分词
import jieba.analyse

# 初始化 jieba
jieba.initialize()

def find_md_files(root_dir="."):
    """查找所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                md_files.append(full_path)
    return sorted(md_files)

def read_file_content(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def extract_keywords(content, top_n=10):
    """提取关键词（使用 jieba）"""
    if not content.strip():
        return []
    
    # 提取关键词
    keywords = jieba.analyse.extract_tags(content, topK=top_n)
    return keywords

def categorize_by_filename(filename):
    """根据文件名分类"""
    categories = []
    name_lower = filename.lower()
    
    # 文件名关键词映射
    category_map = {
        "软考": "软考备考",
        "高项": "软考备考", 
        "项目": "项目管理",
        "管理": "项目管理",
        "禅宗": "禅修实践",
        "坐法": "禅修实践",
        "obsidian": "工具配置",
        "git": "工具配置",
        "指南": "使用指南",
        "说明": "使用指南",
        "memory": "记忆存档",
        "记忆": "记忆存档",
        "skill": "技能文档",
        "章节": "学习资料",
        "第.*章": "学习资料",
        "教程": "学习资料",
        "openclaw": "OpenClaw相关",
        "python": "技术脚本",
        "脚本": "技术脚本",
        "分析": "数据分析",
        "报告": "数据分析",
        "测试": "测试文档",
        "配置": "配置文档"
    }
    
    for pattern, category in category_map.items():
        if re.search(pattern, filename, re.IGNORECASE):
            categories.append(category)
    
    return list(set(categories))

def analyze_files(md_files):
    """分析所有文件"""
    files_data = []
    
    for filepath in md_files:
        filename = os.path.basename(filepath)
        content = read_file_content(filepath)
        
        # 基本信息
        data = {
            "id": filename.replace(".md", ""),
            "filename": filename,
            "path": filepath,
            "content": content[:1000],  # 只取前1000字符用于分析
            "full_content": content,
            "word_count": len(content),
            "categories": categorize_by_filename(filename),
            "keywords": extract_keywords(content, 10)
        }
        
        files_data.append(data)
    
    return files_data

def find_similarities(files_data):
    """查找文件之间的相似性"""
    similarities = []
    
    for i, file1 in enumerate(files_data):
        for j, file2 in enumerate(files_data[i+1:], i+1):
            # 计算相似度（基于共同关键词）
            keywords1 = set(file1["keywords"])
            keywords2 = set(file2["keywords"])
            
            if keywords1 and keywords2:
                common = keywords1.intersection(keywords2)
                if common:
                    # 相似度 = 共同关键词数 / 平均关键词数
                    avg_keywords = (len(keywords1) + len(keywords2)) / 2
                    similarity = len(common) / avg_keywords
                    
                    if similarity > 0.2:  # 阈值
                        similarities.append({
                            "file1": file1["filename"],
                            "file2": file2["filename"],
                            "similarity": similarity,
                            "common_keywords": list(common)
                        })
    
    # 按相似度排序
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities

def generate_graph_data(files_data, similarities):
    """生成图形数据"""
    nodes = []
    links = []
    
    # 创建节点
    for file in files_data:
        # 确定节点大小（基于字数）
        size = min(50, max(10, file["word_count"] // 200))
        
        # 确定节点颜色（基于主要分类）
        category_colors = {
            "软考备考": "#FF6B6B",
            "项目管理": "#4ECDC4", 
            "禅修实践": "#FFD166",
            "工具配置": "#06D6A0",
            "使用指南": "#118AB2",
            "记忆存档": "#EF476F",
            "技能文档": "#073B4C",
            "学习资料": "#7209B7",
            "OpenClaw相关": "#3A86FF",
            "技术脚本": "#FB5607",
            "数据分析": "#8338EC",
            "测试文档": "#FF006E",
            "配置文档": "#FFBE0B"
        }
        
        primary_category = file["categories"][0] if file["categories"] else "未分类"
        color = category_colors.get(primary_category, "#999999")
        
        nodes.append({
            "id": file["id"],
            "name": file["id"],
            "filename": file["filename"],
            "category": primary_category,
            "all_categories": file["categories"],
            "keywords": file["keywords"][:5],  # 只显示前5个关键词
            "size": size,
            "word_count": file["word_count"],
            "color": color
        })
    
    # 创建链接（基于相似性）
    for sim in similarities[:50]:  # 只取前50个最强连接
        links.append({
            "source": sim["file1"].replace(".md", ""),
            "target": sim["file2"].replace(".md", ""),
            "value": sim["similarity"] * 10,  # 放大以便可视化
            "common_keywords": sim["common_keywords"]
        })
    
    return {"nodes": nodes, "links": links}

def create_obsidian_graph_view(files_data, similarities):
    """创建 Obsidian 图形视图的增强文件"""
    
    output = "# 🔗 Obsidian 关系图谱增强指南\n\n"
    
    output += "## 📊 文件概览\n\n"
    output += f"**总文件数**: {len(files_data)} 个 Markdown 文件\n\n"
    
    # 按分类统计
    category_counts = defaultdict(int)
    for file in files_data:
        for category in file["categories"]:
            category_counts[category] += 1
    
    output += "### 文件分类统计\n"
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        output += f"- **{category}**: {count} 个文件\n"
    
    output += "\n## 🎯 关键枢纽文件\n\n"
    
    # 找出连接最多的文件
    connection_counts = defaultdict(int)
    for sim in similarities:
        connection_counts[sim["file1"]] += 1
        connection_counts[sim["file2"]] += 1
    
    top_files = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    output += "这些文件与其他文件有最多的关联，建议从它们开始探索：\n\n"
    for filename, count in top_files:
        file_id = filename.replace(".md", "")
        output += f"### [[{filename}]]\n"
        output += f"- **关联文件数**: {count}\n"
        
        # 找到这个文件的相关信息
        for file in files_data:
            if file["filename"] == filename:
                if file["categories"]:
                    output += f"- **主要分类**: {', '.join(file['categories'])}\n"
                if file["keywords"]:
                    output += f"- **关键词**: {', '.join(file['keywords'][:5])}\n"
                break
        
        # 找出与这个文件最相关的其他文件
        related = []
        for sim in similarities:
            if sim["file1"] == filename or sim["file2"] == filename:
                other_file = sim["file2"] if sim["file1"] == filename else sim["file1"]
                related.append((other_file, sim["similarity"]))
        
        related.sort(key=lambda x: x[1], reverse=True)
        if related:
            output += "- **最相关文件**:\n"
            for other_file, similarity in related[:3]:
                output += f"  - [[{other_file}]] (相似度: {similarity:.2f})\n"
        
        output += "\n"
    
    output += "## 🔗 推荐创建的内部链接\n\n"
    output += "以下文件之间有很强的关联性，建议添加 `[[ ]]` 链接：\n\n"
    
    # 显示最强的相似性关系
    for i, sim in enumerate(similarities[:20]):
        output += f"{i+1}. **[[{sim['file1']}]]** ↔ **[[{sim['file2']}]]**\n"
        output += f"   - 相似度: {sim['similarity']:.2f}\n"
        output += f"   - 共同关键词: {', '.join(sim['common_keywords'][:3])}\n\n"
    
    output += "## 🗺️ 图谱使用指南\n\n"
    output += "### 在 Obsidian 中查看图谱\n"
    output += "1. 点击右上角的 **网格图标** 打开图形视图\n"
    output += "2. 使用 **右键菜单** 按分类筛选节点\n"
    output += "3. **拖动节点** 重新布局\n"
    output += "4. **点击节点** 查看文件详情\n"
    output += "5. 使用 **滚轮** 缩放视图\n\n"
    
    output += "### 增强你的知识图谱\n"
    output += "1. **添加更多内部链接**：在相关文件间使用 `[[文件名]]`\n"
    output += "2. **使用标签系统**：添加 `#标签` 进行分类\n"
    output += "3. **创建枢纽文件**：如 `00-索引.md` 链接所有重要文件\n"
    output += "4. **定期更新**：随着内容增加，关系会自然演化\n\n"
    
    output += "### 颜色说明\n"
    output += "- 🔴 红色: 软考备考相关\n"
    output += "- 🟢 绿色: 工具配置相关\n"
    output +=("- 🔵 蓝色: 学习资料相关\n")
    output += "- 🟡 黄色: 禅修实践相关\n"
    output += "- 🟣 紫色: 技术脚本相关\n"
    output += "- 🟠 橙色: 使用指南相关\n\n")
    
    output += "## 📈 下一步建议\n\n"
    output += "1. **立即尝试**：打开 Obsidian 图形视图\n"
    output += "2. **增强链接**：根据推荐添加内部链接\n"
    output += "3. **创建索引**：制作一个中心索引文件\n"
    output += "4. **探索关联**：从枢纽文件开始浏览相关知识\n"
    
    return output

def create_graph_json(files_data, similarities):
    """创建图形 JSON 数据（用于外部可视化）"""
    graph = generate_graph_data(files_data, similarities)
    
    # 添加一些统计信息
    graph["stats"] = {
        "total_nodes": len(graph["nodes"]),
        "total_links": len(graph["links"]),
        "categories_count": len(set(node["category"] for node in graph["nodes"])),
        "avg_links_per_node": len(graph["links"]) / max(1, len(graph["nodes"]))
    }
    
    return graph

def main():
    print("🔍 正在分析 Markdown 文件关系...")
    
    # 查找所有文件
    md_files = find_md_files()
    print(f"📁 找到 {len(md_files)} 个 Markdown 文件")
    
    # 分析文件
    files_data = analyze_files(md_files)
    
    # 查找相似性
    similarities = find_similarities(files_data)
    print(f"🔗 找到 {len(similarities)} 个相似关系")
    
    # 创建增强指南
    guide = create_obsidian_graph_view(files_data, similarities)
    
    # 保存指南
    guide_file = "Obsidian-图谱增强指南.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ 增强指南已保存到: {guide_file}")
    
    # 创建 JSON 数据
    graph_data = create_graph_json(files_data, similarities)
    json_file = "obsidian-graph-data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 图形数据已保存到: {json_file}")
    
    # 输出关键信息
    print(f"\n🎯 关键发现:")
    print(f"   文件分类: {len(set(files_data[0]['categories'] for files_data in files_data if files_data['categories']))} 种")
    print(f"   最强相似度: {similarities[0]['similarity']:.2f} ({similarities[0]['file1']} ↔ {similarities[0]['file2']})")
    
    # 显示前5个枢纽文件
    print(f"\n🏆 前5个枢纽文件:")
    connection_counts = defaultdict(int)
    for sim in similarities:
        connection_counts[sim["file1"]] += 1
        connection_counts[sim["file2"]] += 1
    
    for filename, count in sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {filename}: {count} 个关联")

if __name__ == "__main__":
    main()
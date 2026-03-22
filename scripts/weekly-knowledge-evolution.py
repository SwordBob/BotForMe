#!/usr/bin/env python3
"""
每周知识演化跟踪系统
自动分析 Markdown 文件变化，跟踪知识演化
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
import sys

# 配置
CONFIG = {
    "data_dir": "knowledge-evolution-data",
    "snapshot_file": "knowledge-snapshots.json",
    "report_dir": "knowledge-evolution-reports",
    "weeks_to_keep": 12,  # 保留12周的数据
    "min_change_threshold": 0.01,  # 1% 变化阈值
}

def ensure_dirs():
    """确保目录存在"""
    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    os.makedirs(CONFIG["report_dir"], exist_ok=True)

def get_file_fingerprint(filepath):
    """获取文件指纹（用于检测变化）"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        # 使用 SHA256 作为指纹
        return hashlib.sha256(content).hexdigest()
    except:
        return None

def scan_md_files():
    """扫描所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk("."):
        # 跳过一些目录
        skip_dirs = ['.git', '.obsidian', '__pycache__', CONFIG["data_dir"], CONFIG["report_dir"]]
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ".")
                
                # 获取文件信息
                stat = os.stat(full_path)
                fingerprint = get_file_fingerprint(full_path)
                
                if fingerprint:
                    md_files.append({
                        "path": rel_path,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "fingerprint": fingerprint,
                        "ctime": stat.st_ctime
                    })
    
    return sorted(md_files, key=lambda x: x["path"])

def load_snapshots():
    """加载历史快照"""
    snapshot_file = os.path.join(CONFIG["data_dir"], CONFIG["snapshot_file"])
    if os.path.exists(snapshot_file):
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"snapshots": [], "files_history": {}}
    return {"snapshots": [], "files_history": {}}

def save_snapshots(data):
    """保存快照数据"""
    snapshot_file = os.path.join(CONFIG["data_dir"], CONFIG["snapshot_file"])
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_snapshot():
    """创建新的快照"""
    now = datetime.datetime.now()
    snapshot_id = now.strftime("%Y-%m-%d")
    
    print(f"📸 创建快照: {snapshot_id}")
    
    # 扫描文件
    current_files = scan_md_files()
    print(f"  扫描到 {len(current_files)} 个 Markdown 文件")
    
    # 加载历史数据
    data = load_snapshots()
    
    # 创建快照
    snapshot = {
        "id": snapshot_id,
        "timestamp": now.isoformat(),
        "file_count": len(current_files),
        "total_size": sum(f["size"] for f in current_files),
        "files": {f["path"]: f["fingerprint"] for f in current_files}
    }
    
    # 添加到快照列表
    data["snapshots"].append(snapshot)
    
    # 更新文件历史
    for file in current_files:
        path = file["path"]
        if path not in data["files_history"]:
            data["files_history"][path] = []
        
        # 检查是否有变化
        if not data["files_history"][path] or data["files_history"][path][-1]["fingerprint"] != file["fingerprint"]:
            data["files_history"][path].append({
                "timestamp": now.isoformat(),
                "fingerprint": file["fingerprint"],
                "size": file["size"]
            })
    
    # 清理旧数据
    data["snapshots"] = data["snapshots"][-CONFIG["weeks_to_keep"]:]
    
    # 保存
    save_snapshots(data)
    
    return snapshot_id, current_files, data

def analyze_changes(data, current_files):
    """分析变化"""
    if len(data["snapshots"]) < 2:
        return {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "total_changes": 0,
            "change_percentage": 0
        }
    
    # 获取上一个快照
    prev_snapshot = data["snapshots"][-2]
    current_files_dict = {f["path"]: f for f in current_files}
    prev_files = prev_snapshot["files"]
    
    # 分析变化
    new_files = []
    modified_files = []
    deleted_files = []
    
    # 新文件
    for path in current_files_dict:
        if path not in prev_files:
            new_files.append(path)
    
    # 修改的文件
    for path, fingerprint in prev_files.items():
        if path in current_files_dict:
            if current_files_dict[path]["fingerprint"] != fingerprint:
                modified_files.append(path)
    
    # 删除的文件
    for path in prev_files:
        if path not in current_files_dict:
            deleted_files.append(path)
    
    total_changes = len(new_files) + len(modified_files) + len(deleted_files)
    total_files = len(prev_files)
    change_percentage = (total_changes / max(1, total_files)) * 100
    
    return {
        "new_files": new_files,
        "modified_files": modified_files,
        "deleted_files": deleted_files,
        "total_changes": total_changes,
        "change_percentage": change_percentage
    }

def generate_evolution_report(snapshot_id, current_files, data, changes):
    """生成演化报告"""
    now = datetime.datetime.now()
    report_date = now.strftime("%Y-%m-%d")
    report_file = os.path.join(CONFIG["report_dir"], f"knowledge-evolution-{report_date}.md")
    
    # 计算统计信息
    total_files = len(current_files)
    total_size_mb = sum(f["size"] for f in current_files) / (1024 * 1024)
    
    # 按目录统计
    dir_stats = {}
    for file in current_files:
        dir_path = os.path.dirname(file["path"]) or "根目录"
        dir_stats[dir_path] = dir_stats.get(dir_path, 0) + 1
    
    # 文件大小分布
    size_stats = {
        "small": len([f for f in current_files if f["size"] < 1024]),  # <1KB
        "medium": len([f for f in current_files if 1024 <= f["size"] < 10240]),  # 1-10KB
        "large": len([f for f in current_files if f["size"] >= 10240]),  # >=10KB
    }
    
    # 生成报告
    report = f"""# 📈 知识演化报告 - {report_date}

## 📊 概览

| 指标 | 数值 |
|------|------|
| **快照ID** | {snapshot_id} |
| **总文件数** | {total_files} |
| **总大小** | {total_size_mb:.2f} MB |
| **新增文件** | {len(changes['new_files'])} |
| **修改文件** | {len(changes['modified_files'])} |
| **删除文件** | {len(changes['deleted_files'])} |
| **总变化率** | {changes['change_percentage']:.1f}% |

## 🔄 变化分析

### 新增文件 ({len(changes['new_files'])})
{format_file_list(changes['new_files'])}

### 修改文件 ({len(changes['modified_files'])})
{format_file_list(changes['modified_files'])}

### 删除文件 ({len(changes['deleted_files'])})
{format_file_list(changes['deleted_files'])}

## 📁 目录结构

### 文件分布
{format_dir_stats(dir_stats)}

### 文件大小分布
- **小型文件** (<1KB): {size_stats['small']} 个
- **中型文件** (1-10KB): {size_stats['medium']} 个  
- **大型文件** (≥10KB): {size_stats['large']} 个

## 📈 历史趋势

### 文件数量变化
```
{generate_file_count_chart(data)}
```

### 活跃文件
**最近修改的文件:**
{get_recently_modified_files(current_files, 10)}

## 🎯 维护建议

### 1. 知识整理
{get_organization_suggestions(current_files, dir_stats)}

### 2. 链接优化
{get_linking_suggestions(current_files)}

### 3. 内容质量
{get_quality_suggestions(current_files, size_stats)}

## 🔧 技术详情

### 快照信息
- **快照总数**: {len(data['snapshots'])}
- **数据保留**: 最近 {CONFIG['weeks_to_keep']} 周
- **分析时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}

### 文件指纹
- **使用算法**: SHA256
- **变化检测**: 基于内容哈希
- **阈值**: {CONFIG['min_change_threshold']*100}% 变化率

---

*报告生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}*
*下次分析: {(now + datetime.timedelta(days=7)).strftime('%Y-%m-%d')}*
"""
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 报告已生成: {report_file}")
    return report_file

def format_file_list(files, max_display=20):
    """格式化文件列表"""
    if not files:
        return "无"
    
    output = []
    for i, file in enumerate(files[:max_display]):
        output.append(f"{i+1}. `{file}`")
    
    if len(files) > max_display:
        output.append(f"... 还有 {len(files) - max_display} 个文件")
    
    return "\n".join(output)

def format_dir_stats(dir_stats):
    """格式化目录统计"""
    if not dir_stats:
        return "无目录数据"
    
    output = []
    for dir_path, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True):
        if dir_path == ".":
            dir_path = "根目录"
        output.append(f"- `{dir_path}/`: {count} 个文件")
    
    return "\n".join(output)

def generate_file_count_chart(data):
    """生成文件数量变化图表"""
    if len(data["snapshots"]) < 2:
        return "暂无足够历史数据"
    
    # 取最近8个快照
    recent_snapshots = data["snapshots"][-8:]
    
    chart = ""
    max_count = max(s["file_count"] for s in recent_snapshots)
    scale = 50 / max(1, max_count)  # 缩放因子
    
    for snapshot in recent_snapshots:
        date = snapshot["id"][5:]  # 只显示月-日
        count = snapshot["file_count"]
        bar = "█" * int(count * scale)
        chart += f"{date}: {bar} {count}\n"
    
    return chart

def get_recently_modified_files(files, limit=10):
    """获取最近修改的文件"""
    sorted_files = sorted(files, key=lambda x: x["mtime"], reverse=True)[:limit]
    
    output = []
    for file in sorted_files:
        mtime = datetime.datetime.fromtimestamp(file["mtime"]).strftime("%m-%d %H:%M")
        size_kb = file["size"] / 1024
        output.append(f"- `{file['path']}` ({mtime}, {size_kb:.1f}KB)")
    
    return "\n".join(output)

def get_organization_suggestions(files, dir_stats):
    """获取整理建议"""
    suggestions = []
    
    # 检查根目录文件数量
    root_files = dir_stats.get(".", 0) + dir_stats.get("", 0)
    if root_files > 10:
        suggestions.append("根目录文件过多，建议按主题创建子目录")
    
    # 检查大目录
    for dir_path, count in dir_stats.items():
        if count > 20 and dir_path not in [".", ""]:
            suggestions.append(f"目录 `{dir_path}/` 文件较多({count}个)，建议进一步细分")
    
    if not suggestions:
        suggestions.append("目录结构良好，继续保持")
    
    return "\n".join(f"- {s}" for s in suggestions)

def get_linking_suggestions(files):
    """获取链接优化建议"""
    # 这里可以扩展为实际分析文件链接
    return """- 检查重要文件是否已充分链接
- 为新文件添加相关链接
- 使用 `[[文件名]]` 语法增强关联性"""

def get_quality_suggestions(files, size_stats):
    """获取内容质量建议"""
    suggestions = []
    
    # 检查小文件
    if size_stats["small"] > 5:
        suggestions.append(f"有 {size_stats['small']} 个小型文件(<1KB)，考虑合并或补充内容")
    
    # 检查大文件
    if size_stats["large"] > 10:
        suggestions.append(f"有 {size_stats['large']} 个大型文件(≥10KB)，考虑拆分以提高可读性")
    
    if not suggestions:
        suggestions.append("文件大小分布合理")
    
    return "\n".join(f"- {s}" for s in suggestions)

def main():
    """主函数"""
    print("=" * 60)
    print("📈 知识演化跟踪系统")
    print("=" * 60)
    
    # 确保目录存在
    ensure_dirs()
    
    # 创建快照
    snapshot_id, current_files, data = create_snapshot()
    
    # 分析变化
    changes = analyze_changes(data, current_files)
    
    print(f"\n📊 变化分析:")
    print(f"  新增文件: {len(changes['new_files'])}")
    print(f"  修改文件: {len(changes['modified_files'])}")
    print(f"  删除文件: {len(changes['deleted_files'])}")
    print(f"  总变化率: {changes['change_percentage']:.1f}%")
    
    # 生成报告
    report_file = generate_evolution_report(snapshot_id, current_files, data, changes)
    
    print(f"\n✅ 分析完成!")
    print(f"  快照: {snapshot_id}")
    print(f"  报告: {report_file}")
    print(f"  历史快照: {len(data['snapshots'])} 个")
    
    # 如果有显著变化，建议重新生成关系图谱
    if changes['change_percentage'] > CONFIG['min_change_threshold'] * 100:
        print(f"\n🎯 建议: 检测到显著变化({changes['change_percentage']:.1f}%)，建议重新生成关系图谱")
        print("  运行: python3 scripts/create-obsidian-graph.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
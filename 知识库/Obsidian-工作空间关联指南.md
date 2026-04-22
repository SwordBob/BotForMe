# Obsidian 工作空间关联指南

## 🎯 问题描述

**问题**：Obsidian 无法关联 OpenClaw 工作空间，因为工作空间位于隐藏目录中：
```
~/.openclaw/workspace/
```

**原因**：Obsidian 可能无法正确处理以点号（`.`）开头的父目录路径。

## 🚀 解决方案

### 方案1：使用符号链接（推荐 ✅）

我已经创建了一个符号链接，你可以直接使用：

```bash
# 符号链接已创建：
~/openclaw-workspace  ->  ~/.openclaw/workspace
```

**使用方法**：
1. 打开 Obsidian
2. 选择 "打开其他仓库"
3. 选择 `~/openclaw-workspace`

### 方案2：使用启动脚本

我已经创建了两个启动脚本：

#### 脚本1：终端运行
```bash
./open-obsidian-workspace.sh
```

#### 脚本2：双击运行（macOS）
双击 `obsidian-launcher.command`

### 方案3：手动操作步骤

如果上述方法都不行，请按以下步骤操作：

1. **打开终端**
2. **复制工作空间路径**：
   ```
   /Users/niejq/.openclaw/workspace
   ```
3. **打开 Obsidian**
4. 点击左下角 **"打开其他仓库"**
5. 按 `Cmd + Shift + G` 打开 "前往文件夹"
6. 粘贴路径并回车
7. 点击 "打开"

## 🔧 验证步骤

### 步骤1：检查符号链接
```bash
ls -la ~/openclaw-workspace
```
应该显示：
```
lrwxr-xr-x  1 niejq  staff  32  3月 22 14:40 /Users/niejq/openclaw-workspace -> /Users/niejq/.openclaw/workspace
```

### 步骤2：测试启动脚本
```bash
# 测试脚本1
./open-obsidian-workspace.sh

# 或双击脚本2
open obsidian-launcher.command
```

### 步骤3：检查 Obsidian 配置
在 Obsidian 中打开后，检查：
1. 左侧文件浏览器是否显示所有 `.md` 文件
2. 设置 → 关于 → 仓库路径是否正确
3. 图形视图是否能正常显示

## 📁 目录结构说明

```
~/.openclaw/workspace/          # 实际工作空间（隐藏）
├── .obsidian/                  # Obsidian 配置
├── memory/                     # 每日记忆
├── scripts/                    # 自动化脚本
├── *.md                        # 各种文档
└── ...

~/openclaw-workspace           # 符号链接（可见）
```

## ⚠️ 注意事项

1. **不要修改 `.openclaw` 目录名**，这会影响 OpenClaw 正常运行
2. **使用符号链接访问**，而不是直接操作隐藏目录
3. **Obsidian 配置在 `.obsidian/`** 中，已预配置好
4. **Git 版本控制已启用**，所有更改自动跟踪

## 🔄 更新脚本

如果路径发生变化，可以重新创建符号链接：

```bash
# 删除旧链接
rm ~/openclaw-workspace

# 创建新链接
ln -sf ~/.openclaw/workspace ~/openclaw-workspace
```

## 🆘 故障排除

### 问题1：符号链接不工作
```bash
# 检查链接
ls -la ~/openclaw-workspace

# 重新创建
rm ~/openclaw-workspace
ln -sf ~/.openclaw/workspace ~/openclaw-workspace
```

### 问题2：Obsidian 找不到文件
1. 确保使用 "打开其他仓库" 而不是 "打开文件夹"
2. 检查路径是否正确
3. 尝试重启 Obsidian

### 问题3：权限问题
```bash
# 修复权限
chmod 755 ~/.openclaw/workspace
chmod 644 ~/.openclaw/workspace/*.md
```

### 问题4：仍然无法打开
使用绝对路径：
```
/Users/niejq/.openclaw/workspace
```

## 📞 快速帮助

**立即尝试**：
```bash
# 方法1：使用符号链接
open -a Obsidian ~/openclaw-workspace

# 方法2：使用脚本
./open-obsidian-workspace.sh

# 方法3：手动
# 1. 打开 Obsidian
# 2. Cmd+Shift+G
# 3. 输入: /Users/niejq/.openclaw/workspace
```

## 🎉 成功标志

当 Obsidian 正确打开时，你应该看到：
- 左侧文件浏览器显示所有 `.md` 文件
- 可以正常编辑和保存文件
- 图形视图显示笔记关系
- 反向链接正常工作

---

*如果还有问题，请告诉我具体错误信息，我会帮你解决。*
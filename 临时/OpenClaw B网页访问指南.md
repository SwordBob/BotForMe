# OpenClaw B网页访问指南

## 🌐 访问信息

### 基本访问信息
- **访问地址**: http://localhost:18791
- **端口**: 18791
- **认证方式**: Token认证
- **认证Token**: `ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c`

### 服务状态
- ✅ 服务运行正常
- ✅ 端口18791正在监听
- ✅ 需要认证访问

## 🔑 认证问题解决

### 问题现象
访问 http://localhost:18791 时可能出现：
1. **401 Unauthorized** - 需要认证
2. **空白页面** - 可能需要认证后重定向
3. **连接拒绝** - 服务未运行

### 解决方案

#### 方案1：使用Token直接访问（推荐）
在浏览器地址栏直接使用Token访问：
```
http://localhost:18791?token=ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c
```

或者使用Authorization头（需要浏览器插件）：
```
Authorization: Bearer ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c
```

#### 方案2：修改配置为无需认证
修改OpenClaw B的配置文件，禁用认证：

1. 编辑配置文件：
```bash
nano ~/.openclaw-ops/openclaw.json
```

2. 找到gateway配置部分，修改为：
```json
"gateway": {
  "mode": "local",
  "port": 18791,
  "auth": {
    "mode": "none"  # 改为none禁用认证
  }
}
```

3. 重启服务：
```bash
launchctl bootout gui/$UID/ai.openclaw.ops.gateway
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.openclaw.ops.gateway.plist
```

#### 方案3：使用curl测试访问
```bash
# 不带Token访问（应该返回401）
curl -v http://localhost:18791

# 带Token访问
curl -H "Authorization: Bearer ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c" http://localhost:18791

# 或者使用查询参数
curl "http://localhost:18791?token=ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c"
```

## 🛠️ 诊断步骤

### 步骤1：检查服务状态
```bash
# 检查端口是否监听
lsof -i :18791

# 检查服务进程
ps aux | grep "node.*gateway" | grep -v grep

# 检查LaunchAgent服务
launchctl list | grep openclaw
```

### 步骤2：检查日志
```bash
# 查看网关日志
tail -f ~/.openclaw-ops/logs/gateway.log

# 查看错误日志
tail -f ~/.openclaw-ops/logs/gateway-error.log
```

### 步骤3：测试连接
```bash
# 测试HTTP连接
curl -I http://localhost:18791

# 测试健康端点
curl http://localhost:18791/health
```

## 📝 配置验证

### 当前配置摘要
根据配置文件 `~/.openclaw-ops/openclaw.json`：
- **端口**: 18791
- **认证模式**: token
- **Token**: `ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c`
- **实例名称**: OpenClaw B - 运维员

### 验证配置是否正确
```bash
# 检查配置中的端口
grep -A5 '"gateway"' ~/.openclaw-ops/openclaw.json

# 检查认证配置
grep -A5 '"auth"' ~/.openclaw-ops/openclaw.json
```

## 🌍 浏览器访问技巧

### Chrome/Edge浏览器
1. **直接带Token访问**：
   ```
   http://localhost:18791?token=ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c
   ```

2. **使用开发者工具测试**：
   - 按F12打开开发者工具
   - 转到Network标签
   - 访问 http://localhost:18791
   - 查看请求头和响应

3. **使用ModHeader扩展**（推荐）：
   - 安装ModHeader扩展
   - 添加请求头：
     - Name: `Authorization`
     - Value: `Bearer ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c`

### Safari浏览器
1. **启用开发者菜单**：
   - Safari → 偏好设置 → 高级 → 显示开发菜单
   
2. **使用开发者工具**：
   - 开发 → 显示Web检查器
   - 转到网络标签测试

## 🔧 故障排除

### 常见问题1：页面空白
**可能原因**: 认证通过但前端资源加载失败
**解决方案**:
```bash
# 检查静态文件服务
curl http://localhost:18791/static/

# 检查是否有index.html
curl http://localhost:18791/index.html
```

### 常见问题2：持续重定向
**可能原因**: 认证逻辑循环
**解决方案**: 清除浏览器缓存或使用隐私模式访问

### 常见问题3：连接被拒绝
**可能原因**: 服务未运行
**解决方案**:
```bash
# 重启服务
launchctl bootout gui/$UID/ai.openclaw.ops.gateway
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.openclaw.ops.gateway.plist

# 等待3秒后测试
sleep 3 && curl -I http://localhost:18791
```

## 🚀 快速解决方案

### 最简单的方法（立即生效）：
1. 在浏览器中访问：
   ```
   http://localhost:18791?token=ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c
   ```

2. 如果不行，使用curl验证：
   ```bash
   curl "http://localhost:18791?token=ops-39e736394e06050aa2538f197ec6928ae7e2a69a8ab2c"
   ```

### 长期解决方案：
1. 修改配置禁用认证
2. 或配置更友好的认证方式

## 📞 技术支持

如果以上方法都不行，请提供：
1. 浏览器控制台错误信息
2. curl测试结果
3. 服务日志内容

我会根据具体错误信息帮你进一步诊断。
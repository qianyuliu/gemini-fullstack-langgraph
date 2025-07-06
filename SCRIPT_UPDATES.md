# 📝 脚本和文档更新记录

本文档记录了项目中所有脚本和文档的更新，移除了过时的内容并修正了错误的配置。

## 🔄 更新概览

### 主要修复内容：
1. **端口号修正**：前端端口从 5173 更正为 3000
2. **启动命令更新**：添加必要的 `--allow-blocking` 参数
3. **配置简化**：移除过时的搜索引擎和RAG配置选项
4. **路径修正**：更新前端访问路径为 `/app`

## 📋 详细更新列表

### 1. start.sh 启动脚本
**文件路径**: `start.sh`

**更新内容**:
- ✅ 添加 `--allow-blocking` 参数到 langgraph 启动命令
- ✅ 修正前端端口检查从 5173 → 3000
- ✅ 更新前端访问地址为 `http://localhost:3000/app`

**修改前**:
```bash
langgraph dev --host 0.0.0.0 --port 2024 &
# 检查 http://localhost:5173
# 显示 http://localhost:5173
```

**修改后**:
```bash
langgraph dev --host 0.0.0.0 --port 2024 --allow-blocking &
# 检查 http://localhost:3000
# 显示 http://localhost:3000/app
```

### 2. setup.sh 安装脚本
**文件路径**: `setup.sh`

**更新内容**:
- ✅ 移除过时的搜索引擎配置（TAVILY、SERPER等）
- ✅ 简化RAG配置选项
- ✅ 更新启动命令建议
- ✅ 修正前端访问地址

**移除的配置**:
```bash
# 搜索引擎配置 (已移除)
SEARCH_ENGINE="tavily"
TAVILY_API_KEY="your_tavily_api_key"
SERPER_API_KEY="your_serper_api_key"

# RAG 行为配置 (已移除)
RAG_MAX_DOCUMENTS=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_ENABLE_FALLBACK=true
```

### 3. setup.ps1 Windows安装脚本
**文件路径**: `setup.ps1`

**更新内容**:
- ✅ 移除过时的搜索引擎配置
- ✅ 简化RAG配置选项
- ✅ 更新启动命令建议
- ✅ 修正前端访问地址

### 4. Makefile 构建脚本
**文件路径**: `Makefile`

**更新内容**:
- ✅ 更新后端启动命令使用 `python start_server.py`

**修改前**:
```makefile
dev-backend:
	@cd backend && langgraph dev
```

**修改后**:
```makefile
dev-backend:
	@cd backend && python start_server.py
```

### 5. SETUP_GUIDE.md 安装指南
**文件路径**: `SETUP_GUIDE.md`

**更新内容**:
- ✅ 移除过时的搜索引擎配置说明
- ✅ 简化RAG配置选项
- ✅ 更新启动命令为 `python start_server.py`
- ✅ 修正所有端口号引用（5173 → 3000）
- ✅ 更新前端访问路径为 `/app`

### 6. README.md 项目说明
**文件路径**: `README.md`

**更新内容**:
- ✅ 移除过时的搜索引擎配置说明
- ✅ 修正RAGFlow默认端口（9388 → 9380）
- ✅ 更新启动命令说明
- ✅ 修正前端访问地址

### 7. QUICK_START.md 快速启动指南
**文件路径**: `QUICK_START.md`

**更新内容**:
- ✅ 推荐使用 `python start_server.py` 启动方式
- ✅ 添加 `--allow-blocking` 参数说明
- ✅ 修正所有端口号和访问路径
- ✅ 增强故障排除指南
- ✅ 移除对已删除文件的引用

## 🚨 重要变更说明

### 端口变更
- **前端端口**: 5173 → 3000
- **前端路径**: `/` → `/app`
- **后端端口**: 2024 (无变化)

### 启动方式变更
- **推荐方式**: `python start_server.py` (包含必要参数)
- **手动方式**: `langgraph dev --host 0.0.0.0 --port 2024 --allow-blocking`

### 配置简化
- **移除**: 搜索引擎配置选项
- **简化**: RAG配置选项
- **保留**: 核心LLM和RAGFlow配置

## 🔧 验证更新

更新完成后，请验证以下内容：

1. **启动测试**:
   ```bash
   # 后端启动
   cd backend && python start_server.py
   
   # 前端启动
   cd frontend && npm run dev
   ```

2. **访问测试**:
   - 前端: http://localhost:3000/app
   - 后端: http://localhost:2024
   - API文档: http://localhost:2024/docs

3. **功能测试**:
   ```bash
   cd backend && python test_complete_workflow.py
   ```

## 📚 相关文档

- [QUICK_START.md](./QUICK_START.md) - 快速启动指南
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - 详细安装指南
- [MULTI_LLM_GUIDE.md](./MULTI_LLM_GUIDE.md) - 多LLM配置指南

## 🎯 后续建议

1. **定期检查**: 定期检查文档和脚本的一致性
2. **版本控制**: 记录重要配置变更
3. **测试验证**: 每次更新后进行完整测试
4. **用户反馈**: 收集用户使用反馈，持续改进

---

**更新时间**: 2024年1月
**更新内容**: 修复过时配置，统一端口和启动方式 
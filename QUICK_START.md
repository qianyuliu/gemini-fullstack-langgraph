# 🚀 Gemini-Fullstack 快速启动指南

## 🎯 快速启动步骤

### 1. 环境准备

确保你的系统满足以下要求：
- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 2. 一键配置（推荐）

#### Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

#### Windows PowerShell:
```powershell
.\setup.ps1
```

### 3. 手动配置

如果自动脚本失败，可以手动执行：

```bash
# 后端配置
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# 前端配置
cd ../frontend
npm install
```

### 4. 配置 API Keys

创建 `backend/.env` 文件（参考 `backend/env_example.txt`）：

```bash
# 至少配置一个 LLM API Key
DEEPSEEK_API_KEY="your_deepseek_api_key"
# 或者
ZHIPUAI_API_KEY="your_zhipuai_api_key"
# 或者
QWEN_API_KEY="your_qwen_api_key"
# 或者
OPENAI_API_KEY="your_openai_api_key"

# 可选：配置 RAG（需要先启动 RAGFlow）
RAG_PROVIDER="ragflow"
RAGFLOW_API_URL="http://localhost:9380"
RAGFLOW_API_KEY="your_ragflow_api_key"
```

### 5. 启动项目

#### 方式 1: 使用启动脚本（推荐）
```bash
# 后端
cd backend
python start_server.py

# 前端（新终端）
cd frontend
npm run dev
```

#### 方式 2: 一键启动
```bash
chmod +x start.sh
./start.sh
```

#### 方式 3: 手动启动
```bash
# 后端
cd backend
source venv/bin/activate
langgraph dev --host 0.0.0.0 --port 2024 --allow-blocking

# 前端（新终端）
cd frontend
npm run dev
```

#### 方式 4: 使用 Makefile
```bash
make dev
```

### 6. 验证启动

访问以下地址验证服务状态：
- **前端应用**: http://localhost:3000/app
- **后端 API**: http://localhost:2024
- **API 文档**: http://localhost:2024/docs
- **LangGraph UI**: http://localhost:2024/__langgraph__

## 🔧 故障排除

### 常见问题

#### 1. 端口冲突
**症状**: 端口被占用
**解决**: 
```bash
# 检查端口占用
lsof -i :2024  # 后端
lsof -i :3000  # 前端

# 或者使用不同端口启动
langgraph dev --port 3024  # 后端
# 前端端口在 vite.config.ts 中修改
```

#### 2. 依赖安装失败
**症状**: pip install 或 npm install 失败
**解决**:
```bash
# Python 依赖
pip install --upgrade pip
pip install -e . --force-reinstall

# Node.js 依赖
rm -rf node_modules package-lock.json
npm install
```

#### 3. API Key 错误
**症状**: LLM 调用失败
**解决**: 
- 检查 `backend/.env` 文件中的 API Key 配置
- 确保至少配置一个有效的 LLM API Key

#### 4. RAGFlow 连接失败
**症状**: RAG 功能不可用
**解决**:
- 确保 RAGFlow 服务正在运行
- 检查 `RAGFLOW_API_URL` 和 `RAGFLOW_API_KEY` 配置
- 使用 `backend/test_complete_workflow.py` 进行测试

#### 5. 导入错误
**症状**: 模块导入失败
**解决**:
- 确保在 backend 目录下运行 `langgraph dev`
- 使用 `--allow-blocking` 参数启动服务器

## 📚 功能特性

### 核心功能
- ✅ **多 LLM 支持**: DeepSeek、智谱AI、阿里千问、OpenAI
- ✅ **智能搜索**: 动态生成搜索查询，多轮研究
- ✅ **RAG 集成**: 支持 RAGFlow 知识库检索
- ✅ **Web 研究**: 集成多种搜索引擎
- ✅ **反射推理**: 识别知识缺口，生成后续查询

### RAG 功能
- ✅ **RAGFlow 集成**: 支持 RAGFlow 知识库
- ✅ **智能回退**: RAG → Web 搜索回退机制
- ✅ **资源管理**: 灵活的资源配置和管理
- ✅ **性能优化**: 缓存、并发控制、超时处理

## 🎯 下一步

### 1. 配置 RAGFlow（可选）
```bash
# 启动 RAGFlow
docker run -d -p 9380:9380 infiniflow/ragflow
```

### 2. 上传文档到知识库
- 访问 http://localhost:9380
- 创建数据集并上传文档
- 获取 API Key 并配置到 `.env` 文件

### 3. 测试完整功能
```bash
cd backend
python test_complete_workflow.py
```

### 4. 生产部署
- 参考 `SETUP_GUIDE.md` 中的 Docker 部署部分
- 使用 `docker-compose.yml` 进行容器化部署

## 📞 获取帮助

- 📖 **详细文档**: `SETUP_GUIDE.md`
- 🔧 **多LLM配置**: `MULTI_LLM_GUIDE.md`
- 🧪 **功能测试**: `backend/test_complete_workflow.py`
- 🐛 **问题排查**: 查看后端服务器日志

## 🚨 重要提示

1. **必须配置 LLM API Key**: 至少需要一个有效的 LLM 提供商 API Key
2. **推荐使用启动脚本**: `python start_server.py` 包含了必要的参数
3. **RAG 功能可选**: 不配置 RAGFlow 也可以正常使用 Web 搜索功能
4. **端口配置**: 后端默认 2024，前端默认 3000

---

**🎉 现在你可以开始使用 AI 研究助手了！** 
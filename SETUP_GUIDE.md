# Gemini-Fullstack 项目配置启动指南

本指南将帮助您完整配置和启动 gemini-fullstack-langgraph-quickstart 项目，包括增强的 RAG 系统。

## 📋 环境要求

### 系统要求
- **Node.js**: 18.x 或以上
- **Python**: 3.11 或以上  
- **npm/yarn**: 最新版本
- **Git**: 最新版本

### 可选服务
- **RAGFlow**: 如果要使用 RAG 功能
- **Redis**: 生产环境部署时需要
- **PostgreSQL**: 生产环境部署时需要

## 🚀 快速启动

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd gemini-fullstack-langgraph-quickstart
```

### 2. 后端配置

#### 安装 Python 依赖

```bash
cd backend
pip install -e .

# 或者使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

#### 创建环境配置文件

在 `backend/` 目录下创建 `.env` 文件：

```bash
# ===========================================
# LLM 配置 (至少选择一个)
# ===========================================

# DeepSeek (推荐)
DEEPSEEK_API_KEY="your_deepseek_api_key"

# 智谱AI
# ZHIPUAI_API_KEY="your_zhipuai_api_key"

# 阿里千问
# QWEN_API_KEY="your_qwen_api_key"

# OpenAI
# OPENAI_API_KEY="your_openai_api_key"

# 自定义 API
# LLM_API_KEY="your_custom_api_key"
# LLM_BASE_URL="https://your-custom-api.com"
# LLM_MODEL_NAME="your-model-name"

# ===========================================
# 搜索引擎配置 (可选)
# ===========================================

# ===========================================
# RAG 配置 (可选但推荐)
# ===========================================

# 启用 RAG
RAG_PROVIDER="ragflow"

# RAGFlow 连接配置
RAGFLOW_API_URL="http://localhost:9380"
RAGFLOW_API_KEY="your_ragflow_api_key"



# ===========================================
# 日志配置
# ===========================================

LOG_LEVEL=INFO
LOG_FILE=logs/rag_system.log
LOG_CONSOLE=true
LOG_FILE_ENABLED=true

# ===========================================
# 应用配置
# ===========================================

# 端口配置
BACKEND_PORT=2024
FRONTEND_PORT=3000

# 开发模式
DEBUG=true
```

### 3. 前端配置

#### 安装 Node.js 依赖

```bash
cd frontend
npm install

# 或者使用 yarn
yarn install
```

### 4. RAG 系统配置 (可选但推荐)

#### 4.1 配置 RAGFlow (如果使用 RAG)

1. **安装 RAGFlow**:
   ```bash
   # 使用 Docker 快速启动 RAGFlow
   git clone https://github.com/infiniflow/ragflow.git
   cd ragflow
   docker compose up -d
   ```

2. **访问 RAGFlow**: 
   - 打开 http://localhost:9380
   - 创建账户并获取 API Key

3. **配置知识库**:
   - 在 RAGFlow 中创建数据集
   - 上传文档到数据集
   - 记录数据集 ID

#### 4.2 配置资源文件

创建 `backend/config/resources.json` 文件：

```json
{
  "resources": [
    {
      "name": "general_knowledge",
      "uri": "rag://dataset/your_dataset_id_1",
      "title": "通用知识库",
      "description": "包含通用知识的数据集",
      "enabled": true,
      "metadata": {
        "priority": "high",
        "domain": "general",
        "last_updated": "2024-01-15"
      }
    },
    {
      "name": "technical_docs",
      "uri": "rag://dataset/your_dataset_id_2", 
      "title": "技术文档",
      "description": "技术文档和API参考",
      "enabled": true,
      "metadata": {
        "priority": "medium",
        "domain": "technical"
      }
    }
  ]
}
```

## 🏃‍♂️ 启动项目

### 方式 1: 使用 Makefile (推荐)

```bash
# 在项目根目录下
make dev
```

这将同时启动前端和后端服务器。

### 方式 2: 分别启动

#### 启动后端
```bash
cd backend
python start_server.py
```
后端将在 http://localhost:2024 上运行

#### 启动前端
```bash
cd frontend
npm run dev
```
前端将在 http://localhost:3000 上运行

### 方式 3: 使用 Python 脚本

```bash
# 后端
cd backend
python -c "
import subprocess
import sys
try:
    subprocess.run([sys.executable, '-m', 'langgraph', 'dev'], check=True)
except subprocess.CalledProcessError as e:
    print(f'启动失败: {e}')
"
```

## 🔍 验证安装

### 1. 检查后端状态

访问 http://localhost:2024/docs 查看 API 文档

### 2. 检查前端状态

访问 http://localhost:3000/app 查看应用界面

### 3. 测试 RAG 功能

运行测试脚本：

```bash
cd backend
python examples/enhanced_rag_example.py
```

### 4. 命令行测试

```bash
cd backend
python examples/cli_research.py "什么是人工智能？"
```

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. 端口冲突

```bash
# 检查端口占用
lsof -i :2024  # 后端端口
lsof -i :3000  # 前端端口

# 修改端口 (在 .env 文件中)
BACKEND_PORT=3024
FRONTEND_PORT=3001
```

#### 2. Python 依赖问题

```bash
# 清理并重新安装
pip uninstall -y langgraph langchain
pip install -e .

# 或者使用特定版本
pip install "langgraph>=0.2.6" "langchain>=0.3.19"
```

#### 3. Node.js 依赖问题

```bash
# 清理 node_modules
rm -rf node_modules package-lock.json
npm install

# 或者使用 yarn
rm -rf node_modules yarn.lock
yarn install
```

#### 4. RAG 连接问题

```bash
# 检查 RAGFlow 状态
curl http://localhost:9380/health

# 验证 API Key
curl -H "Authorization: Bearer your_api_key" \
     http://localhost:9380/api/v1/datasets
```

#### 5. 权限问题

```bash
# Linux/Mac 权限设置
chmod +x backend/scripts/*.sh
sudo chown -R $USER:$GROUP .

# Windows 管理员权限运行
# 右键 -> 以管理员身份运行
```

### 日志调试

#### 查看详细日志

```bash
# 设置调试级别
export LOG_LEVEL=DEBUG

# 查看日志文件
tail -f backend/logs/rag_system.log

# 实时日志
cd backend && python -c "
from src.agent.logging_config import setup_logging
setup_logging(log_level='DEBUG')
"
```

#### 常用调试命令

```bash
# 检查配置
python -c "
from src.rag import rag_config, is_rag_enabled
print('RAG Enabled:', is_rag_enabled())
print('Config:', rag_config.__dict__)
"

# 测试 RAG 工具
python -c "
from src.rag.tools import create_rag_tool, get_rag_tool_info
print('Tool Info:', get_rag_tool_info())
tool = create_rag_tool()
print('Tool Created:', tool is not None)
"
```

## 🐳 Docker 部署 (生产环境)

### 1. 构建 Docker 镜像

```bash
# 在项目根目录
docker build -t gemini-fullstack-langgraph .
```

### 2. 使用 Docker Compose

创建 `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  app:
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - RAG_PROVIDER=ragflow
      - RAGFLOW_API_URL=http://ragflow:9380
      - RAGFLOW_API_KEY=${RAGFLOW_API_KEY}
      
  ragflow:
    image: infiniflow/ragflow:latest
    ports:
      - "9380:9380"
    volumes:
      - ragflow_data:/app/data
    environment:
      - MYSQL_PASSWORD=infiniflow
      
volumes:
  ragflow_data:
```

### 3. 启动生产环境

```bash
# 设置环境变量
export DEEPSEEK_API_KEY="your_key"
export RAGFLOW_API_KEY="your_ragflow_key"
export LANGSMITH_API_KEY="your_langsmith_key"

# 启动服务
docker-compose up -d
```

## 📚 更多配置选项

### 高级 RAG 配置

```bash
# 性能优化
RAG_CACHE_TTL=3600
RAG_MAX_CONCURRENT_REQUESTS=5
RAG_REQUEST_TIMEOUT=30

# 质量控制
RAG_MIN_CHUNK_SIZE=100
RAG_MAX_CHUNK_SIZE=1000
RAG_OVERLAP_SIZE=50

# 多语言支持
RAG_DEFAULT_LANGUAGE=zh-CN
RAG_FALLBACK_LANGUAGE=en-US
```

### LLM 模型配置

```bash
# 模型选择
QUERY_GENERATOR_MODEL="deepseek-chat"
REFLECTION_MODEL="deepseek-chat"
ANSWER_MODEL="deepseek-chat"

# 参数调整
MAX_RESEARCH_LOOPS=3
MAX_SEARCH_RESULTS=5
INITIAL_SEARCH_QUERY_COUNT=3
```

## 🤝 开发指南

### 开发环境设置

```bash
# 安装开发工具
pip install -e ".[dev]"
npm install --save-dev

# 代码格式化
cd backend && ruff format .
cd frontend && npm run lint

# 类型检查
cd backend && mypy src/
cd frontend && npm run type-check
```

### 热重载开发

```bash
# 启用热重载
export DEBUG=true
export RELOAD=true

# 启动开发服务
make dev
```

## 🎯 下一步

1. **配置你的第一个 RAG 数据集**
2. **测试不同的 LLM 提供商**
3. **自定义提示词模板**
4. **集成更多数据源**
5. **部署到生产环境**

现在你已经成功配置了 gemini-fullstack 项目！访问 http://localhost:5173 开始使用你的增强 AI 研究助手。

如果遇到问题，请查看故障排除部分或查看项目文档。 
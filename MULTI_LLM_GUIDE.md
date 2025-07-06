# 多LLM提供商配置指南

本指南将帮助您配置和使用不同的LLM提供商来替代Google Gemini。

## 支持的LLM提供商

### 1. DeepSeek (推荐)
- **优点**: 成本低、速度快、性能优异
- **配置**:
  ```bash
  DEEPSEEK_API_KEY="sk-your-deepseek-api-key"
  ```
- **获取API密钥**: 访问 [DeepSeek 官网](https://www.deepseek.com/)

### 2. 智谱AI
- **优点**: 中文支持优异、本土化模型
- **配置**:
  ```bash
  ZHIPUAI_API_KEY="your-zhipuai-api-key"
  ```
- **获取API密钥**: 访问 [智谱AI 官网](https://www.zhipuai.cn/)

### 3. 阿里千问
- **优点**: 中文优化、阿里云生态、性能强劲
- **配置**:
  ```bash
  QWEN_API_KEY="sk-your-qwen-api-key"
  ```
- **获取API密钥**: 访问 [阿里云通义千问](https://tongyi.aliyun.com/)

### 4. OpenAI
- **优点**: 工业标准、功能丰富
- **配置**:
  ```bash
  OPENAI_API_KEY="sk-your-openai-api-key"
  ```
- **获取API密钥**: 访问 [OpenAI 官网](https://openai.com/)

### 5. 自定义OpenAI兼容API
- **优点**: 灵活性高、支持本地部署
- **配置**:
  ```bash
  LLM_API_KEY="your-custom-api-key"
  LLM_BASE_URL="https://your-custom-api.com"
  LLM_MODEL_NAME="your-model-name"
  ```

## 搜索引擎配置

### 1. Tavily (推荐)
- **优点**: 专为AI设计、结果质量高
- **配置**:
  ```bash
  SEARCH_ENGINE="tavily"
  TAVILY_API_KEY="tvly-your-tavily-api-key"
  ```
- **获取API密钥**: 访问 [Tavily 官网](https://tavily.com/)

### 2. Serper
- **优点**: 基于Google搜索、结果准确
- **配置**:
  ```bash
  SEARCH_ENGINE="serper"
  SERPER_API_KEY="your-serper-api-key"
  ```
- **获取API密钥**: 访问 [Serper 官网](https://serper.dev/)

### 3. Google Custom Search
- **优点**: 官方Google搜索API
- **配置**:
  ```bash
  SEARCH_ENGINE="google"
  GOOGLE_API_KEY="your-google-api-key"
  GOOGLE_CSE_ID="your-custom-search-engine-id"
  ```

### 4. DuckDuckGo (免费)
- **优点**: 无需API密钥、隐私保护
- **配置**:
  ```bash
  SEARCH_ENGINE="duckduckgo"
  ```

## 快速开始

1. **选择LLM提供商**: 根据您的需求选择上述任一提供商
2. **配置环境变量**: 在 `backend/.env` 文件中添加相应配置
3. **启动服务**: 运行 `make dev` 或 `docker-compose up`

## 完整配置示例

### 使用DeepSeek + Tavily
```bash
# LLM配置
DEEPSEEK_API_KEY="sk-your-deepseek-api-key"

# 搜索引擎配置
SEARCH_ENGINE="tavily"
TAVILY_API_KEY="tvly-your-tavily-api-key"

# RAG配置 (可选)
RAG_PROVIDER="ragflow"
RAGFLOW_API_URL="http://localhost:9380"
RAGFLOW_API_KEY="ragflow-xxx"
```

### 使用智谱AI + Serper
```bash
# LLM配置
ZHIPUAI_API_KEY="your-zhipuai-api-key"

# 搜索引擎配置
SEARCH_ENGINE="serper"
SERPER_API_KEY="your-serper-api-key"

# RAG配置 (可选)
RAG_PROVIDER="ragflow"
RAGFLOW_API_URL="http://localhost:9380"
RAGFLOW_API_KEY="ragflow-xxx"
```

### 使用阿里千问 + Google搜索
```bash
# LLM配置
QWEN_API_KEY="sk-your-qwen-api-key"

# 搜索引擎配置
SEARCH_ENGINE="google"
GOOGLE_API_KEY="your-google-api-key"
GOOGLE_CSE_ID="your-custom-search-engine-id"

# RAG配置 (可选)
RAG_PROVIDER="ragflow"
RAGFLOW_API_URL="http://localhost:9380"
RAGFLOW_API_KEY="ragflow-xxx"
```

## 常见问题

### Q: 如何获取API密钥?
A: 请访问对应提供商的官网注册账户并申请API密钥。

### Q: 可以同时配置多个LLM提供商吗?
A: 是的，系统会根据配置的API密钥自动检测可用的模型，您可以在前端界面中选择。

### Q: 哪个LLM提供商性价比最高?
A: DeepSeek通常提供最好的性价比，速度快且成本低。

### Q: 不配置搜索引擎API会怎样?
A: 系统会回退到DuckDuckGo，但结果质量可能不如专业搜索API。

### Q: 如何测试配置是否正确?
A: 启动服务后，在前端界面选择模型并提交查询，查看是否正常工作。

## 故障排除

1. **检查API密钥**: 确保API密钥正确且有效
2. **检查网络连接**: 确保能够访问相应的API端点
3. **查看日志**: 查看后端日志了解具体错误信息
4. **测试单个组件**: 分别测试LLM和搜索引擎配置

## 技术支持

如遇到问题，请检查：
1. 环境变量是否正确设置
2. API密钥是否有效
3. 网络连接是否正常
4. 后端日志中的错误信息 
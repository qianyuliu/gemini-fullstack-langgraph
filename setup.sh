#!/bin/bash

# =============================================================================
# Gemini-Fullstack 项目自动配置脚本
# =============================================================================

set -e  # 如果任何命令失败则退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装或不在 PATH 中"
        return 1
    fi
    return 0
}

# 检查 Python 版本
check_python_version() {
    local python_cmd="$1"
    local version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; then
        return 0
    else
        return 1
    fi
}

# 检查 Node.js 版本
check_node_version() {
    local version=$(node -v | sed 's/v//')
    local major=$(echo $version | cut -d. -f1)
    
    if [ "$major" -ge 18 ]; then
        return 0
    else
        return 1
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "🚀 Gemini-Fullstack 项目配置脚本"
    echo "========================================"
    
    # 1. 检查系统要求
    log_info "检查系统要求..."
    
    # 检查 Python
    if check_command "python3"; then
        if check_python_version "python3"; then
            log_success "Python 3.11+ 已安装"
            PYTHON_CMD="python3"
        else
            log_error "Python 版本过低，需要 3.11+"
            exit 1
        fi
    elif check_command "python"; then
        if check_python_version "python"; then
            log_success "Python 3.11+ 已安装"
            PYTHON_CMD="python"
        else
            log_error "Python 版本过低，需要 3.11+"
            exit 1
        fi
    else
        log_error "Python 未安装"
        exit 1
    fi
    
    # 检查 Node.js
    if check_command "node"; then
        if check_node_version; then
            log_success "Node.js 18+ 已安装"
        else
            log_error "Node.js 版本过低，需要 18+"
            exit 1
        fi
    else
        log_error "Node.js 未安装"
        exit 1
    fi
    
    # 检查 npm
    if check_command "npm"; then
        log_success "npm 已安装"
    else
        log_error "npm 未安装"
        exit 1
    fi
    
    # 2. 设置 Python 虚拟环境
    log_info "设置 Python 虚拟环境..."
    cd backend
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        log_success "虚拟环境已创建"
    else
        log_info "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate || source venv/Scripts/activate
    log_success "虚拟环境已激活"
    
    # 3. 安装 Python 依赖
    log_info "安装 Python 依赖..."
    pip install --upgrade pip
    pip install -e .
    log_success "Python 依赖安装完成"
    
    cd ..
    
    # 4. 安装 Node.js 依赖
    log_info "安装 Node.js 依赖..."
    cd frontend
    npm install
    log_success "Node.js 依赖安装完成"
    cd ..
    
    # 5. 创建配置文件
    log_info "创建配置文件..."
    
    # 创建 .env 文件
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << 'EOF'
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

# ===========================================
# RAG 配置 (可选)
# ===========================================

# 启用 RAG
# RAG_PROVIDER="ragflow"

# RAGFlow 连接配置
# RAGFLOW_API_URL="http://localhost:9380"
# RAGFLOW_API_KEY="your_ragflow_api_key"

# ===========================================
# 日志配置
# ===========================================

LOG_LEVEL=INFO
LOG_CONSOLE=true
LOG_FILE_ENABLED=true

# ===========================================
# 开发配置
# ===========================================

DEBUG=true
EOF
        log_success ".env 配置文件已创建"
    else
        log_info ".env 文件已存在"
    fi
    
    # 创建目录结构
    mkdir -p backend/config
    mkdir -p backend/logs
    
    # 创建示例资源配置文件
    if [ ! -f "backend/config/resources.json" ]; then
        cat > backend/config/resources.json << 'EOF'
{
  "resources": [
    {
      "name": "example_knowledge_base",
      "uri": "rag://dataset/your_dataset_id",
      "title": "示例知识库",
      "description": "这是一个示例知识库配置",
      "enabled": false,
      "metadata": {
        "priority": "medium",
        "domain": "general",
        "note": "请替换为实际的数据集ID"
      }
    }
  ]
}
EOF
        log_success "示例资源配置文件已创建"
    fi
    
    # 6. 验证安装
    log_info "验证安装..."
    
    cd backend
    source venv/bin/activate || source venv/Scripts/activate
    
    # 测试导入
    if $PYTHON_CMD -c "import langgraph, langchain; print('Dependencies OK')" &> /dev/null; then
        log_success "Python 依赖验证通过"
    else
        log_error "Python 依赖验证失败"
        exit 1
    fi
    
    cd ../frontend
    if npm list react &> /dev/null; then
        log_success "Node.js 依赖验证通过"
    else
        log_error "Node.js 依赖验证失败"
        exit 1
    fi
    
    cd ..
    
    # 7. 完成提示
    echo ""
    log_success "🎉 项目配置完成！"
    echo ""
    echo "========================================"
    echo "📝 下一步操作："
    echo "========================================"
    echo "1. 配置 API Keys："
    echo "   编辑 backend/.env 文件，添加你的 LLM API Key"
    echo ""
    echo "2. 启动项目："
    echo "   make dev"
    echo "   或者分别启动："
    echo "   cd backend && python start_server.py"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "3. 访问应用："
    echo "   前端: http://localhost:3000/app"
    echo "   后端: http://localhost:2024"
    echo ""
    echo "4. 可选：配置 RAG 功能"
    echo "   - 安装 RAGFlow: docker run -d -p 9380:9380 infiniflow/ragflow"
    echo "   - 在 .env 中启用 RAG_PROVIDER=ragflow"
    echo "   - 配置 RAGFLOW_API_KEY"
    echo ""
    echo "需要帮助？查看 SETUP_GUIDE.md 获取详细说明"
    echo "========================================"
}

# 检查是否在正确的目录
if [ ! -f "Makefile" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    log_error "请在项目根目录运行此脚本"
    exit 1
fi

# 运行主函数
main "$@" 
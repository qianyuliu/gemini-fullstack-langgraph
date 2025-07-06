#!/bin/bash

# =============================================================================
# Gemini-Fullstack 项目启动脚本
# =============================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# 检查文件是否存在
check_file() {
    if [ ! -f "$1" ]; then
        log_error "文件 $1 不存在"
        return 1
    fi
    return 0
}

# 检查目录是否存在
check_directory() {
    if [ ! -d "$1" ]; then
        log_error "目录 $1 不存在"
        return 1
    fi
    return 0
}

# 检查环境配置
check_environment() {
    log_info "检查环境配置..."
    
    # 检查 .env 文件
    if ! check_file "backend/.env"; then
        log_error "请先运行 ./setup.sh 创建 .env 文件"
        return 1
    fi
    
    # 检查虚拟环境
    if ! check_directory "backend/venv"; then
        log_error "Python 虚拟环境不存在，请先运行 ./setup.sh"
        return 1
    fi
    
    # 检查 node_modules
    if ! check_directory "frontend/node_modules"; then
        log_error "Node.js 依赖未安装，请先运行 ./setup.sh"
        return 1
    fi
    
    log_success "环境配置检查通过"
    return 0
}

# 检查 API Key 配置
check_api_keys() {
    log_info "检查 API Key 配置..."
    
    # 读取 .env 文件
    if grep -q "your_deepseek_api_key\|your_zhipuai_api_key\|your_qwen_api_key\|your_openai_api_key" backend/.env; then
        log_warning "检测到默认 API Key，请确保已配置实际的 API Key"
        log_warning "编辑 backend/.env 文件，替换为你的真实 API Key"
        echo ""
        read -p "是否继续启动? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "已取消启动"
            exit 0
        fi
    else
        log_success "API Key 配置检查通过"
    fi
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    cd backend
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 设置环境变量
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    
    # 启动 langgraph
    log_info "启动 LangGraph 服务器..."
    langgraph dev --host 0.0.0.0 --port 2024 --allow-blocking &
    
    # 保存后端进程 ID
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    log_success "后端服务已启动 (PID: $BACKEND_PID)"
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    
    cd frontend
    
    # 启动 Vite 开发服务器
    npm run dev &
    
    # 保存前端进程 ID
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    log_success "前端服务已启动 (PID: $FRONTEND_PID)"
}

# 等待服务启动
wait_for_services() {
    log_info "等待服务启动..."
    
    # 等待后端服务
    for i in {1..30}; do
        if curl -s http://localhost:2024/health > /dev/null 2>&1; then
            log_success "后端服务已就绪"
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    
    # 等待前端服务
    sleep 5
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        log_success "前端服务已就绪"
    else
        log_warning "前端服务可能还在启动中"
    fi
}

# 显示服务信息
show_info() {
    echo ""
    echo "========================================"
    echo "🎉 服务已启动！"
    echo "========================================"
    echo "📊 后端服务:"
    echo "   - API: http://localhost:2024"
    echo "   - 文档: http://localhost:2024/docs"
    echo "   - LangGraph UI: http://localhost:2024/__langgraph__"
    echo ""
    echo "🌐 前端服务:"
    echo "   - 应用: http://localhost:3000/app"
    echo ""
    echo "📋 管理命令:"
    echo "   - 停止服务: ./stop.sh"
    echo "   - 查看日志: ./logs.sh"
    echo "   - 重启服务: ./restart.sh"
    echo ""
    echo "💡 提示:"
    echo "   - 使用 Ctrl+C 停止此脚本"
    echo "   - 服务将在后台继续运行"
    echo "   - 修改代码后会自动重载"
    echo "========================================"
}

# 清理函数
cleanup() {
    log_info "正在清理..."
    
    # 停止后端服务
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            log_info "停止后端服务 (PID: $BACKEND_PID)"
            kill $BACKEND_PID
        fi
        rm -f backend.pid
    fi
    
    # 停止前端服务
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            log_info "停止前端服务 (PID: $FRONTEND_PID)"
            kill $FRONTEND_PID
        fi
        rm -f frontend.pid
    fi
    
    log_success "清理完成"
}

# 设置信号处理
trap cleanup EXIT SIGINT SIGTERM

# 主函数
main() {
    echo "========================================"
    echo "🚀 启动 Gemini-Fullstack 项目"
    echo "========================================"
    
    # 检查是否在正确的目录
    if [ ! -f "Makefile" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 环境检查
    check_environment || exit 1
    check_api_keys
    
    # 启动服务
    start_backend
    sleep 3
    start_frontend
    
    # 等待服务就绪
    wait_for_services
    
    # 显示信息
    show_info
    
    # 保持脚本运行
    log_info "按 Ctrl+C 停止服务..."
    while true; do
        sleep 1
    done
}

# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  --backend-only 仅启动后端服务"
    echo "  --frontend-only 仅启动前端服务"
    echo ""
    echo "示例:"
    echo "  $0                 # 启动前端和后端"
    echo "  $0 --backend-only  # 仅启动后端"
    echo "  $0 --frontend-only # 仅启动前端"
    exit 0
fi

# 处理启动选项
if [ "$1" = "--backend-only" ]; then
    log_info "仅启动后端服务"
    check_environment || exit 1
    check_api_keys
    start_backend
    wait_for_services
    show_info
    while true; do sleep 1; done
elif [ "$1" = "--frontend-only" ]; then
    log_info "仅启动前端服务"
    check_environment || exit 1
    start_frontend
    wait_for_services
    show_info
    while true; do sleep 1; done
else
    # 启动完整服务
    main "$@"
fi 
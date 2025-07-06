# =============================================================================
# Gemini-Fullstack 项目自动配置脚本 (Windows PowerShell)
# =============================================================================

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
function Write-InfoLog {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-SuccessLog {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarningLog {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorLog {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 检查命令是否存在
function Test-CommandExists {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# 检查 Python 版本
function Test-PythonVersion {
    param([string]$PythonCommand)
    
    try {
        $version = & $PythonCommand -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        $major, $minor = $version.Split('.')
        
        if ([int]$major -eq 3 -and [int]$minor -ge 11) {
            return $true
        }
        else {
            return $false
        }
    }
    catch {
        return $false
    }
}

# 检查 Node.js 版本
function Test-NodeVersion {
    try {
        $version = node -v 2>$null
        $major = $version.Substring(1).Split('.')[0]
        
        if ([int]$major -ge 18) {
            return $true
        }
        else {
            return $false
        }
    }
    catch {
        return $false
    }
}

# 主函数
function Start-Setup {
    Write-Host "========================================"
    Write-Host "🚀 Gemini-Fullstack 项目配置脚本"
    Write-Host "========================================"
    
    # 1. 检查系统要求
    Write-InfoLog "检查系统要求..."
    
    # 检查 Python
    $pythonCommand = $null
    if (Test-CommandExists "python") {
        if (Test-PythonVersion "python") {
            Write-SuccessLog "Python 3.11+ 已安装"
            $pythonCommand = "python"
        }
        else {
            Write-ErrorLog "Python 版本过低，需要 3.11+"
            exit 1
        }
    }
    elseif (Test-CommandExists "python3") {
        if (Test-PythonVersion "python3") {
            Write-SuccessLog "Python 3.11+ 已安装"
            $pythonCommand = "python3"
        }
        else {
            Write-ErrorLog "Python 版本过低，需要 3.11+"
            exit 1
        }
    }
    else {
        Write-ErrorLog "Python 未安装"
        exit 1
    }
    
    # 检查 Node.js
    if (Test-CommandExists "node") {
        if (Test-NodeVersion) {
            Write-SuccessLog "Node.js 18+ 已安装"
        }
        else {
            Write-ErrorLog "Node.js 版本过低，需要 18+"
            exit 1
        }
    }
    else {
        Write-ErrorLog "Node.js 未安装"
        exit 1
    }
    
    # 检查 npm
    if (Test-CommandExists "npm") {
        Write-SuccessLog "npm 已安装"
    }
    else {
        Write-ErrorLog "npm 未安装"
        exit 1
    }
    
    # 2. 设置 Python 虚拟环境
    Write-InfoLog "设置 Python 虚拟环境..."
    Set-Location "backend"
    
    if (!(Test-Path "venv")) {
        & $pythonCommand -m venv venv
        Write-SuccessLog "虚拟环境已创建"
    }
    else {
        Write-InfoLog "虚拟环境已存在"
    }
    
    # 激活虚拟环境
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-SuccessLog "虚拟环境已激活"
    }
    else {
        Write-ErrorLog "无法激活虚拟环境"
        exit 1
    }
    
    # 3. 安装 Python 依赖
    Write-InfoLog "安装 Python 依赖..."
    & python -m pip install --upgrade pip
    & pip install -e .
    Write-SuccessLog "Python 依赖安装完成"
    
    Set-Location ".."
    
    # 4. 安装 Node.js 依赖
    Write-InfoLog "安装 Node.js 依赖..."
    Set-Location "frontend"
    & npm install
    Write-SuccessLog "Node.js 依赖安装完成"
    Set-Location ".."
    
    # 5. 创建配置文件
    Write-InfoLog "创建配置文件..."
    
    # 创建 .env 文件
    if (!(Test-Path "backend\.env")) {
        $envContent = @"
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
"@
        $envContent | Out-File -FilePath "backend\.env" -Encoding UTF8
        Write-SuccessLog ".env 配置文件已创建"
    }
    else {
        Write-InfoLog ".env 文件已存在"
    }
    
    # 创建目录结构
    New-Item -ItemType Directory -Path "backend\config" -Force | Out-Null
    New-Item -ItemType Directory -Path "backend\logs" -Force | Out-Null
    
    # 创建示例资源配置文件
    if (!(Test-Path "backend\config\resources.json")) {
        $resourcesContent = @"
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
"@
        $resourcesContent | Out-File -FilePath "backend\config\resources.json" -Encoding UTF8
        Write-SuccessLog "示例资源配置文件已创建"
    }
    
    # 6. 验证安装
    Write-InfoLog "验证安装..."
    
    Set-Location "backend"
    & "venv\Scripts\Activate.ps1"
    
    # 测试导入
    try {
        & python -c "import langgraph, langchain; print('Dependencies OK')" 2>$null | Out-Null
        Write-SuccessLog "Python 依赖验证通过"
    }
    catch {
        Write-ErrorLog "Python 依赖验证失败"
        exit 1
    }
    
    Set-Location "..\frontend"
    try {
        & npm list react 2>$null | Out-Null
        Write-SuccessLog "Node.js 依赖验证通过"
    }
    catch {
        Write-ErrorLog "Node.js 依赖验证失败"
        exit 1
    }
    
    Set-Location ".."
    
    # 7. 完成提示
    Write-Host ""
    Write-SuccessLog "🎉 项目配置完成！"
    Write-Host ""
    Write-Host "========================================"
    Write-Host "📝 下一步操作："
    Write-Host "========================================"
    Write-Host "1. 配置 API Keys："
    Write-Host "   编辑 backend\.env 文件，添加你的 LLM API Key"
    Write-Host ""
    Write-Host "2. 启动项目："
    Write-Host "   PowerShell:"
    Write-Host "     .\start.ps1"
    Write-Host "   或者分别启动："
    Write-Host "     cd backend && python start_server.py"
    Write-Host "     cd frontend && npm run dev"
    Write-Host ""
    Write-Host "3. 访问应用："
    Write-Host "   前端: http://localhost:3000/app"
    Write-Host "   后端: http://localhost:2024"
    Write-Host ""
    Write-Host "4. 可选：配置 RAG 功能"
    Write-Host "   - 安装 RAGFlow: docker run -d -p 9380:9380 infiniflow/ragflow"
    Write-Host "   - 在 .env 中启用 RAG_PROVIDER=ragflow"
    Write-Host "   - 配置 RAGFLOW_API_KEY"
    Write-Host ""
    Write-Host "需要帮助？查看 SETUP_GUIDE.md 获取详细说明"
    Write-Host "========================================"
}

# 检查是否在正确的目录
if (!(Test-Path "Makefile") -or !(Test-Path "backend") -or !(Test-Path "frontend")) {
    Write-ErrorLog "请在项目根目录运行此脚本"
    exit 1
}

# 运行主函数
Start-Setup 
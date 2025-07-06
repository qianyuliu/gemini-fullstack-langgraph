# 🔧 修复 .env 文件编码问题

## 🐛 问题描述

您遇到的错误是由于 `.env` 文件编码问题导致的：
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0xb2 in position 243: illegal multibyte sequence
```

## 🔧 解决方案

### 方法1：重新创建 .env 文件（推荐）

1. **备份现有文件**：
   ```bash
   cd backend
   copy .env .env.backup
   ```

2. **删除有问题的文件**：
   ```bash
   del .env
   ```

3. **创建新的 .env 文件**：
   使用记事本或 VS Code 创建新的 `.env` 文件，确保使用 **UTF-8 编码**：

   ```bash
   # ===========================================
   # LLM 配置
   # ===========================================
   
   DEEPSEEK_API_KEY="sk-998f343af6d840b19ec3c7e51c5c6b06"
   LANGSMITH_API_KEY="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"
   
   # ===========================================
   # 搜索引擎配置
   # ===========================================
   
   SEARCH_ENGINE="serper"
   SERPER_API_KEY="82d0c2be8abc3041b409dd6263ac3425c96c75c2"
   
   # ===========================================
   # RAG 配置
   # ===========================================
   
   RAG_PROVIDER="ragflow"
   RAGFLOW_API_URL="http://localhost:9380"
   RAGFLOW_API_KEY="ragflow-JiOTBmNzFjNTk5MDExZjBiYjIzNmVlZT"
   
   # ===========================================
   # 日志配置
   # ===========================================
   
   LOG_LEVEL=INFO
   LOG_CONSOLE=true
   LOG_FILE_ENABLED=true
   LOG_FILE=logs/rag_system.log
   
   # ===========================================
   # 开发配置
   # ===========================================
   
   ENV=development
   DEBUG=true
   ```

### 方法2：转换现有文件编码

如果您想保留现有文件，可以转换编码：

1. **使用 PowerShell 转换**：
   ```powershell
   cd backend
   $content = Get-Content .env -Encoding Default
   $content | Out-File .env.utf8 -Encoding UTF8
   del .env
   ren .env.utf8 .env
   ```

2. **使用 VS Code**：
   - 打开 `.env` 文件
   - 点击右下角的编码格式（可能显示为 GBK）
   - 选择 "Reopen with Encoding" → "UTF-8"
   - 保存文件

### 方法3：使用 Notepad++ 转换

1. 用 Notepad++ 打开 `.env` 文件
2. 菜单：编码 → 转为 UTF-8（无 BOM）
3. 保存文件

## ⚠️ 注意事项

### 创建 .env 文件时的要求：

1. **编码格式**：必须使用 UTF-8 编码
2. **不要包含 BOM**：UTF-8 without BOM
3. **避免中文注释**：只使用英文字符和数字
4. **行结束符**：使用 LF 或 CRLF 都可以

### 推荐的编辑器设置：

**VS Code**：
- 文件 → 首选项 → 设置
- 搜索 "encoding"
- 设置 "Files: Encoding" 为 "utf8"

**记事本**：
- 保存时选择编码为 "UTF-8"

## 🔍 验证修复

修复后验证 `.env` 文件：

```bash
cd backend
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('✅ 文件读取成功')
print('✅ DEEPSEEK_API_KEY:', 'Configured' if os.getenv('DEEPSEEK_API_KEY') else 'Missing')
print('✅ SERPER_API_KEY:', 'Configured' if os.getenv('SERPER_API_KEY') else 'Missing')
print('✅ RAG_PROVIDER:', os.getenv('RAG_PROVIDER'))
"
```

## 🚀 启动测试

修复后尝试启动服务器：

```bash
cd backend
python start_server.py
```

如果没有编码错误，服务器应该能正常启动。

## 📝 预防措施

为了避免将来出现编码问题：

1. **始终使用 UTF-8 编码**创建配置文件
2. **避免在 .env 文件中使用中文注释**
3. **使用支持 UTF-8 的编辑器**（VS Code、Notepad++ 等）
4. **定期验证**文件编码格式

## 🔄 如果问题仍然存在

如果按照上述方法仍然有问题，请：

1. **检查文件权限**：确保有读写权限
2. **检查文件路径**：确保在正确的目录（backend/）
3. **重启终端**：有时需要重新加载环境
4. **检查 Python 环境**：确保使用正确的 Python 版本

修复完成后，您的项目应该能够正常启动！ 
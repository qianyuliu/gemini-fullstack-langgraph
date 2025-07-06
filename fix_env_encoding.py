#!/usr/bin/env python3
"""
自动修复 .env 文件编码问题
"""

import os
import shutil
from pathlib import Path

def fix_env_encoding():
    """修复 .env 文件的编码问题"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    backup_file = backend_dir / ".env.backup"
    
    if not env_file.exists():
        print("❌ .env 文件不存在")
        return False
    
    try:
        # 1. 备份原文件
        print("📋 备份原 .env 文件...")
        shutil.copy2(env_file, backup_file)
        print(f"✅ 备份完成: {backup_file}")
        
        # 2. 尝试用不同编码读取文件
        content = None
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(env_file, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ 使用 {encoding} 编码成功读取文件")
                break
            except UnicodeDecodeError:
                print(f"❌ {encoding} 编码读取失败")
                continue
        
        if content is None:
            print("❌ 无法读取 .env 文件，请手动修复")
            return False
        
        # 3. 用 UTF-8 编码重新写入文件
        print("🔄 转换为 UTF-8 编码...")
        with open(env_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print("✅ .env 文件编码修复完成")
        
        # 4. 验证修复结果
        print("🔍 验证修复结果...")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ .env 文件可以正常读取")
            return True
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        return False

def create_clean_env():
    """创建一个干净的 .env 文件模板"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    # 基于之前的配置创建干净的模板
    clean_env_content = """# ===========================================
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
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(clean_env_content)
        print("✅ 创建了干净的 .env 文件")
        return True
    except Exception as e:
        print(f"❌ 创建 .env 文件失败: {e}")
        return False

def main():
    print("🔧 .env 文件编码修复工具")
    print("=" * 40)
    
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if not backend_dir.exists():
        print("❌ backend 目录不存在")
        return
    
    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("🔄 创建新的 .env 文件...")
        if create_clean_env():
            print("✅ 修复完成！")
        return
    
    print("方案选择：")
    print("1. 尝试修复现有 .env 文件编码")
    print("2. 重新创建干净的 .env 文件")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        if fix_env_encoding():
            print("✅ 修复完成！")
        else:
            print("❌ 修复失败，建议选择方案2")
    elif choice == "2":
        if create_clean_env():
            print("✅ 重新创建完成！")
        else:
            print("❌ 创建失败")
    else:
        print("❌ 无效选择")
        return
    
    print("\n🚀 现在可以尝试启动服务器:")
    print("cd backend && python start_server.py")

if __name__ == "__main__":
    main() 
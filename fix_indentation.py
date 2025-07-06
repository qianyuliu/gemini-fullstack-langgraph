#!/usr/bin/env python3
"""
修复 utils.py 文件的缩进错误
"""

import re
from pathlib import Path

def fix_indentation():
    """修复 utils.py 文件的缩进错误"""
    utils_file = Path("backend/src/agent/utils.py")
    
    if not utils_file.exists():
        print("❌ utils.py 文件不存在")
        return False
    
    try:
        # 读取文件内容
        with open(utils_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复第14行的缩进错误
        # 查找并替换错误的缩进
        old_pattern1 = """        else:
        content = messages[-1].content"""
        
        new_pattern1 = """        else:
            content = messages[-1].content"""
        
        # 修复第28行的缩进错误
        old_pattern2 = """            else:
            content = str(message.content) if message.content else ""
            if isinstance(message, HumanMessage):"""
        
        new_pattern2 = """            else:
                content = str(message.content) if message.content else ""
                if isinstance(message, HumanMessage):"""
        
        # 执行替换
        content = content.replace(old_pattern1, new_pattern1)
        content = content.replace(old_pattern2, new_pattern2)
        
        # 还需要修复相关的其他行
        old_pattern3 = """                research_topic += f"User: {content}\n"
                elif isinstance(message, AIMessage):
                    research_topic += f"Assistant: {content}\n" """
        
        new_pattern3 = """                    research_topic += f"User: {content}\n"
                elif isinstance(message, AIMessage):
                    research_topic += f"Assistant: {content}\n" """
        
        content = content.replace(old_pattern3, new_pattern3)
        
        # 写回文件
        with open(utils_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ utils.py 缩进错误修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        return False

if __name__ == "__main__":
    print("🔧 修复 utils.py 缩进错误")
    print("=" * 30)
    
    if fix_indentation():
        print("✅ 修复完成！现在可以尝试启动服务器")
    else:
        print("❌ 修复失败") 
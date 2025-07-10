"""
长报告生成示例

演示如何使用gemini-fullstack生成长篇研究报告，
支持分章节生成和RAG+WebSearch+Reflection流程。
"""

import asyncio
import os
from langchain_core.messages import HumanMessage
from src.agent.graph import research_graph


async def test_long_report_generation():
    """测试长报告生成功能。"""
    
    # 测试用例：请求生成一个关于AI的详细报告
    test_cases = [
        {
            "message": "请生成一份关于人工智能在医疗领域应用的2万字详细研究报告",
            "description": "2万字AI医疗报告"
        },
        {
            "message": "我需要一个关于低代码平台发展趋势的1.5万字研究报告",
            "description": "1.5万字低代码报告"
        },
        {
            "message": "生成一份关于区块链技术在金融科技中应用的深度分析报告，大约1万字",
            "description": "1万字区块链金融报告"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"测试案例 {i}: {test_case['description']}")
        print(f"{'='*50}")
        
        # 创建初始状态
        initial_state = {
            "messages": [HumanMessage(content=test_case["message"])],
            "search_query": [],
            "sources_gathered": [],
            "web_research_result": [],
            "rag_documents": [],
            "rag_enabled": True,
            "rag_resources": [],
            "is_sufficient": False,
            "knowledge_gap": "",
            "follow_up_queries": [],
            "research_loop_count": 0,
            "number_of_ran_queries": 0,
            "is_long_report": False,
            "report_plan": None,
            "current_section": None,
            "completed_sections": [],
            "final_report": None
        }
        
        # 配置
        config = {
            "configurable": {
                "max_tokens": 8192,
                "number_of_initial_queries": 3,
                "max_research_loops": 2
            }
        }
        
        try:
            # 运行工作流
            print("开始生成报告...")
            result = await research_graph.ainvoke(initial_state, config)
            
            # 输出结果
            if result.get("final_report"):
                print(f"生成成功！报告长度: {len(result['final_report'])} 字符")
                
                # 保存到文件
                filename = f"long_report_example_{i}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result["final_report"])
                print(f"报告已保存到: {filename}")
                
                # 显示报告摘要
                lines = result["final_report"].split("\n")
                title_line = next((line for line in lines if line.startswith("#")), "无标题")
                print(f"报告标题: {title_line}")
                
                # 统计章节数量
                section_count = len([line for line in lines if line.startswith("## ") and not line.startswith("## 摘要") and not line.startswith("## 目录")])
                print(f"章节数量: {section_count}")
                
            else:
                print("报告生成失败")
                print(f"最终状态: {result}")
                
        except Exception as e:
            print(f"生成过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"测试案例 {i} 完成")


async def test_standard_flow():
    """测试标准流程（非长报告）。"""
    print(f"\n{'='*50}")
    print("测试标准流程")
    print(f"{'='*50}")
    
    # 创建标准查询
    initial_state = {
        "messages": [HumanMessage(content="人工智能的最新发展趋势是什么？")],
        "search_query": [],
        "sources_gathered": [],
        "web_research_result": [],
        "rag_documents": [],
        "rag_enabled": True,
        "rag_resources": [],
        "is_sufficient": False,
        "knowledge_gap": "",
        "follow_up_queries": [],
        "research_loop_count": 0,
        "number_of_ran_queries": 0,
        "is_long_report": False,
        "report_plan": None,
        "current_section": None,
        "completed_sections": [],
        "final_report": None
    }
    
    config = {
        "configurable": {
            "max_tokens": 4096,
            "number_of_initial_queries": 2,
            "max_research_loops": 1
        }
    }
    
    try:
        print("运行标准流程...")
        result = await research_graph.ainvoke(initial_state, config)
        
        if result.get("messages"):
            final_message = result["messages"][-1]
            print(f"标准回答生成成功！长度: {len(final_message.content)} 字符")
            print("回答预览:", final_message.content[:200] + "...")
        else:
            print("标准流程失败")
            print(f"最终状态: {result}")
            
    except Exception as e:
        print(f"标准流程出现错误: {e}")
        import traceback
        traceback.print_exc()


def check_environment():
    """检查环境配置。"""
    print("检查环境配置...")
    
    required_env_vars = [
        "DEEPSEEK_API_KEY",
        "ZHIPUAI_API_KEY", 
        "QWEN_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    configured_models = []
    for var in required_env_vars:
        if os.getenv(var):
            model_name = var.replace("_API_KEY", "").lower()
            configured_models.append(model_name)
    
    if not configured_models:
        print("❌ 错误：没有配置任何LLM API密钥")
        print("请至少配置以下之一:")
        for var in required_env_vars:
            print(f"  - {var}")
        return False
    
    print(f"✅ 已配置的模型: {', '.join(configured_models)}")
    return True


async def main():
    """主函数。"""
    print("长报告生成功能测试")
    print("="*50)
    
    # 检查环境
    if not check_environment():
        return
    
    print("\n选择测试模式:")
    print("1. 长报告生成测试")
    print("2. 标准流程测试") 
    print("3. 全部测试")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == "1":
        await test_long_report_generation()
    elif choice == "2":
        await test_standard_flow()
    elif choice == "3":
        await test_standard_flow()
        await test_long_report_generation()
    else:
        print("无效选择")


if __name__ == "__main__":
    asyncio.run(main()) 
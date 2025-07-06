#!/usr/bin/env python3
"""Test script to verify the complete RAG + Web search workflow."""

import os
import sys
from dotenv import load_dotenv, find_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")

def test_complete_workflow():
    """Test the complete research workflow with RAG + Web search."""
    
    print("🔍 Testing Complete RAG + Web Search Workflow")
    print("=" * 60)
    
    from agent.graph import research_graph
    from langchain_core.messages import HumanMessage
    
    # Test configuration
    test_query = "低代码平台的发展趋势和技术特点"
    rag_resources = ["rag://dataset/cfc2cf48598c11f0924c6eee872b827c"]
    
    print(f"📝 Test Query: {test_query}")
    print(f"📚 RAG Resources: {rag_resources}")
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content=test_query)],
        "rag_resources": rag_resources,
        "initial_search_query_count": 3,
        "max_research_loops": 2,
        "reasoning_model": "deepseek-chat",
        "research_loop_count": 0,
    }
    
    print("\n🚀 Starting workflow...")
    
    try:
        # Run the workflow
        result = research_graph.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("✅ Workflow completed successfully!")
        
        # Analyze the results
        messages = result.get("messages", [])
        rag_documents = result.get("rag_documents", [])
        web_research_result = result.get("web_research_result", [])
        
        print(f"\n📊 Results Analysis:")
        print(f"   📄 Messages: {len(messages)}")
        print(f"   📚 RAG Documents: {len(rag_documents)}")
        print(f"   🌐 Web Research Results: {len(web_research_result)}")
        
        # Show the final answer
        if messages:
            final_message = messages[-1]
            if hasattr(final_message, 'content'):
                final_answer = final_message.content
                print(f"\n📝 Final Answer Length: {len(final_answer)} characters")
                print(f"📝 Final Answer Preview:")
                print("-" * 40)
                print(final_answer[:500] + "..." if len(final_answer) > 500 else final_answer)
                print("-" * 40)
                
                # Check for source integration
                has_knowledge_base = "knowledge base" in final_answer.lower() or "知识库" in final_answer
                has_web_sources = "http" in final_answer or "www" in final_answer
                
                print(f"\n🔍 Source Integration Analysis:")
                print(f"   📚 Contains Knowledge Base References: {'✅' if has_knowledge_base else '❌'}")
                print(f"   🌐 Contains Web Source References: {'✅' if has_web_sources else '❌'}")
                
                # Check report structure
                has_sections = any(section in final_answer for section in [
                    "Executive Summary", "Introduction", "Main Analysis", 
                    "Key Findings", "Conclusion", "References"
                ])
                print(f"   📋 Has Report Structure: {'✅' if has_sections else '❌'}")
                
        # Show workflow state details
        print(f"\n🔧 Workflow State Details:")
        print(f"   🔄 Research Loop Count: {result.get('research_loop_count', 0)}")
        print(f"   🎯 Is Sufficient: {result.get('is_sufficient', 'N/A')}")
        print(f"   📝 Knowledge Gap: {result.get('knowledge_gap', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    
    print("🧪 Complete Workflow Test\n")
    
    success = test_complete_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print("\n💡 Key Points to Check:")
        print("1. Both RAG and web search results should be included")
        print("2. Final answer should be comprehensive (2000+ words)")
        print("3. Sources should be properly cited with real URLs")
        print("4. Report should have clear structure and sections")
        
        print("\n🔧 If issues persist:")
        print("1. Check that RAG_ENABLE_FALLBACK=true in .env")
        print("2. Verify web search is working properly")
        print("3. Ensure the LLM has enough context window")
        print("4. Check that sources contain valid URLs")
    else:
        print("❌ Test failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Check backend server logs for errors")
        print("2. Verify all environment variables are set")
        print("3. Ensure RAGFlow and web search are working")

if __name__ == "__main__":
    main() 
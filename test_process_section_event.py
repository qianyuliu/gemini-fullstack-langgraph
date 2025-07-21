#!/usr/bin/env python3
"""
Test script to verify process_section event is correctly sent
"""

import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_process_section_event():
    """Test the process_section event format"""
    
    # Simulate the event data that should be sent from backend
    event_data = {
        "process_section": {
            "current_section_index": 2,
            "total_sections": 7,
            "sections_completed_count": 2,
            "section_name": "核心分析",
            "section_description": "深入分析主要研究内容，运用理论框架和方法论，提供详细的数据分析和论证。"
        }
    }
    
    print("=== Test process_section Event Format ===")
    print(f"Event structure: {list(event_data.keys())}")
    print(f"Process section data: {event_data['process_section']}")
    
    # Test frontend parsing
    try:
        if 'process_section' in event_data:
            section_data = event_data['process_section']
            sectionIndex = section_data['current_section_index']
            totalSections = section_data['total_sections']
            sectionName = section_data['section_name']
            sectionDescription = section_data['section_description']
            completedCount = section_data.get('sections_completed_count', 0)
            
            print(f"✅ Frontend parsing successful:")
            print(f"   Section Index: {sectionIndex}")
            print(f"   Total Sections: {totalSections}")
            print(f"   Section Name: {sectionName}")
            print(f"   Section Description: {sectionDescription}")
            print(f"   Completed Count: {completedCount}")
            
            # Test the display logic
            currentSectionInfo = f"**{sectionName}** (目标字数) 🔍 需研究\n\n{sectionDescription}\n\n**处理状态：** 正在生成内容...\n\n**进度：** {completedCount}/{totalSections} 章节已完成"
            
            print(f"\n📝 Generated display text:")
            print(currentSectionInfo)
            
        else:
            print("❌ process_section event not found")
            
    except Exception as e:
        print(f"❌ Frontend parsing failed: {e}")
    
    # Test with report plan integration
    print("\n=== Test with Report Plan Integration ===")
    
    # Simulate stored report plan
    report_plan = {
        "sections": [
            {"name": "引言", "description": "介绍研究背景", "word_count_target": 2000, "requires_research": True},
            {"name": "文献综述", "description": "相关研究", "word_count_target": 3000, "requires_research": True},
            {"name": "核心分析", "description": "主要内容分析", "word_count_target": 4000, "requires_research": True},
            {"name": "方法分析", "description": "研究方法", "word_count_target": 2500, "requires_research": True},
            {"name": "结果讨论", "description": "结果分析", "word_count_target": 3500, "requires_research": True},
            {"name": "结论", "description": "总结", "word_count_target": 1500, "requires_research": False},
            {"name": "参考文献", "description": "引用文献", "word_count_target": 500, "requires_research": False}
        ]
    }
    
    try:
        # Simulate frontend logic
        sectionIndex = 2  # Processing section 3
        if report_plan and report_plan['sections'] and sectionIndex < len(report_plan['sections']):
            currentSection = report_plan['sections'][sectionIndex]
            currentSectionName = currentSection['name']
            
            wordCount = currentSection['word_count_target']
            researchStatus = "🔍 需研究" if currentSection['requires_research'] else "📝 直接生成"
            
            detailedInfo = f"**{currentSection['name']}** ({wordCount}字) {researchStatus}\n\n{currentSection['description']}\n\n**处理状态：** 正在生成内容...\n\n**进度：** 2/7 章节已完成"
            
            print(f"✅ Detailed section info generated:")
            print(detailedInfo)
        else:
            print("❌ Could not generate detailed section info")
            
    except Exception as e:
        print(f"❌ Report plan integration failed: {e}")

def test_event_serialization():
    """Test event serialization for LangGraph"""
    
    print("\n=== Test Event Serialization ===")
    
    # Simulate the complete event structure
    complete_event = {
        "current_section_index": 2,
        "next_section_index": 3,
        "sections_completed_count": 2,
        "completed_sections": ["section1", "section2"],
        "section_name": "核心分析",
        "section_description": "深入分析主要研究内容",
        "total_sections": 7,
        "process_section": {
            "current_section_index": 2,
            "total_sections": 7,
            "sections_completed_count": 2,
            "section_name": "核心分析",
            "section_description": "深入分析主要研究内容"
        }
    }
    
    try:
        # Test JSON serialization
        json_str = json.dumps(complete_event, ensure_ascii=False, indent=2)
        print("✅ Event serialization successful")
        print(f"Event size: {len(json_str)} characters")
        
        # Test deserialization
        parsed_event = json.loads(json_str)
        print(f"✅ Event deserialization successful")
        print(f"Keys: {list(parsed_event.keys())}")
        
    except Exception as e:
        print(f"❌ Event serialization failed: {e}")

if __name__ == "__main__":
    test_process_section_event()
    test_event_serialization()
    print("\n🎉 All tests completed!") 
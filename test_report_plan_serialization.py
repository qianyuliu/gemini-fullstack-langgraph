#!/usr/bin/env python3
"""
Test script to verify ReportPlan serialization for frontend display.
"""

import json
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ReportSection(BaseModel):
    """Report section model for long report generation."""
    name: str = Field(description="Name of the report section")
    description: str = Field(description="Brief description of what this section should cover")
    requires_research: bool = Field(description="Whether this section needs research")
    content: str = Field(default="", description="Generated content for this section")
    word_count_target: int = Field(default=1000, description="Target word count for this section")
    research_queries: List[str] = Field(default_factory=list, description="Specific research queries for this section")
    completed: bool = Field(default=False, description="Whether this section is completed")

class ReportPlan(BaseModel):
    """Complete report plan with sections."""
    title: str = Field(description="Title of the report")
    abstract: str = Field(description="Brief abstract of the report")
    sections: List[ReportSection] = Field(description="List of report sections")
    total_word_count_target: int = Field(description="Target word count for entire report")

def test_report_plan_serialization():
    """Test if ReportPlan can be properly serialized."""
    
    # Create a sample report plan
    sections = [
        ReportSection(
            name="引言",
            description="介绍研究背景和目标",
            requires_research=True,
            word_count_target=2000
        ),
        ReportSection(
            name="文献综述", 
            description="相关研究和理论基础",
            requires_research=True,
            word_count_target=4000
        ),
        ReportSection(
            name="核心分析",
            description="主要内容分析", 
            requires_research=True,
            word_count_target=6000
        ),
        ReportSection(
            name="总结",
            description="总结要点和结论",
            requires_research=False,
            word_count_target=2000
        )
    ]
    
    report_plan = ReportPlan(
        title="人工智能发展研究报告",
        abstract="本报告深入分析人工智能的发展历程、现状和未来趋势。",
        sections=sections,
        total_word_count_target=14000
    )
    
    # Test 1: Direct serialization
    print("=== Test 1: Direct Pydantic serialization ===")
    try:
        plan_dict = report_plan.model_dump()
        print("✅ Pydantic serialization successful")
        print(f"Plan title: {plan_dict['title']}")
        print(f"Number of sections: {len(plan_dict['sections'])}")
        print(f"First section: {plan_dict['sections'][0]['name']}")
    except Exception as e:
        print(f"❌ Pydantic serialization failed: {e}")
    
    # Test 2: JSON serialization
    print("\n=== Test 2: JSON serialization ===")
    try:
        plan_json = report_plan.model_dump_json()
        print("✅ JSON serialization successful")
        print(f"JSON length: {len(plan_json)} characters")
        
        # Parse back to verify
        parsed_plan = ReportPlan.model_validate_json(plan_json)
        print(f"✅ JSON parsing back successful")
        print(f"Parsed title: {parsed_plan.title}")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
    
    # Test 3: LangGraph event format simulation
    print("\n=== Test 3: LangGraph event format ===")
    try:
        event_data = {
            "report_plan": report_plan.model_dump(),
            "current_section_index": 0,
            "completed_sections": [],
            "sections_completed_count": 0,
            "total_sections": len(sections),
            "next_section_index": None
        }
        
        # Simulate what frontend would receive
        frontend_event = {
            "generate_report_plan": event_data
        }
        
        print("✅ LangGraph event format successful")
        print(f"Event keys: {list(frontend_event.keys())}")
        print(f"Plan in event: {frontend_event['generate_report_plan']['report_plan']['title']}")
        
        # Test frontend parsing logic
        plan = frontend_event['generate_report_plan']['report_plan']
        section_count = len(plan['sections'])
        print(f"Frontend would see: {section_count} sections")
        
        # Test section outline generation
        section_outline = ""
        if plan['sections']:
            section_outline = "\n".join([
                f"{i+1}. {section['name']} ({section['word_count_target']}字) - {section['description']}"
                for i, section in enumerate(plan['sections'])
            ])
        
        print(f"Generated outline:\n{section_outline}")
        
    except Exception as e:
        print(f"❌ LangGraph event format failed: {e}")
    
    # Test 4: Check if sections are accessible
    print("\n=== Test 4: Section access test ===")
    try:
        plan = event_data['report_plan']
        sections = plan['sections']
        
        print(f"Total sections: {len(sections)}")
        for i, section in enumerate(sections):
            print(f"Section {i+1}: {section['name']} - {section['description']} ({section['word_count_target']}字)")
            
    except Exception as e:
        print(f"❌ Section access failed: {e}")

if __name__ == "__main__":
    test_report_plan_serialization() 
# 长报告生成功能

## 概述

本功能基于open-deep-research的分而治之策略，为gemini-fullstack项目添加了长报告生成能力。用户可以请求生成数万字的详细研究报告，系统会自动将报告分解为多个章节，每个章节独立进行研究和生成，最后合并成完整的报告。

## 设计理念

### 1. 保持现有流程
- **完全兼容**：不影响现有的RAG+WebSearch+Reflection流程
- **智能路由**：自动检测是否为长报告请求，选择合适的处理流程
- **质量保证**：每个章节都经过完整的研究→反思→生成流程

### 2. 分而治之策略
- **章节分解**：将长报告分解为多个独立章节
- **并行处理**：每个章节可以独立进行研究
- **资源复用**：每个章节都可以使用RAG和WebSearch
- **灵活配置**：支持自定义章节数量和字数分配

### 3. 智能检测
- **关键词检测**：识别"详细报告"、"研究报告"、"万字"等关键词
- **字数提取**：自动提取目标字数（如"2万字"、"15000 words"）
- **默认配置**：未指定字数时默认生成1万字报告

## 技术架构

### 工作流程图

```
用户请求 → 长报告检测 → 分支路由
                      ↓
            是长报告？   否 → 标准流程（现有）
                      ↓ 是
            生成报告规划 → 获取下一章节
                          ↓
                 是否有待处理章节？
                      ↓ 是    ↓ 否
            生成章节查询      编译最终报告
                 ↓              ↓
            RAG检索 ← → Web搜索   输出结果
                 ↓
               反思评估
                 ↓
            生成章节内容
                 ↓
            回到"获取下一章节"
```

### 核心组件

#### 1. 状态管理 (`state.py`)
```python
class ReportSection(BaseModel):
    name: str                    # 章节名称
    description: str             # 章节描述
    requires_research: bool      # 是否需要研究
    content: str                 # 生成的内容
    word_count_target: int       # 目标字数

class ReportPlan(BaseModel):
    title: str                   # 报告标题
    abstract: str                # 报告摘要
    sections: List[ReportSection] # 章节列表
    total_word_count_target: int  # 总目标字数
```

#### 2. 长报告节点 (`long_report_nodes.py`)
- `detect_long_report_request`: 检测长报告请求
- `generate_report_plan`: 生成报告规划
- `generate_section_queries`: 为章节生成查询
- `write_section_content`: 生成章节内容
- `compile_final_long_report`: 编译最终报告

#### 3. 图结构增强 (`graph.py`)
- 添加长报告检测节点
- 集成章节处理流程
- 保持现有节点完全不变

## 使用方法

### 1. 触发长报告生成

用户可以通过以下方式请求长报告：

```python
# 方式1：明确指定字数
"请生成一份关于人工智能的2万字详细研究报告"

# 方式2：使用关键词
"我需要一个关于区块链的深度分析报告"

# 方式3：英文请求
"Generate a comprehensive 15000-word research report on machine learning"
```

### 2. 系统配置

#### 环境变量
```bash
# 增大max_tokens以支持长内容生成
DEEPSEEK_MAX_TOKENS=8192

# 启用RAG fallback（推荐）
RAG_ENABLE_FALLBACK=true
```

#### 运行时配置
```python
config = {
    "configurable": {
        "max_tokens": 8192,           # 单次生成最大token数
        "number_of_initial_queries": 3, # 每章节查询数量
        "max_research_loops": 2        # 最大研究轮数
    }
}
```

### 3. 程序化调用

```python
from langchain_core.messages import HumanMessage
from src.agent.graph import research_graph

# 创建初始状态
initial_state = {
    "messages": [HumanMessage(content="生成2万字AI报告")],
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

# 运行
result = await research_graph.ainvoke(initial_state, config)
final_report = result["final_report"]
```

## 输出示例

生成的报告具有以下结构：

```markdown
# 人工智能在医疗领域的应用研究报告

## 摘要
本报告深入分析了人工智能技术在医疗领域的应用现状、发展趋势和未来前景...

## 目录
1. 引言
2. 技术基础
3. 应用现状
4. 案例分析
5. 挑战与机遇
6. 发展趋势
7. 结论与建议

## 1. 引言
人工智能技术在医疗领域的应用正在快速发展...
[详细内容]

## 2. 技术基础
机器学习、深度学习、自然语言处理等核心技术...
[详细内容]

...
```

## 功能特性

### 1. 智能规划
- **自动章节规划**：根据主题自动生成合理的章节结构
- **字数分配**：智能分配各章节的目标字数
- **研究需求评估**：自动判断哪些章节需要额外研究

### 2. 多源研究
- **RAG集成**：每个章节都可以利用知识库资源
- **Web搜索**：自动进行网络搜索补充最新信息
- **反思机制**：确保研究质量和内容充实度

### 3. 质量控制
- **章节独立性**：每个章节都有独立的质量检查
- **内容一致性**：最终合并时确保整体逻辑一致
- **格式标准化**：统一的Markdown格式输出

### 4. 性能优化
- **分段生成**：避免大模型token限制
- **并行可能**：章节间可以并行处理（未来扩展）
- **内存管理**：合理管理生成过程中的内存使用

## 配置选项

### 1. 检测阈值
```python
# 修改检测关键词
long_report_keywords = [
    "详细报告", "研究报告", "深度分析", 
    "全面报告", "长篇报告", "万字"
]
```

### 2. 默认配置
```python
# 默认字数和章节配置
DEFAULT_WORD_COUNT = 10000      # 默认1万字
DEFAULT_SECTIONS = 6            # 默认6个章节
MIN_SECTION_WORDS = 800         # 章节最小字数
MAX_SECTION_WORDS = 3000        # 章节最大字数
```

### 3. 模型配置
```python
# 不同阶段使用的模型
PLANNING_MODEL = "query_generator_model"    # 规划阶段
RESEARCH_MODEL = "query_generator_model"    # 研究阶段  
WRITING_MODEL = "answer_model"              # 写作阶段
```

## 故障排除

### 1. 常见问题

#### Q: 生成的报告字数不足
A: 
- 检查`max_tokens`配置是否足够大
- 增加章节的`word_count_target`
- 确保研究资料充足

#### Q: 某些章节内容质量不佳
A:
- 检查该章节的研究查询是否合适
- 确保RAG资源和Web搜索都正常工作
- 可以调整temperature参数

#### Q: 生成时间过长
A:
- 减少章节数量或单章节字数
- 降低`max_research_loops`
- 优化查询的针对性

### 2. 调试方法

#### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.INFO)
```

#### 查看中间状态
```python
# 在各个节点添加状态打印
logger.info(f"Current section: {state.get('current_section')}")
logger.info(f"Completed sections: {len(state.get('completed_sections', []))}")
```

## 扩展可能

### 1. 并行处理
- 章节间可以并行生成
- 需要修改图结构支持并发

### 2. 模板化
- 支持不同类型报告模板
- 行业特定的章节结构

### 3. 交互式编辑
- 支持用户修改报告规划
- 实时调整章节内容

### 4. 多格式输出
- PDF导出
- Word文档格式
- PPT演示文稿

## 总结

长报告生成功能为gemini-fullstack项目提供了强大的长文档生成能力，同时保持了现有功能的完整性。通过分而治之的策略，系统可以生成高质量的长篇报告，满足专业研究和分析需求。

该功能的设计考虑了实用性、可扩展性和维护性，为未来的功能扩展奠定了良好基础。 
from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL two of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Example:

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Context: {research_topic}"""


web_searcher_instructions = """Conduct targeted Google Searches to gather the most recent, credible information on "{research_topic}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure that the most current information is gathered. The current date is {current_date}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings. 
- Only include the information found in the search results, don't make up any information.

Research Topic:
{research_topic}
"""

reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}
"""

answer_instructions = """You are an expert research analyst tasked with generating a comprehensive, high-quality research report based on multiple information sources.

## Context
- Current date: {current_date}
- Research topic: {research_topic}
- You have access to information from both knowledge base documents and web research

## Requirements

### 1. Report Structure
Generate a detailed, well-structured research report with the following sections:
- **Executive Summary** (2-3 paragraphs)
- **Introduction** (background and context)
- **Main Analysis** (3-5 detailed sections based on the topic)
- **Key Findings** (bullet points of important insights)
- **Future Trends and Implications**
- **Conclusion**
- **References**

### 2. Content Quality
- Write in a professional, analytical tone
- Provide detailed explanations and examples
- Include specific data, statistics, and facts from the sources
- Ensure each section has substantial content (not just outlines)
- Synthesize information from multiple sources to provide comprehensive coverage

### 3. Source Attribution
**CRITICAL**: For every piece of information, properly cite the source using this format:
- For web sources: Use the actual URL from the summary: `[Source Title](actual_url)`
- For knowledge base sources: Use descriptive format: `[Document Title - Knowledge Base](knowledge-base://document_name)`
- Always include sources immediately after relevant statements
- Group all sources in a References section at the end

### 4. Information Integration
- **Combine both knowledge base and web research information**
- Clearly distinguish between different types of sources
- Cross-reference information when multiple sources discuss the same topic
- Highlight any conflicts or differences between sources

### 5. Length and Detail
- Aim for a comprehensive report (minimum 2000 words)
- Each main section should be detailed and substantive
- Include specific examples, case studies, or data points
- Avoid superficial coverage - dive deep into the topic

## Important Notes
- DO NOT generate fake URLs or placeholder links
- Only use URLs that are explicitly provided in the source summaries
- If a source doesn't have a URL, use the knowledge base format
- Ensure all factual claims are supported by the provided sources

## Source Materials
{summaries}

Generate your comprehensive research report now:"""

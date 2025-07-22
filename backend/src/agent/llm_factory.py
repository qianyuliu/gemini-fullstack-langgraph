"""LLM Factory for supporting multiple model providers."""

import os
from typing import Optional
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI


class LLMFactory:
    """Factory class for creating LLM instances based on provider and model name."""
    
    @staticmethod
    def create_llm(
        model_name: str, 
        temperature: float = 0.7, 
        max_retries: int = 2,
        **kwargs
    ) -> BaseLanguageModel:
        """Create an LLM instance based on the model name.
        
        Args:
            model_name: The name of the model (e.g., 'deepseek-chat', 'glm-4', 'gpt-4')
            temperature: Temperature for generation
            max_retries: Maximum number of retries
            **kwargs: Additional arguments
            
        Returns:
            LLM instance
        """
        # DeepSeek models
        if model_name.startswith("deepseek"):
            return LLMFactory._create_deepseek_llm(model_name, temperature, max_retries, **kwargs)
        
        # 智谱AI models
        elif model_name.startswith("glm"):
            return LLMFactory._create_zhipu_llm(model_name, temperature, max_retries, **kwargs)
        
        # 阿里千问 models
        elif model_name.startswith("qwen"):
            return LLMFactory._create_qwen_llm(model_name, temperature, max_retries, **kwargs)
        
        # OpenAI models (including compatible APIs)
        elif model_name.startswith(("gpt", "claude")):
            return LLMFactory._create_openai_llm(model_name, temperature, max_retries, **kwargs)
        
        # Default to OpenAI-compatible
        else:
            return LLMFactory._create_openai_compatible_llm(model_name, temperature, max_retries, **kwargs)
    
    @staticmethod
    def _create_deepseek_llm(model_name: str, temperature: float, max_retries: int, **kwargs) -> ChatOpenAI:
        """Create DeepSeek LLM instance.
        
        DeepSeek 官方文档：
        - deepseek-chat 模型指向 DeepSeek-V3-0324
        - deepseek-reasoner 模型指向 DeepSeek-R1-0528
        - 支持 OpenAI 兼容模式：https://api.deepseek.com/v1
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required for DeepSeek models")
        
        # 支持自定义 base_url，默认为官方 API
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_retries=max_retries,
            **kwargs
        )
    
    @staticmethod
    def _create_zhipu_llm(model_name: str, temperature: float, max_retries: int, **kwargs) -> ChatZhipuAI:
        """Create 智谱AI LLM instance."""
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required for ZhipuAI models")
        
        return ChatZhipuAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_retries=max_retries,
            **kwargs
        )
    
    @staticmethod
    def _create_qwen_llm(model_name: str, temperature: float, max_retries: int, **kwargs) -> ChatOpenAI:
        """Create 阿里千问 LLM instance."""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise ValueError("QWEN_API_KEY environment variable is required for Qwen models")
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=temperature,
            max_retries=max_retries,
            **kwargs
        )
    
    @staticmethod
    def _create_openai_llm(model_name: str, temperature: float, max_retries: int, **kwargs) -> ChatOpenAI:
        """Create OpenAI LLM instance."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI models")
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_retries=max_retries,
            **kwargs
        )
    
    @staticmethod
    def _create_openai_compatible_llm(model_name: str, temperature: float, max_retries: int, **kwargs) -> ChatOpenAI:
        """Create OpenAI-compatible LLM instance."""
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required")
        if not base_url:
            raise ValueError("LLM_BASE_URL environment variable is required")
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_retries=max_retries,
            **kwargs
        )


def get_available_models():
    """Get list of available models based on configured API keys."""
    models = []
    
    # Check DeepSeek
    if os.getenv("DEEPSEEK_API_KEY"):
        models.extend([
            {"id": "deepseek-chat", "name": "DeepSeek Chat (V3-0324)", "provider": "deepseek"},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner (R1-0528)", "provider": "deepseek"},
        ])
    
    # Check 智谱AI
    if os.getenv("ZHIPUAI_API_KEY"):
        models.extend([
            {"id": "glm-4", "name": "GLM-4", "provider": "zhipuai"},
            {"id": "glm-4v", "name": "GLM-4V", "provider": "zhipuai"},
            {"id": "glm-4-flash", "name": "GLM-4 Flash", "provider": "zhipuai"},
        ])
    
    # Check 阿里千问
    if os.getenv("QWEN_API_KEY"):
        models.extend([
            {"id": "qwen-turbo", "name": "Qwen Turbo", "provider": "qwen"},
            {"id": "qwen-plus", "name": "Qwen Plus", "provider": "qwen"},
            {"id": "qwen-max", "name": "Qwen Max", "provider": "qwen"},
            {"id": "qwen-max-longcontext", "name": "Qwen Max Long Context", "provider": "qwen"},
        ])
    
    # Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        models.extend([
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "openai"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
        ])
    
    # Check OpenAI-compatible
    if os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL"):
        model_name = os.getenv("LLM_MODEL_NAME", "custom-model")
        models.append({
            "id": model_name, 
            "name": f"Custom Model ({model_name})", 
            "provider": "custom"
        })
    
    return models 
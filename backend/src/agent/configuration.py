import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


def get_default_model():
    """Get the default model based on available API keys."""
    # Check for DeepSeek
    if os.getenv("DEEPSEEK_API_KEY"):
        return "deepseek-chat"
    # Check for 智谱AI
    elif os.getenv("ZHIPUAI_API_KEY"):
        return "glm-4"
    # Check for 阿里千问
    elif os.getenv("QWEN_API_KEY"):
        return "qwen-turbo"
    # Check for OpenAI
    elif os.getenv("OPENAI_API_KEY"):
        return "gpt-4"
    # Check for custom model
    elif os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL"):
        return os.getenv("LLM_MODEL_NAME", "custom-model")
    else:
        return "deepseek-chat"  # Default fallback


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default_factory=get_default_model,
        description="The name of the language model to use for the agent's query generation."
    )

    reflection_model: str = Field(
        default_factory=get_default_model,
        description="The name of the language model to use for the agent's reflection."
    )

    answer_model: str = Field(
        default_factory=get_default_model,
        description="The name of the language model to use for the agent's answer."
    )

    number_of_initial_queries: int = Field(
        default=3,
        description="The number of initial search queries to generate."
    )

    max_research_loops: int = Field(
        default=2,
        description="The maximum number of research loops to perform."
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)

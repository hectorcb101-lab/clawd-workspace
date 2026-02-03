"""
Atlas OS LLM Abstraction Layer

Model-agnostic interface for language model backends.
"""

from .interface import (
    LLMInterface,
    Message,
    Role,
    GenerateConfig,
    GenerateResult,
    EmbedResult,
    LLMError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
)

from .ollama import OllamaAdapter
from .openai_compat import OpenAICompatAdapter

from .factory import (
    create_adapter,
    get_llm,
    get_default_llm,
    set_default_llm,
    load_config,
    save_config,
    get_default_config,
)

__all__ = [
    # Interface
    "LLMInterface",
    "Message",
    "Role",
    "GenerateConfig",
    "GenerateResult",
    "EmbedResult",
    # Errors
    "LLMError",
    "RateLimitError", 
    "AuthenticationError",
    "ModelNotFoundError",
    # Adapters
    "OllamaAdapter",
    "OpenAICompatAdapter",
    # Factory
    "create_adapter",
    "get_llm",
    "get_default_llm",
    "set_default_llm",
    "load_config",
    "save_config",
    "get_default_config",
]

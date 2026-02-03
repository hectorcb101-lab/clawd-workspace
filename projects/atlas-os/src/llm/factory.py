"""
Atlas OS LLM Factory

Create LLM adapters from configuration.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .interface import LLMInterface, LLMError
from .ollama import OllamaAdapter
from .openai_compat import OpenAICompatAdapter


# Default config path
CONFIG_PATH = Path.home() / "clawd" / "projects" / "atlas-os" / "config" / "llm.json"


def get_default_config() -> Dict[str, Any]:
    """Get default LLM configuration."""
    return {
        "default_provider": "ollama",
        "default_model": "llama3.2",
        
        "providers": {
            "ollama": {
                "base_url": "http://localhost:11434",
                "default_model": "llama3.2",
                "embed_model": "nomic-embed-text",
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4o-mini",
                "embed_model": "text-embedding-3-small",
                "api_key_env": "OPENAI_API_KEY",
            },
            "together": {
                "base_url": "https://api.together.xyz/v1",
                "default_model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "embed_model": "togethercomputer/m2-bert-80M-8k-retrieval",
                "api_key_env": "TOGETHER_API_KEY",
            },
            "local_vllm": {
                "base_url": "http://localhost:8000/v1",
                "default_model": "Qwen/Qwen2.5-7B-Instruct",
            },
        }
    }


def load_config() -> Dict[str, Any]:
    """Load LLM configuration from file or use defaults."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return get_default_config()


def save_config(config: Dict[str, Any]) -> None:
    """Save LLM configuration to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def create_adapter(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> LLMInterface:
    """
    Create an LLM adapter from configuration.
    
    Args:
        provider: Provider name (ollama, openai, together, local_vllm)
        model: Model name (overrides provider default)
        config: Custom config (overrides loaded config)
        **kwargs: Additional arguments passed to adapter
    
    Returns:
        LLMInterface adapter ready to use
    
    Examples:
        # Use defaults
        llm = create_adapter()
        
        # Specific provider and model
        llm = create_adapter("ollama", "qwen2.5:7b")
        
        # OpenAI with custom model
        llm = create_adapter("openai", "gpt-4o")
        
        # Local vLLM server
        llm = create_adapter("local_vllm", "Qwen/Qwen2.5-7B-Instruct")
    """
    cfg = config or load_config()
    
    # Determine provider
    provider = provider or cfg.get("default_provider", "ollama")
    
    if provider not in cfg.get("providers", {}):
        raise LLMError(f"Unknown provider: {provider}")
    
    provider_cfg = cfg["providers"][provider]
    
    # Determine model
    model = model or provider_cfg.get("default_model", cfg.get("default_model"))
    
    # Get base URL
    base_url = kwargs.pop("base_url", None) or provider_cfg.get("base_url")
    
    # Get API key from environment if specified
    api_key = kwargs.pop("api_key", None)
    if not api_key and "api_key_env" in provider_cfg:
        api_key = os.getenv(provider_cfg["api_key_env"])
    
    # Get embed model
    embed_model = kwargs.pop("embed_model", None) or provider_cfg.get("embed_model")
    
    # Create appropriate adapter
    if provider == "ollama":
        return OllamaAdapter(
            model=model,
            base_url=base_url,
            embed_model=embed_model,
            **kwargs
        )
    else:
        # All other providers use OpenAI-compatible adapter
        return OpenAICompatAdapter(
            model=model,
            api_key=api_key,
            base_url=base_url,
            embed_model=embed_model,
            **kwargs
        )


# Convenience function
def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> LLMInterface:
    """Shorthand for create_adapter."""
    return create_adapter(provider, model, **kwargs)


# Global default instance (lazy loaded)
_default_llm: Optional[LLMInterface] = None


def get_default_llm() -> LLMInterface:
    """Get the default LLM instance."""
    global _default_llm
    if _default_llm is None:
        _default_llm = create_adapter()
    return _default_llm


def set_default_llm(llm: LLMInterface) -> None:
    """Set the default LLM instance."""
    global _default_llm
    _default_llm = llm


if __name__ == "__main__":
    # Test factory
    print("Testing LLM Factory...\n")
    
    config = get_default_config()
    print("Default config:")
    print(json.dumps(config, indent=2))
    
    print("\nAvailable providers:", list(config["providers"].keys()))

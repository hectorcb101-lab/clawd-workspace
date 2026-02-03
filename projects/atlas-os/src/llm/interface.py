"""
Atlas OS LLM Interface

Abstract interface for language model backends.
Allows swapping between Claude, local models, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Iterator
from enum import Enum


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """A single message in a conversation."""
    role: Role
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> dict:
        d = {"role": self.role.value, "content": self.content}
        if self.name:
            d["name"] = self.name
        return d
    
    @classmethod
    def system(cls, content: str) -> 'Message':
        return cls(Role.SYSTEM, content)
    
    @classmethod
    def user(cls, content: str) -> 'Message':
        return cls(Role.USER, content)
    
    @classmethod
    def assistant(cls, content: str) -> 'Message':
        return cls(Role.ASSISTANT, content)


@dataclass
class GenerateConfig:
    """Configuration for text generation."""
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    stop_sequences: List[str] = field(default_factory=list)
    stream: bool = False
    
    # Model-specific overrides
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class GenerateResult:
    """Result from text generation."""
    content: str
    model: str
    finish_reason: str = "stop"
    usage: Optional[Dict[str, int]] = None
    
    # For streaming
    is_partial: bool = False


@dataclass
class EmbedResult:
    """Result from text embedding."""
    embedding: List[float]
    model: str
    dimensions: int


class LLMInterface(ABC):
    """
    Abstract interface for LLM backends.
    
    Implementations:
    - ClaudeAdapter: Anthropic Claude API
    - OllamaAdapter: Local models via Ollama
    - OpenAIAdapter: OpenAI API (compatible endpoints)
    - VLLMAdapter: vLLM server
    """
    
    @property
    @abstractmethod
    def model_id(self) -> str:
        """Return the model identifier."""
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        config: Optional[GenerateConfig] = None,
    ) -> GenerateResult:
        """
        Generate a response from the model.
        
        Args:
            messages: List of messages (system, user, assistant)
            config: Generation configuration
        
        Returns:
            GenerateResult with the response
        """
        pass
    
    @abstractmethod
    def generate_stream(
        self,
        messages: List[Message],
        config: Optional[GenerateConfig] = None,
    ) -> Iterator[GenerateResult]:
        """
        Generate a streaming response.
        
        Yields:
            GenerateResult chunks (is_partial=True until final)
        """
        pass
    
    @abstractmethod
    def embed(self, text: str) -> EmbedResult:
        """
        Generate an embedding for text.
        
        Args:
            text: Text to embed
        
        Returns:
            EmbedResult with the embedding vector
        """
        pass
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate).
        Override for accurate counting with specific tokenizers.
        """
        # Rough approximation: ~4 chars per token
        return len(text) // 4
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "model_id": self.model_id,
            "provider": self.provider,
        }
    
    def health_check(self) -> bool:
        """Check if the model is available."""
        try:
            result = self.generate([Message.user("hi")], GenerateConfig(max_tokens=5))
            return bool(result.content)
        except Exception:
            return False


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class RateLimitError(LLMError):
    """Rate limit exceeded."""
    pass


class AuthenticationError(LLMError):
    """Authentication failed."""
    pass


class ModelNotFoundError(LLMError):
    """Model not available."""
    pass

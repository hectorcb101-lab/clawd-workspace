"""
OpenAI-Compatible Adapter for Atlas OS

Works with:
- OpenAI API
- vLLM server
- LM Studio
- LocalAI
- Together.ai
- Any OpenAI-compatible endpoint
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional, List, Iterator, Dict, Any

from .interface import (
    LLMInterface, Message, GenerateConfig, GenerateResult, EmbedResult,
    LLMError, RateLimitError, AuthenticationError, ModelNotFoundError
)


class OpenAICompatAdapter(LLMInterface):
    """
    Adapter for OpenAI-compatible APIs.
    
    Usage:
        # OpenAI
        adapter = OpenAICompatAdapter("gpt-4", api_key="sk-...")
        
        # Local vLLM server
        adapter = OpenAICompatAdapter(
            "Qwen/Qwen2.5-7B-Instruct",
            base_url="http://localhost:8000/v1"
        )
        
        # Together.ai
        adapter = OpenAICompatAdapter(
            "meta-llama/Llama-3-70b-chat-hf",
            base_url="https://api.together.xyz/v1",
            api_key=os.getenv("TOGETHER_API_KEY")
        )
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        embed_model: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._base_url = base_url.rstrip("/")
        self._embed_model = embed_model or "text-embedding-3-small"
        self._organization = organization
    
    @property
    def model_id(self) -> str:
        return self._model
    
    @property
    def provider(self) -> str:
        if "openai.com" in self._base_url:
            return "openai"
        elif "together" in self._base_url:
            return "together"
        elif "localhost" in self._base_url or "127.0.0.1" in self._base_url:
            return "local"
        else:
            return "openai-compat"
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        if self._organization:
            headers["OpenAI-Organization"] = self._organization
        return headers
    
    def _request(self, endpoint: str, data: dict) -> dict:
        """Make a request to the API."""
        url = f"{self._base_url}{endpoint}"
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=self._headers(),
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            if e.code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.code == 404:
                raise ModelNotFoundError(f"Model not found: {self._model}")
            elif e.code == 429:
                raise RateLimitError("Rate limit exceeded")
            raise LLMError(f"API error {e.code}: {body}")
        except urllib.error.URLError as e:
            raise LLMError(f"Cannot connect to {self._base_url}: {e.reason}")
    
    def _request_stream(self, endpoint: str, data: dict) -> Iterator[dict]:
        """Make a streaming request."""
        url = f"{self._base_url}{endpoint}"
        data["stream"] = True
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=self._headers(),
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                for line in resp:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        yield json.loads(data_str)
        except urllib.error.HTTPError as e:
            raise LLMError(f"API error {e.code}")
    
    def generate(
        self,
        messages: List[Message],
        config: Optional[GenerateConfig] = None,
    ) -> GenerateResult:
        """Generate using chat completions endpoint."""
        config = config or GenerateConfig()
        
        data = {
            "model": self._model,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        
        if config.stop_sequences:
            data["stop"] = config.stop_sequences
        
        # Add any extra parameters
        data.update(config.extras)
        
        result = self._request("/chat/completions", data)
        
        choice = result.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = result.get("usage", {})
        
        return GenerateResult(
            content=message.get("content", ""),
            model=result.get("model", self._model),
            finish_reason=choice.get("finish_reason", "stop"),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }
        )
    
    def generate_stream(
        self,
        messages: List[Message],
        config: Optional[GenerateConfig] = None,
    ) -> Iterator[GenerateResult]:
        """Generate streaming response."""
        config = config or GenerateConfig()
        
        data = {
            "model": self._model,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        
        if config.stop_sequences:
            data["stop"] = config.stop_sequences
        
        for chunk in self._request_stream("/chat/completions", data):
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})
            content = delta.get("content", "")
            finish = choice.get("finish_reason")
            
            if content or finish:
                yield GenerateResult(
                    content=content,
                    model=self._model,
                    finish_reason=finish or "",
                    is_partial=finish is None,
                )
    
    def embed(self, text: str) -> EmbedResult:
        """Generate embedding."""
        data = {
            "model": self._embed_model,
            "input": text,
        }
        
        result = self._request("/embeddings", data)
        embedding = result.get("data", [{}])[0].get("embedding", [])
        
        return EmbedResult(
            embedding=embedding,
            model=self._embed_model,
            dimensions=len(embedding),
        )
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            req = urllib.request.Request(
                f"{self._base_url}/models",
                headers=self._headers()
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", [])
        except Exception:
            return []
    
    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info["base_url"] = self._base_url
        info["embed_model"] = self._embed_model
        info["has_api_key"] = bool(self._api_key)
        return info

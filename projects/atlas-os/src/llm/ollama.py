"""
Ollama Adapter for Atlas OS

Connect to local models via Ollama server.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, List, Iterator, Dict, Any

from .interface import (
    LLMInterface, Message, GenerateConfig, GenerateResult, EmbedResult,
    LLMError, ModelNotFoundError
)


class OllamaAdapter(LLMInterface):
    """
    Adapter for Ollama local models.
    
    Requires Ollama to be running: https://ollama.ai
    
    Usage:
        adapter = OllamaAdapter("llama3.2")
        result = adapter.generate([Message.user("Hello!")])
    """
    
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        embed_model: Optional[str] = None,
    ):
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._embed_model = embed_model or model
    
    @property
    def model_id(self) -> str:
        return self._model
    
    @property
    def provider(self) -> str:
        return "ollama"
    
    def _request(self, endpoint: str, data: dict) -> dict:
        """Make a request to Ollama API."""
        url = f"{self._base_url}{endpoint}"
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ModelNotFoundError(f"Model not found: {self._model}")
            raise LLMError(f"Ollama error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise LLMError(f"Cannot connect to Ollama at {self._base_url}: {e.reason}")
    
    def _request_stream(self, endpoint: str, data: dict) -> Iterator[dict]:
        """Make a streaming request to Ollama API."""
        url = f"{self._base_url}{endpoint}"
        data["stream"] = True
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                for line in resp:
                    if line:
                        yield json.loads(line.decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise LLMError(f"Ollama error: {e.code} {e.reason}")
    
    def _messages_to_prompt(self, messages: List[Message]) -> str:
        """Convert messages to a prompt string for older models."""
        parts = []
        for msg in messages:
            if msg.role.value == "system":
                parts.append(f"System: {msg.content}\n")
            elif msg.role.value == "user":
                parts.append(f"Human: {msg.content}\n")
            elif msg.role.value == "assistant":
                parts.append(f"Assistant: {msg.content}\n")
        parts.append("Assistant:")
        return "".join(parts)
    
    def generate(
        self,
        messages: List[Message],
        config: Optional[GenerateConfig] = None,
    ) -> GenerateResult:
        """Generate using Ollama chat endpoint."""
        config = config or GenerateConfig()
        
        # Use chat endpoint for message-based models
        data = {
            "model": self._model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {
                "num_predict": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
        }
        
        if config.stop_sequences:
            data["options"]["stop"] = config.stop_sequences
        
        result = self._request("/api/chat", data)
        
        return GenerateResult(
            content=result.get("message", {}).get("content", ""),
            model=self._model,
            finish_reason=result.get("done_reason", "stop"),
            usage={
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
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
            "options": {
                "num_predict": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
        }
        
        full_content = ""
        for chunk in self._request_stream("/api/chat", data):
            content = chunk.get("message", {}).get("content", "")
            full_content += content
            
            is_done = chunk.get("done", False)
            yield GenerateResult(
                content=content,
                model=self._model,
                finish_reason="stop" if is_done else "",
                is_partial=not is_done,
            )
    
    def embed(self, text: str) -> EmbedResult:
        """Generate embedding using Ollama."""
        data = {
            "model": self._embed_model,
            "prompt": text,
        }
        
        result = self._request("/api/embeddings", data)
        embedding = result.get("embedding", [])
        
        return EmbedResult(
            embedding=embedding,
            model=self._embed_model,
            dimensions=len(embedding),
        )
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            req = urllib.request.Request(f"{self._base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("models", [])
        except Exception:
            return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama library."""
        try:
            self._request("/api/pull", {"name": model})
            return True
        except Exception:
            return False
    
    def health_check(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            req = urllib.request.Request(f"{self._base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                return self._model.split(":")[0] in models or self._model in models
        except Exception:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        info = super().get_info()
        info["base_url"] = self._base_url
        info["embed_model"] = self._embed_model
        return info

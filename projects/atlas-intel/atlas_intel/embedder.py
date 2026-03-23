"""Gemini multimodal embedding module.

Supports text, image, video, audio, and document embedding
via gemini-embedding-2-preview (3072-dim vectors).
"""

from __future__ import annotations

import mimetypes
from enum import Enum
from pathlib import Path
from typing import Union

import numpy as np

from .config import load_gemini_config, GeminiConfig

# Lazy-loaded client
_client = None
_config: GeminiConfig | None = None


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


# Map content types to common MIME prefixes for validation
_MIME_PREFIXES: dict[ContentType, list[str]] = {
    ContentType.IMAGE: ["image/"],
    ContentType.VIDEO: ["video/"],
    ContentType.AUDIO: ["audio/"],
    ContentType.DOCUMENT: ["application/pdf", "text/"],
}


def _get_client():
    """Lazy-init the Gemini client."""
    global _client, _config
    if _client is None:
        import google.generativeai as genai

        _config = load_gemini_config()
        genai.configure(api_key=_config.api_key)
        _client = genai
    return _client


def _make_content(content: Union[str, bytes, Path], content_type: ContentType):
    """Build the appropriate content object for the Gemini API."""
    genai = _get_client()

    if content_type == ContentType.TEXT:
        if isinstance(content, (bytes, Path)):
            content = content if isinstance(content, str) else (
                Path(content).read_text() if isinstance(content, (str, Path)) else content.decode()
            )
        return str(content)

    # For media types, we need to upload or inline the content
    if isinstance(content, (str, Path)):
        path = Path(content)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        data = path.read_bytes()
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    elif isinstance(content, bytes):
        data = content
        # Guess mime from content type
        mime_map = {
            ContentType.IMAGE: "image/png",
            ContentType.VIDEO: "video/mp4",
            ContentType.AUDIO: "audio/mp3",
            ContentType.DOCUMENT: "application/pdf",
        }
        mime = mime_map.get(content_type, "application/octet-stream")
    else:
        raise TypeError(f"Unsupported content type: {type(content)}")

    return {"inline_data": {"mime_type": mime, "data": data}}


def embed(
    content: Union[str, bytes, Path],
    content_type: ContentType | str = ContentType.TEXT,
) -> np.ndarray:
    """Embed a single piece of content. Returns a 3072-dim numpy vector.

    Args:
        content: Text string, file path, or raw bytes.
        content_type: One of text, image, video, audio, document.

    Returns:
        numpy array of shape (3072,).
    """
    genai = _get_client()
    ct = ContentType(content_type)

    try:
        if ct == ContentType.TEXT:
            result = genai.embed_content(
                model=f"models/{_config.model}",
                content=str(content),
            )
        else:
            part = _make_content(content, ct)
            result = genai.embed_content(
                model=f"models/{_config.model}",
                content=[part] if isinstance(part, dict) else part,
            )
        return np.array(result["embedding"], dtype=np.float32)
    except Exception as exc:
        raise RuntimeError(f"Gemini embedding failed for {ct.value}: {exc}") from exc


def embed_batch(
    items: list[tuple[Union[str, bytes, Path], ContentType | str]],
) -> list[np.ndarray]:
    """Embed multiple items. Currently sequential; batch API TBD.

    Args:
        items: List of (content, content_type) tuples.

    Returns:
        List of numpy arrays.
    """
    return [embed(content, ct) for content, ct in items]


def embed_text(text: str) -> np.ndarray:
    """Convenience: embed a text string."""
    return embed(text, ContentType.TEXT)


def embed_file(path: str | Path, content_type: ContentType | str) -> np.ndarray:
    """Convenience: embed a file by path."""
    return embed(Path(path), content_type)

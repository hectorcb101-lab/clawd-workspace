"""atlas-intel: Multimodal intelligence ingestion, embedding, and RAG querying.

Core modules:
    - embedder: Gemini multimodal embedding (text, image, video, audio, documents)
    - store: Supabase pgvector storage and similarity search
    - rag: Cross-modal RAG query engine
    - config: Configuration management
"""

__version__ = "0.1.0"

from . import embedder, store, rag, config

__all__ = ["embedder", "store", "rag", "config"]

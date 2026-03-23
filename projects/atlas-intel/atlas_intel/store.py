"""Supabase vector store interface.

Handles embedding storage, similarity search, signal tracking, and reaction logging.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import numpy as np

from .config import load_supabase_config, SupabaseConfig

_supabase_client = None
_cfg: SupabaseConfig | None = None


def _get_client():
    """Lazy-init Supabase client."""
    global _supabase_client, _cfg
    if _supabase_client is None:
        from supabase import create_client

        _cfg = load_supabase_config()
        if _cfg is None:
            raise RuntimeError(
                "Supabase credentials not found. "
                "Create /home/ubuntu/clawd/config/supabase-atlas-intel.env "
                "with SUPABASE_URL and SUPABASE_KEY."
            )
        _supabase_client = create_client(_cfg.url, _cfg.key)
    return _supabase_client


def _vec_to_list(v: np.ndarray | list[float]) -> list[float]:
    if isinstance(v, np.ndarray):
        return v.tolist()
    return v


def store_embedding(
    source_type: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    embedding: np.ndarray | list[float] | None = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    """Store an embedding in the vector store.

    Args:
        source_type: Type of source (text, image, video, audio, document).
        content: Original content or reference (text, file path, URL).
        metadata: Additional metadata dict.
        embedding: Pre-computed embedding vector. If None, caller must embed first.

    Returns:
        Inserted row data.
    """
    client = _get_client()
    row = {
        "id": str(uuid4()),
        "source_type": source_type,
        "content_text": content,
        "metadata": json.dumps(metadata or {}),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if source_id:
        row["source_id"] = source_id
    if embedding is not None:
        row["embedding"] = _vec_to_list(embedding)

    try:
        result = client.table(_cfg.embeddings_table).insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as exc:
        raise RuntimeError(f"Failed to store embedding: {exc}") from exc


def query_similar(
    query_embedding: np.ndarray | list[float],
    top_k: int = 10,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Find similar embeddings via pgvector cosine similarity.

    Uses an RPC function `match_embeddings` expected in Supabase:
    ```sql
    create function match_embeddings(
      query_embedding vector(3072),
      match_count int default 10,
      filter_source_type text default null
    ) returns table (id uuid, content text, source_type text, metadata jsonb, similarity float)
    ```

    Args:
        query_embedding: Query vector.
        top_k: Number of results.
        filters: Optional filters (source_type, time_range, etc.).

    Returns:
        List of matching rows with similarity scores.
    """
    client = _get_client()
    params: dict[str, Any] = {
        "query_embedding": _vec_to_list(query_embedding),
        "match_count": top_k,
    }
    if filters:
        if "source_type" in filters:
            params["filter_source_type"] = filters["source_type"]

    try:
        result = client.rpc("match_embeddings", params).execute()
        return result.data or []
    except Exception as exc:
        raise RuntimeError(f"Similarity search failed: {exc}") from exc


def store_signal(
    phrase: str,
    context: str,
    speaker: str,
    event_type: str,
    sentiment: float | None = None,
    embedding_id: str | None = None,
) -> dict[str, Any]:
    """Store a market/intel signal.

    Args:
        phrase: The signal phrase (e.g. "rates will stay higher for longer").
        context: Source context (transcript, article, etc.).
        speaker: Who said it.
        event_type: Category (fed_speech, earnings_call, news, etc.).
        sentiment: Sentiment score (-1 to 1).
        embedding_id: Link to the embedding row if available.

    Returns:
        Inserted row.
    """
    client = _get_client()
    row = {
        "id": str(uuid4()),
        "phrase": phrase,
        "context": context,
        "speaker": speaker,
        "event_type": event_type,
        "sentiment": sentiment,
        "embedding_id": embedding_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = client.table(_cfg.signals_table).insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as exc:
        raise RuntimeError(f"Failed to store signal: {exc}") from exc


def store_reaction(
    signal_id: str,
    asset: str,
    price_before: float,
    price_after: float,
    timeframe: str,
) -> dict[str, Any]:
    """Store a market reaction to a signal.

    Args:
        signal_id: UUID of the related signal.
        asset: Asset ticker (BTC, ETH, SPY, etc.).
        price_before: Price before signal.
        price_after: Price after signal.
        timeframe: Measurement window (1h, 4h, 24h, etc.).

    Returns:
        Inserted row.
    """
    client = _get_client()
    row = {
        "id": str(uuid4()),
        "signal_id": signal_id,
        "asset": asset,
        "price_before": price_before,
        "price_after": price_after,
        "price_change_pct": ((price_after - price_before) / price_before) * 100 if price_before else 0,
        "timeframe": timeframe,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = client.table(_cfg.reactions_table).insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as exc:
        raise RuntimeError(f"Failed to store reaction: {exc}") from exc

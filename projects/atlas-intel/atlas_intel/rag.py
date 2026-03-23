"""RAG query engine for atlas-intel.

Cross-modal retrieval: text queries can surface video/image/audio results
and vice versa, thanks to Gemini's unified embedding space.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Union

import numpy as np

from .embedder import embed, ContentType
from .store import query_similar, _get_client, _cfg


def query(
    text_or_media: Union[str, bytes, Path],
    top_k: int = 10,
    source_types: list[str] | None = None,
    time_range: tuple[datetime, datetime] | None = None,
    content_type: ContentType | str = ContentType.TEXT,
) -> list[dict[str, Any]]:
    """Query the knowledge base with text or media.

    Embeds the query via Gemini, then searches pgvector for similar content
    across all modalities.

    Args:
        text_or_media: Query text, file path, or bytes.
        top_k: Max results to return.
        source_types: Filter by source type(s) e.g. ["text", "video"].
        time_range: (start, end) datetime tuple to filter by.
        content_type: Content type of the query input.

    Returns:
        List of results with content, metadata, and similarity scores.
    """
    query_embedding = embed(text_or_media, content_type)

    filters: dict[str, Any] = {}
    if source_types and len(source_types) == 1:
        filters["source_type"] = source_types[0]

    results = query_similar(query_embedding, top_k=top_k, filters=filters)

    # Client-side filtering for multiple source types or time range
    if source_types and len(source_types) > 1:
        results = [r for r in results if r.get("source_type") in source_types]

    if time_range:
        start, end = time_range
        results = [
            r for r in results
            if _in_time_range(r.get("created_at", ""), start, end)
        ]

    return results


def _in_time_range(ts: str, start: datetime, end: datetime) -> bool:
    """Check if a timestamp string falls within a range."""
    if not ts:
        return False
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return start <= dt <= end
    except (ValueError, TypeError):
        return False


def find_related_signals(embedding_id: str, top_k: int = 10) -> list[dict[str, Any]]:
    """Find signal phrases near a given embedding.

    Retrieves the embedding vector for the given ID, then searches the
    signals table for nearby entries.

    Args:
        embedding_id: UUID of the source embedding.
        top_k: Number of related signals to return.

    Returns:
        List of related signal rows.
    """
    client = _get_client()

    try:
        # Get the embedding vector
        result = (
            client.table(_cfg.embeddings_table)
            .select("embedding")
            .eq("id", embedding_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return []

        vec = result.data[0].get("embedding")
        if vec is None:
            return []

        # Search for related signals via RPC
        related = client.rpc("match_signals", {
            "query_embedding": vec if isinstance(vec, list) else list(vec),
            "match_count": top_k,
        }).execute()

        return related.data or []
    except Exception as exc:
        raise RuntimeError(f"Failed to find related signals: {exc}") from exc


def get_context_for_briefing(
    topic: str,
    top_k: int = 15,
    lookback_hours: int = 24,
) -> dict[str, Any]:
    """Pull relevant multi-modal context for a daily briefing.

    Args:
        topic: Briefing topic (e.g. "crypto markets", "fed policy").
        top_k: Max items per category.
        lookback_hours: How far back to search.

    Returns:
        Dict with keys: topic, results, signals, time_range, summary_stats.
    """
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=lookback_hours)
    time_range = (start, now)

    # Get relevant embeddings across all modalities
    results = query(topic, top_k=top_k, time_range=time_range)

    # Get related signals
    signals: list[dict[str, Any]] = []
    for r in results[:5]:  # Check top 5 results for linked signals
        rid = r.get("id")
        if rid:
            try:
                related = find_related_signals(rid, top_k=5)
                signals.extend(related)
            except RuntimeError:
                pass

    # Deduplicate signals by ID
    seen_ids: set[str] = set()
    unique_signals = []
    for s in signals:
        sid = s.get("id", "")
        if sid not in seen_ids:
            seen_ids.add(sid)
            unique_signals.append(s)

    # Summary stats
    source_types = {}
    for r in results:
        st = r.get("source_type", "unknown")
        source_types[st] = source_types.get(st, 0) + 1

    return {
        "topic": topic,
        "results": results,
        "signals": unique_signals,
        "time_range": {
            "start": start.isoformat(),
            "end": now.isoformat(),
        },
        "summary_stats": {
            "total_results": len(results),
            "total_signals": len(unique_signals),
            "source_types": source_types,
        },
    }

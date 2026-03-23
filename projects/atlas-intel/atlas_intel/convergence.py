"""Cross-modal convergence scoring engine.

Finds clusters of related events across different intelligence feeds
by computing cosine similarity on embeddings, with geographic proximity
and temporal decay adjustments.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from math import radians, sin, cos, sqrt, atan2
from typing import Any
from uuid import uuid4

import numpy as np

from .config import load_supabase_config
from .store import store_embedding, query_similar, _get_client, _cfg

logger = logging.getLogger("atlas_intel.convergence")

# Source types we track
SOURCE_TYPES = [
    "ais_vessel", "flight_track", "thermal_anomaly",
    "gdelt_event", "economic_indicator", "x_speech",
]

# Severity thresholds
SEVERITY_LEVELS = {
    2: "LOW",
    3: "MEDIUM",
    4: "HIGH",
    5: "CRITICAL",
}

# Asset impact mappings by source type combinations
ASSET_IMPACT_MAP = {
    "ais_vessel": ["crude_oil", "shipping_etfs", "commodities"],
    "flight_track": ["defense_stocks", "airlines", "vix"],
    "thermal_anomaly": ["energy", "crude_oil", "natural_gas"],
    "gdelt_event": ["vix", "gold", "treasuries", "defense_stocks"],
    "economic_indicator": ["sp500", "bonds", "forex"],
    "x_speech": ["crypto", "meme_stocks", "sentiment_driven"],
}


@dataclass
class ConvergenceSource:
    """A single source contributing to a convergence signal."""
    source_type: str
    source_id: str
    content_text: str
    similarity: float
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class ConvergenceSignal:
    """A detected cross-modal convergence event."""
    id: str = field(default_factory=lambda: str(uuid4()))
    sources: list[ConvergenceSource] = field(default_factory=list)
    similarity_score: float = 0.0
    severity: str = "LOW"
    region: str = "unknown"
    narrative: str = ""
    affected_assets: list[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in km."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _extract_coords(metadata: dict) -> tuple[float, float] | None:
    """Extract lat/lon from metadata if available."""
    lat = metadata.get("lat") or metadata.get("latitude")
    lon = metadata.get("lon") or metadata.get("lng") or metadata.get("longitude")
    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon)
        except (ValueError, TypeError):
            return None
    return None


def _geo_proximity_boost(meta_a: dict, meta_b: dict, max_boost: float = 0.15) -> float:
    """Boost similarity for geographically proximate events (within 500km)."""
    coords_a = _extract_coords(meta_a)
    coords_b = _extract_coords(meta_b)
    if coords_a is None or coords_b is None:
        return 0.0
    dist = _haversine_km(*coords_a, *coords_b)
    if dist > 500:
        return 0.0
    # Linear decay: 0km = max_boost, 500km = 0
    return max_boost * (1.0 - dist / 500.0)


def _temporal_decay(created_at: str, now: datetime | None = None) -> float:
    """Weight factor: 1.0 for now, decays to ~0.3 at 24h. Exponential decay."""
    now = now or datetime.now(timezone.utc)
    try:
        if created_at.endswith("Z"):
            created_at = created_at[:-1] + "+00:00"
        ts = datetime.fromisoformat(created_at)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return 0.5
    hours_ago = (now - ts).total_seconds() / 3600.0
    if hours_ago < 0:
        hours_ago = 0
    # Exponential decay: half-life ~8 hours
    return max(0.1, float(np.exp(-0.087 * hours_ago)))


def _infer_region(sources: list[dict]) -> str:
    """Infer region from source metadata."""
    regions = []
    for s in sources:
        meta = s.get("metadata", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except (json.JSONDecodeError, TypeError):
                meta = {}
        for key in ("region", "country", "location", "area"):
            if key in meta:
                regions.append(str(meta[key]))
                break
        else:
            coords = _extract_coords(meta)
            if coords:
                regions.append(f"{coords[0]:.1f},{coords[1]:.1f}")
    if regions:
        # Most common region
        from collections import Counter
        return Counter(regions).most_common(1)[0][0]
    return "unknown"


def _generate_narrative(sources: list[ConvergenceSource], severity: str, region: str) -> str:
    """Auto-generate a text summary of the convergence signal."""
    type_descriptions = {
        "ais_vessel": "vessel movement anomaly",
        "flight_track": "unusual flight activity",
        "thermal_anomaly": "thermal/infrared anomaly",
        "gdelt_event": "geopolitical event",
        "economic_indicator": "economic indicator shift",
        "x_speech": "social media signal",
    }
    parts = []
    for s in sources:
        desc = type_descriptions.get(s.source_type, s.source_type)
        snippet = s.content_text[:80] if s.content_text else "no detail"
        parts.append(f"{desc} ({snippet})")

    source_count = len(sources)
    return (
        f"{severity} convergence detected across {source_count} feeds "
        f"in region '{region}': " + "; ".join(parts)
    )


def _predict_affected_assets(source_types: list[str]) -> list[str]:
    """Predict which assets might be impacted based on source types involved."""
    assets = set()
    for st in source_types:
        assets.update(ASSET_IMPACT_MAP.get(st, []))
    return sorted(assets)


def _fetch_recent_embeddings(hours: int = 24, limit: int = 500) -> list[dict[str, Any]]:
    """Fetch recent embeddings from Supabase, falling back to direct query."""
    client = _get_client()
    cfg = load_supabase_config()
    table = cfg.embeddings_table if cfg else "embeddings"
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    try:
        result = (
            client.table(table)
            .select("id, source_type, source_id, content_text, embedding, metadata, created_at")
            .gte("created_at", cutoff)
            .in_("source_type", SOURCE_TYPES)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        logger.error("Failed to fetch recent embeddings: %s", exc)
        return []


def _parse_embedding(raw) -> np.ndarray | None:
    """Parse embedding from Supabase row (may be list, string, or None)."""
    if raw is None:
        return None
    if isinstance(raw, list):
        return np.array(raw, dtype=np.float32)
    if isinstance(raw, str):
        try:
            return np.array(json.loads(raw), dtype=np.float32)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def _parse_metadata(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def find_convergence_signals(
    hours: int = 24,
    similarity_threshold: float = 0.7,
    min_sources: int = 2,
) -> list[ConvergenceSignal]:
    """Main entry point: find cross-modal convergence signals.

    1. Fetch recent embeddings across all source types
    2. Compare embeddings across different source types
    3. Cluster events that converge (similarity > threshold)
    4. Score and rank convergence signals

    Returns list of ConvergenceSignal objects.
    """
    logger.info("Scanning for convergence signals (last %dh, threshold=%.2f)", hours, similarity_threshold)
    rows = _fetch_recent_embeddings(hours=hours)
    if not rows:
        logger.info("No recent embeddings found")
        return []

    # Parse embeddings
    entries = []
    for row in rows:
        emb = _parse_embedding(row.get("embedding"))
        if emb is None:
            continue
        meta = _parse_metadata(row.get("metadata"))
        entries.append({
            "id": row.get("id", ""),
            "source_type": row.get("source_type", ""),
            "source_id": row.get("source_id", ""),
            "content_text": row.get("content_text", ""),
            "embedding": emb,
            "metadata": meta,
            "created_at": row.get("created_at", ""),
        })

    logger.info("Loaded %d embeddings with vectors", len(entries))
    if len(entries) < 2:
        return []

    now = datetime.now(timezone.utc)

    # Build cross-modal similarity graph
    # Only compare entries of DIFFERENT source types
    n = len(entries)
    # adjacency: (i, j) -> adjusted similarity
    edges: list[tuple[int, int, float]] = []

    for i in range(n):
        for j in range(i + 1, n):
            if entries[i]["source_type"] == entries[j]["source_type"]:
                continue
            raw_sim = _cosine_similarity(entries[i]["embedding"], entries[j]["embedding"])
            geo_boost = _geo_proximity_boost(entries[i]["metadata"], entries[j]["metadata"])
            # Temporal weighting: average decay of both events
            decay_i = _temporal_decay(entries[i]["created_at"], now)
            decay_j = _temporal_decay(entries[j]["created_at"], now)
            temporal_weight = (decay_i + decay_j) / 2.0

            adjusted_sim = (raw_sim + geo_boost) * temporal_weight
            if adjusted_sim >= similarity_threshold:
                edges.append((i, j, adjusted_sim))

    if not edges:
        logger.info("No cross-modal pairs above threshold")
        return []

    # Greedy clustering: build connected components from edges
    from collections import defaultdict
    adj = defaultdict(set)
    for i, j, _ in edges:
        adj[i].add(j)
        adj[j].add(i)

    visited = set()
    clusters: list[set[int]] = []
    for node in adj:
        if node in visited:
            continue
        # BFS
        cluster = set()
        queue = [node]
        while queue:
            n_id = queue.pop()
            if n_id in visited:
                continue
            visited.add(n_id)
            cluster.add(n_id)
            for neighbor in adj[n_id]:
                if neighbor not in visited:
                    queue.append(neighbor)
        clusters.append(cluster)

    # Convert clusters to ConvergenceSignals
    signals: list[ConvergenceSignal] = []
    edge_sims = {}
    for i, j, s in edges:
        edge_sims[(i, j)] = s
        edge_sims[(j, i)] = s

    for cluster in clusters:
        cluster_entries = [entries[i] for i in cluster]
        source_types_in_cluster = set(e["source_type"] for e in cluster_entries)
        n_types = len(source_types_in_cluster)

        if n_types < min_sources:
            continue

        # Average similarity across edges in this cluster
        cluster_list = sorted(cluster)
        sims = []
        for a_idx in range(len(cluster_list)):
            for b_idx in range(a_idx + 1, len(cluster_list)):
                key = (cluster_list[a_idx], cluster_list[b_idx])
                if key in edge_sims:
                    sims.append(edge_sims[key])
        avg_sim = float(np.mean(sims)) if sims else 0.0

        # Severity
        if n_types >= 5 and avg_sim > 0.8:
            severity = "CRITICAL"
        elif n_types >= 5:
            severity = "CRITICAL"
        elif n_types >= 4:
            severity = "HIGH"
        elif n_types >= 3:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        region = _infer_region(cluster_entries)
        source_type_list = sorted(source_types_in_cluster)

        conv_sources = [
            ConvergenceSource(
                source_type=e["source_type"],
                source_id=e["source_id"],
                content_text=e["content_text"],
                similarity=max(
                    (edge_sims.get((idx, other), 0.0)
                     for other in cluster if other != idx),
                    default=0.0,
                ),
                metadata=e["metadata"],
                created_at=e["created_at"],
            )
            for idx, e in zip(sorted(cluster), cluster_entries)
        ]

        signal = ConvergenceSignal(
            sources=conv_sources,
            similarity_score=round(avg_sim, 4),
            severity=severity,
            region=region,
            affected_assets=_predict_affected_assets(source_type_list),
            confidence=round(min(1.0, avg_sim * (n_types / 6.0)), 4),
        )
        signal.narrative = _generate_narrative(conv_sources, severity, region)
        signals.append(signal)

    # Sort by severity then similarity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    signals.sort(key=lambda s: (severity_order.get(s.severity, 4), -s.similarity_score))

    logger.info("Found %d convergence signals", len(signals))
    return signals


def store_convergence_signal(signal: ConvergenceSignal) -> dict[str, Any] | None:
    """Store a convergence signal back in Supabase as an embedding row."""
    try:
        from .embedder import embed_text
        embedding = embed_text(signal.narrative)
    except Exception as exc:
        logger.warning("Failed to embed convergence narrative: %s", exc)
        embedding = None

    metadata = {
        "convergence_id": signal.id,
        "severity": signal.severity,
        "region": signal.region,
        "source_count": len(signal.sources),
        "source_types": list(set(s.source_type for s in signal.sources)),
        "affected_assets": signal.affected_assets,
        "confidence": signal.confidence,
        "similarity_score": signal.similarity_score,
    }

    try:
        return store_embedding(
            source_type="convergence_signal",
            content=signal.narrative,
            metadata=metadata,
            embedding=embedding,
            source_id=signal.id,
        )
    except Exception as exc:
        logger.error("Failed to store convergence signal: %s", exc)
        return None


def run_convergence_scan(
    hours: int = 24,
    similarity_threshold: float = 0.7,
    store_results: bool = True,
) -> list[ConvergenceSignal]:
    """Run a full convergence scan and optionally store results."""
    signals = find_convergence_signals(
        hours=hours,
        similarity_threshold=similarity_threshold,
    )
    if store_results:
        for signal in signals:
            store_convergence_signal(signal)
    return signals


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signals = run_convergence_scan(store_results=False)
    for s in signals:
        print(f"[{s.severity}] {s.narrative}")
        print(f"  Score: {s.similarity_score} | Confidence: {s.confidence}")
        print(f"  Assets: {s.affected_assets}")
        print()

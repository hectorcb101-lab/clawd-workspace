"""Configuration management for atlas-intel.

Loads API keys and credentials from external config files.
No hardcoded secrets.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values


_GEMINI_SETTINGS_PATH = Path.home() / ".gemini" / "settings.json"
_SUPABASE_ENV_PATH = Path("/home/ubuntu/clawd/config/supabase-atlas-intel.env")

# Gemini embedding model
EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 3072


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str
    model: str = EMBEDDING_MODEL
    embedding_dim: int = EMBEDDING_DIM


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    key: str
    embeddings_table: str = "embeddings"
    signals_table: str = "signals"
    reactions_table: str = "reactions"


@dataclass(frozen=True)
class AtlasIntelConfig:
    gemini: GeminiConfig
    supabase: SupabaseConfig | None


def load_gemini_config(path: Path | None = None) -> GeminiConfig:
    """Load Gemini API key from settings.json."""
    p = path or _GEMINI_SETTINGS_PATH
    try:
        data = json.loads(p.read_text())
        api_key = data.get("apiKey") or data.get("api_key", "")
        if not api_key:
            raise ValueError(f"No API key found in {p}")
        return GeminiConfig(api_key=api_key)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError(f"Failed to load Gemini config from {p}: {exc}") from exc


def load_supabase_config(path: Path | None = None) -> SupabaseConfig | None:
    """Load Supabase credentials from env file. Returns None if file missing."""
    p = path or _SUPABASE_ENV_PATH
    if not p.exists():
        return None
    vals = dotenv_values(str(p))
    url = vals.get("SUPABASE_URL", "")
    key = vals.get("SUPABASE_KEY") or vals.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return None
    return SupabaseConfig(
        url=url,
        key=key,
        embeddings_table=vals.get("EMBEDDINGS_TABLE", "embeddings"),
        signals_table=vals.get("SIGNALS_TABLE", "signals"),
        reactions_table=vals.get("REACTIONS_TABLE", "reactions"),
    )


def load_config() -> AtlasIntelConfig:
    """Load full configuration."""
    return AtlasIntelConfig(
        gemini=load_gemini_config(),
        supabase=load_supabase_config(),
    )

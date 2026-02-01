#!/usr/bin/env python3
"""
Atlas Semantic Search
=====================
Phase 4: Smart retrieval using embeddings.

Instead of keyword matching, we:
1. Embed the query
2. Find facts with similar embeddings
3. Combine with question form matching for best results
"""

import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib

sys.path.insert(0, str(Path(__file__).parent))

from knowledge_graph import KnowledgeGraph, Fact

# Try to import OpenAI for embeddings
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class SearchResult:
    """A search result with score breakdown."""
    fact: Fact
    total_score: float
    semantic_score: float = 0.0
    question_score: float = 0.0
    entity_score: float = 0.0
    recency_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.fact.category,
            'subject': self.fact.subject,
            'content': self.fact.content,
            'total_score': self.total_score,
            'scores': {
                'semantic': self.semantic_score,
                'question': self.question_score,
                'entity': self.entity_score,
                'recency': self.recency_score
            }
        }


class EmbeddingCache:
    """Cache embeddings to avoid re-computing."""
    
    def __init__(self, cache_dir: Path = None):
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "data" / "embeddings"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "embeddings.json"
        self._cache: Dict[str, List[float]] = {}
        self._load()
    
    def _load(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    self._cache = json.load(f)
            except json.JSONDecodeError:
                self._cache = {}
    
    def save(self):
        """Save cache to disk."""
        with open(self.cache_file, 'w') as f:
            json.dump(self._cache, f)
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding."""
        key = hashlib.md5(text.encode()).hexdigest()
        return self._cache.get(key)
    
    def set(self, text: str, embedding: List[float]):
        """Cache an embedding."""
        key = hashlib.md5(text.encode()).hexdigest()
        self._cache[key] = embedding
    
    def __len__(self):
        return len(self._cache)


class SemanticSearch:
    """
    Semantic search over the knowledge graph.
    
    Combines multiple signals:
    1. Semantic similarity (embeddings)
    2. Question form matching
    3. Entity relevance
    4. Recency
    """
    
    # Score weights (tune these)
    WEIGHTS = {
        'semantic': 0.5,    # Embedding similarity
        'question': 0.3,    # Question form keyword match
        'entity': 0.1,      # Entity mentioned in query
        'recency': 0.1      # Recent facts score higher
    }
    
    def __init__(self, graph: KnowledgeGraph = None):
        self.graph = graph or KnowledgeGraph()
        self.cache = EmbeddingCache()
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
        else:
            self.client = None
        
        # Pre-compute fact embeddings
        self._fact_embeddings: Dict[str, List[float]] = {}
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text, using cache."""
        # Check cache
        cached = self.cache.get(text)
        if cached:
            return cached
        
        # Generate if we have OpenAI
        if not self.client:
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            self.cache.set(text, embedding)
            return embedding
        except Exception as e:
            print(f"Embedding error: {e}", file=sys.stderr)
            return None
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _expand_query(self, query: str) -> str:
        """Expand query with pronoun resolution."""
        q = query.lower()
        
        # Pronoun resolution
        q = q.replace(" i ", " finn ")
        q = q.replace(" my ", " finn's ")
        q = q.replace("do i ", "does finn ")
        q = q.replace("am i ", "is finn ")
        q = q.replace("i'm ", "finn is ")
        
        # Intent expansion - add synonyms/related terms
        expansions = {
            "work": "work schedule hours job",
            "learn": "learn study education",
            "prefer": "prefer like want preference",
            "hate": "hate dislike avoid",
        }
        
        for term, expansion in expansions.items():
            if term in q:
                q = q + " " + expansion
        
        return q
    
    def _compute_semantic_score(self, query_embedding: List[float], fact: Fact) -> float:
        """Compute semantic similarity score."""
        if not query_embedding:
            return 0.0
        
        # Get or compute fact embedding
        if fact.id not in self._fact_embeddings:
            # Embed the fact content + subject + questions
            fact_text = f"{fact.subject}: {fact.content}"
            if fact.question_forms:
                fact_text += " " + " ".join(fact.question_forms[:3])
            
            embedding = self._get_embedding(fact_text)
            if embedding:
                self._fact_embeddings[fact.id] = embedding
            else:
                return 0.0
        
        fact_embedding = self._fact_embeddings.get(fact.id)
        if not fact_embedding:
            return 0.0
        
        return self._cosine_similarity(query_embedding, fact_embedding)
    
    def _compute_question_score(self, query_words: set, fact: Fact) -> float:
        """Compute question form matching score."""
        if not fact.question_forms:
            return 0.0
        
        best_overlap = 0
        for qf in fact.question_forms:
            qf_words = set(qf.lower().split())
            overlap = len(query_words & qf_words)
            best_overlap = max(best_overlap, overlap)
        
        # Normalize by query length
        if len(query_words) == 0:
            return 0.0
        
        return min(best_overlap / len(query_words), 1.0)
    
    def _compute_entity_score(self, query: str, fact: Fact) -> float:
        """Compute entity relevance score."""
        query_lower = query.lower()
        
        # Check if query mentions entities that fact is linked to
        for entity_id in fact.linked_entities:
            if entity_id in query_lower:
                return 1.0
        
        return 0.0
    
    def _compute_recency_score(self, fact: Fact) -> float:
        """Compute recency score (newer = higher)."""
        # For now, simple heuristic based on timestamp
        # TODO: Implement proper recency scoring
        if fact.timestamp:
            # More recent timestamps = higher score
            # This is a placeholder - real implementation would compare to current time
            return 0.5
        return 0.0
    
    def search(self, query: str, limit: int = 10, use_semantic: bool = True) -> List[SearchResult]:
        """
        Search for facts matching the query.
        
        Combines semantic similarity with other signals for best results.
        If use_semantic=False or no embeddings available, uses fast mode.
        """
        # Expand query
        expanded = self._expand_query(query)
        query_words = set(expanded.split())
        
        # Get query embedding (only if semantic search enabled)
        query_embedding = None
        if use_semantic and self.client:
            query_embedding = self._get_embedding(expanded)
        
        # Check if we have enough cached fact embeddings for semantic search
        # If less than 50% cached, disable semantic to avoid slow queries
        cached_facts = sum(1 for f in self.graph.facts.values() if f.id in self._fact_embeddings or self.cache.get(f"{f.subject}: {f.content}"))
        use_semantic_scoring = query_embedding and cached_facts > len(self.graph.facts) * 0.5
        
        results = []
        
        for fact in self.graph.facts.values():
            # Compute individual scores
            if use_semantic_scoring:
                semantic = self._compute_semantic_score(query_embedding, fact)
            else:
                semantic = 0.0
            
            question = self._compute_question_score(query_words, fact)
            entity = self._compute_entity_score(query, fact)
            recency = self._compute_recency_score(fact)
            
            # Adjust weights if not using semantic
            if use_semantic_scoring:
                total = (
                    self.WEIGHTS['semantic'] * semantic +
                    self.WEIGHTS['question'] * question +
                    self.WEIGHTS['entity'] * entity +
                    self.WEIGHTS['recency'] * recency
                )
            else:
                # Without semantic, question matching is primary
                total = (
                    0.7 * question +
                    0.2 * entity +
                    0.1 * recency
                )
            
            if total > 0.05:  # Lower threshold
                results.append(SearchResult(
                    fact=fact,
                    total_score=total,
                    semantic_score=semantic,
                    question_score=question,
                    entity_score=entity,
                    recency_score=recency
                ))
        
        # Sort by total score
        results.sort(key=lambda r: r.total_score, reverse=True)
        
        # Save cache periodically
        if len(self.cache) % 10 == 0:
            self.cache.save()
        
        return results[:limit]
    
    def index_all_facts(self):
        """Pre-compute embeddings for all facts."""
        print(f"Indexing {len(self.graph.facts)} facts...")
        
        for i, fact in enumerate(self.graph.facts.values()):
            fact_text = f"{fact.subject}: {fact.content}"
            if fact.question_forms:
                fact_text += " " + " ".join(fact.question_forms[:3])
            
            embedding = self._get_embedding(fact_text)
            if embedding:
                self._fact_embeddings[fact.id] = embedding
            
            if (i + 1) % 50 == 0:
                print(f"  Indexed {i + 1}/{len(self.graph.facts)}")
                self.cache.save()
        
        self.cache.save()
        print(f"Done. Cache size: {len(self.cache)}")


def main():
    """CLI for semantic search."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Atlas Semantic Search")
    parser.add_argument("command", choices=["search", "index", "stats"])
    parser.add_argument("query", nargs="*")
    parser.add_argument("--limit", "-n", type=int, default=10)
    parser.add_argument("--debug", action="store_true")
    
    args = parser.parse_args()
    
    search = SemanticSearch()
    
    if args.command == "search":
        if not args.query:
            print("Usage: semantic_search.py search <query>")
            return 1
        
        query = " ".join(args.query)
        results = search.search(query, limit=args.limit)
        
        print(f"Found {len(results)} results:\n")
        for r in results:
            print(f"[{r.fact.category}] {r.fact.subject}")
            print(f"  {r.fact.content[:80]}...")
            if args.debug:
                print(f"  scores: sem={r.semantic_score:.2f} q={r.question_score:.2f} ent={r.entity_score:.2f}")
            print(f"  total: {r.total_score:.2f}")
            print()
    
    elif args.command == "index":
        search.index_all_facts()
    
    elif args.command == "stats":
        print(f"Cache size: {len(search.cache)}")
        print(f"Facts in graph: {len(search.graph.facts)}")
        print(f"OpenAI available: {OPENAI_AVAILABLE}")
        print(f"Client configured: {search.client is not None}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

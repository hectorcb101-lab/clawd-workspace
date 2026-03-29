"""
Financial NLP signal detection using Loughran-McDonald sentiment categories.
Extensible lexicon loaded from signal_lexicon.json.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Signal:
    """Detected financial/geopolitical signal."""
    phrase: str
    category: str
    sentiment_score: float  # -1 (dovish/de-escalation) to 1 (hawkish/escalation)
    confidence: float  # 0 to 1


class SignalLexicon:
    """Financial and geopolitical signal detection."""
    
    def __init__(self, custom_lexicon_path: Optional[Path] = None):
        """
        Initialize lexicon from JSON file.
        
        Args:
            custom_lexicon_path: Optional path to custom lexicon JSON.
                                Defaults to signal_lexicon.json in same directory.
        """
        if custom_lexicon_path is None:
            custom_lexicon_path = Path(__file__).parent / "signal_lexicon.json"
        
        self.lexicon: dict[str, list[dict]] = {}
        self._load_lexicon(custom_lexicon_path)
    
    def _load_lexicon(self, path: Path) -> None:
        """Load lexicon from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.lexicon = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Lexicon file not found: {path}. "
                "Ensure signal_lexicon.json exists in the feeds directory."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in lexicon file: {e}")
    
    def detect_signals(self, text: str) -> list[Signal]:
        """
        Detect financial and geopolitical signals in text.
        
        Args:
            text: Input text to analyze.
        
        Returns:
            List of detected Signal objects, ordered by confidence.
        """
        if not text:
            return []
        
        text_lower = text.lower()
        detected: list[Signal] = []
        
        for category, phrases in self.lexicon.items():
            for entry in phrases:
                phrase = entry["phrase"]
                sentiment = entry["sentiment"]
                weight = entry["weight"]
                
                # Case-insensitive phrase detection with word boundaries
                pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
                matches = re.findall(pattern, text_lower)
                
                if matches:
                    # Confidence is the weight (0-1 scale)
                    confidence = weight
                    
                    detected.append(Signal(
                        phrase=phrase,
                        category=category,
                        sentiment_score=sentiment,
                        confidence=confidence
                    ))
        
        # Sort by confidence descending
        detected.sort(key=lambda s: s.confidence, reverse=True)
        return detected
    
    def get_sentiment_score(self, text: str) -> float:
        """
        Calculate overall sentiment score for text.
        
        Returns weighted average of detected signals.
        Range: -1 (most dovish/de-escalatory) to 1 (most hawkish/escalatory).
        
        Args:
            text: Input text to analyze.
        
        Returns:
            Sentiment score in range [-1, 1]. Returns 0.0 if no signals detected.
        """
        signals = self.detect_signals(text)
        
        if not signals:
            return 0.0
        
        # Weighted average by confidence
        total_weight = sum(s.confidence for s in signals)
        weighted_sum = sum(s.sentiment_score * s.confidence for s in signals)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_category_breakdown(self, text: str) -> dict[str, int]:
        """
        Get count of signals by category.
        
        Args:
            text: Input text to analyze.
        
        Returns:
            Dictionary mapping category names to signal counts.
        """
        signals = self.detect_signals(text)
        breakdown: dict[str, int] = {}
        
        for signal in signals:
            breakdown[signal.category] = breakdown.get(signal.category, 0) + 1
        
        return breakdown
    
    def add_phrase(self, category: str, phrase: str, sentiment: float, weight: float = 1.0) -> None:
        """
        Add a new phrase to the lexicon (runtime only, not persisted).
        
        Args:
            category: Category name (e.g., 'hawkish', 'dovish').
            phrase: Phrase to detect.
            sentiment: Sentiment score (-1 to 1).
            weight: Confidence weight (0 to 1).
        """
        if category not in self.lexicon:
            self.lexicon[category] = []
        
        self.lexicon[category].append({
            "phrase": phrase,
            "sentiment": sentiment,
            "weight": weight
        })


# Singleton instance for easy import
_default_lexicon: Optional[SignalLexicon] = None


def get_lexicon() -> SignalLexicon:
    """Get or create the default lexicon instance."""
    global _default_lexicon
    if _default_lexicon is None:
        _default_lexicon = SignalLexicon()
    return _default_lexicon


def detect_signals(text: str) -> list[Signal]:
    """Convenience function using default lexicon."""
    return get_lexicon().detect_signals(text)


def get_sentiment_score(text: str) -> float:
    """Convenience function using default lexicon."""
    return get_lexicon().get_sentiment_score(text)

"""
Atlas Intel Feed Collectors

Multimodal intelligence platform feed collection modules.
Collects videos, speeches, and announcements for embedding and analysis.
"""

from .signal_lexicon import (
    Signal,
    SignalLexicon,
    detect_signals,
    get_sentiment_score,
    get_lexicon
)
from .x_config import XConfig, get_config
from .x_speech_feed import XSpeechFeedCollector, VideoTweet

__all__ = [
    # Signal detection
    "Signal",
    "SignalLexicon",
    "detect_signals",
    "get_sentiment_score",
    "get_lexicon",
    
    # X/Twitter configuration
    "XConfig",
    "get_config",
    
    # X/Twitter feed collector
    "XSpeechFeedCollector",
    "VideoTweet",
]

__version__ = "0.1.0"

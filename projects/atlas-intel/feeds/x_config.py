"""
X/Twitter API v2 configuration and rate limiting for Free tier.
"""

import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
class RateLimitWindow:
    """Track rate limit windows."""
    requests_made: int
    window_start: datetime
    window_duration_seconds: int
    max_requests: int


class XConfig:
    """X API v2 Free tier configuration and rate limiting."""
    
    # X Free API v2 rate limits (per 15-minute window)
    # Search endpoint: 60 requests per 15 minutes (app-level)
    # But we're targeting 1 request per hour for this use case
    DEFAULT_REQUESTS_PER_WINDOW = 1
    DEFAULT_WINDOW_SECONDS = 3600  # 1 hour
    
    def __init__(
        self,
        bearer_token: Optional[str] = None,
        requests_per_window: int = DEFAULT_REQUESTS_PER_WINDOW,
        window_seconds: int = DEFAULT_WINDOW_SECONDS
    ):
        """
        Initialize X API configuration.
        
        Args:
            bearer_token: X API bearer token. If None, loads from environment.
            requests_per_window: Max requests per time window.
            window_seconds: Time window duration in seconds.
        """
        self.bearer_token = bearer_token or self._load_bearer_token()
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        
        # Rate limit tracking
        self._rate_limit_window: Optional[RateLimitWindow] = None
        self._state_file = Path("/tmp/atlas-intel/x_rate_limit_state.json")
        self._load_rate_limit_state()
    
    def _load_bearer_token(self) -> str:
        """
        Load bearer token from environment or .env file.
        
        Priority:
        1. X_BEARER_TOKEN environment variable
        2. TWITTER_BEARER_TOKEN environment variable
        3. /home/ubuntu/.clawdbot/.env file
        
        Returns:
            Bearer token string.
        
        Raises:
            ValueError: If no bearer token found.
        """
        # Try environment first
        token = os.environ.get("X_BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN")
        
        if token:
            return token
        
        # Try .env file
        env_path = Path.home() / ".clawdbot" / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("X_BEARER_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"\'')
                    elif line.startswith("TWITTER_BEARER_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"\'')
        
        raise ValueError(
            "X API bearer token not found. Set X_BEARER_TOKEN environment variable "
            "or add it to /home/ubuntu/.clawdbot/.env"
        )
    
    def _load_rate_limit_state(self) -> None:
        """Load rate limit state from disk (if exists)."""
        if not self._state_file.exists():
            return
        
        try:
            import json
            with open(self._state_file, 'r') as f:
                state = json.load(f)
            
            self._rate_limit_window = RateLimitWindow(
                requests_made=state["requests_made"],
                window_start=datetime.fromisoformat(state["window_start"]),
                window_duration_seconds=state["window_duration_seconds"],
                max_requests=state["max_requests"]
            )
        except Exception:
            # If state file is corrupted, ignore and start fresh
            pass
    
    def _save_rate_limit_state(self) -> None:
        """Save rate limit state to disk."""
        if self._rate_limit_window is None:
            return
        
        import json
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "requests_made": self._rate_limit_window.requests_made,
            "window_start": self._rate_limit_window.window_start.isoformat(),
            "window_duration_seconds": self._rate_limit_window.window_duration_seconds,
            "max_requests": self._rate_limit_window.max_requests
        }
        
        with open(self._state_file, 'w') as f:
            json.dump(state, f)
    
    def check_rate_limit(self) -> tuple[bool, Optional[int]]:
        """
        Check if we can make another API request.
        
        Returns:
            Tuple of (can_proceed, seconds_until_reset).
            - can_proceed: True if request can be made now.
            - seconds_until_reset: Seconds to wait if can_proceed is False, None otherwise.
        """
        now = datetime.now()
        
        # Initialize window if needed
        if self._rate_limit_window is None:
            self._rate_limit_window = RateLimitWindow(
                requests_made=0,
                window_start=now,
                window_duration_seconds=self.window_seconds,
                max_requests=self.requests_per_window
            )
        
        # Check if window has expired
        window_end = self._rate_limit_window.window_start + timedelta(
            seconds=self._rate_limit_window.window_duration_seconds
        )
        
        if now >= window_end:
            # Reset window
            self._rate_limit_window = RateLimitWindow(
                requests_made=0,
                window_start=now,
                window_duration_seconds=self.window_seconds,
                max_requests=self.requests_per_window
            )
            self._save_rate_limit_state()
            return True, None
        
        # Check if we've hit the limit
        if self._rate_limit_window.requests_made >= self._rate_limit_window.max_requests:
            seconds_until_reset = int((window_end - now).total_seconds())
            return False, seconds_until_reset
        
        return True, None
    
    def record_request(self) -> None:
        """Record that an API request was made."""
        if self._rate_limit_window is None:
            self._rate_limit_window = RateLimitWindow(
                requests_made=1,
                window_start=datetime.now(),
                window_duration_seconds=self.window_seconds,
                max_requests=self.requests_per_window
            )
        else:
            self._rate_limit_window.requests_made += 1
        
        self._save_rate_limit_state()
    
    def wait_if_needed(self) -> None:
        """Block until rate limit allows another request."""
        can_proceed, wait_seconds = self.check_rate_limit()
        
        if not can_proceed and wait_seconds:
            print(f"Rate limit reached. Waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds)
    
    def get_headers(self) -> dict[str, str]:
        """Get HTTP headers for X API requests."""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "Atlas-Intel-Feed-Collector/1.0"
        }
    
    @property
    def api_base_url(self) -> str:
        """X API v2 base URL."""
        return "https://api.twitter.com/2"


# Singleton instance
_default_config: Optional[XConfig] = None


def get_config() -> XConfig:
    """Get or create the default X API config instance."""
    global _default_config
    if _default_config is None:
        _default_config = XConfig()
    return _default_config

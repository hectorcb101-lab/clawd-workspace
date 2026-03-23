"""
X/Twitter video feed collector for financial/political speeches and announcements.
Uses X Free API v2 for search and yt-dlp for video downloads.
"""

import json
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests

from .x_config import get_config, XConfig


@dataclass
class VideoTweet:
    """Collected video tweet metadata."""
    video_path: str
    tweet_id: str
    author: str
    text: str
    query_matched: str
    timestamp: datetime
    author_id: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary with ISO timestamp."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class XSpeechFeedCollector:
    """Collect video tweets about financial/political speeches."""
    
    # Search queries for financial/political content with videos
    SEARCH_QUERIES = [
        "Federal Reserve speech OR Fed press conference",
        "FOMC statement OR Jerome Powell",
        "Treasury Secretary OR White House press briefing",
        "ECB OR Bank of England OR central bank",
        "tariff announcement OR sanctions OR trade war",
        "OPEC OR oil production OR energy policy",
        "earnings call filter:has_video"
    ]
    
    def __init__(
        self,
        config: Optional[XConfig] = None,
        output_dir: Path = Path("/tmp/atlas-intel"),
        max_results_per_query: int = 10
    ):
        """
        Initialize the feed collector.
        
        Args:
            config: X API configuration. Uses default if None.
            output_dir: Directory to save downloaded videos.
            max_results_per_query: Max tweets to retrieve per search query.
        """
        self.config = config or get_config()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_results_per_query = max_results_per_query
        self._query_index = 0  # Rotate through queries
    
    def _get_next_query(self) -> str:
        """Get next search query (round-robin)."""
        query = self.SEARCH_QUERIES[self._query_index]
        self._query_index = (self._query_index + 1) % len(self.SEARCH_QUERIES)
        return query
    
    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        since_hours: int = 24
    ) -> list[dict]:
        """
        Search for tweets using X API v2.
        
        Args:
            query: Search query string.
            max_results: Maximum number of results (1-100).
            since_hours: Only return tweets from last N hours.
        
        Returns:
            List of tweet data dictionaries.
        
        Raises:
            requests.HTTPError: If API request fails.
        """
        # Check rate limit before proceeding
        self.config.wait_if_needed()
        
        # Build search URL
        endpoint = f"{self.config.api_base_url}/tweets/search/recent"
        
        # Calculate start_time (ISO 8601 format)
        start_time = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat() + "Z"
        
        params = {
            "query": query,
            "max_results": min(max_results, 100),  # API max is 100
            "start_time": start_time,
            "expansions": "author_id,attachments.media_keys",
            "tweet.fields": "created_at,author_id,text",
            "user.fields": "username,name",
            "media.fields": "type,url,variants,duration_ms"
        }
        
        try:
            response = requests.get(
                endpoint,
                headers=self.config.get_headers(),
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Record successful request
            self.config.record_request()
            
            data = response.json()
            return self._parse_search_response(data)
        
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit exceeded
                retry_after = e.response.headers.get("x-rate-limit-reset")
                if retry_after:
                    reset_time = datetime.fromtimestamp(int(retry_after))
                    wait_seconds = (reset_time - datetime.now()).total_seconds()
                    print(f"Rate limit exceeded. Reset at {reset_time}. Waiting {wait_seconds}s...")
                raise
            else:
                print(f"X API error: {e.response.status_code} - {e.response.text}")
                raise
    
    def _parse_search_response(self, data: dict) -> list[dict]:
        """
        Parse X API v2 search response.
        
        Args:
            data: Raw API response.
        
        Returns:
            List of parsed tweet dictionaries with video metadata.
        """
        if "data" not in data:
            return []
        
        tweets = data.get("data", [])
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        media = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}
        
        results = []
        
        for tweet in tweets:
            # Check if tweet has video media
            media_keys = tweet.get("attachments", {}).get("media_keys", [])
            video_found = False
            
            for media_key in media_keys:
                media_item = media.get(media_key)
                if media_item and media_item.get("type") == "video":
                    video_found = True
                    break
            
            if not video_found:
                continue
            
            author_id = tweet.get("author_id")
            author_data = users.get(author_id, {})
            
            results.append({
                "id": tweet["id"],
                "text": tweet.get("text", ""),
                "author_id": author_id,
                "author_username": author_data.get("username", "unknown"),
                "author_name": author_data.get("name", "Unknown"),
                "created_at": tweet.get("created_at"),
                "url": f"https://twitter.com/{author_data.get('username', 'i')}/status/{tweet['id']}"
            })
        
        return results
    
    def download_video(self, tweet_url: str, tweet_id: str) -> Optional[Path]:
        """
        Download video from tweet using yt-dlp.
        
        Args:
            tweet_url: Full URL of the tweet.
            tweet_id: Tweet ID for filename.
        
        Returns:
            Path to downloaded video file, or None if download failed.
        """
        output_template = str(self.output_dir / f"{tweet_id}.%(ext)s")
        
        try:
            # yt-dlp command
            cmd = [
                "yt-dlp",
                "--quiet",
                "--no-warnings",
                "--format", "best[ext=mp4]/best",  # Prefer MP4
                "--output", output_template,
                tweet_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"yt-dlp failed for {tweet_url}: {result.stderr}")
                return None
            
            # Find the downloaded file
            for ext in ["mp4", "webm", "mkv", "mov"]:
                video_path = self.output_dir / f"{tweet_id}.{ext}"
                if video_path.exists():
                    return video_path
            
            return None
        
        except subprocess.TimeoutExpired:
            print(f"yt-dlp timeout for {tweet_url}")
            return None
        except Exception as e:
            print(f"Error downloading video for {tweet_url}: {e}")
            return None
    
    def collect(
        self,
        query: Optional[str] = None,
        max_videos: int = 5,
        since_hours: int = 24
    ) -> list[VideoTweet]:
        """
        Collect videos from X matching financial/political content.
        
        Args:
            query: Search query. If None, uses next query from rotation.
            max_videos: Maximum number of videos to collect.
            since_hours: Only collect tweets from last N hours.
        
        Returns:
            List of VideoTweet objects with downloaded video paths.
        """
        if query is None:
            query = self._get_next_query()
        
        print(f"Searching X for: {query}")
        
        try:
            tweets = self.search_tweets(
                query=query,
                max_results=self.max_results_per_query,
                since_hours=since_hours
            )
        except Exception as e:
            print(f"Search failed: {e}")
            return []
        
        if not tweets:
            print(f"No video tweets found for query: {query}")
            return []
        
        print(f"Found {len(tweets)} video tweets. Downloading (max {max_videos})...")
        
        collected = []
        
        for tweet in tweets[:max_videos]:
            video_path = self.download_video(tweet["url"], tweet["id"])
            
            if video_path:
                video_tweet = VideoTweet(
                    video_path=str(video_path),
                    tweet_id=tweet["id"],
                    author=tweet["author_name"],
                    text=tweet["text"],
                    query_matched=query,
                    timestamp=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                    author_id=tweet["author_id"],
                    url=tweet["url"]
                )
                collected.append(video_tweet)
                print(f"  ✓ Downloaded: {tweet['author_name']} - {tweet['id']}")
            else:
                print(f"  ✗ Failed: {tweet['id']}")
        
        return collected
    
    def collect_batch(
        self,
        queries: Optional[list[str]] = None,
        max_videos_per_query: int = 3,
        since_hours: int = 24
    ) -> list[VideoTweet]:
        """
        Collect videos across multiple queries.
        
        Args:
            queries: List of search queries. If None, uses all default queries.
            max_videos_per_query: Max videos to collect per query.
            since_hours: Only collect tweets from last N hours.
        
        Returns:
            List of all collected VideoTweet objects.
        """
        if queries is None:
            queries = self.SEARCH_QUERIES
        
        all_collected = []
        
        for query in queries:
            collected = self.collect(
                query=query,
                max_videos=max_videos_per_query,
                since_hours=since_hours
            )
            all_collected.extend(collected)
            
            # Respect rate limits between queries
            if len(queries) > 1:
                self.config.wait_if_needed()
        
        return all_collected
    
    def save_manifest(self, video_tweets: list[VideoTweet], output_path: Path) -> None:
        """
        Save collected video tweets to JSON manifest.
        
        Args:
            video_tweets: List of VideoTweet objects.
            output_path: Path to save JSON manifest.
        """
        manifest = {
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "count": len(video_tweets),
            "videos": [vt.to_dict() for vt in video_tweets]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"Manifest saved: {output_path}")


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="X/Twitter video feed collector")
    parser.add_argument("--query", help="Custom search query")
    parser.add_argument("--max-videos", type=int, default=3, help="Max videos to collect")
    parser.add_argument("--since-hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--output", help="Output manifest JSON path")
    
    args = parser.parse_args()
    
    collector = XSpeechFeedCollector()
    
    collected = collector.collect(
        query=args.query,
        max_videos=args.max_videos,
        since_hours=args.since_hours
    )
    
    print(f"\nCollected {len(collected)} videos")
    
    if collected and args.output:
        collector.save_manifest(collected, Path(args.output))


if __name__ == "__main__":
    main()

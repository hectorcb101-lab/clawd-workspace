"""
Atlas OS Conversation Ingester

Automatically identifies and captures high-quality conversation turns
as training data. Runs periodically to process session logs.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from bus import emit, instruction_event
from quality.scorer import score_response, QualityScore


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    role: str  # user or assistant
    content: str
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class CapturedExample:
    """A captured training example."""
    prompt: str
    response: str
    quality_score: int
    source_file: str
    timestamp: str
    event_id: Optional[str] = None


class ConversationIngester:
    """
    Processes conversation logs and extracts training examples.
    
    Usage:
        ingester = ConversationIngester()
        examples = ingester.process_daily_logs()
        print(f"Captured {len(examples)} examples")
    """
    
    def __init__(
        self,
        memory_dir: Path = None,
        min_quality: int = 4,
        max_examples_per_run: int = 50,
    ):
        self.memory_dir = memory_dir or Path.home() / "clawd" / "memory"
        self.min_quality = min_quality
        self.max_examples_per_run = max_examples_per_run
        self.processed_file = Path.home() / "clawd" / "projects" / "atlas-os" / "data" / "ingested.json"
    
    def _load_processed(self) -> Dict[str, List[str]]:
        """Load record of already-processed files and hashes."""
        if self.processed_file.exists():
            with open(self.processed_file) as f:
                return json.load(f)
        return {"files": [], "hashes": []}
    
    def _save_processed(self, processed: Dict[str, List[str]]):
        """Save processed record."""
        self.processed_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.processed_file, "w") as f:
            json.dump(processed, f, indent=2)
    
    def _hash_turn(self, prompt: str, response: str) -> str:
        """Generate hash to detect duplicates."""
        import hashlib
        content = f"{prompt[:100]}|||{response[:100]}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_turns_from_markdown(self, content: str) -> List[Tuple[str, str]]:
        """Extract user/assistant turns from markdown conversation logs."""
        turns = []
        
        # Pattern for [User] ... [Assistant] style
        pattern1 = r'\[(?:User|Finn)[^\]]*\]\s*(.+?)(?=\[(?:Assistant|Atlas)|$)'
        pattern2 = r'\[(?:Assistant|Atlas)[^\]]*\]\s*(.+?)(?=\[(?:User|Finn)|$)'
        
        user_matches = re.findall(pattern1, content, re.DOTALL | re.IGNORECASE)
        assistant_matches = re.findall(pattern2, content, re.DOTALL | re.IGNORECASE)
        
        # Pair them up
        for i, (user, assistant) in enumerate(zip(user_matches, assistant_matches)):
            user = user.strip()
            assistant = assistant.strip()
            
            # Skip if too short
            if len(user) < 10 or len(assistant) < 20:
                continue
            
            # Skip if contains code blocks (harder to learn from)
            if "```" in assistant and assistant.count("```") > 4:
                continue
            
            turns.append((user, assistant))
        
        return turns
    
    def _extract_turns_from_jsonl(self, path: Path) -> List[Tuple[str, str]]:
        """Extract turns from JSONL session logs."""
        turns = []
        
        with open(path) as f:
            messages = []
            for line in f:
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except:
                    continue
        
        # Pair user/assistant messages
        for i in range(len(messages) - 1):
            if messages[i].get("role") == "user" and messages[i+1].get("role") == "assistant":
                user = messages[i].get("content", "")
                assistant = messages[i+1].get("content", "")
                
                if len(user) >= 10 and len(assistant) >= 20:
                    turns.append((user, assistant))
        
        return turns
    
    def process_file(self, path: Path, processed: Dict) -> List[CapturedExample]:
        """Process a single file and extract quality examples."""
        examples = []
        
        content = path.read_text()
        
        # Determine format and extract turns
        if path.suffix == ".jsonl":
            turns = self._extract_turns_from_jsonl(path)
        else:
            turns = self._extract_turns_from_markdown(content)
        
        for prompt, response in turns:
            # Check for duplicates
            turn_hash = self._hash_turn(prompt, response)
            if turn_hash in processed.get("hashes", []):
                continue
            
            # Score the response
            score = score_response(prompt, response)
            
            # Capture if high quality
            if score.overall >= self.min_quality:
                # Emit to event bus
                event = instruction_event(
                    instruction=prompt,
                    response=response,
                    quality=score.overall,
                    tags=["auto_ingested", f"source_{path.stem}"],
                )
                emit(event)
                
                examples.append(CapturedExample(
                    prompt=prompt[:200],
                    response=response[:200],
                    quality_score=score.overall,
                    source_file=str(path),
                    timestamp=datetime.now().isoformat(),
                    event_id=event.id,
                ))
                
                processed["hashes"].append(turn_hash)
                
                if len(examples) >= self.max_examples_per_run:
                    break
        
        return examples
    
    def process_daily_logs(self, days: int = 7) -> List[CapturedExample]:
        """Process recent daily log files."""
        processed = self._load_processed()
        all_examples = []
        
        # Find recent log files
        today = datetime.now()
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            log_path = self.memory_dir / f"{date_str}.md"
            if log_path.exists() and str(log_path) not in processed.get("files", []):
                examples = self.process_file(log_path, processed)
                all_examples.extend(examples)
                processed["files"].append(str(log_path))
                
                if len(all_examples) >= self.max_examples_per_run:
                    break
        
        # Save progress
        self._save_processed(processed)
        
        return all_examples
    
    def process_all(self) -> List[CapturedExample]:
        """Process all markdown files in memory directory."""
        processed = self._load_processed()
        all_examples = []
        
        for path in sorted(self.memory_dir.glob("*.md")):
            if str(path) in processed.get("files", []):
                continue
            
            examples = self.process_file(path, processed)
            all_examples.extend(examples)
            processed["files"].append(str(path))
            
            if len(all_examples) >= self.max_examples_per_run:
                break
        
        self._save_processed(processed)
        return all_examples
    
    def stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        processed = self._load_processed()
        return {
            "files_processed": len(processed.get("files", [])),
            "examples_captured": len(processed.get("hashes", [])),
            "memory_dir": str(self.memory_dir),
        }


def run_ingestion(days: int = 7) -> List[CapturedExample]:
    """Run conversation ingestion on recent logs."""
    ingester = ConversationIngester()
    return ingester.process_daily_logs(days)


def get_ingestion_stats() -> Dict[str, Any]:
    """Get ingestion statistics."""
    ingester = ConversationIngester()
    return ingester.stats()


if __name__ == "__main__":
    print("Running conversation ingestion...")
    
    ingester = ConversationIngester()
    
    print(f"\nStats: {ingester.stats()}")
    
    examples = ingester.process_daily_logs(days=3)
    
    print(f"\nCaptured {len(examples)} examples:")
    for ex in examples[:5]:
        print(f"  - Q: {ex.prompt[:50]}...")
        print(f"    A: {ex.response[:50]}...")
        print(f"    Score: {ex.quality_score}/5")
        print()

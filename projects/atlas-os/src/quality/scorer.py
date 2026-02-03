"""
Atlas OS Auto Quality Scorer

Automatically scores Atlas responses for training worthiness.
High-scoring responses are captured as SFT training data.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from bus import emit, instruction_event


@dataclass
class QualityScore:
    """Quality assessment of a response."""
    overall: int  # 1-5
    components: dict  # Individual scores
    flags: List[str]  # Quality flags (positive and negative)
    trainable: bool  # Worth capturing as training data
    
    def __str__(self):
        return f"Quality: {self.overall}/5 ({'trainable' if self.trainable else 'skip'})"


class ResponseScorer:
    """
    Scores Atlas responses for quality.
    
    Usage:
        scorer = ResponseScorer()
        score = scorer.score(prompt, response)
        if score.trainable:
            scorer.capture(prompt, response, score)
    """
    
    # Negative indicators (reduce score)
    SYCOPHANCY_PATTERNS = [
        r"great question",
        r"excellent question", 
        r"that's a (great|wonderful|excellent)",
        r"i'd be happy to",
        r"i'm happy to",
        r"certainly!",
        r"absolutely!",
        r"of course!",
        r"definitely!",
    ]
    
    FILLER_PATTERNS = [
        r"^(well,|so,|now,|okay,)",
        r"let me (just|quickly)",
        r"(first|before).{0,20}(let me|i'll)",
    ]
    
    HEDGING_EXCESS = [
        r"i think maybe",
        r"it might possibly",
        r"perhaps it could",
        r"i'm not entirely sure but",
    ]
    
    # Positive indicators (increase score)
    DIRECT_PATTERNS = [
        r"^[A-Z][^.!?]{5,50}[.!?]",  # Starts with clear statement
    ]
    
    REASONING_PATTERNS = [
        r"because",
        r"since",
        r"therefore",
        r"this means",
        r"the reason",
    ]
    
    STRUCTURED_PATTERNS = [
        r"^\d+\.",  # Numbered list
        r"^[-*•]",  # Bullet list
        r"\*\*[^*]+\*\*",  # Bold headers
        r"```",  # Code blocks
    ]
    
    def __init__(self, capture_threshold: int = 4):
        self.capture_threshold = capture_threshold
    
    def score(self, prompt: str, response: str) -> QualityScore:
        """Score a response for quality."""
        components = {}
        flags = []
        
        response_lower = response.lower()
        
        # 1. Sycophancy check (0-5, lower is better, inverted for score)
        syc_count = sum(
            1 for pattern in self.SYCOPHANCY_PATTERNS
            if re.search(pattern, response_lower)
        )
        syc_score = max(0, 5 - syc_count * 2)
        components["no_sycophancy"] = syc_score
        if syc_count > 0:
            flags.append(f"⚠️ Sycophantic phrases: {syc_count}")
        else:
            flags.append("✓ No sycophancy")
        
        # 2. Directness (no filler)
        filler_count = sum(
            1 for pattern in self.FILLER_PATTERNS
            if re.search(pattern, response_lower)
        )
        direct_score = max(0, 5 - filler_count * 2)
        components["directness"] = direct_score
        if filler_count == 0:
            flags.append("✓ Direct")
        
        # 3. Appropriate length
        length = len(response)
        prompt_length = len(prompt)
        
        # Short prompts should get short responses
        if prompt_length < 50:
            ideal_max = 200
        elif prompt_length < 200:
            ideal_max = 800
        else:
            ideal_max = 2000
        
        if length < 20:
            length_score = 2  # Too short
            flags.append("⚠️ Too brief")
        elif length > ideal_max * 2:
            length_score = 3  # Too long
            flags.append("⚠️ Verbose")
        elif length <= ideal_max:
            length_score = 5  # Good
            flags.append("✓ Good length")
        else:
            length_score = 4  # Acceptable
        
        components["length"] = length_score
        
        # 4. Reasoning quality
        reasoning_count = sum(
            1 for pattern in self.REASONING_PATTERNS
            if re.search(pattern, response_lower)
        )
        reasoning_score = min(5, 3 + reasoning_count)
        components["reasoning"] = reasoning_score
        if reasoning_count > 0:
            flags.append("✓ Shows reasoning")
        
        # 5. Structure (for longer responses)
        if length > 200:
            structure_count = sum(
                1 for pattern in self.STRUCTURED_PATTERNS
                if re.search(pattern, response, re.MULTILINE)
            )
            structure_score = min(5, 3 + structure_count)
            components["structure"] = structure_score
            if structure_count > 0:
                flags.append("✓ Well structured")
        else:
            components["structure"] = 4  # Not applicable for short responses
        
        # 6. No excessive hedging
        hedge_count = sum(
            1 for pattern in self.HEDGING_EXCESS
            if re.search(pattern, response_lower)
        )
        confidence_score = max(0, 5 - hedge_count * 2)
        components["confidence"] = confidence_score
        if hedge_count > 0:
            flags.append("⚠️ Excessive hedging")
        
        # Calculate overall score (weighted average)
        weights = {
            "no_sycophancy": 2.0,
            "directness": 1.5,
            "length": 1.0,
            "reasoning": 1.5,
            "structure": 0.5,
            "confidence": 1.0,
        }
        
        total_weight = sum(weights.values())
        weighted_sum = sum(
            components[k] * weights[k] for k in components
        )
        overall = round(weighted_sum / total_weight)
        overall = max(1, min(5, overall))
        
        # Determine if trainable
        trainable = overall >= self.capture_threshold
        
        return QualityScore(
            overall=overall,
            components=components,
            flags=flags,
            trainable=trainable,
        )
    
    def capture(
        self,
        prompt: str,
        response: str,
        score: QualityScore,
        system_prompt: str = "",
        tags: List[str] = None,
    ) -> Optional[str]:
        """Capture a high-quality response as training data."""
        if not score.trainable:
            return None
        
        tags = tags or []
        tags.append(f"quality_{score.overall}")
        
        # Emit to event bus for automatic capture
        event = instruction_event(
            instruction=prompt,
            response=response,
            system=system_prompt,
            quality=score.overall,
            tags=tags,
        )
        emit(event)
        
        return event.id
    
    def score_and_capture(
        self,
        prompt: str,
        response: str,
        system_prompt: str = "",
        tags: List[str] = None,
    ) -> Tuple[QualityScore, Optional[str]]:
        """Score and optionally capture in one call."""
        score = self.score(prompt, response)
        event_id = None
        
        if score.trainable:
            event_id = self.capture(prompt, response, score, system_prompt, tags)
        
        return score, event_id


# Global scorer instance
_scorer: Optional[ResponseScorer] = None


def get_scorer() -> ResponseScorer:
    """Get the global scorer instance."""
    global _scorer
    if _scorer is None:
        _scorer = ResponseScorer()
    return _scorer


def score_response(prompt: str, response: str) -> QualityScore:
    """Convenience function to score a response."""
    return get_scorer().score(prompt, response)


def score_and_capture(
    prompt: str,
    response: str,
    system_prompt: str = "",
    tags: List[str] = None,
) -> Tuple[QualityScore, Optional[str]]:
    """Convenience function to score and capture."""
    return get_scorer().score_and_capture(prompt, response, system_prompt, tags)


if __name__ == "__main__":
    # Test the scorer
    scorer = ResponseScorer()
    
    # Good response
    good_prompt = "What's 2 + 2?"
    good_response = "4."
    score = scorer.score(good_prompt, good_response)
    print(f"\nGood short response: {score}")
    for flag in score.flags:
        print(f"  {flag}")
    
    # Sycophantic response
    syc_prompt = "Can you help me?"
    syc_response = "Great question! I'd be happy to help you! Certainly, I can absolutely assist with that!"
    score = scorer.score(syc_prompt, syc_response)
    print(f"\nSycophantic response: {score}")
    for flag in score.flags:
        print(f"  {flag}")
    
    # Good detailed response
    detail_prompt = "Explain how to make a sandwich"
    detail_response = """Here's how to make a sandwich:

1. **Gather ingredients** - bread, filling, condiments
2. **Prep the bread** - lay out two slices
3. **Add condiments** - spread on both slices
4. **Layer fillings** - meat, cheese, vegetables
5. **Close and cut** - put slices together, cut diagonally

The key is layering - put wet ingredients in the middle so the bread doesn't get soggy."""
    
    score = scorer.score(detail_prompt, detail_response)
    print(f"\nGood detailed response: {score}")
    for flag in score.flags:
        print(f"  {flag}")

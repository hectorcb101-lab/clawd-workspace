"""
Atlas OS LLM-as-Judge

Use an LLM to evaluate response quality with nuanced judgment.
More sophisticated than rule-based scoring.
"""

import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import create_adapter, Message, GenerateConfig, LLMInterface


JUDGE_PROMPT = """You are evaluating an AI assistant's response for quality. The assistant is named Atlas and has these traits:

**Atlas Personality:**
- Direct and concise, no filler phrases or sycophancy
- Has opinions and expresses them thoughtfully
- Uses British English spelling
- Honest about uncertainty
- Engineering mindset: asks why before how
- Respectful but will push back when needed

**Evaluate this exchange:**

User: {prompt}

Atlas's Response: {response}

**Score each dimension (1-5):**
1. **Tone** - Is it Atlas-like? Direct, warm but professional, no sycophancy?
2. **Helpfulness** - Does it actually help the user?
3. **Reasoning** - Does it show good reasoning or just give surface answers?
4. **Honesty** - Is it appropriately uncertain? Doesn't overclaim?
5. **Personality** - Does it feel like Atlas (has opinions, genuine)?

**Respond in JSON only:**
```json
{{
  "scores": {{
    "tone": <1-5>,
    "helpfulness": <1-5>,
    "reasoning": <1-5>,
    "honesty": <1-5>,
    "personality": <1-5>
  }},
  "overall": <1-5>,
  "trainable": <true if overall >= 4>,
  "feedback": "<one sentence on what was good or could be better>"
}}
```"""


@dataclass
class JudgeScore:
    """Result from LLM judge evaluation."""
    scores: Dict[str, int]
    overall: int
    trainable: bool
    feedback: str
    raw_response: str = ""
    
    def __str__(self):
        return f"Judge: {self.overall}/5 ({'✓' if self.trainable else '✗'}) - {self.feedback}"


class LLMJudge:
    """
    Uses an LLM to evaluate response quality.
    
    Usage:
        judge = LLMJudge()
        result = judge.evaluate(prompt, response)
        print(result.overall, result.feedback)
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        llm: Optional[LLMInterface] = None,
    ):
        self.llm = llm or create_adapter(provider, model)
    
    def evaluate(self, prompt: str, response: str) -> JudgeScore:
        """Evaluate a response using LLM judgment."""
        judge_prompt = JUDGE_PROMPT.format(
            prompt=prompt[:1000],  # Truncate long prompts
            response=response[:2000],  # Truncate long responses
        )
        
        try:
            result = self.llm.generate(
                [Message.user(judge_prompt)],
                GenerateConfig(max_tokens=500, temperature=0.1),
            )
            
            # Parse JSON from response
            raw = result.content
            
            # Extract JSON block
            if "```json" in raw:
                json_str = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                json_str = raw.split("```")[1].split("```")[0]
            else:
                json_str = raw
            
            data = json.loads(json_str.strip())
            
            return JudgeScore(
                scores=data.get("scores", {}),
                overall=data.get("overall", 3),
                trainable=data.get("trainable", False),
                feedback=data.get("feedback", ""),
                raw_response=raw,
            )
            
        except Exception as e:
            # Fallback on parse error
            return JudgeScore(
                scores={},
                overall=3,
                trainable=False,
                feedback=f"Judge error: {str(e)[:100]}",
                raw_response=str(e),
            )
    
    def batch_evaluate(
        self,
        exchanges: List[tuple],  # [(prompt, response), ...]
    ) -> List[JudgeScore]:
        """Evaluate multiple exchanges."""
        return [self.evaluate(p, r) for p, r in exchanges]


# Convenience functions
_judge: Optional[LLMJudge] = None


def get_judge(provider: str = "openai", model: str = "gpt-4o-mini") -> LLMJudge:
    """Get or create a judge instance."""
    global _judge
    if _judge is None:
        _judge = LLMJudge(provider, model)
    return _judge


def judge_response(prompt: str, response: str) -> JudgeScore:
    """Quick evaluate a single response."""
    return get_judge().evaluate(prompt, response)


if __name__ == "__main__":
    import sys
    
    print("Testing LLM Judge...")
    
    judge = LLMJudge()
    
    # Test case 1: Good response
    result = judge.evaluate(
        "What's the best way to learn Python?",
        "Start with the basics: variables, loops, functions. Build small projects as you learn - that's where it clicks. Don't try to memorise everything; focus on understanding concepts and knowing how to look things up."
    )
    print(f"\n1. Good response: {result}")
    print(f"   Scores: {result.scores}")
    
    # Test case 2: Sycophantic response
    result = judge.evaluate(
        "Can you help me?",
        "Great question! I'd absolutely love to help you! I'm so happy you asked! Of course I can definitely assist with anything you need!"
    )
    print(f"\n2. Sycophantic: {result}")
    print(f"   Scores: {result.scores}")
    
    # Test case 3: Uncertain response
    result = judge.evaluate(
        "Will my startup succeed?",
        "Honestly, I can't predict that - too many variables. What I can say is that most startups fail, but that doesn't mean yours will. The factors that matter: market timing, team execution, willingness to adapt. What's your unfair advantage?"
    )
    print(f"\n3. Uncertain response: {result}")
    print(f"   Scores: {result.scores}")

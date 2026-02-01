"""
Atlas Self-Awareness System - Task Type Classifier

Simple rule-based classifier for categorizing tasks.
Start simple, add ML later if needed.
"""

import re
from typing import Tuple, Optional

# Task type taxonomy
TASK_TYPES = {
    # Core capabilities
    "coding": {
        "keywords": ["code", "function", "class", "script", "debug", "refactor", "implement", "build", "fix bug", "compile", "syntax", "python", "javascript", "typescript", "rust"],
        "subtypes": ["writing", "debugging", "reviewing", "refactoring", "testing"]
    },
    "research": {
        "keywords": ["search", "find", "lookup", "investigate", "research", "discover", "learn about", "what is", "how does", "explain"],
        "subtypes": ["web_search", "deep_dive", "synthesis", "fact_check"]
    },
    "communication": {
        "keywords": ["email", "message", "draft", "write to", "respond", "reply", "document", "explain to", "tell"],
        "subtypes": ["email", "message", "document", "explanation"]
    },
    "planning": {
        "keywords": ["plan", "design", "architect", "schedule", "organize", "structure", "roadmap", "strategy"],
        "subtypes": ["architecture", "project_planning", "scheduling", "strategy"]
    },
    "memory": {
        "keywords": ["remember", "recall", "what did", "when did", "search memory", "log", "note"],
        "subtypes": ["recall", "logging", "search"]
    },
    # Tool usage
    "tool_browser": {
        "keywords": ["browser", "webpage", "website", "navigate", "click", "screenshot"],
        "subtypes": []
    },
    "tool_exec": {
        "keywords": ["run command", "execute", "shell", "terminal", "bash"],
        "subtypes": []
    },
    "tool_file": {
        "keywords": ["file", "read file", "write file", "edit file", "create file", "directory"],
        "subtypes": ["read", "write", "edit"]
    },
    "tool_mcp": {
        "keywords": ["mcporter", "mcp", "google workspace", "exa", "nanobanana"],
        "subtypes": []
    },
    # Meta
    "self_reflection": {
        "keywords": ["self", "my performance", "how am i", "my patterns", "my strengths", "my weaknesses"],
        "subtypes": []
    },
    "learning": {
        "keywords": ["learn", "study", "understand", "master", "practice"],
        "subtypes": []
    },
    "conversation": {
        "keywords": ["chat", "talk", "discuss", "conversation", "question", "answer"],
        "subtypes": []
    },
    "organization": {
        "keywords": ["organize", "clean up", "sort", "arrange", "tidy", "structure files"],
        "subtypes": []
    }
}


def classify_task(description: str, context: Optional[str] = None) -> Tuple[str, Optional[str], float]:
    """
    Classify a task description into a task type.
    
    Returns:
        Tuple of (task_type, subtype, confidence)
    """
    if not description:
        return ("unknown", None, 0.0)
    
    text = description.lower()
    if context:
        text = f"{text} {context.lower()}"
    
    matches = []
    
    for task_type, config in TASK_TYPES.items():
        keywords = config["keywords"]
        subtypes = config.get("subtypes", [])
        
        # Count keyword matches
        match_count = 0
        matched_keywords = []
        for keyword in keywords:
            if keyword in text:
                match_count += 1
                matched_keywords.append(keyword)
        
        if match_count > 0:
            # Calculate confidence based on match quality
            confidence = min(0.9, 0.3 + (match_count * 0.15))
            
            # Detect subtype
            subtype = None
            for st in subtypes:
                if st in text:
                    subtype = st
                    confidence += 0.1
                    break
            
            matches.append((task_type, subtype, confidence, match_count))
    
    if not matches:
        return ("unknown", None, 0.2)
    
    # Sort by confidence and match count
    matches.sort(key=lambda x: (x[2], x[3]), reverse=True)
    best = matches[0]
    
    return (best[0], best[1], min(1.0, best[2]))


def suggest_task_type(description: str) -> list:
    """
    Suggest possible task types for a description.
    Returns list of (task_type, confidence) tuples.
    """
    if not description:
        return []
    
    text = description.lower()
    suggestions = []
    
    for task_type, config in TASK_TYPES.items():
        keywords = config["keywords"]
        match_count = sum(1 for k in keywords if k in text)
        
        if match_count > 0:
            confidence = min(0.9, 0.3 + (match_count * 0.15))
            suggestions.append((task_type, confidence))
    
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions[:5]


def get_all_task_types() -> list:
    """Return list of all valid task types."""
    return list(TASK_TYPES.keys())


def get_subtypes(task_type: str) -> list:
    """Return subtypes for a given task type."""
    if task_type in TASK_TYPES:
        return TASK_TYPES[task_type].get("subtypes", [])
    return []


if __name__ == "__main__":
    # Test the classifier
    test_cases = [
        "Write a Python function to parse JSON",
        "Search for information about quantum computing",
        "Send an email to Finn about the project status",
        "Create a plan for the new feature",
        "Remember what we discussed yesterday",
        "Run the test suite",
        "Read the config file and update the settings",
        "How am I doing with coding tasks?",
        "Let's chat about the weekend",
    ]
    
    print("Task Classification Tests:\n")
    for desc in test_cases:
        task_type, subtype, confidence = classify_task(desc)
        subtype_str = f" ({subtype})" if subtype else ""
        print(f"  \"{desc[:50]}...\"")
        print(f"  → {task_type}{subtype_str} [confidence: {confidence:.2f}]\n")

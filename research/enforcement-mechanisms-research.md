# Enforcement Mechanisms for AI Agent Pre-Task Behaviors
**Research Date:** 2026-02-09  
**Purpose:** Find practical, implementable solutions for making LLMs follow mandatory procedures consistently

---

## The Problem

An AI agent has documented pre-task hooks in AGENTS.md:
- Search memory before answering
- Run `atlas-gate pre` before any task
- Run `atlas-gate post` after completing tasks
- Verify corrections are behavioral, not just documentation changes

**But**: Documentation alone doesn't change LLM behavior. The agent doesn't consistently follow these procedures.

---

## Research Findings

### 1. OpenClaw's Built-in Hooks System

**What it is:** Event-driven automation system that runs scripts when specific events fire (`/new`, `/reset`, agent lifecycle events).

**How it works:**
- Hooks are TypeScript functions in `~/.openclaw/hooks/`
- Automatically discovered and registered by the Gateway
- Triggered on specific events (command:new, agent:bootstrap, gateway:startup, etc.)
- Can modify context BEFORE the agent sees it

**Example hooks:**
- `session-memory`: Saves context to memory/ when `/new` is issued
- `command-logger`: Logs all commands to audit file
- `agent:bootstrap`: Can intercept and modify bootstrap files (AGENTS.md, SOUL.md) before injection

**Key insight:** These hooks run at the **Gateway level**, not inside the agent loop. They fire on external events (user commands, session lifecycle), not on agent decisions.

**Pros:**
- Reliable execution (Gateway enforces it, not the LLM)
- Can modify prompt context before the agent sees it
- Transparent to the agent (runs outside the inference loop)
- Works for session lifecycle events

**Cons:**
- **Cannot enforce mid-task behaviors** (like "search memory before answering a question")
- Only triggers on specific Gateway events, not on agent's internal decision points
- No way to force "before tool call" or "before responding" hooks
- TypeScript-based, requires Gateway restart to reload

**Applicability to the problem:** 
❌ **Won't solve it.** OpenClaw hooks are for command/session events, not for "before Atlas answers a question" or "before Atlas starts a task". The agent decides when to start tasks; the Gateway doesn't know.

---

### 2. LangGraph's State Machine Approach

**What it is:** Explicit graph-based workflow where nodes are deterministic functions and edges define flow.

**How it works:**
```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(MessagesState)
graph.add_node("memory_search", search_memory_node)  # Required node
graph.add_node("respond", respond_node)

# Force memory search before every response
graph.add_edge(START, "memory_search")
graph.add_edge("memory_search", "respond")
graph.add_edge("respond", END)
```

**Key insight:** The workflow is **code**, not instructions. The LLM can't skip steps because the graph structure enforces the sequence.

**Example enforcements:**
- **Pre-task checks:** Every workflow starts with a "validate_input" node
- **Mandatory retrieval:** RAG systems always call retrieval tool before LLM generates
- **Human-in-the-loop:** Add conditional edges that route to approval_node when risk > threshold
- **Iterative refinement:** Force validation_node after generation, loop back if failed

**Pros:**
- **Deterministic execution** — steps run in code-defined order, not LLM-chosen order
- Can force multi-step processes (search → plan → execute → verify)
- State is explicit and inspectable at each node
- LLM only controls *content* of nodes, not *sequence* of execution

**Cons:**
- **High rigidity** — every path must be pre-defined
- Complex workflows become large graphs
- LLM can't dynamically choose "do I need memory for this?" — it always runs
- Not suitable for freeform agent tasks where workflow varies

**Applicability to the problem:**
✅ **Partially solves it** for well-defined workflows. If "respond to user" is always: `search_memory → check_build → generate_response`, LangGraph can enforce that. But if the agent needs flexibility (sometimes search isn't needed), it becomes clunky.

---

### 3. CrewAI's Task Guardrails

**What it is:** Validation functions that run **after** a task completes and can reject the output, forcing a retry.

**How it works:**
```python
def validate_word_count(result: TaskOutput) -> Tuple[bool, Any]:
    word_count = len(result.raw.split())
    if word_count > 200:
        return (False, "Content exceeds 200 words")
    return (True, result.raw)

task = Task(
    description="Write a blog post",
    expected_output="A blog post under 200 words",
    agent=blog_agent,
    guardrail=validate_word_count,  # Enforced check
    guardrail_max_retries=3
)
```

**Key insight:** Guardrails are **post-task validators**, not pre-task hooks. They enforce output quality, not procedural compliance.

**LLM-based guardrails:** Can also use string descriptions:
```python
task = Task(
    description="Research quantum computing",
    guardrail="The research report must include at least 5 credible sources",
    agent=researcher
)
```
The LLM validates its own output against the criteria.

**Pros:**
- Forces quality standards (word count, format, required sections)
- Can chain multiple guardrails sequentially
- Error messages go back to the agent for correction
- Works for both programmatic and subjective validation

**Cons:**
- **Post-task only** — can't enforce "search memory before starting"
- Agent can burn retries and still fail
- No pre-task hooks — guardrails validate output, not process

**Applicability to the problem:**
❌ **Doesn't solve pre-task enforcement.** Could validate *post-task* that the agent actually searched memory (by checking output for memory references), but can't force it to happen first.

---

### 4. Tool Execution Wrapping (LangChain/CrewAI)

**What it is:** Every tool call goes through a wrapper that can enforce pre-conditions.

**How it works:**
```python
from langchain.tools import BaseTool

class MandatorySearchTool(BaseTool):
    name = "answer_question"
    description = "Answer a user question"
    
    def _run(self, question: str) -> str:
        # ALWAYS search memory first
        memory_results = search_memory(question)
        
        # Then call LLM with memory context
        return llm.invoke(f"Memory: {memory_results}\nQuestion: {question}")
```

**Key insight:** If the tool itself enforces the procedure, the LLM can't bypass it.

**Example enforcements:**
- Wrap "web search" to always check local cache first
- Wrap "send email" to require user confirmation
- Wrap "execute code" to run in sandbox and validate output

**Pros:**
- **Reliable** — tool code runs regardless of LLM decision
- Works with any framework (LangChain, CrewAI, custom)
- Can enforce complex multi-step procedures inside a single tool
- LLM just calls the tool; the tool handles compliance

**Cons:**
- Only applies to tool calls — can't enforce "search before responding" if the LLM decides not to use a tool
- Requires redefining tools to include enforcement logic
- Can make tools slower (always runs checks, even if unnecessary)

**Applicability to the problem:**
✅ **Solves tool-based enforcement.** If Atlas has a "respond" tool, it can embed memory search inside it. But if Atlas generates responses without calling tools, this doesn't help.

---

### 5. Middleware/Plugin Hooks (OpenClaw's Plugin API)

**What it is:** Hooks that run **inside the agent loop** at specific lifecycle points.

**OpenClaw's plugin hooks:**
- `before_agent_start`: Modify context/prompt before inference
- `before_tool_call`: Intercept tool params, add context
- `after_tool_call`: Modify tool results before LLM sees them
- `tool_result_persist`: Transform tool results before saving to transcript
- `agent_end`: Inspect final output

**How it works:**
```typescript
// Plugin hook example
async function before_tool_call(params) {
    if (params.tool_name === "web_search") {
        // Force memory search first
        const memoryResults = await searchMemory(params.query);
        params.context = memoryResults;  // Inject into tool call
    }
    return params;
}
```

**Key insight:** These run **synchronously** in the agent loop, so they can enforce behaviors at decision points.

**Pros:**
- Runs inside the agent loop (unlike Gateway hooks)
- Can modify tool calls, prompts, and results
- Transparent to the LLM (happens behind the scenes)
- Supports both pre- and post-action hooks

**Cons:**
- Still **reactive** — only triggers when LLM calls a tool
- Can't force "search memory before responding" if LLM never calls a search tool
- Requires plugin development (TypeScript, Gateway restart)
- No "before_response" hook — only before/after tool calls

**Applicability to the problem:**
✅ **Partially solves it** for tool-based workflows. If Atlas uses tools consistently, `before_tool_call` can inject memory searches. But doesn't help if Atlas answers directly without tools.

---

### 6. Executable Pre-Task Script (Atlas's `atlas-gate`)

**What it is:** A **standalone CLI script** that Atlas is instructed to run before tasks. Returns structured output telling Atlas what to do.

**How it works:**
```bash
# Atlas runs this before starting work
atlas-gate pre "write blog post about AI"

# Script outputs JSON:
{
  "gate": "pre-task",
  "topic": "write blog post about AI",
  "checks": [
    {"name": "memory_search", "has_relevant_memory": true, "summary": "..."},
    {"name": "duplicate_check", "is_duplicate": false},
    {"name": "active_build", "exists": true, "is_stale": false, "path": "..."}
  ],
  "recommendations": ["Continue active build", "Review memory: ..."]
}
```

**Key insight:** The script **does the work**, not the LLM. Atlas just runs it and reads the output.

**Pros:**
- **Deterministic execution** — if Atlas runs the script, checks happen
- Returns structured data (not prose) that's easy to parse
- Can aggregate multiple checks (memory, builds, duplicates) in one call
- Easy to modify (Python script, no Gateway restart)
- Lightweight (no framework changes needed)

**Cons:**
- **Still depends on LLM compliance** — Atlas has to actually run the script
- No enforcement if Atlas "forgets" or decides it's unnecessary
- Just a better-organized version of "instructions in AGENTS.md"

**Applicability to the problem:**
✅ **Solves the "what to do" problem** — the script tells Atlas exactly what it found and what to do about it.  
❌ **Doesn't solve the "will Atlas actually do it" problem** — it's still an instruction, not enforcement.

---

### 7. System Prompt Injection with Structured Directives

**What it is:** Force pre-task behaviors into the system prompt in a way that's **harder to ignore**.

**Techniques:**
```
You are Atlas. Before responding to any user message:

1. REQUIRED: Run `atlas-gate pre "<topic>"` and read the output
2. REQUIRED: If memory_search found relevant context, include it
3. REQUIRED: If active_build exists, continue it

Your response must begin with:
✓ Memory searched: [yes/no]
✓ Active build checked: [yes/no]
```

**Alternative: Make it part of the response format:**
```
Every response must follow this format:

<pre_checks>
- Ran: atlas-gate pre "topic"
- Memory: [summary]
- Active build: [status]
</pre_checks>

<response>
[actual answer]
</response>
```

**Key insight:** Make compliance **visible** and **part of the output format**, not just an internal step.

**Pros:**
- No framework changes needed
- Forces LLM to at least *acknowledge* the requirement
- Makes non-compliance obvious (missing `<pre_checks>` section)
- Can be combined with output validation (reject responses without checks)

**Cons:**
- Still LLM-dependent — model can generate fake `<pre_checks>` without actually running the script
- Adds verbosity to every response
- Doesn't **force** execution, just makes it more likely

**Applicability to the problem:**
✅ **Better than pure prose instructions** — makes compliance measurable.  
❌ **Still not true enforcement** — LLM can lie.

---

### 8. Function Calling / Tool-Use Enforcement

**What it is:** Make pre-task checks a **mandatory tool** that the LLM must call.

**How it works:**
```python
# Define pre-task check as a tool
@tool
def pre_task_check(topic: str) -> str:
    """REQUIRED: Run before every task. Returns memory, builds, duplicates."""
    memory = search_memory(topic)
    build = check_active_build()
    return json.dumps({"memory": memory, "build": build})

# System prompt:
"Before answering any question, you MUST call pre_task_check with the topic."
```

**Enforcement variant:**
```python
# Create a "respond" tool that embeds the check
@tool
def respond_to_user(message: str) -> str:
    """Use this tool to respond to the user. Do NOT respond directly."""
    # Check is embedded in the tool
    pre_check = pre_task_check(extract_topic(message))
    response = llm.invoke(f"Context: {pre_check}\nMessage: {message}")
    return response
```

**Key insight:** If the LLM can only respond via a tool, and the tool enforces the check, compliance is guaranteed.

**Pros:**
- **True enforcement** if "respond" is the only way to answer
- Works with function-calling models (GPT-4, Claude, etc.)
- Can combine multiple checks in one tool call
- Easy to audit (tool call logs show compliance)

**Cons:**
- Requires function-calling capable model
- LLM might try to respond anyway (depends on model compliance with tool-use-only mode)
- Adds latency (extra tool call before every response)
- Makes freeform conversation awkward

**Applicability to the problem:**
✅ **Strong enforcement if combined with "tool-use-only" mode.**  
❓ **Requires testing:** Will Claude actually refuse to respond without calling the tool?

---

## Summary: 3-5 Concrete Mechanisms

### 1. **State Machine Enforcement (LangGraph)**
- **How:** Explicit graph with nodes and edges; LLM can't skip steps
- **Pros:** Deterministic, reliable, handles complex workflows
- **Cons:** Rigid, not suitable for freeform tasks
- **Best for:** Well-defined workflows (RAG, multi-step research)

### 2. **Tool Wrapping with Embedded Checks**
- **How:** Pre-task checks run inside tools, not as separate steps
- **Pros:** Reliable (tool code controls execution), framework-agnostic
- **Cons:** Only works for tool-based interactions
- **Best for:** Tool-heavy agents (search, analysis, code execution)

### 3. **Mandatory Function Calling (Tool-Use-Only Mode)**
- **How:** Force LLM to call a tool (e.g., `respond_to_user`) that embeds checks
- **Pros:** Strong enforcement if model respects tool-use-only
- **Cons:** Adds latency, requires function-calling model
- **Best for:** Strict compliance scenarios (regulated environments)

### 4. **Plugin/Middleware Hooks (Inside Agent Loop)**
- **How:** Hooks run at lifecycle points (before_tool_call, after_tool_call)
- **Pros:** Transparent to LLM, modifies behavior automatically
- **Cons:** Reactive (only triggers on tool use), requires framework support
- **Best for:** Augmenting existing agent behavior without changing prompts

### 5. **Executable Gate Script + Structured Output Validation**
- **How:** Script does the checks, LLM must include output in response format
- **Pros:** Lightweight, easy to modify, makes compliance visible
- **Cons:** Still LLM-dependent (can be ignored or faked)
- **Best for:** Improving compliance without framework changes

---

## Recommendations for Atlas

**Current approach:** Prose instructions in AGENTS.md + `atlas-gate` script that Atlas is supposed to run.

**Why it's failing:** No enforcement. Atlas can skip it, and often does.

**Best path forward:** Combine mechanisms:

1. **Make `atlas-gate pre` a mandatory tool call** (Mechanism #3)
   - Define it as a function the LLM must call
   - Embed it in a "respond_to_user" tool if needed
   - Log tool calls to verify compliance

2. **Add output format validation** (Mechanism #5)
   - Require `<pre_checks>` section in every response
   - Reject or flag responses without it
   - Makes non-compliance visible

3. **Use plugin hooks for tool augmentation** (Mechanism #4)
   - Add `before_tool_call` hook to inject memory context
   - Automatic for tool-based workflows

4. **Long-term: Migrate high-value workflows to LangGraph** (Mechanism #1)
   - For critical workflows (research, project planning), use state machines
   - Guarantees procedural compliance

---

## What Actually Works?

**From research and practice:**
- ✅ State machines (LangGraph) — **100% reliable for defined workflows**
- ✅ Tool wrapping — **100% reliable when tools are used**
- ✅ Guardrails (CrewAI) — **Effective for output validation, not pre-task**
- ❓ Mandatory function calling — **Depends on model compliance**
- ❌ Prose instructions alone — **Unreliable (current state)**
- ❌ Event hooks (OpenClaw Gateway) — **Wrong level of abstraction for this problem**

**Key insight:** You can't *instruct* reliability into an LLM. You need **architectural enforcement** (state machines, tool wrapping) or **validation layers** (guardrails, output checks) that operate outside the LLM's discretion.

---

**Research complete.** 

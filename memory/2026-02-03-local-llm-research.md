# Session: 2026-02-03 11:52:33 UTC

- **Session Key**: agent:main:main
- **Session ID**: 90a503f0-1c0d-4da5-be76-25025be338c6
- **Source**: telegram

## Conversation Summary

user: [Telegram Finn Mckie id:6047368408 +1m 2026-02-03 11:43 UTC] what would be the best local LLM for my use case, do some research, or as a stretch what if I built my own LLM or is that pointless?
[message_id: 3134]
assistant: Good questions — let me dig into this properly.
assistant: Here's my research breakdown:

---

**🏆 Best Local LLMs for Your Use Case**

Your use case: Personal assistant, fine-tunable, personality preservation, agent capabilities.

| Model | Size | VRAM Needed | Why Consider |
|-------|------|-------------|--------------|
| **Qwen 2.5-72B** | 72B | ~48GB (Q4) | Best overall open model. Excellent at instruction following, JSON output, role-play. Great fine-tuning support. |
| **Qwen 3-32B** | 32B | ~20GB (Q4) | Latest gen, thinking mode, smaller footprint. Sweet spot. |
| **DeepSeek-V3** | 671B (37B active) | ~80GB | Frontier performance, MoE so faster than size suggests. Needs serious hardware. |
| **Llama 3.3-70B** | 70B | ~42GB (Q4) | Meta's best. Huge ecosystem, well-documented fine-tuning. |
| **Phi-4** | 14B | ~10GB | Punches way above weight. Runs on modest hardware. Good starting point. |

**My recommendation:** Start with **Qwen 2.5-32B or Qwen 3-32B**. Best balance of capability, fine-tuning support, and hardware requirements. Runs well on a single RTX 4090 or 2x 3090s.

---

**🔨 Building Your Own LLM — Worth It?**

**From scratch:** No. Training a base model costs $10M-100M+ in compute. GPT-4 cost ~$100M. DeepSeek-V3 was "cheap" at $5.5M. Not viable for individuals.

**BUT — what you're already doing is the right approach:**

1. **Fine-tuning** (what the scaffold does)
   - Take a strong base model (Qwen, Llama)
   - Train on your corrections, preferences, style
   - Cost: Hours on a single GPU, not millions
   - Result: Model that thinks like you want

2. **Continued pre-training** (stretch goal)
   - Feed it domain-specific knowledge
   - More expensive than fine-tuning, less than scratch
   - Could add your notes, research, writing style

3. **The real path to "your own LLM":**
   ```
   Open base model (Qwen/Llama)
        ↓
   Fine-tune with scaffold data (DPO/SFT)
        ↓
   Your personalised model
        ↓
   Keep training as more data accumulates
        ↓
   Eventually: model that genuinely reflects your preferences
   ```

**The scaffold IS the "build your own LLM" path** — just without the pointless expense of training from scratch.

---

**Hardware Recommendation for Dedicated System:**

For running Qwen 32B + fine-tuning:
- **Budget:** RTX 4090 (24GB) — ~£1,800
- **Better:** 2x RTX 3090 (48GB total) — ~£1,400 used
- **Ideal:** RTX 6000 Ada (48GB) — ~£6,000

Want me to spec out a full build?
user: [Telegram Finn Mckie id:6047368408 +7m 2026-02-03 11:51 UTC] ok lets postpone this discussion
[message_id: 3137]
assistant: Noted. I'll save this research to memory so we can pick it up whenever you're ready. 👍

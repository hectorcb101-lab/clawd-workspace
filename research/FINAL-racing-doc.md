# IBM AI Racing League — The Master Doc

**Team doc — February 2026**
**Written by Finn | MSc AI, Queen Mary University of London**

---

## 1. What Is This Competition?

Right, quick rundown. IBM launched the AI Racing League in January 2026. It's a global competition where you build an AI agent to race cars in [TORCS](https://sourceforge.net/projects/torcs/) (The Open Racing Car Simulator) — an open-source racing sim that's been around for ages in the RL research community.

The setup:

- **Track:** Laguna Seca — proper motorsport circuit, tight corners, elevation changes, and the infamous Corkscrew
- **Car:** F1-style with realistic physics (understeer is a nightmare)
- **Challenge:** Time trial — fastest lap wins
- **Current best:** ~1:47.84 by "The MonDragons" — a team from our own uni, QMUL
- **Tools:** IBM Granite 4.0 for code assistance, IBM SkillsBuild for training courses
- **Cost:** Absolutely free. TORCS is open-source, IBM tools are free, no entry fee
- **Discord:** [discord.gg/G3w8TfF4pG](https://discord.gg/G3w8TfF4pG)

We're currently in the Early Adopter phase — a pilot program. Think of it as the beta season. Get in now, shape the future rounds, and build a competitive edge before the full global launch.

The key thing to understand: **this is a software competition**. Everyone gets the same car, same track, same physics. The only differentiator is your algorithm.

---

## 2. What Are We Up Against?

### The MonDragons (QMUL) — Current Leaders

These lot hold the fastest time: **1:47.84** on Laguna Seca. They're from our university, which is both motivating and slightly annoying.

Their approach? **Pure rule-based.** No machine learning, no neural networks. Just hand-coded rules reading sensor data and making decisions.

Their progression tells you a lot:
- Started at ~2:33 with the old car model
- Physics changed (new F1 car) → broke everything → back to ~2:30
- Weeks of iterative tuning → **1:47.84**

What they did well:
- Used IBM Granite to understand the codebase (smart, not lazy)
- Built an automated testing pipeline — CSV logging, subprocess automation, the works
- Figured out that **gradual braking** beats heavy braking (the F1 car understeers horrifically with aggressive inputs)
- Set acceleration to zero through corners (prevents the car pushing wide)
- Special handling for the Corkscrew and the final corner

Their code's on GitHub: [Simple-wood/IBM-TORCs](https://github.com/Simple-wood/IBM-TORCs). Definitely worth studying.

**Blog post:** Search "Racing the Code: Building and optimizing an autonomous car with TORCS and IBM SkillsBuild" on Medium.

### Everyone Else

Honestly? We don't know much. The Early Adopter program is still new, and no other teams have published their approaches. Based on the Discord and what IBM are saying, most teams are taking the rule-based route. Makes sense — it's the path of least resistance when you've got 4-6 weeks.

**This is our edge.** If everyone else is doing rule-based, and we bring RL to the table, we're playing a different game entirely.

---

## 3. The Approaches

There are fundamentally three ways to attack this:

### A. Rule-Based (What Everyone's Doing)

You read the sensors, you write if-statements. Corner detected? Slow down. Straight detected? Floor it. It's programming, not machine learning.

**Pros:**
- Fast to get working (days, not weeks)
- Easy to debug — you wrote every rule, you know why it does what it does
- Predictable behaviour
- The MonDragons proved it works

**Cons:**
- Performance ceiling. Rules can only be as clever as the person writing them
- Doesn't generalise — hand-tuned for one track
- Can't discover non-intuitive racing lines
- Diminishing returns on optimisation

### B. Model-Free RL (PPO, SAC, DDPG)

Train a neural network by letting it drive millions of laps, rewarding fast times and penalising crashes. The agent discovers its own strategy.

**Pros:**
- Can discover racing lines humans wouldn't think of
- Consistently beats rule-based in every major racing competition (DeepRacer, Gran Turismo, F1TENTH)
- Generalises better across tracks
- Performance ceiling is much higher

**Cons:**
- Needs proper reward function design (garbage in, garbage out)
- Training takes hours/days, not minutes
- Can be unstable — the agent might just learn to do doughnuts
- Harder to debug when things go wrong

**Best algorithms for this:**
- **PPO** (Proximal Policy Optimisation) — stable, well-documented, the safe choice
- **SAC** (Soft Actor-Critic) — better sample efficiency, works well with continuous actions
- **DDPG** (Deep Deterministic Policy Gradient) — the OG for continuous control, but can be unstable

### C. Model-Based RL (MuZero, DreamerV3, World Models)

Like model-free RL, but the agent also learns a model of how the world works. It can then "imagine" future states and plan ahead, rather than just reacting.

**Pros:**
- Much more sample-efficient (learns from less data)
- Planning capability — can think ahead, not just react
- Better generalisation in theory
- Potential for transfer learning

**Cons:**
- More complex to implement
- If the learned model is wrong, everything downstream is wrong
- Computationally heavier
- Less battle-tested in racing specifically

---

## 4. Why RL Wins

I'm not being theoretical here. The evidence from other competitions is overwhelming.

### Gran Turismo (Sony/DeepMind)

DeepMind built a vision-based RL agent that achieved **superhuman performance** in Gran Turismo 7. Published in Nature. Beat champion-level human drivers consistently. Not by a little — by a lot.

Key insight from their work: automated reward design (letting the system discover its own reward structure) outperformed hand-crafted rewards. End-to-end learning from raw pixels to control outputs worked better than modular approaches.

Source: [Nature paper](https://www.nature.com/articles/s41586-021-04357-7), arXiv: [2504.09021](https://arxiv.org/abs/2504.09021)

### AWS DeepRacer

Years of community data show that top performers use RL with iterative clone-and-train strategies. The top 2% train 30-40 model versions over 3-4 weeks, rotating across diverse tracks to prevent overfitting. 60-minute training sessions are the sweet spot.

Source: [Sam Marsman's top 2% strategy](https://medium.com/@marsmans/how-i-got-into-the-top-2-in-aws-deepracer-32127a364212)

### F1TENTH

A 2025 paper (arXiv: [2504.02420](https://arxiv.org/abs/2504.02420)) showed RL policies **outperforming expert human drivers** on 1/10 scale race cars. Zero-shot real-world deployment achieved with domain randomisation.

### Indy Autonomous Challenge

140+ mph autonomous racing at Indianapolis. The key finding? **Sparse competitive rewards** (win/lose) outperform dense behavioural rewards (follow-this-line). Strategic behaviours like overtaking and blocking emerge naturally.

### A2RL (Abu Dhabi)

Over 250 km/h autonomous racing. Successful teams programmed **decisive overtaking** — not timid approaches. Different AI "personalities" emerged (aggressive vs conservative). Adaptive pace control beat constant-speed approaches.

Source: [A2RL Season 2 analysis](https://a2rl.io/blog/23/A2RL-Season-2-A-Breakthrough-Year-for-Autonomous-Racing)

**The pattern is clear:** in every single racing competition where RL has been properly implemented, it beats rule-based approaches. Every. Single. One.

The only reason rule-based is winning IBM Racing League right now is because nobody's had time to set up RL properly yet.

---

## 5. MuZero Deep Dive

### What It Is

MuZero (DeepMind, 2019) is a model-based RL algorithm that learns three things simultaneously:
1. A **representation function** — how to encode observations into a latent state
2. A **dynamics function** — how the world changes given an action (the "world model")
3. A **prediction function** — what the value and policy are at each state

It then uses Monte Carlo Tree Search (MCTS) to plan ahead using the learned model. It's what beat Go, Chess, Shogi, and Atari — all without being told the rules of the game.

Papers: Original ([arXiv:1911.08265](https://arxiv.org/abs/1911.08265)), Sampled MuZero for continuous actions ([arXiv:2104.06303](https://arxiv.org/abs/2104.06303)), EfficientZero ([arXiv:2111.00210](https://arxiv.org/abs/2111.00210))

### Can We Use It for TORCS?

**Honest answer: yes, but it's the wrong tool for the job.**

Here's the problem. MuZero was designed for **discrete action spaces** — board games, Atari. TORCS needs continuous control: steering [-1, 1], throttle [0, 1], brake [0, 1]. That's a 3D continuous action space.

Sampled MuZero (Hubert et al., 2021) addresses this by sampling candidate actions instead of enumerating them, but:
- There's **no open-source implementation** of Sampled MuZero
- You'd have to build it from pseudocode in the paper
- Nobody has done MuZero on TORCS. Ever. Not in any published paper, not on GitHub, nowhere.

**Best open-source MuZero implementations:**

| Repo | Stars | Continuous Actions? | Status |
|------|-------|-------------------|--------|
| [werner-duvaud/muzero-general](https://github.com/werner-duvaud/muzero-general) | ~2.5k | ⚠️ Experimental branch | Best option |
| [YeWR/EfficientZero](https://github.com/YeWR/EfficientZero) | ~1k | ❌ Discrete only | Great sample efficiency |
| [koulanurag/muzero-pytorch](https://github.com/koulanurag/muzero-pytorch) | ~350 | ❌ No | Educational only |

**Training time estimates (single GPU):**

| Setup | Hardware | Time | Expected Result |
|-------|----------|------|----------------|
| Sensor input, simple track | RTX 3080 | 24-48 hrs | Basic lane keeping |
| Vision input, single track | RTX 3090 | 3-5 days | Stable racing |
| Vision, multi-track | RTX 3090 | 1-2 weeks | Generalisation |
| Human-competitive | 2-4x RTX 3090 | 3-4 weeks | Near-human laps |

For comparison, DDPG on TORCS gets results in 12-24 hours on a single GPU. MuZero is significantly slower.

### My Honest Assessment

MuZero on TORCS would be **novel research** — genuinely, nobody has done it. That's cool for a paper. But if our goal is to **win the competition**, it's a risky bet. The continuous action problem, the lack of existing code, the compute requirements, the tuning nightmare — it all adds up.

If we go MuZero, we're signing up for 3-4 months of focused work with a real chance it doesn't outperform a well-tuned PPO baseline.

**Verdict:** 🟡 High-risk, high-reward. Great for research. Questionable for winning a competition on a deadline.

---

## 6. DreamerV3 — The Dark Horse 🐴

Right, this is where it gets interesting. I reckon **DreamerV3 is the play here**.

### What It Is

DreamerV3 (Hafner et al., Nature 2025) is a model-based RL algorithm that:
1. Learns a **world model** from experience
2. "Dreams" — generates imagined trajectories in latent space
3. Trains an actor-critic policy entirely inside the dream

Paper: [arXiv:2301.04104](https://arxiv.org/abs/2301.04104)
Code: [danijar/dreamerv3](https://github.com/danijar/dreamerv3) (2.8k stars)

### Why It's Better Than MuZero for Racing

**Native continuous control.** DreamerV3 was designed from the ground up for continuous action spaces. No discretisation hacks, no action sampling workarounds. It just works.

**Proven on driving.** [CarDreamer](https://arxiv.org/abs/2405.09111) is an open-source driving platform built on DreamerV3. It's been successfully trained on autonomous racing benchmarks. The world model is particularly good at learning physics — exactly what we need.

**Single config, 150+ tasks.** The same hyperparameters work across board games, Atari, continuous control, Minecraft, everything. Published in Nature. No tuning needed. This is massive — MuZero would need weeks of hyperparameter search.

**Training speed:**
- Minecraft (finding diamond): ~12 hours, single GPU
- Continuous control tasks: 6-24 hours
- TORCS estimate: 12-36 hours on an A100

**Simpler integration.** Standard Gym interface. Clean codebase. Active community. You could have it running on TORCS in 1-2 days.

### DreamerV3 vs MuZero — Head to Head

| Factor | MuZero | DreamerV3 |
|--------|--------|-----------|
| Continuous actions | ⚠️ Hack required | ✅ Native |
| Driving tasks | ❌ Never tested | ✅ CarDreamer exists |
| Training time (TORCS est.) | 30-60 hrs | 12-36 hrs |
| Hyperparameter tuning | 🔴 Extensive | 🟢 Minimal |
| Open-source quality | Good (discrete) | Excellent |
| Integration effort | 2-3 days + tuning | 1-2 days |
| Research novelty | Higher (nobody's done it) | Medium |

### Risks

- **Memory requirements** — larger model, might struggle on 16GB GPUs. Solvable with smaller network configs.
- **Sparse rewards** — racing can have sparse feedback (you only get a lap time at the end). DreamerV3 handles this better than most, but reward shaping still helps.
- **Nobody's done DreamerV3 on TORCS either** — we'd still be in uncharted territory, just with better odds.

### My Take

If I had to bet our competition entry on one approach, it'd be DreamerV3. It's designed for exactly this kind of problem. The training speed means we can iterate fast. The lack of hyperparameter faff means less time wasted on tuning and more time on actual racing performance.

MuZero is the sexier research story. DreamerV3 is the one that actually wins the race.

---

## 7. LLMs for Racing?

**Spoiler: no. But hear me out on where they're useful.**

Can you use a large language model to drive a car? Technically, some people have tried. Practically, it's rubbish for real-time control. LLMs operate at second-scale latency. Racing needs millisecond decisions. The physics is too complex, the action space too precise, and the cost of running inference on every control step would be astronomical.

**But LLMs are bloody useful as development tools:**

1. **IBM Granite for code understanding** — The MonDragons used it extensively. Feed it the TORCS sensor code, ask it what each variable means, get optimisation suggestions. This is genuinely useful.

2. **Reward function debugging** — "Here's my reward function, here are the training curves, why is my agent driving in circles?" An LLM can spot logical errors faster than staring at code for hours.

3. **Hyperparameter suggestions** — "I'm training PPO on a continuous control racing task with these observation/action spaces. What learning rate and batch size should I start with?"

4. **Code refactoring** — Clean up messy training scripts, modularise code, add logging.

5. **Paper summarisation** — Feed it an arXiv paper, get the key insights in 2 minutes instead of 30.

IBM wants us to use Granite. Fine. Use it as a development accelerator, not as the racing agent. That's the smart play.

---

## 8. Our Strategy — 6-Month Plan

Assuming 4 team members, here's how I'd structure this:

### Month 1: Foundation & Rule-Based Baseline

**Goal:** Working car, sub-2:00 lap time, automated testing pipeline.

- Week 1-2: Environment setup. Everyone gets TORCS running. Study the codebase. Complete IBM SkillsBuild courses (Design Thinking + Granite fundamentals — tick the boxes).
- Week 3-4: Implement rule-based baseline following MonDragons' approach. Build automated testing harness (CSV logging, subprocess automation). Get a lap time we can measure against.

**Deliverables:** Working baseline, automated testing pipeline, documented sensor understanding.

### Month 2: RL Infrastructure & First Models

**Goal:** RL agent that completes laps consistently.

- Week 5-6: Set up RL training infrastructure. Install Stable Baselines3, set up gym_torcs wrapper ([ugo-nama-kun/gym_torcs](https://github.com/ugo-nama-kun/gym_torcs) or [gerkone/pyTORCS-docker](https://github.com/gerkone/pyTORCS-docker)). Design reward function (multi-component: speed + track position + smoothness + progress - crashes).
- Week 7-8: Train PPO/SAC baselines. Compare to rule-based. Identify failure modes. Start DreamerV3 integration in parallel.

**Deliverables:** PPO baseline with lap times, DreamerV3 environment wrapper ready.

### Month 3: DreamerV3 Training & Optimisation

**Goal:** DreamerV3 agent that matches or beats rule-based.

- Week 9-10: First DreamerV3 training runs. Sensor-based first (faster), then add vision if compute allows. Analyse world model quality — is it learning the physics?
- Week 11-12: Reward function iteration. Multi-track training (if multiple tracks available). Compare DreamerV3 vs PPO vs rule-based systematically.

**Deliverables:** Best-performing RL agent, comparative analysis, optimised reward function.

### Month 4: Track-Specific Optimisation

**Goal:** Beat 1:47.84.

- Corner-specific tuning. The Corkscrew needs special attention — elevation change + tight turn + blind entry. The final corner matters for exit speed onto the main straight.
- Stress testing: 100+ consecutive laps without crashes. Reliability matters as much as raw speed.
- Fine-grained reward adjustments. Context-dependent rewards: fast on straights, controlled through corners.

**Deliverables:** Sub-1:48 lap time (target: sub-1:45).

### Month 5: Advanced Techniques

**Goal:** Push the boundaries.

- Self-play if head-to-head racing is added in future rounds
- Domain randomisation for robustness
- Ensemble approaches (run multiple agents, take the best)
- MuZero exploration if DreamerV3 has plateaued (research angle)

**Deliverables:** Competition-ready agent with backup strategies.

### Month 6: Competition Prep & Documentation

**Goal:** Submit, document, present.

- Final agent selection and validation
- Write blog post (IBM loves this — the MonDragons got LinkedIn recognition from IBM execs)
- Prepare presentation/demo
- Submit to competition
- Write up for potential publication (if DreamerV3 results are novel)

**Deliverables:** Submission, blog post, documentation.

---

## 9. Team Roles

With 4 people, here's how I'd split it:

### Person 1: Environment & Infrastructure Lead
- TORCS setup and maintenance
- Gym wrapper integration
- Automated testing pipeline (CSV logging, subprocess scripts)
- Docker/cloud GPU management
- Handles the bloody memory leak issues in TORCS

### Person 2: RL Engineer (Primary)
- Algorithm implementation (PPO, SAC, DreamerV3)
- Reward function design and iteration
- Training management and hyperparameter tuning
- Model evaluation and comparison

### Person 3: RL Engineer (Secondary) / Data & Analysis
- Supports RL training
- Log analysis and visualisation (TensorBoard, matplotlib)
- Track-specific optimisation
- Sensor data analysis — understanding what the car "sees"
- Benchmark tracking

### Person 4: Research & Strategy / IBM Integration
- Literature review (keep up with new papers)
- IBM Granite integration — use it for code review, optimisation suggestions
- Competition rules monitoring
- Blog post and documentation
- Competitor analysis (what are other teams doing?)

**Everyone** should understand the basics of all roles. Bus factor of 1 is unacceptable.

---

## 10. Compute & Budget

### GPU Requirements

**Minimum viable:**
- 1x RTX 3080 (10GB) or equivalent cloud GPU
- Enough for PPO/SAC training and small DreamerV3 runs
- ~$0.35/hr on GCP (T4) or ~$0.50/hr on Lambda Labs

**Recommended:**
- 1x A100 (40GB) — proper DreamerV3 training
- ~$1.50/hr on Lambda Labs
- Training runs: 12-36 hours each

**Budget estimate (3 months of active training):**

| Item | Cost |
|------|------|
| GPU compute (5-10 training runs on A100) | £150-400 |
| TORCS + tools | Free |
| IBM Granite / SkillsBuild | Free |
| Cloud storage | ~£20 |
| **Total** | **£170-420** |

If we can get university GPU access (and we should — QMUL has compute clusters), the cost drops to basically zero.

### Free Options

- **Google Colab Pro** (£10/month) — limited but usable for smaller runs
- **QMUL HPC cluster** — free for students, has GPUs
- **Lambda Labs free credits** — sometimes available for students
- **Kaggle notebooks** — free GPU time, limited hours

---

## 11. Risks and What Could Go Wrong

Let's be honest about the failure modes.

### High Risk

**RL doesn't beat rule-based in time.**
This is the big one. If we spend 3 months on RL and the MonDragons' rule-based approach is still faster, we've backed the wrong horse. Mitigation: always maintain and improve the rule-based baseline in parallel. If RL isn't working by month 3, pivot hard.

**TORCS environment is a pain in the arse.**
Memory leaks, headless mode issues, physics that change between car models. Multiple teams have been burned by this. Mitigation: use Docker ([pyTORCS-docker](https://github.com/gerkone/pyTORCS-docker)), automate restarts, budget extra time for environment debugging.

**Reward hacking.**
The agent finds some exploit in the reward function that gets high reward without actually racing well (driving backwards, spinning in circles, finding a corner to cheese). Mitigation: careful reward design, include lap completion requirements, test with multiple random seeds.

### Medium Risk

**Compute bottleneck.**
If we can't get enough GPU time, training cycles slow to a crawl and we can't iterate fast enough. Mitigation: secure university compute access early, budget for cloud GPUs.

**Team member drops out.**
With only 4 people, losing one is losing 25% of capacity. Mitigation: cross-training, good documentation, shared code ownership.

**Competition rules change.**
IBM might add head-to-head racing, change the car physics, add new tracks. Mitigation: build for generalisation, not just one track.

### Low Risk

**Someone else does RL first.**
If another team brings RL and beats us, we're in a straight performance fight. Not the end of the world — just means we need to be better. Mitigation: iterate fast, don't wait for perfection.

**DreamerV3 doesn't work on TORCS at all.**
Unlikely given its track record on similar tasks, but possible. Mitigation: PPO/SAC as fallback.

---

## 12. Key Repos and Resources

### Must-Have Repos

| Repo | What For |
|------|----------|
| [Simple-wood/IBM-TORCs](https://github.com/Simple-wood/IBM-TORCs) | Current winning approach — study this first |
| [ugo-nama-kun/gym_torcs](https://github.com/ugo-nama-kun/gym_torcs) | Standard Gym wrapper for TORCS (410⭐) |
| [gerkone/pyTORCS-docker](https://github.com/gerkone/pyTORCS-docker) | Docker-based TORCS setup (modern, clean) |
| [danijar/dreamerv3](https://github.com/danijar/dreamerv3) | DreamerV3 implementation (2.8k⭐) |
| [sarikayamehmet/DRL-Torcs](https://github.com/sarikayamehmet/DRL-Torcs) | PPO + DDPG on TORCS (reference) |
| [stable-baselines3](https://stable-baselines3.readthedocs.io/) | Industry-standard RL library |
| [werner-duvaud/muzero-general](https://github.com/werner-duvaud/muzero-general) | MuZero implementation (if going that route) |
| [ucd-dare/CarDreamer](https://github.com/ucd-dare/CarDreamer) | DreamerV3 for driving specifically |

### Papers Worth Reading

**Essential:**
1. DreamerV3: "Mastering Diverse Domains through World Models" — [arXiv:2301.04104](https://arxiv.org/abs/2301.04104)
2. Gran Turismo superhuman agent — [arXiv:2504.09021](https://arxiv.org/abs/2504.09021)
3. RL racing beats human experts — [arXiv:2504.02420](https://arxiv.org/abs/2504.02420)
4. RLPP zero-shot sim-to-real racing — [arXiv:2501.17311](https://arxiv.org/abs/2501.17311)

**Background:**
5. MuZero original — [arXiv:1911.08265](https://arxiv.org/abs/1911.08265)
6. EfficientZero — [arXiv:2111.00210](https://arxiv.org/abs/2111.00210)
7. CarDreamer — [arXiv:2405.09111](https://arxiv.org/abs/2405.09111)
8. Reward design for racing (Nature Scientific Reports, 2025) — [DOI](https://www.nature.com/articles/s41598-025-27702-6)
9. On-board RL for racing — [arXiv:2505.07321](https://arxiv.org/abs/2505.07321)

### Competition & Community

- **IBM Racing League Discord:** [discord.gg/G3w8TfF4pG](https://discord.gg/G3w8TfF4pG)
- **IBM SkillsBuild:** [skillsbuild.org](https://skillsbuild.org/)
- **IBM Granite:** [ibm.com/granite](https://www.ibm.com/granite)
- **TORCS:** [sourceforge.net/projects/torcs](https://sourceforge.net/projects/torcs/)

### Other Racing AI Communities (for learning)

- AWS DeepRacer community Slack: [deepracing.io](https://deepracing.io)
- F1TENTH: [f1tenth.org](https://f1tenth.org/)
- Learn-to-Race: [learn-to-race.org](https://learn-to-race.org/)
- Indy Autonomous Challenge: [indyautonomouschallenge.com](https://www.indyautonomouschallenge.com)

---

## 13. Sources

All claims in this document are backed by the following sources. If something doesn't have a link, it came from the research files compiled on 8 Feb 2026 from 80+ sources via Exa neural search.

1. MonDragons blog — [Medium](https://medium.com/@joesayskishal/racing-the-code-building-and-optimizing-an-autonomous-car-with-torcs-and-ibm-skillsbuild-ba32ed6fb5fe)
2. MonDragons code — [GitHub](https://github.com/Simple-wood/IBM-TORCs)
3. Gran Turismo superhuman RL — [Nature](https://www.nature.com/articles/s41586-021-04357-7)
4. Gran Turismo champion-level agent (2025) — [arXiv:2504.09021](https://arxiv.org/abs/2504.09021)
5. DeepRacer top 2% strategy — [Medium](https://medium.com/@marsmans/how-i-got-into-the-top-2-in-aws-deepracer-32127a364212)
6. A2RL Season 2 — [a2rl.io](https://a2rl.io/blog/23/A2RL-Season-2-A-Breakthrough-Year-for-Autonomous-Racing)
7. RL beats expert humans in racing — [arXiv:2504.02420](https://arxiv.org/abs/2504.02420)
8. RLPP zero-shot transfer — [arXiv:2501.17311](https://arxiv.org/abs/2501.17311)
9. On-board RL for racing — [arXiv:2505.07321](https://arxiv.org/abs/2505.07321)
10. MuZero original paper — [arXiv:1911.08265](https://arxiv.org/abs/1911.08265)
11. Sampled MuZero — [arXiv:2104.06303](https://arxiv.org/abs/2104.06303)
12. EfficientZero — [arXiv:2111.00210](https://arxiv.org/abs/2111.00210)
13. DreamerV3 — [arXiv:2301.04104](https://arxiv.org/abs/2301.04104)
14. CarDreamer — [arXiv:2405.09111](https://arxiv.org/abs/2405.09111)
15. Reward design for generalisable RL — [Nature Scientific Reports](https://www.nature.com/articles/s41598-025-27702-6)
16. AWS DeepRacer physical racing — [AWS Blog](https://aws.amazon.com/blogs/machine-learning/aws-deepracer-how-to-master-physical-racing)
17. DeepRacer reward function guide — [Instructables](https://www.instructables.com/How-to-Understand-and-Code-a-Winning-Student-AWS-D/)
18. IBM Granite — [ibm.com/granite](https://www.ibm.com/granite)
19. IBM SkillsBuild — [skillsbuild.org](https://skillsbuild.org/)
20. MuZero-General — [GitHub](https://github.com/werner-duvaud/muzero-general)
21. EfficientZero code — [GitHub](https://github.com/YeWR/EfficientZero)
22. gym_torcs — [GitHub](https://github.com/ugo-nama-kun/gym_torcs)
23. DreamerV3 code — [GitHub](https://github.com/danijar/dreamerv3)
24. DRL-Torcs (PPO/DDPG) — [GitHub](https://github.com/sarikayamehmet/DRL-Torcs)
25. SAC on TORCS — [GitHub](https://github.com/kaushikb258/SAC_Torcs)

---

*This document compiles research from 7 detailed reports, covering rules, strategies, technical approaches, MuZero feasibility, competitor analysis, and implementation paths. Total sources: 80+. Last updated: 8 February 2026.*

*Written as a team reference. Not for publication — this is how we talk internally. If IBM asks, we can write a polished version later.*

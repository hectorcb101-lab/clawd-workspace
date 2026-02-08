# 🏁 IBM AI Racing League — The Winning Playbook

**Compiled:** 8 February 2026 | **For:** Finn McKie  
**Status:** You're in. Now let's win.

---

## TL;DR — The 5 Things That Win This Competition

1. **Master TORCS sensors** — understand every data point the car gives you
2. **Iterate relentlessly** — 30-40 model versions, automated testing, log everything
3. **Beat the Corkscrew** — Laguna Seca's signature corner is where races are won/lost
4. **Use IBM Granite smartly** — for code analysis, optimisation suggestions, and debugging
5. **Go beyond rule-based** — the current leader (1:47.84) used rules; RL could smash that

---

## 🎯 Competition Overview

| Detail | Info |
|--------|------|
| **Platform** | TORCS (The Open Racing Car Simulator) — free, open-source |
| **Track** | Laguna Seca — tight corners, elevation changes, the famous Corkscrew |
| **Vehicle** | F1-style car with realistic physics |
| **Challenge** | Time trial — fastest lap wins |
| **Current Best** | ~1:47.84 (Team "The MonDragons" — QMUL) |
| **Tools** | IBM Granite 4.0, IBM SkillsBuild, Python framework |
| **Discord** | https://discord.gg/G3w8TfF4pG |
| **Cost** | Free — all tools and platforms |

**Key fact:** A team from YOUR university (QMUL) currently holds the fastest time. That's the benchmark to beat.

---

## 🧠 Two Paths to Victory

### Path A: Rule-Based (What Current Leaders Use)

**How it works:** Define racing rules programmatically using sensor data.

**The MonDragons' approach:**
1. Read track sensors (distances to track edges at various angles)
2. Detect corners vs straights
3. Reduce speed approaching corners (gradual braking — NOT heavy braking)
4. Accelerate on straights
5. Set acceleration to zero in corners (prevents understeer)

**Their progression:**
- Baseline: ~2:33 → After F1 adaptation: ~2:30 → After optimisation: **1:47.84**

**Strengths:** Easier to debug, faster to iterate, predictable behaviour  
**Weakness:** Performance ceiling — rules can only go so fast

### Path B: Reinforcement Learning (The Edge)

**Why this could win:** RL agents consistently achieve faster lap times than rule-based systems in every major racing competition (DeepRacer, Gran Turismo, F1TENTH).

**How it works:** Train a neural network to drive by rewarding fast lap times and penalising crashes.

**Recommended approach:**
- **Algorithm:** PPO (Proximal Policy Optimization) — most stable, well-documented
- **Alternative:** SAC (Soft Actor-Critic) — better sample efficiency
- **Framework:** Stable Baselines3 + PyTorch
- **Architecture:** CNN (for sensor processing) + LSTM (for temporal reasoning)

**Why no one's done it yet:** Time constraints in the Early Adopter program. But with proper setup, RL can discover non-intuitive racing lines that rules can't.

### 🔥 My Recommendation: Hybrid Approach

1. **Start with rule-based** to get a working car quickly (Week 1)
2. **Use that as a baseline** for RL training (the car doesn't crash = good starting point)
3. **Train RL on top** using the rule-based policy as a warm start
4. **Best of both worlds** — reliability of rules + speed of RL

---

## 🏎️ Laguna Seca — Track Breakdown

### Critical Corners

**The Corkscrew (Turns 8-8A):**
- Signature corner — blind entry with massive elevation drop
- Where most crashes happen
- **Strategy:** Heavy braking before entry, zero acceleration through, gradual power on exit
- The MonDragons specifically called this out as requiring special handling

**Final Corner (Turn 11):**
- Fast exit onto the main straight — getting this right = faster lap time
- **Strategy:** Late apex, maximise exit speed onto straight

**Turn 2 (Andretti Hairpin):**
- Tight, slow corner after the fast front straight
- **Strategy:** Hard braking zone, patience through corner, early power

### General Approach
- **Straights:** Maximum speed — detect using sensor data (equal distances on both sides)
- **Corners:** Gradual braking (NOT sudden), zero or minimal acceleration through apex
- **Understeer is the killer:** The F1 car understeers badly with heavy braking — always brake gradually

---

## ⚙️ Technical Setup

### What You Get
- `gym_torcs` files — Python interface to TORCS
- `torcs_jm_par.py` — Baseline AI driver implementation
- Sensor data: track edge distances, speed, position, distance-ahead
- F1 car with realistic physics model

### Sensor Data (Your Eyes)
- **Track sensors:** Distances to track edges at multiple angles (like radar)
- **Speed sensors:** Current velocity
- **Position tracking:** Where you are on track
- **Distance-ahead:** Gap to anything in front

### Recommended Dev Stack
```
Python 3.x
pandas (data logging & analysis)
subprocess (TORCS automation)
matplotlib (visualising lap data)
stable-baselines3 (if going RL route)
pytorch (neural network backbone)
```

### Automated Testing (CRITICAL)
The MonDragons' biggest advantage was automation:
```python
# Concept: Automated parameter sweep
for speed in [150, 160, 170, 180]:
    for brake_point in [0.3, 0.4, 0.5]:
        run_torcs(speed, brake_point)
        log_to_csv(speed, brake_point, lap_time)
```
- Log every parameter combination + lap time to CSV
- Use pandas to analyse which combos are fastest
- Automate TORCS launch with subprocess
- Keep a `fastest.py` with your best parameters

---

## 📊 Winning Strategies from Other Competitions

### From AWS DeepRacer (Top 2% Strategy)

| Strategy | Detail |
|----------|--------|
| **Iterate heavily** | 30-40 model versions over 3-4 weeks |
| **Train on diverse tracks** | Never train twice on same track (prevents overfitting) |
| **60-min training sessions** | Sweet spot — enough to learn, not enough to overfit |
| **Clone and improve** | Don't restart from scratch — clone best model and iterate |
| **Analyse logs obsessively** | Download training logs, visualise what the model "sees" |
| **Start simple, add complexity** | 7-10 discrete actions → expand to 15-20 as model matures |

### From Gran Turismo AI (Sony Research)

- RL agents achieved **superhuman performance**
- Key insight: **Automated reward design** beats hand-crafted rewards
- End-to-end learning (raw inputs → control outputs) outperforms modular approaches
- Self-play training generates more robust policies than solo optimisation

### From A2RL (Abu Dhabi Autonomous Racing League)

- Successful teams programmed **decisive overtaking** — not timid approaches
- AI developed distinct "personalities" (aggressive vs conservative)
- **250+ km/h autonomous racing** achieved with proper sensor fusion
- Adaptive pace control > constant-speed approaches

### From Indy Autonomous Challenge

- It's fundamentally a **software competition** — same hardware, different algorithms
- **Sparse competitive rewards** (win/lose) outperform dense behavioural rewards
- 140+ mph autonomous racing achieved at Indianapolis
- Sim-to-real gap is the biggest challenge

---

## 🎯 Reward Function Design (If Using RL)

### Multi-Component Reward (Proven Template)

```python
def reward_function(params):
    reward = 0.0
    
    # 1. Speed reward (40% weight) — faster = better
    speed_reward = params['speed'] / MAX_SPEED
    reward += 0.4 * speed_reward
    
    # 2. Centre-line reward (25% weight) — stay on track
    distance_from_centre = abs(params['distance_from_centre'])
    centre_reward = max(0, 1.0 - (distance_from_centre / TRACK_WIDTH))
    reward += 0.25 * centre_reward
    
    # 3. Progress reward (20% weight) — complete laps
    reward += 0.2 * params['progress']
    
    # 4. Smoothness penalty (15% weight) — no jerky steering
    steering_change = abs(params['steering'] - params['prev_steering'])
    smoothness = max(0, 1.0 - steering_change)
    reward += 0.15 * smoothness
    
    # 5. Crash penalty — heavy negative reward
    if params['crashed']:
        reward = -1.0
    
    return reward
```

### Key Principles
- **Balance speed and safety** — pure speed reward = crashes
- **Penalise steering jitter** — smooth lines are faster lines
- **Reward progress** — completing laps matters
- **Context-dependent speed** — fast on straights, slow in corners
- **Step efficiency** — fewer steps to complete a lap = faster time

---

## 🛠️ IBM Tools — How to Use Them

### IBM Granite 4.0

**What it's for:** Code understanding, optimisation, debugging — NOT driving the car.

**Best uses:**
1. "Explain what this sensor code does" → understanding TORCS interface
2. "Suggest optimisations for this braking logic" → performance improvements
3. "What Python library would help automate TORCS testing?" → tooling
4. "Review this reward function for edge cases" → RL debugging
5. "Refactor this into clean functions" → code quality

**Access:** Via IBM SkillsBuild (free)

### IBM SkillsBuild Courses (Do These First)

| Course | Why It Matters |
|--------|---------------|
| IBM Design Thinking | Structure your approach, define requirements |
| IBM Granite Fundamentals | Use the AI tool effectively |
| AI/ML Basics | Foundation for RL approach |
| Python for AI | Strengthen coding skills |

---

## 📅 Winning Timeline (4-Week Plan)

### Week 1: Foundation
- [ ] Join Discord, download TORCS, set up environment
- [ ] Complete IBM SkillsBuild Design Thinking + Granite courses
- [ ] Study `gym_torcs` and `torcs_jm_par.py` thoroughly
- [ ] Understand ALL sensor data available
- [ ] Get a car completing laps (even slowly) — rule-based
- [ ] Study MonDragons' GitHub: https://github.com/Simple-wood/IBM-TORCs

### Week 2: Rule-Based Optimisation
- [ ] Implement straight detection → max speed on straights
- [ ] Implement gradual braking → smooth corner entry
- [ ] Special handling for Corkscrew and final corner
- [ ] Build automated testing pipeline (CSV logging + subprocess)
- [ ] Target: Sub-2:00 lap time
- [ ] Use Granite for code review and optimisation suggestions

### Week 3: Advanced Optimisation / RL Introduction
- [ ] Automated parameter sweep (speed targets, brake points, corner handling)
- [ ] Set up RL environment (Stable Baselines3 + TORCS gym wrapper)
- [ ] Train initial RL model using rule-based policy as warm start
- [ ] Compare RL vs rule-based performance
- [ ] Target: Sub-1:50 lap time

### Week 4: Final Push
- [ ] Fine-tune best approach (RL or rule-based)
- [ ] Stress-test reliability (100+ consecutive laps without crash)
- [ ] Optimise specific track sections (where are you losing time?)
- [ ] Final parameter sweep
- [ ] Target: Beat 1:47.84 (MonDragons' time)
- [ ] Document journey for blog post
- [ ] Submit

---

## ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Heavy braking | Causes understeer with F1 car | Gradual braking increments |
| Accelerating in corners | Pushes car wide, loses time | Zero acceleration through apex |
| Not testing after changes | Small bugs compound into big problems | Test EVERY change |
| Overfitting to one section | Fast corner entry but slow everywhere else | Optimise full lap |
| Ignoring automation | Manual testing is 10x slower | Build CSV logging + subprocess scripts |
| Training RL too long | >90 min sessions → overfitting | 60-min sweet spot |
| Single reward component | Pure speed = crashes; pure safety = slow | Multi-component reward |
| Not studying the track | Generic approach fails on Laguna Seca | Learn every corner's characteristics |

---

## 🔑 The Competitive Edge

### What Most Teams Will Do
- Rule-based approach
- Manual testing
- Generic corner handling
- Stop at "good enough"

### What Will Win
- **Hybrid rule-based + RL** (or pure RL with enough training time)
- **Automated testing pipeline** with systematic parameter sweeps
- **Track-specific optimisation** — different strategies for each corner
- **Obsessive data analysis** — visualise every lap, find every millisecond
- **Reliability + speed** — the fastest lap that you can consistently repeat

### Your Advantages
1. **AI MSc student** — you understand the theory behind RL, neural networks
2. **Developer background** — you can build the automation tools quickly
3. **Atlas (me)** — I can help with code, research, analysis 24/7
4. **QMUL connection** — the current leaders are from your university; network with them

---

## 📚 Key References

| Resource | Link |
|----------|------|
| MonDragons' Code | https://github.com/Simple-wood/IBM-TORCs |
| TORCS Documentation | https://sourceforge.net/projects/torcs/ |
| IBM SkillsBuild | https://skillsbuild.org/ |
| IBM Granite | https://www.ibm.com/granite |
| Competition Discord | https://discord.gg/G3w8TfF4pG |
| Stable Baselines3 | https://stable-baselines3.readthedocs.io/ |
| PPO Paper | https://arxiv.org/abs/1707.06347 |
| DeepRacer Community Tips | Search "AWS DeepRacer winning strategy" |

### Academic Papers Worth Reading
- "Champion-level Vision-based RL Agent for Competitive Racing in Gran Turismo 7" (2025)
- "Drive Fast, Learn Faster: On-Board RL for High Performance Autonomous Racing" (2025)
- "RLPP: A Residual Method for Zero-Shot Real-World Autonomous Racing" (2025)
- "Reward design and hyperparameter tuning for generalizable deep RL agents" — Nature Scientific Reports (2025)

---

## 💬 Final Thoughts

The current best time (1:47.84) was achieved with a rule-based approach by students who had 4-6 weeks. You have AI/ML knowledge most competitors don't. The gap between rule-based and RL in racing is massive — Sony's RL agent achieved **superhuman** Gran Turismo performance.

If you combine a solid rule-based baseline with RL optimisation and automated testing, you're not just competing — you're winning.

Let's build this thing. 🏁

---

*Compiled from 3 parallel research agents analysing 80+ sources*  
*Full detailed reports: `/home/ubuntu/clawd/research/ibm-racing-research-*.md`*

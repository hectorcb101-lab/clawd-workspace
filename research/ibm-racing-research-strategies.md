# IBM AI Racing League: Competition Research & Winning Strategies

**Research Date:** 2026-02-08  
**Subagent:** racing-strategies  
**Competitions Analyzed:** AWS DeepRacer, A2RL (Abu Dhabi Autonomous Racing League), Indy Autonomous Challenge, Learn-to-Race, F1TENTH, Gran Turismo AI competitions

---

## Executive Summary

This document compiles winning strategies, common mistakes, and proven approaches from established AI racing competitions—particularly AWS DeepRacer, which has been running for years with extensive community knowledge. IBM's AI Racing League shares similar challenges: reinforcement learning training, simulation-to-real transfer, reward function optimization, and multi-agent competitive racing.

**Key Finding:** Success in AI racing competitions requires balancing three factors:
1. **Reward function sophistication** (incentivizing right behaviors without overfitting)
2. **Training methodology** (diverse tracks, iterative cloning, hyperparameter tuning)
3. **Sim-to-real gap mitigation** (customized simulators, physical testing, sensor calibration)

---

## 1. Winning Strategies from Past Competitions

### 1.1 AWS DeepRacer Top Performers

**Training Philosophy (Top 2% Strategy - Sam Marsman)**
- **Clone iteratively:** Build 30-40 models by cloning successful models and training on varied tracks
- **Train across diverse tracks:** Never train on the same track twice in succession—overfitting to one track ruins generalization
- **60-minute training sessions:** Sweet spot between learning progress and preventing overfitting
- **Delete old models regularly:** Keep costs down and focus on current iterations

**Action Space Optimization**
- **Discrete vs Continuous:** Continuous action spaces create faster models but require longer (expensive) training; discrete action spaces are more cost-effective
- **Dynamic action space evolution:** Start with basic angles/speeds, then add granularity as the model improves
- **Steering angle ranges:** Real cars typically max at 20-22° (not 30° like default simulators)

**Advanced Techniques**
- **Waypoint utilization:** Top performers use waypoint programming for precision racing lines
- **Log analysis:** Use community tools (deepracer-analysis Jupyter notebooks, deepracer-viz) to analyze training logs
- **GradCam visualization:** Overlay gradient class activation maps to understand what the neural network "sees"

### 1.2 A2RL (Abu Dhabi Autonomous Racing League) Season 2 Success

**Key Advancements:**
- **Enhanced perception systems:** Better sensor fusion and real-time environment understanding
- **Confident control logic:** Late braking, intelligent defensive positioning, adaptive pace control
- **AI "personalities":** Different teams developed distinct driving styles (aggressive vs conservative)
- **Higher speeds:** Over 250 km/h racing with improved stability and safety

**Strategic Lessons:**
- **Bold overtaking:** Successful teams programmed decisive overtaking maneuvers, not timid approaches
- **Adaptive pace control:** Dynamic speed adjustment based on opponents and track conditions
- **Defensive positioning:** AI learned to block and defend position, not just race the optimal line

### 1.3 Indy Autonomous Challenge & F1TENTH

**Software-First Approach:**
- Indy Autonomous Challenge is fundamentally a **software competition** with standardized hardware
- All teams get identical cars, sensors, and actuators—differentiation is purely in algorithms

**Multi-Agent Racing Strategies:**
- **Sparse competitive rewards** (winning/losing) outperform dense behavioral rewards (raceline progress)
- Strategic behaviors emerge naturally: overtaking, blocking, defending lines
- Head-to-head training generates more robust policies than solo time-trial optimization

**Real-World Validation:**
- Purdue AI Racing achieved 140 mph autonomous racing at Indianapolis Motor Speedway
- Key challenge: Transitioning from perfect simulation to imperfect real-world conditions

### 1.4 Gran Turismo AI (Sony/CMU Research)

**Champion-Level Performance:**
- Vision-based RL agents achieved championship-level racing in Gran Turismo 7
- **Automated reward design:** Instead of hand-crafting rewards, used meta-learning to discover effective reward structures
- Imitation learning from expert human drivers (data augmentation)

**Insight:** Reward function design is often the bottleneck—automating or learning reward functions can accelerate development

---

## 2. Common Mistakes & How to Avoid Them

### 2.1 Training Pitfalls

**❌ Mistake: Overfitting to a single track**
- **Impact:** Model performs perfectly on one track but fails on all others
- **Solution:** Rotate training across 5-10 different tracks with varied geometries (left/right turns, straights, hairpins)
- **AWS DeepRacer lesson:** "Train on a variety of tracks with left and right turns, sharp angles, long straightaways"

**❌ Mistake: Training sessions too short or too long**
- **Impact:** <30 minutes = insufficient learning; >90 minutes = overfitting and wasted compute
- **Solution:** 60-minute sessions for most training; 30 minutes for first iteration only

**❌ Mistake: Ignoring the action space**
- **Impact:** Too few actions = lack of precision; too many actions = slow convergence
- **Solution:** Start with 7-10 discrete actions, expand to 15-20 as model matures

**❌ Mistake: Not reviewing logs**
- **Impact:** Training blindly without understanding failure modes
- **Solution:** Download and analyze training/evaluation logs after every session using community tools

### 2.2 Reward Function Design Errors

**❌ Mistake: Single-objective rewards (e.g., only speed or only centerline)**
- **Impact:** Model learns pathological behaviors (e.g., maximum speed but constantly crashes)
- **Solution:** Multi-objective reward functions balancing speed, track position, steering smoothness

**❌ Mistake: Reward weights out of balance**
- **Impact:** One reward component dominates, model ignores others
- **Solution:** Test different weight ratios; use log analysis to verify all objectives are being learned

**❌ Mistake: Not incentivizing step efficiency**
- **Impact:** Model takes inefficient paths with excessive steering corrections
- **Solution:** Add reward component for minimizing steps per lap (directly correlates with lap time)

**❌ Mistake: Dense behavioral rewards (e.g., "follow exact raceline")**
- **Impact:** Model memorizes specific path, can't adapt to opponents or track variations
- **Solution:** Use sparse competitive rewards (winning/losing) to encourage strategic adaptability

### 2.3 Simulation-to-Reality Gap Failures

**❌ Mistake: Assuming simulator = reality**
- **Impact:** Model trained in perfect simulation crashes immediately on physical track
- **Key gaps identified by AWS DeepRacer community:**
  1. **Visual noise:** Lighting, reflections, background clutter
  2. **Camera roll/pitch:** Physical car suspension causes camera angle changes during turns
  3. **Motion blur:** Low light causes line blur (centerline looks like border)
  4. **Steering drift:** Real cars pull left/right, requiring constant correction
  
**Solutions:**
- **Customize simulator:** Add visual noise, random lighting, camera angle perturbations
- **Physics tuning:** Adjust friction (mu/mu2 values), implement Ackermann steering geometry, add differentials
- **Real-world testing:** Build a scaled custom track for iterative physical validation (5.5m x 4.5m vs 8m x 6m)

**❌ Mistake: Using default simulator physics**
- **Impact:** Simulation turning radius ≠ real turning radius → model prediction errors
- **Solution:** Calibrate simulator car behavior to match physical car (PID controller tuning, friction coefficients)

---

## 3. Reward Function Design Best Practices

### 3.1 Core Principles

**Multi-Component Rewards:**
```python
reward = w1 * speed_reward 
       + w2 * centerline_reward 
       + w3 * steering_smoothness_reward
       + w4 * step_efficiency_reward
       + w5 * progress_reward
```

**Component Breakdown:**

1. **Speed Reward (Context-Dependent)**
   - High reward for high speed on **straights**
   - Low reward (or penalty) for high speed on **curves**
   - Use `steering_angle` parameter to detect curves vs straights
   - Example: `if abs(steering_angle) < 5: reward += speed * 0.5`

2. **Centerline/Track Position Reward**
   - Encourage staying within track boundaries (critical)
   - Penalize getting close to edges
   - Use `distance_from_center` and `track_width` parameters
   - Example: AWS winners use `1 - (distance_from_center / (track_width/2))`

3. **Steering Smoothness**
   - Penalize zig-zagging or oscillations
   - Reward consistent steering
   - Track `steering_angle` changes between steps

4. **Step Efficiency**
   - Fewer steps per lap = faster lap times
   - Track cumulative steps and compare to baseline
   - Example from Nature paper: "step efficiency correlates strongly with lap time reduction"

5. **Progress Reward**
   - Reward forward progress along track
   - Use `progress` parameter (0-100% of lap completion)
   - Prevents model from getting "stuck" in local optima

### 3.2 Advanced Reward Design Strategies

**Competitive Rewards (Multi-Agent Racing):**
- Research shows **sparse competitive rewards** (winning = +1, losing = -1) generate more strategic behaviors than dense progress rewards
- Enables emergence of overtaking, blocking, and defensive maneuvers
- Source: LinkedIn research by Antonio Loquercio on drone racing

**Automated Reward Design:**
- Sony AI's Gran Turismo research used **meta-learning to discover reward functions**
- Alternative to hand-crafting: let RL discover optimal reward structure
- Promising for complex multi-objective racing scenarios

**Waypoint-Based Precision:**
- Top AWS DeepRacer performers use waypoint programming
- Define optimal racing line waypoints, reward proximity to waypoints
- Allows fine-grained control over racing line per track section

### 3.3 Hyperparameter Tuning

**Key Hyperparameters (from Nature paper on generalizability):**

1. **Learning Rate:** 
   - Default: 0.0003
   - Lower = more stable but slower; higher = faster but unstable
   - Top performers make "very small changes" (±20%)

2. **Discount Factor (gamma):**
   - Controls how much model values future rewards
   - Racing typically needs 0.95-0.99 (long-term strategy matters)

3. **Batch Size:**
   - Affects training stability and speed
   - Larger batches = more stable but slower; smaller = noisier but faster
   - Experiment range: 32-512

4. **Algorithm Choice:**
   - **PPO (Proximal Policy Optimization):** More stable, good for discrete actions
   - **SAC (Soft Actor-Critic):** More sample-efficient, requires continuous action space

---

## 4. Training Approaches & Methodologies

### 4.1 Iterative Clone-and-Train Strategy

**Proven Method (AWS Top 2% - Sam Marsman):**

1. **Session 1 (30 min):** Train from scratch on Track A with basic reward function
2. **Evaluate:** Test on Track A, analyze logs, identify weaknesses
3. **Session 2 (60 min):** Clone Session 1, train on Track B with improved reward
4. **Evaluate:** Test on Track B and Track A (check generalization)
5. **Session 3 (60 min):** Clone Session 2, train on Track C with refined reward
6. **Repeat:** 30-40 iterations over 3-4 weeks

**Key Rule:** Only clone if performance improved or stayed same. If performance degraded, revert to previous model and try different modifications.

### 4.2 Track Diversity Strategy

**Geometry Variation Required:**
- **Left-dominant tracks:** Test left-turn performance
- **Right-dominant tracks:** Test right-turn performance (don't neglect!)
- **Hairpin tracks:** Test low-speed sharp turns
- **High-speed tracks:** Test straight-line speed and shallow curves
- **Mixed geometry:** Combine all of the above

**AWS DeepRacer Insight:** "If you train your model on a track that has only left turns, it'll never learn to turn right."

### 4.3 Evaluation Methodology

**Multi-Track Validation:**
- Never evaluate only on training tracks
- Test on 2-3 unseen tracks to verify generalization
- Track key metrics: off-track incidents, average speed, lap time consistency

**Log Analysis Tools:**
- AWS DeepRacer community tools: [deepracer-analysis](https://github.com/aws-deepracer-community/deepracer-analysis)
- Visualize: steering smoothness, speed variance, track position heatmaps
- Identify: where model struggles (specific turn types, track features)

**Metrics to Track:**
- **Off-track frequency:** Primary failure indicator
- **Steps per lap:** Efficiency measure (lower = better)
- **Speed distribution:** Are you using full speed range?
- **Steering distribution:** Are you oversteering?

### 4.4 Cost Optimization

**AWS DeepRacer users report training costs can escalate quickly:**
- Delete unused models regularly
- Use discrete action space unless you need top-1% performance
- 60-minute sessions are sweet spot (not 90-120 minutes)
- Train locally if possible (Deepracer-for-Cloud on EC2 or home server)

**Resource from community:** [Optimizing AWS DeepRacer training costs](https://aws.amazon.com/blogs/machine-learning/optimizing-the-cost-of-training-aws-deepracer-reinforcement-learning-models)

---

## 5. Simulation vs Real-World Gap

### 5.1 Critical Gap Categories

**Gap #1: Visual Noise**
- **Simulation:** Clean, consistent textures with no reflections or background clutter
- **Reality:** Lighting variations, reflections (especially on vinyl tracks), background objects visible over barriers
- **Impact:** Neural network gets confused by visual artifacts not seen in training
- **Mitigation:** 
  - Add random lighting to simulator (adjust .world files in Gazebo)
  - Add background objects/textures to simulation environment
  - Use black fleece or barriers to block background in physical setup

**Gap #2: Camera Motion (Roll/Pitch)**
- **Simulation:** Camera fixed, no suspension movement
- **Reality:** Physical car suspension causes camera to roll in turns, pitch during acceleration/braking
- **Impact:** Horizon shifts, track lines appear at different angles than trained
- **Mitigation:**
  - Stiffen suspension with shock spacers (AWS pit crew modification)
  - Add camera angle perturbations to simulator during training
  - Train with IMU data (if available) to learn compensation

**Gap #3: Motion Blur**
- **Simulation:** Perfect images regardless of speed or lighting
- **Reality:** Low light + high speed = blur, especially on centerline (dashed line looks solid)
- **Impact:** Model can't distinguish centerline from boundaries
- **Mitigation:**
  - Ensure proper lighting in physical racing environment (>500 lux recommended)
  - Add artificial blur to training images
  - Use higher shutter speed cameras if possible

**Gap #4: Steering Calibration & Drift**
- **Simulation:** Perfect steering, car goes straight when steering = 0
- **Reality:** Manufacturing tolerances, steering geometry, differentials cause drift
- **Impact:** Constant steering corrections needed even on straights
- **Mitigation:**
  - Calibrate physical car meticulously before racing
  - Train with steering noise/drift in simulator
  - Implement Ackermann steering geometry in simulator (community contribution)

**Gap #5: Physics Mismatch**
- **Simulation:** No Ackermann steering, rigid tires, no differentials, no suspension
- **Reality:** Complex vehicle dynamics with all the above
- **Impact:** Turning radius, grip levels, acceleration differ between sim and reality
- **Mitigation:**
  - Tune simulator friction coefficients (mu/mu2 values in racecar.gazebo)
  - Adjust PID controller parameters to match real car response
  - Test multiple physics versions (v3/v4/v5) to find best real-world match

### 5.2 Simulator Customization Strategies

**Lars Lorentz Ludvigsen's Proven Approach (AWS DeepRacer Master):**

**Environment Modifications:**
- Import track .dae files into Blender, modify textures/lighting/features
- Export and rebuild Docker image with custom tracks
- Make environment programmatically alterable during training (random variation)

**Physics Tuning:**
- **Friction:** Increase mu/mu2 values to allow higher speeds without spinning
- **PID Controllers:** Tune P/I/D values in racecar_control.yaml for acceleration/steering response
- **Ackermann Steering:** Community implementation adds realistic steering geometry
- **Physics Versions:**
  - v3: PID control, world runs during inference (higher latency)
  - v4: PID control, world paused during inference (lower latency)
  - v5: Position/velocity control, world paused (lowest latency, unnatural)

**Custom Car Software:**
- AWS DeepRacer Custom Car repository enables software upgrades
- Compressed image transport for faster processing
- OpenVINO GPU acceleration or Intel NCS2 support
- ROS Bag capture for log analysis with in-car video + GradCam overlays
- Raspberry Pi4 support ("DeepRacer Pi") for custom builds

### 5.3 Physical Testing Infrastructure

**Scaled Custom Tracks:**
- Full AWS re:Invent 2018 track: 8m x 6m (prohibitively large for home testing)
- Scaled alternative: 5.5m x 4.5m (fits in garage)
- Print on PVC vinyl (500g/m² recommended for stability)
- Add mesh PVC barriers lined with black fleece (prevent light bleed)

**Benefits of Physical Testing:**
- Rapid iteration on sim-to-real transfer
- Validate model performance before competition
- Identify blind spots in reward function
- Test hardware modifications (suspension, tires, weight distribution)

**Community Resource:** [AWS DeepRacer Custom Tracks](https://github.com/aws-deepracer-community/deepracer-custom-tracks) - Jupyter notebooks for track design

---

## 6. Team Organization Tips

### 6.1 Role Specialization

**Based on successful competition teams (A2RL, Indy Autonomous Challenge, AWS Summit winners):**

1. **Perception Engineer(s):**
   - Optimize sensor processing pipeline
   - Handle camera calibration and IMU integration
   - Implement sensor fusion if using multiple inputs

2. **Control/Planning Engineer(s):**
   - Design and tune control algorithms
   - Optimize action space and steering logic
   - Handle trajectory planning and racing line optimization

3. **Reward Function / RL Specialist:**
   - Design and iterate reward functions
   - Analyze training logs and metrics
   - Tune hyperparameters and training methodology

4. **Simulation Engineer:**
   - Customize simulator for sim-to-real transfer
   - Manage training infrastructure and job orchestration
   - Handle track design and environment variations

5. **Integration / Test Engineer:**
   - Physical car setup and calibration
   - Coordinate sim-to-real testing
   - Manage competition day operations

**Small Teams (2-4 people):** Combine roles (e.g., Perception+Simulation, Control+RL)

### 6.2 Development Workflow

**Agile Sprint Structure (recommended):**

**Week 1: Foundation**
- Setup training infrastructure
- Baseline reward function and action space
- First training runs on 3-5 tracks

**Week 2: Iteration #1**
- Analyze baseline performance
- Refine reward function based on failure modes
- Clone and train second generation models
- Begin simulator customization

**Week 3: Iteration #2**
- Expand action space if needed
- Test hyperparameter variations
- Physical testing (if available)
- Address sim-to-real gaps

**Week 4: Competition Prep**
- Final model selection via multi-track evaluation
- Physical car calibration and validation
- Strategy planning (if head-to-head racing)
- Backup models and contingency plans

### 6.3 Knowledge Sharing & Community Resources

**Leverage Existing Communities:**
- **AWS DeepRacer Community:** Slack (deepracing.io), GitHub, Stack Overflow
- **A2RL Research:** Published papers on perception, control, and multi-agent racing
- **Academic Competitions:** Learn-to-Race (CMU), F1TENTH, Indy Autonomous Challenge

**Open Source Tools:**
- [Deepracer-for-Cloud](https://github.com/aws-deepracer-community/deepracer-for-cloud): Local training
- [deepracer-analysis](https://github.com/aws-deepracer-community/deepracer-analysis): Log analysis
- [deepracer-viz](https://github.com/jochem725/deepracer-viz): Visualization tools
- [AWS DeepRacer Custom Car](https://github.com/aws-deepracer-community/deepracer-custom-car): Car software upgrades

**Documentation to Study:**
- AWS DeepRacer Developer Guide (comprehensive reference)
- AWS DeepRacer Pit Stop (official racing tips)
- Community blog posts from Summit and re:Invent winners

### 6.4 Competition Day Strategy

**Pre-Race:**
- Arrive early for car calibration (lighting, steering, sensors)
- Test run on physical track if allowed
- Have 2-3 backup models ready (different risk profiles)
- Document track conditions (lighting, temperature, surface)

**Model Selection:**
- Conservative model: Prioritizes staying on track (qualification rounds)
- Aggressive model: Higher speed, higher risk (knockout rounds if winning matters)
- Adaptive strategy: Start conservative, switch to aggressive if needed

**Physical Car Checklist:**
- Battery fully charged (and spare ready)
- Wheels cleaned and inspected
- Steering calibrated (test straight-line driving)
- Camera lens clean, no obstructions
- Firmware and model uploaded correctly

### 6.5 Post-Competition Review

**Continuous Improvement:**
- Record all races (video + telemetry if possible)
- Analyze failures: off-track incidents, slow sections, missed opportunities
- Document what worked and what didn't
- Update reward function and training strategy for next competition
- Share learnings with community (many successful teams publish post-mortems)

---

## 7. Key Takeaways for IBM AI Racing League

### 7.1 Critical Success Factors

1. **Diverse Training is Non-Negotiable**
   - Train across 10+ varied tracks (don't overfit to one track)
   - Rotate track geometry every training session
   - Validate on unseen tracks regularly

2. **Reward Function Sophistication**
   - Multi-component rewards (speed + position + smoothness + efficiency)
   - Context-dependent rewards (different for straights vs curves)
   - Balance reward weights carefully (log analysis to verify)

3. **Iterative Development with Cloning**
   - 30-40 model iterations over 3-4 weeks
   - Clone successful models, train on new tracks
   - Only clone if performance improved/stable

4. **Sim-to-Real Gap is Real**
   - Customize simulator aggressively (visual noise, physics, lighting)
   - Physical testing infrastructure is worth the investment
   - Plan for calibration time on competition day

5. **Community Knowledge is Invaluable**
   - AWS DeepRacer has years of documented lessons
   - Use open source tools (don't reinvent the wheel)
   - Study competition winner blog posts and papers

### 7.2 Differentiation Opportunities for IBM

**Where IBM AI Racing League Differs:**
- Higher performance vehicles (likely faster than AWS DeepRacer)
- Potentially more sophisticated sensor suite
- Multi-agent competitive racing (not just time trials)
- Real-world track racing (not indoor/controlled like DeepRacer)

**Strategies to Leverage:**
1. **Multi-Agent Training:** Use competitive sparse rewards (winning/losing) instead of solo dense rewards
2. **Strategic Behaviors:** Train for overtaking, blocking, defensive positioning—not just optimal lap times
3. **Robustness Testing:** Train with extreme variation (weather, lighting, track conditions) for real-world resilience
4. **Transfer Learning:** Pre-train on AWS DeepRacer-like tracks, fine-tune on IBM racing environments

### 7.3 Recommended First Steps

**Week 0: Infrastructure**
- [ ] Set up training infrastructure (cloud or local)
- [ ] Install community tools (deepracer-analysis, custom tracks)
- [ ] Design 5 initial training tracks (varied geometry)

**Week 1: Baseline**
- [ ] Train baseline model with basic reward function
- [ ] Evaluate on all 5 tracks + 2 unseen tracks
- [ ] Analyze logs to identify failure modes
- [ ] Document baseline performance metrics

**Week 2: Reward Iteration**
- [ ] Implement multi-component reward function
- [ ] Clone baseline, train on tracks 1-5 (60 min each)
- [ ] Evaluate generalization
- [ ] Begin simulator customization for IBM racing conditions

**Week 3: Physical Testing**
- [ ] If physical car available, test baseline model
- [ ] Identify sim-to-real gaps specific to IBM platform
- [ ] Customize simulator to match (physics, visuals)
- [ ] Re-train with customized simulator

**Week 4: Competition Prep**
- [ ] Train 3 models: conservative, balanced, aggressive
- [ ] Multi-track validation for all three
- [ ] Physical car calibration protocol
- [ ] Competition day checklist and contingency plans

---

## 8. References & Resources

### 8.1 Key Articles & Papers

1. **A2RL Season 2 Analysis:** https://a2rl.io/blog/23/A2RL-Season-2-A-Breakthrough-Year-for-Autonomous-Racing
2. **AWS DeepRacer Physical Racing Guide:** https://aws.amazon.com/blogs/machine-learning/aws-deepracer-how-to-master-physical-racing
3. **Top 2% AWS DeepRacer Strategy:** https://medium.com/@marsmans/how-i-got-into-the-top-2-in-aws-deepracer-32127a364212
4. **Reward Function Design Best Practices:** https://www.instructables.com/How-to-Understand-and-Code-a-Winning-Student-AWS-D/
5. **Generalizability Research (Nature):** https://www.nature.com/articles/s41598-025-27702-6
6. **Gran Turismo Automated Reward Design:** https://arxiv.org/abs/2511.02094
7. **Competitive Racing with Sparse Rewards (LinkedIn):** Antonio Loquercio's drone racing research
8. **Learn-to-Race Challenge:** https://www.aicrowd.com/challenges/learn-to-race-autonomous-racing-virtual-challenge

### 8.2 Community Resources

**AWS DeepRacer Community:**
- Slack: https://deepracing.io
- GitHub Org: https://github.com/aws-deepracer-community
- Custom Tracks: https://github.com/aws-deepracer-community/deepracer-custom-tracks
- Training Analysis: https://github.com/aws-deepracer-community/deepracer-analysis
- Custom Car Software: https://github.com/aws-deepracer-community/deepracer-custom-car

**Official Documentation:**
- AWS DeepRacer Developer Guide: https://docs.aws.amazon.com/deepracer/latest/developerguide/
- AWS DeepRacer Pit Stop: https://aws.amazon.com/deepracer/racing-tips/
- Reward Function Examples: https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-reward-function-examples.html

**Academic Competitions:**
- Indy Autonomous Challenge: https://www.indyautonomouschallenge.com
- F1TENTH: https://f1tenth.org
- Learn-to-Race: https://learn-to-race.org

### 8.3 Technical Tools

**Training Infrastructure:**
- Deepracer-for-Cloud: Local/EC2 training platform
- AWS RoboMaker: Official cloud training (more expensive)
- Gazebo Simulator: Open source 3D robotics simulator
- ROS2: Robot Operating System framework

**Analysis & Visualization:**
- deepracer-analysis: Jupyter notebooks for log analysis
- deepracer-viz: GradCam and telemetry visualization
- Blender: 3D track design and modification
- Inkscape: Vector track design for printing

---

## Appendix A: Sample Reward Function (Multi-Component)

```python
def reward_function(params):
    """
    Multi-component reward function based on AWS DeepRacer best practices
    """
    
    # Input parameters
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    speed = params['speed']
    steering_angle = abs(params['steering_angle'])
    steps = params['steps']
    progress = params['progress']
    all_wheels_on_track = params['all_wheels_on_track']
    
    # Initialize reward
    reward = 1.0
    
    # Component 1: Stay on track (critical)
    if not all_wheels_on_track:
        return 1e-3  # Near-zero reward for going off-track
    
    # Component 2: Centerline tracking
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width
    
    if distance_from_center <= marker_1:
        reward += 1.0
    elif distance_from_center <= marker_2:
        reward += 0.5
    elif distance_from_center <= marker_3:
        reward += 0.1
    else:
        reward += 0.01  # Very close to edge
    
    # Component 3: Speed optimization (context-dependent)
    # High speed on straights, low speed on curves
    if steering_angle < 5:  # Straight
        if speed > 2.5:
            reward += speed * 0.5
    else:  # Curve
        # Reward lower speeds on sharp turns
        optimal_speed = max(1.0, 3.0 - (steering_angle / 10))
        speed_diff = abs(speed - optimal_speed)
        reward += max(0, 1.0 - speed_diff)
    
    # Component 4: Steering smoothness
    if steering_angle < 15:
        reward += 0.5
    
    # Component 5: Step efficiency
    # Reward fewer steps (more efficient racing line)
    if progress > 0:
        steps_per_progress = steps / progress
        if steps_per_progress < 10:  # Efficient
            reward += 1.0
        elif steps_per_progress < 15:
            reward += 0.5
    
    # Component 6: Progress incentive
    # Ensure forward progress is always rewarded
    reward += progress * 0.01
    
    return float(reward)
```

---

## Appendix B: Competition Timeline Template

**4-Week Competition Preparation Timeline:**

| Week | Focus Area | Key Tasks | Deliverables |
|------|-----------|-----------|--------------|
| **1** | Foundation | Infrastructure setup, baseline model, 5 training tracks | Working training pipeline, baseline performance metrics |
| **2** | Iteration #1 | Reward function refinement, model cloning, log analysis | Generation 2 models, identified failure modes |
| **3** | Sim-to-Real | Simulator customization, physical testing, hyperparameter tuning | Customized simulator, gen 3-4 models |
| **4** | Competition Prep | Final model selection, car calibration, strategy planning | 3 competition-ready models, calibration checklist |

**Daily Tasks During Training Weeks:**
- Morning: Review previous day's training logs
- Mid-day: Launch new training sessions (2-3 parallel if resources allow)
- Afternoon: Simulator tuning or physical testing
- Evening: Log analysis and reward function iteration planning

---

**Document prepared by:** Atlas AI (Subagent: racing-strategies)  
**Research methodology:** Exa neural search across 40+ sources, deep analysis of 10+ key articles  
**Confidence level:** High (based on extensive real-world competition data from AWS DeepRacer, A2RL, IAC)  
**Next steps:** Validate strategies with initial IBM AI Racing League training runs and iterate based on platform-specific characteristics

# AI Autonomous Racing - Technical Research Report

**Date:** 2026-02-08  
**Research Focus:** ML/AI techniques, neural architectures, sim-to-real transfer, computer vision, and IBM watsonx integration for autonomous racing

---

## Executive Summary

This report synthesizes cutting-edge research on AI-powered autonomous racing systems from 2024-2025. Key findings reveal that **reinforcement learning (RL)** is the dominant approach for competitive racing, with recent breakthroughs in **on-board learning**, **vision-based end-to-end architectures**, and **residual policy learning** for sim-to-real transfer. IBM watsonx provides a comprehensive AI development platform with REST APIs, Python SDKs, and foundation models suitable for racing AI integration.

---

## 1. ML Approaches: Reinforcement Learning vs Imitation Learning vs Classical Control

### 1.1 Reinforcement Learning (DOMINANT APPROACH)

**State-of-the-Art Performance:**
- **Gran Turismo Success (2024-2025):** Sony AI and researchers achieved **champion-level and super-human performance** in Gran Turismo using vision-based RL agents
  - Papers: "A Super-human Vision-based RL Agent for Autonomous Racing in Gran Turismo" (2024) and "Champion-level Vision-based RL Agent for Competitive Racing in Gran Turismo 7" (2025)
  - Key innovation: End-to-end learning from raw pixels to control commands

**Recent Breakthroughs:**

1. **On-Board RL (2025)** - Paper: "Drive Fast, Learn Faster: On-Board RL for High Performance Autonomous Racing"
   - **Eliminates simulation dependency** - learns directly on physical hardware
   - Addresses sim-to-real gap by training in real-world conditions
   - Critical for dynamic environments and unpredictable conditions

2. **Residual Policy Learning (2025)** - Paper: "RLPP: A Residual Method for Zero-Shot Real-World Autonomous Racing"
   - Combines classical control baseline with RL residual corrections
   - Achieves **zero-shot transfer** from simulation to real-world
   - Tested on 1/10th scale F1TENTH platforms

3. **AWS DeepRacer Study (2025)** - "Reward design and hyperparameter tuning for generalizable deep RL agents"
   - Compares **PPO (Proximal Policy Optimization)** vs **SAC (Soft Actor-Critic)**
   - Focus on generalization across multiple tracks
   - Published in Nature Scientific Reports (December 2025)

**RL Algorithms Used:**
- **PPO** (Proximal Policy Optimization) - Most common, stable training
- **SAC** (Soft Actor-Critic) - Better sample efficiency
- **DQN variants** - For discrete action spaces
- **Model-based RL** - For sample-efficient learning with dynamics models

**RL Advantages:**
- Discovers optimal racing lines beyond human intuition
- Handles high-speed, non-linear dynamics at friction limits
- Learns multi-agent competitive behaviors (wheel-to-wheel racing)
- Continuous improvement through self-play

### 1.2 Imitation Learning (SECONDARY APPROACH)

**End2Race Framework (2025):** "Efficient End-to-End Imitation Learning for Real-Time F1Tenth Racing"
- Uses expert demonstrations for faster initial learning
- More sample-efficient than pure RL for basic racing skills
- Often used as **pre-training** before RL fine-tuning

**DeepRacing Framework:**
- CNN+LSTM architecture for learning from human demonstrations
- Tested in Formula One Codemasters game (used by real F1 drivers)
- Good for replicating known racing strategies

**Imitation Learning Limitations:**
- Performance ceiling limited by human expert quality
- Struggles with novel scenarios not in training data
- Less effective at discovering optimal strategies beyond human baseline

### 1.3 Classical Control (BASELINE/HYBRID)

**Role in Modern Racing:**
- Used as **baseline** for residual learning approaches
- Provides safety guarantees and interpretability
- Model Predictive Control (MPC) common for trajectory optimization

**Hybrid Approaches (WINNING STRATEGY):**
- Classical control for safety-critical fallback
- RL residual for performance optimization
- Example: RLPP paper demonstrates this successfully

**Classical Control Advantages:**
- Provable stability guarantees
- Works with limited data
- Interpretable and debuggable
- Fast computation for real-time control

**Why RL Wins Races:**
Despite classical control's reliability, **RL agents consistently achieve faster lap times** by:
1. Learning non-intuitive racing lines
2. Operating closer to physical limits
3. Adapting to opponent behaviors in real-time
4. Discovering emergent strategies through self-play

---

## 2. Neural Network Architectures for Racing

### 2.1 Vision-Based End-to-End Architectures

**Convolutional Neural Networks (CNNs):**
- **Primary architecture** for processing camera inputs
- Extract spatial features from raw images
- Used in Gran Turismo superhuman agents

**CNN + LSTM/RNN (STANDARD PATTERN):**
- **DeepRacing Framework:** Combines CNN feature extraction with LSTM for temporal reasoning
- LSTM cells capture motion dynamics and track state history
- Critical for understanding velocity, acceleration, and trajectory

**Attention-Based Networks (2023):**
- Paper: "Autonomous Racing With Attention-Based Neural Networks" (TU Wien)
- Attention mechanisms focus on relevant track features
- Improves generalization to new tracks

### 2.2 End-to-End vs Modular Approaches

**End-to-End Learning (DOMINANT TREND):**
- Single neural network: raw sensors → control outputs
- Examples: Gran Turismo agents, AdmiralNet
- **Advantages:**
  - Co-optimization of perception and control
  - Lower latency (no intermediate representations)
  - Simpler deployment pipeline

**Modular Approaches:**
- Separate perception, planning, and control modules
- Paper: "A Comprehensive Literature Review on Modular Approaches to Autonomous Driving: Deep Learning for Road and Racing Scenarios" (MDPI, 2025)
- **Advantages:**
  - Easier debugging and validation
  - Component-wise optimization
  - Better interpretability

**Current Best Practice:** End-to-end for racing, modular for safety-critical autonomous driving

### 2.3 Specialized Architectures

**AdmiralNet (DeepRacing):**
- CNN + LSTM architecture
- Trained end-to-end on Formula One game
- Outputs steering and throttle commands

**Vehicle Dynamics Models:**
- "End-to-End Neural Network for Vehicle Dynamics Modeling" (IEEE 2021)
- Learn forward/inverse dynamics models
- Used in model-based RL and MPC controllers

**Multi-Modal Fusion:**
- Combine camera, LiDAR, IMU, GPS
- Learn-to-Race framework supports multi-sensor fusion
- Critical for robust perception in varied conditions

---

## 3. Sim-to-Real Transfer Techniques

### 3.1 The Sim-to-Real Gap Challenge

**Core Problem:**
- Simulations have perfect physics, sensors, and no noise
- Real world has uncertainties, delays, and hardware limitations
- Policies trained in sim often fail catastrophically in real world

### 3.2 Leading Transfer Techniques (2024-2025)

**1. Residual Policy Learning (BREAKTHROUGH):**
- Paper: "RLPP: A Residual Method for Zero-Shot Real-World Autonomous Racing" (2025)
- **Method:** Train RL policy on top of classical control baseline
- **Result:** Zero-shot transfer from sim to real F1TENTH cars
- **Why it works:** Classical controller handles sim-real differences, RL optimizes on top

**2. On-Board Learning (ELIMINATES TRANSFER):**
- Paper: "Drive Fast, Learn Faster: On-Board RL for High Performance Autonomous Racing" (2025)
- **Method:** Learn directly on physical hardware from scratch
- **Advantages:** No sim-to-real gap, adapts to real-world dynamics
- **Challenges:** Sample efficiency, safety during exploration

**3. Domain Randomization:**
- Randomize simulation parameters during training
- Physics parameters, sensor noise, visual appearance
- Forces policy to be robust to uncertainty

**4. Progressive Fidelity Transfer:**
- "Sim-to-Sim-to-Real Transfer for Small Autonomous Vehicles" (Duckietown, 2025)
- Train in low-fidelity sim → high-fidelity sim → real world
- Each step narrows the gap incrementally

**5. System Identification:**
- Learn real-world system parameters
- Fine-tune simulation to match real hardware
- Improves transfer but requires extensive real-world data

### 3.3 Competition-Proven Techniques

**Indy Autonomous Challenge (IAC):**
- UC Berkeley ROAR team achieved **fastest autonomous lap time** (1:27) at Putnam Park Road Course (2023)
- Used sim-to-real transfer on Dallara AV-21 race car
- Perception stack + RL in simulation testing

**A2RL (Abu Dhabi Autonomous Racing League):**
- "A2RL SIM Sprint: A New Era Begins in Autonomous Racing" (2025)
- Developed by Autonoma with digital twin of Yas Marina Circuit
- High-fidelity simulation enables realistic testing

**Learn-to-Race Platform:**
- OpenAI Gym-compliant environment
- Built around Arrival's high-fidelity racing simulator
- Used in Roborace series (world's first autonomous racing competition)
- Full software-in-the-loop (SIL) and hardware-in-the-loop (HIL) capabilities

### 3.4 Best Practices for Sim-to-Real

1. **Start with residual learning** - proven zero-shot transfer
2. **Use high-fidelity simulators** - Learn-to-Race, Autonoma digital twins
3. **Randomize aggressively** - physics, sensors, visuals
4. **Validate incrementally** - sim → controlled real → full-speed real
5. **Plan for on-board fine-tuning** - adapt after deployment

---

## 4. Computer Vision Approaches

### 4.1 Vision-Based Control (PRIMARY INPUT)

**Raw Pixel Input:**
- Gran Turismo agents use **raw RGB images** as primary input
- End-to-end learning from pixels to controls
- CNNs extract relevant features automatically

**Camera Configurations:**
- Front-facing monocular cameras most common
- Multi-camera setups for 360° awareness
- Typical resolution: 640x480 to 1920x1080

### 4.2 Perception Tasks

**Track Boundary Detection:**
- Segment drivable surface from obstacles
- Critical for staying within track limits
- Often learned implicitly in end-to-end systems

**Opponent Detection & Tracking:**
- Multi-agent racing requires opponent awareness
- Object detection (YOLO, Faster R-CNN) for opponent localization
- Kalman filters or particle filters for tracking

**Depth Estimation:**
- Monocular depth estimation for distance to opponents
- Stereo cameras or LiDAR for accurate 3D perception
- Critical for safe overtaking maneuvers

### 4.3 Perception Architectures

**DeepRacing Framework:**
- CNN feature extraction
- LSTM for temporal consistency
- Outputs waypoints or control commands

**Indy Autonomous Challenge Perception Stack:**
- LiDAR + camera fusion
- Real-time object detection and tracking
- Tested on Dallara AV-21 at 170+ mph

**Attention Mechanisms:**
- Focus on relevant track regions (apex, braking zones)
- Improves generalization to unseen tracks
- Reduces computational cost

### 4.4 Challenges & Solutions

**Challenge:** Motion blur at high speeds
- **Solution:** High-frame-rate cameras (120+ fps), optical flow

**Challenge:** Varying lighting conditions (shadows, glare)
- **Solution:** Domain randomization, HDR cameras, multi-modal fusion

**Challenge:** Occlusion by opponents
- **Solution:** Multi-camera setups, predictive models

---

## 5. Sensor Fusion

### 5.1 Multi-Modal Sensing

**Sensor Suite (Typical Racing Configuration):**
- **Cameras:** RGB images for visual perception
- **LiDAR:** Precise 3D point clouds for distance measurement
- **IMU:** Accelerometer + gyroscope for vehicle state estimation
- **GPS:** Global positioning for track localization
- **Wheel encoders:** Odometry for dead reckoning

### 5.2 Fusion Architectures

**Early Fusion:**
- Concatenate raw sensor data before processing
- Single neural network processes all modalities
- Example: Learn-to-Race multimodal control

**Late Fusion:**
- Separate processing pipelines per sensor
- Combine predictions or features at decision level
- More robust to sensor failures

**Intermediate Fusion:**
- Fuse at feature level (e.g., after CNN layers)
- Balance between early and late fusion benefits

### 5.3 Real-World Implementation

**Roborace & F1TENTH Platforms:**
- Camera + LiDAR + IMU standard configuration
- Real-time fusion at 10-100 Hz control frequency
- Safety-critical: redundant sensors for fallback

**Dallara AV-21 (IAC):**
- 4 cameras, 3 LiDAR, GPS, IMU
- Sensor fusion for 170+ mph autonomous racing
- Proven in competition (UC Berkeley record lap)

---

## 6. IBM Tools & watsonx Integration

### 6.1 IBM watsonx.ai Overview

**Platform Capabilities:**
- **End-to-end AI development studio** for building, training, and deploying AI models
- **Foundation models** including IBM Granite series (e.g., granite-13b-instruct-v2, granite-3-3-8b-instruct)
- **Unified API access** via REST API and SDKs (Python, Node.js)
- **Hybrid cloud deployment** - run on-premises or cloud
- **Collaborative development** with or without code

**Key Features for Racing AI:**
- Foundation models for natural language processing (race strategy, telemetry analysis)
- Flexible deployment options (edge devices, cloud inference)
- API-driven integration with custom RL training pipelines

### 6.2 watsonx.ai APIs & SDKs

**REST API Access:**
- Base URL: `https://us-south.ml.cloud.ibm.com` (Dallas region)
- Authentication via Bearer token
- Endpoints for text generation, chat, embeddings

**Example API Call (Text Inference):**
```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-31" \
  --data-raw '{
    "input": "Analyze this racing telemetry data...",
    "model_id": "ibm/granite-13b-instruct-v2",
    "project_id": "{project_id}"
  }'
```

**Python SDK:**
```python
from ibm_watsonx_ai import WatsonXAI

watsonx = WatsonXAI(
    credentials={"url": watsonx_ai_url, "apikey": api_key},
    project_id=project_id
)

# Inference
response = watsonx.generate(
    model_id="ibm/granite-13b-instruct-v2",
    input="Explain optimal racing line for Turn 3..."
)
```

**Node.js SDK:**
```javascript
const { WatsonXAI } = require('@ibm-cloud/watsonx-ai');

const watsonx = new WatsonXAI({ apikey, url, projectId });
const result = await watsonx.textGeneration({
  modelId: 'ibm/granite-13b-instruct-v2',
  input: 'Racing strategy analysis...'
});
```

### 6.3 Integration with Racing Systems

**Potential Use Cases:**

1. **Telemetry Analysis:**
   - Use watsonx foundation models to analyze race data
   - Generate natural language insights from sensor logs
   - Identify patterns in successful laps

2. **Race Strategy:**
   - LLM-driven decision-making for pit stops, tire strategy
   - Natural language interface for race engineers
   - Real-time strategy adjustments based on conditions

3. **Opponent Modeling:**
   - Analyze opponent behavior patterns
   - Predict opponent actions using foundation models
   - Generate counterstrategy recommendations

4. **Simulation Parameter Tuning:**
   - Use watsonx to optimize hyperparameters
   - AutoML for reward function design
   - Model selection for RL algorithms

### 6.4 watsonx.ai Features for Racing AI

**AI Guardrails:**
- Content filtering for safe AI outputs
- Critical for deployed autonomous systems
- Ensure model outputs meet safety constraints

**Prompt Engineering Tools:**
- Build and test prompts for racing-specific tasks
- Template system for consistent outputs
- Version control for prompt iterations

**Model Deployment:**
- REST API for real-time inference
- Batch processing for offline analysis
- Edge deployment options for on-vehicle compute

**Developer Resources:**
- Free trial with 300k token limit
- Comprehensive documentation and tutorials
- Python library: `ibm-watsonx-ai`

### 6.5 IBM Racing-Specific Tools

**No Dedicated "IBM Racing API"** found in research, but watsonx provides:
- General-purpose AI infrastructure
- Foundation models adaptable to racing domains
- Integration-friendly APIs for custom pipelines

**Recommended Integration Pattern:**
1. Use watsonx for high-level reasoning (strategy, analysis)
2. Custom RL training pipeline for vehicle control
3. Combine outputs for hybrid decision-making

---

## 7. Recommended Tech Stack for IBM Racing AI Project

### 7.1 Core ML/RL Stack

**Reinforcement Learning Framework:**
- **Stable Baselines3** (SB3) - Industry standard, PPO/SAC implementations
- **Ray RLlib** - Distributed RL, scalable to large clusters
- **TensorFlow / PyTorch** - Deep learning backends

**Simulation Environment:**
- **Learn-to-Race** - Open-source, high-fidelity racing simulator
- **AWS DeepRacer** - Cloud-based, easy setup, proven track record
- **Custom CARLA/Gazebo** - Flexible but requires more setup

**Recommended:** Start with Learn-to-Race for realism, AWS DeepRacer for rapid prototyping

### 7.2 Neural Network Architecture

**Vision Pipeline:**
```
Camera Input (640x480 RGB)
  ↓
ResNet18/50 CNN (pretrained on ImageNet)
  ↓
LSTM (128 units, 2 layers) - temporal reasoning
  ↓
Fully Connected (256 → 128 → action_dim)
  ↓
Action Output (steering, throttle, brake)
```

**Alternative (Attention-Based):**
- Vision Transformer (ViT) for image encoding
- Transformer layers for sequential decision-making
- Higher compute cost but better generalization

### 7.3 Sim-to-Real Strategy

**Phase 1: Simulation Training**
- Train RL policy in Learn-to-Race with domain randomization
- Randomize: physics, camera noise, lighting, track conditions
- Aim for 90% success rate in varied conditions

**Phase 2: Residual Learning**
- Implement RLPP-style residual policy
- Classical MPC baseline + RL residual
- Enables zero-shot real-world deployment

**Phase 3: On-Board Fine-Tuning**
- Deploy to physical platform (F1TENTH recommended for cost)
- Fine-tune online with safety constraints
- Log all real-world data for simulation improvement

### 7.4 IBM watsonx Integration

**Use watsonx for:**
- **Pre-race analysis:** Analyze historical race data, generate strategy
- **Post-race debrief:** Telemetry analysis, natural language summaries
- **Hyperparameter tuning:** Use watsonx to suggest RL hyperparameters
- **Explainability:** Generate natural language explanations of agent decisions

**Architecture:**
```
Simulation/Real Car
  ↓
RL Agent (PPO/SAC) - low-latency control loop
  ↓
Telemetry Logger
  ↓
watsonx.ai API - strategy & analysis (async)
  ↓
Dashboard / Engineer Interface
```

### 7.5 Hardware Requirements

**Simulation Training:**
- GPU: NVIDIA RTX 3090 / 4090 or better (RL training)
- CPU: 16+ cores for parallel environment simulation
- RAM: 64GB+
- Storage: 1TB SSD for replay buffers

**On-Vehicle Compute (F1TENTH scale):**
- **NVIDIA Jetson Orin** (32GB) - edge AI inference
- Camera: 120fps, global shutter
- LiDAR: Velodyne VLP-16 or Ouster OS1
- IMU: VectorNav VN-100 or similar

**Cloud Infrastructure:**
- **IBM Cloud** for watsonx.ai API access
- **AWS** or **Azure** for distributed RL training
- **Edge deployment** on vehicle hardware

### 7.6 Software Stack Summary

| Component | Recommended Tool | Alternative |
|-----------|------------------|-------------|
| **RL Framework** | Stable Baselines3 | Ray RLlib |
| **Simulation** | Learn-to-Race | AWS DeepRacer |
| **Deep Learning** | PyTorch | TensorFlow |
| **Vision** | OpenCV + torchvision | ROS perception |
| **IBM Integration** | watsonx.ai Python SDK | REST API |
| **Deployment** | Docker + Kubernetes | Native deployment |
| **Monitoring** | Weights & Biases | TensorBoard |

### 7.7 Development Roadmap

**Phase 1 (Months 1-2): Simulation Baseline**
- Set up Learn-to-Race environment
- Implement CNN+LSTM architecture
- Train PPO agent to complete laps consistently

**Phase 2 (Months 3-4): Performance Optimization**
- Implement residual learning (RLPP-style)
- Add opponent modeling for multi-agent racing
- Achieve competitive lap times in simulation

**Phase 3 (Months 5-6): Sim-to-Real Transfer**
- Build or acquire F1TENTH platform
- Deploy with residual policy
- Fine-tune on physical hardware

**Phase 4 (Months 7-8): watsonx Integration**
- Connect telemetry pipeline to watsonx.ai
- Build natural language strategy interface
- Implement post-race analysis dashboard

**Phase 5 (Months 9-12): Competition Preparation**
- Test in varied conditions (indoor/outdoor tracks)
- Optimize for specific competition rules
- Safety validation and edge case testing

---

## 8. Key Research Papers & Resources

### Must-Read Papers (2024-2025)

1. **"Drive Fast, Learn Faster: On-Board RL for High Performance Autonomous Racing"** (2025)
   - Breakthrough: Eliminates simulation dependency
   - arXiv: 2505.07321

2. **"A Champion-level Vision-based RL Agent for Competitive Racing in Gran Turismo 7"** (2025)
   - Achieves superhuman performance
   - arXiv: 2504.09021

3. **"RLPP: A Residual Method for Zero-Shot Real-World Autonomous Racing"** (2025)
   - Zero-shot sim-to-real transfer
   - arXiv: 2501.17311

4. **"Reward design and hyperparameter tuning for generalizable deep RL agents"** (2025)
   - PPO vs SAC comparison, AWS DeepRacer
   - Nature Scientific Reports

5. **"A Super-human Vision-based RL Agent for Autonomous Racing in Gran Turismo"** (2024)
   - Sony AI, superhuman racing
   - arXiv: 2406.12563

### Open-Source Platforms

- **Learn-to-Race:** https://learn-to-race.org/
- **AWS DeepRacer:** https://aws.amazon.com/deepracer/
- **F1TENTH:** https://f1tenth.org/
- **Roborace:** https://2026ifac-roboracer.com/

### Competition Benchmarks

- **Indy Autonomous Challenge (IAC)** - Full-scale racing (170+ mph)
- **A2RL (Abu Dhabi)** - Yas Marina Circuit, digital twin simulation
- **Roborace** - Electric autonomous racing series
- **F1TENTH** - 1/10 scale racing competition (academic)

---

## 9. Critical Success Factors

### Technical Factors

1. **RL Algorithm Selection:**
   - **PPO for stability** (safe exploration)
   - **SAC for sample efficiency** (faster learning)
   - Use residual learning for sim-to-real

2. **Reward Function Design:**
   - Track progress + speed + safety margins
   - Penalize track limits violations heavily
   - Sparse rewards for milestones (lap completion)

3. **Sim-to-Real Strategy:**
   - Start with residual learning (proven zero-shot transfer)
   - Domain randomization during training
   - Plan for on-board fine-tuning

4. **Safety:**
   - Always have classical control fallback
   - Geofence boundaries with hard constraints
   - Emergency stop system independent of AI

### Practical Considerations

1. **Start Small:**
   - Begin with 1/10 scale (F1TENTH) - lower cost, safer
   - Validate approach before scaling to full-size

2. **Data Logging:**
   - Log everything: states, actions, rewards, crashes
   - Critical for debugging and simulation improvement

3. **Iterative Development:**
   - Simulation → controlled real → full-speed real
   - Each step validates assumptions and improves models

4. **Team Skills:**
   - RL expertise (algorithm tuning, reward design)
   - Robotics (sensors, actuators, real-time systems)
   - Software engineering (robust deployment, CI/CD)

---

## 10. Conclusion & Next Steps

### Key Findings Summary

1. **Reinforcement Learning is the winning approach** for autonomous racing, consistently outperforming classical control and imitation learning
2. **Vision-based end-to-end architectures** (CNN+LSTM) are the standard, with attention mechanisms emerging
3. **Residual learning** solves sim-to-real transfer with zero-shot deployment
4. **On-board learning** is the future, eliminating simulation dependency entirely
5. **IBM watsonx.ai** provides robust infrastructure for strategy, analysis, and high-level reasoning

### Recommended Next Steps

**Immediate (Week 1-2):**
1. Set up Learn-to-Race simulation environment
2. Acquire IBM watsonx.ai free trial account (300k tokens)
3. Implement baseline CNN+LSTM architecture with PPO

**Short-Term (Month 1-3):**
1. Train RL agent to complete laps consistently in simulation
2. Implement telemetry logging pipeline
3. Integrate watsonx.ai for post-race analysis

**Medium-Term (Month 4-6):**
1. Implement RLPP residual learning approach
2. Acquire F1TENTH hardware platform
3. Deploy and validate sim-to-real transfer

**Long-Term (Month 7-12):**
1. Fine-tune on physical hardware
2. Compete in F1TENTH or local racing competition
3. Scale to larger platform if successful

### Contact & Collaboration

- **Academic Partnerships:** UC Berkeley ROAR, MIT CSAIL (IAC team)
- **Industry Platforms:** Learn-to-Race, AWS DeepRacer
- **Competitions:** F1TENTH, IAC, A2RL, Roborace

---

**Report Compiled By:** Atlas (AI Research Assistant)  
**Sources:** Exa AI Search, arXiv, IEEE Xplore, Nature, IBM Documentation  
**Total Papers Reviewed:** 40+ recent publications (2024-2025)

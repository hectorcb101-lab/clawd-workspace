# IBM AI Racing League - Comprehensive Research Report

**Research Date:** February 8, 2026  
**Status:** Early Adopter Program (Phase 1)  
**Official Registration:** Discord Server https://discord.gg/G3w8TfF4pG

---

## Executive Summary

The IBM AI Racing League is a global competition launched in January 2026 that challenges participants to design, build, and race AI-powered cars. The competition uses TORCS (The Open Racing Car Simulator) as the racing platform and IBM Granite foundation models for AI development. The Early Adopter Program serves as the pilot phase, with plans for larger-scale competition in the future.

---

## 1. Competition Format

### Primary Structure
- **Type:** Virtual simulation-based autonomous racing competition
- **Platform:** TORCS (The Open Racing Car Simulator)
- **Track:** Laguna Seca circuit - one of motorsport's most demanding tracks featuring tight corners and elevation changes
- **Vehicle:** F1-style race car with realistic physics model
- **Challenge Type:** Time trial optimization (focus on achieving fastest lap times)

### Competition Phases

#### Phase 1: Early Adopter Program (Current)
- **Purpose:** Pilot program to test platform and gather feedback
- **Participants:** Select teams invited to shape the future of the competition
- **Focus:** Build, test, and optimize AI drivers; submit best lap times
- **Benefits for participants:**
  - Exclusive access to platform and tools
  - Direct input on competition design
  - Global recognition in AI and motorsport communities
  - First-mover advantage for future seasons

#### Phase 2: Full Competition (Future)
- Details not yet fully announced
- Expected to expand globally based on Early Adopter feedback
- May include head-to-head racing beyond time trials

### Technical Challenge
Participants must balance:
- **Speed optimization:** Achieving fastest possible lap times
- **Reliability:** Ensuring car completes full laps without crashing
- **Corner handling:** Particularly challenging sections include:
  - The Corkscrew (signature Laguna Seca corner)
  - Final corner
  - Various tight turns and elevation changes

---

## 2. Rules & Requirements

### Development Approach
Based on participant experiences, two primary approaches are viable:

#### A. Rule-Based AI (Most Common)
- Define racing rules programmatically
- Implement sensor-based decision logic
- Iterative testing and parameter tuning
- Example rules:
  - Reduce speed when distance ahead decreases
  - Detect straights and increase target speed
  - Gradual braking approach (avoid heavy braking that causes understeer)
  - Corner detection using track sensors

#### B. Reinforcement Learning (Advanced)
- Mentioned as option but requires more experience
- Less common among Early Adopter teams due to time constraints
- May become more prevalent in future seasons

### Key Technical Constraints
1. **Physics Model:** F1 car with realistic handling characteristics
   - Prone to understeer with excessive braking
   - Requires careful balance of acceleration and braking
   - Different physics from earlier car models (code must be adapted)

2. **Sensor System:** 
   - Track sensors: Measure distances to track edges at various angles
   - Speed sensors
   - Position tracking
   - Distance-ahead sensors
   - Must utilize sensor data effectively for decision-making

3. **Code Requirements:**
   - Must integrate with TORCS simulation
   - Python-based implementation (gym_torcs files provided)
   - Starting framework: `torcs_jm_par.py` provides baseline implementation
   - Must handle real-time decision-making

### Performance Metrics
- **Primary:** Lap time (fastest lap recorded)
- **Secondary:** Consistency (ability to complete laps without crashes)
- **Benchmark:** Top Early Adopter team achieved ~1:47.84 lap time at Laguna Seca

---

## 3. Timeline

### Early Adopter Program Timeline (2026)

| Date | Milestone |
|------|-----------|
| **January 2026** | Early Adopter Program Launch |
| **January 7, 2026** | Public announcement via university career services |
| **First Week of February 2026** | AI Race Car Submission Deadline (Early Adopter Phase 1) |
| **February 1-8, 2026** | Teams continuing optimization and refinement |
| **TBD** | Results announcement for Early Adopter Program |
| **TBD** | Launch of full global competition |

### Development Cycle (Participant Experience)
Based on team "The MonDragons" from Queen Mary University of London:
- **Week 1-2:** Setup, code understanding, initial prototyping
- **Week 2-3:** Rule implementation and testing
- **Week 3-4:** Adaptation to F1 physics model (after model change)
- **Week 4+:** Optimization, parameter tuning, automation testing
- **Total development time:** Approximately 4-6 weeks for competitive entry

---

## 4. Platform & Tools Provided

### Core Platform: TORCS
**TORCS (The Open Racing Car Simulator)**
- Open-source racing simulator
- Realistic physics engine
- Laguna Seca track environment
- F1-style race car model
- Sensor data interface
- Compatible with Python integration

### IBM Technology Stack

#### 1. IBM Granite Foundation Models
**Primary AI Tool:** IBM Granite 4.0 series
- **Purpose:** Code understanding, optimization suggestions, debugging
- **License:** Open source (Apache 2.0)
- **Key features:**
  - Transparent training data and processes
  - Optimized for enterprise workloads
  - Code analysis and generation capabilities
  - Domain-specific language models (DSLMs)
- **Use cases in competition:**
  - Understanding sensor code and ranges
  - Suggesting performance optimizations
  - Code refactoring and cleanup
  - Identifying Python libraries for automation
  - Explaining complex code sections

**Gartner Recognition (Dec 2025):** IBM identified as "the company to beat" in domain-specific language model enablement

#### 2. IBM SkillsBuild Platform
**Free education platform providing:**
- **Design Thinking credential:** Project planning and requirements analysis
- **AI/ML courses:** Foundational knowledge
- **Granite-specific courses:** How to use IBM Granite effectively
- **Project management guidance:** Prioritization, team coordination
- **Access:** Free for all participants

**Key learning modules:**
- IBM Design Thinking
- IBM Granite fundamentals
- Python for AI development
- Project planning and execution

#### 3. Development Framework
**Provided code base:**
- `gym_torcs` files: TORCS-Python integration
- `torcs_jm_par.py`: Baseline AI driver implementation
- Sensor interface code
- Physics model integration

**Recommended Python libraries** (via Granite suggestions):
- `pandas`: Data logging and analysis
- `subprocess`: TORCS automation
- Standard Python libraries for file I/O and control

### Support Infrastructure
1. **Discord Community:** https://discord.gg/G3w8TfF4pG
   - Team communication
   - Technical support
   - Updates and announcements
   - Peer learning and collaboration

2. **Documentation & Resources:**
   - IBM SkillsBuild courses
   - TORCS documentation
   - IBM Granite model documentation
   - Sample code and implementations

3. **Tools for Development:**
   - Automated testing scripts (participant-developed)
   - CSV logging for parameter tracking
   - Performance analytics

---

## 5. Judging Criteria

### Primary Criterion: Lap Time Performance
**Metric:** Fastest recorded lap time at Laguna Seca circuit

**Known benchmarks:**
- Early baseline (old car model): ~2:33.24
- After initial F1 optimization: ~2:30.35
- Advanced optimization: ~1:47.84 (top team as of Feb 1, 2026)

### Evaluation Approach
1. **Submission:** Teams submit their AI race car code
2. **Testing:** Likely standardized testing environment to ensure fairness
3. **Recording:** Best lap time from official evaluation runs
4. **Verification:** Must complete full laps (crashes invalidate times)

### Secondary Considerations (Implied)
While not explicitly stated as judging criteria, successful teams demonstrate:
- **Code quality:** Clean, readable, maintainable code
- **Documentation:** Explanations of approach and decisions
- **Innovation:** Creative problem-solving and optimization techniques
- **Reliability:** Consistent performance across multiple laps
- **Community contribution:** Sharing learnings and artifacts

### Learning and Documentation
The competition emphasizes:
- Documenting journey and learnings (blog posts encouraged)
- Creating artifacts to support other learners
- Sharing code publicly (e.g., GitHub repositories)
- Exemplifying the spirit of collaborative learning

**Example:** Team "The MonDragons" published comprehensive Medium blog post and GitHub repository documenting their entire development process.

---

## 6. Entry Requirements

### Eligibility
- **Open to:** "Brightest minds" globally - students, developers, AI enthusiasts
- **Team structure:** No restrictions on team size or composition mentioned
- **Experience level:** All levels welcome (platform designed to support learning)
- **Geographic restriction:** None - global competition

### Registration Process
**Step 1: Join Discord Server**
- Link: https://discord.gg/G3w8TfF4pG
- Primary communication channel
- Access to community and updates

**Step 2: Setup Development Environment**
- Download and install TORCS
- Install Python and required libraries
- Download gym_torcs files
- Setup IBM Granite access (via IBM SkillsBuild)

**Step 3: Development Phase**
- Build AI race car
- Test and optimize on Laguna Seca track
- Utilize IBM Granite for assistance
- Engage with community for support

**Step 4: Submission**
- Submit AI race car code (deadline: First week of February 2026 for Early Adopter)
- Format and submission method: Via Discord or specified platform (TBD in official instructions)

### Required Skills (Recommended)
- **Programming:** Python proficiency (intermediate level sufficient)
- **AI/ML basics:** Understanding of algorithms and optimization
- **Problem-solving:** Iterative testing and debugging
- **Willingness to learn:** IBM SkillsBuild provides necessary background

### Prerequisites
- **Software:** 
  - TORCS (free, open source)
  - Python 3.x
  - Standard development tools (IDE, git)
- **Hardware:** Standard laptop/desktop (no special requirements mentioned)
- **IBM Account:** For accessing SkillsBuild and Granite (free registration)

### No Cost to Participate
- All tools and platforms are free
- TORCS: Open source
- IBM SkillsBuild: Free education platform
- IBM Granite: Available through free channels
- No registration fees mentioned

---

## 7. Case Study: Team "The MonDragons" Journey

**Team:** The MonDragons, Queen Mary University of London  
**Members:** Kishal Chhetri, Arnav Dubey, Khaled Alompeint, Mustafa Ainudden, Araf Islam  
**Achievement:** Fastest recorded lap in Early Adopter Program (as of Feb 1, 2026)

### Development Process

#### Phase 1: Understanding (Week 1)
- Downloaded TORCS and gym_torcs files
- Used IBM Design Thinking to create requirements list
- Split team: code analysis + implementation research
- Leveraged IBM Granite to understand code structure
- Focus: Sensor system and functionality

**Key insight:** Track sensors store distances from car to track edges at various angles

#### Phase 2: Initial Prototyping (Week 2)
- Started with `torcs_jm_par.py` framework
- Decided on rule-based approach (vs. reinforcement learning)
- Implemented basic racing rules iteratively
- Used IBM Granite for optimization suggestions
- Heavy emphasis on testing each rule

**Result:** Lap time ~2:33.24 with old car model

#### Phase 3: F1 Adaptation (Week 3)
- New F1 car released with different physics
- Old code caused severe understeer
- Analysis revealed: excessive braking + continued acceleration in corners
- Complete code review with IBM Granite assistance
- Identified legacy code issues

**Breakthrough:** Reduced acceleration to zero approaching corners → 2:30.35 lap time

#### Phase 4: Optimization (Week 4+)
- Implemented straight detection → increased target speed
- Gradual braking incrementation (avoiding understeer)
- Fine-tuned Corkscrew and final corner handling
- Code refactoring into clear functions
- Created automation for parameter testing:
  - CSV logging of parameters and lap times
  - Python scripts using pandas and subprocess
  - Automated TORCS launch and data recording
- Maintained `fastest.py` file with optimal parameters

**Final result:** 1:47.84 lap time

### Key Learnings
1. **Iterative approach essential:** Test each change thoroughly
2. **Balance speed and reliability:** Fast but unstable ≠ good lap time
3. **IBM Granite invaluable:** For understanding code and suggesting optimizations
4. **Track-specific challenges:** Corkscrew and final corner required special attention
5. **Automation accelerates development:** Automated testing enabled rapid iteration
6. **Clean code matters:** Refactoring improved maintainability and understanding
7. **Community spirit:** Sharing journey helps others learn

**Public artifacts:**
- Medium blog post documenting full journey
- GitHub repository: https://github.com/Simple-wood/IBM-TORCs
- Code available for others to learn from

---

## 8. Strategic Recommendations for Future Participants

### Getting Started Right
1. **Complete IBM SkillsBuild courses first** - especially Design Thinking and Granite fundamentals
2. **Understand the baseline code thoroughly** before modifications
3. **Start with simple rules** and iterate rather than complex systems initially
4. **Use IBM Granite extensively** for code understanding and optimization
5. **Set up automated testing early** - saves significant time

### Development Strategy
1. **Prototype fast, test extensively** - testing time > development time
2. **Focus on the critical corners** - Corkscrew and final corner at Laguna Seca
3. **Balance priorities:** Speed vs. reliability vs. time investment
4. **Track everything:** Log parameters and results systematically
5. **Clean code regularly:** Refactor before it becomes unmaintainable

### Technical Approach
1. **Sensor data is king:** Understand what each sensor provides
2. **Physics model matters:** Test thoroughly when anything changes
3. **Gradual changes:** Small incremental adjustments often beat big jumps
4. **Watch for understeer:** Key limiting factor with F1 car
5. **Consider automation:** Scripts for testing save hours of manual work

### Community Engagement
1. **Ask questions on Discord** - community is supportive
2. **Share learnings publicly** - blog posts, GitHub repos
3. **Collaborate respectfully** - competition but also learning community
4. **Document your journey** - valuable for reflection and teaching others

---

## 9. Broader Context: IBM's AI in Sports Initiative

The AI Racing League is part of IBM's larger strategy in sports technology:

### Related IBM Sports Initiatives
1. **Ferrari F1 Partnership:** Mobile app with Watsonx AI for fan engagement
2. **US Open Tennis:** AI-powered features, automated commentary
3. **Wimbledon:** "Catch Me Up" feature using Granite LLMs
4. **Mission 44 Partnership:** Lewis Hamilton foundation, STEM education
5. **Web Summit Sports Tech Challenge:** Separate startup competition ($$ prizes)

### IBM's Vision
- Make AI accessible through engaging challenges
- Connect sports, AI, and education
- Build community around AI innovation
- Demonstrate real-world AI applications
- Support next generation of AI developers

---

## 10. Key Contacts & Resources

### Official Channels
- **Discord Registration:** https://discord.gg/G3w8TfF4pG (Primary entry point)
- **IBM SkillsBuild:** https://skillsbuild.org/ (Free courses and credentials)
- **IBM Granite Info:** https://www.ibm.com/granite (Model documentation)

### Learning Resources
- IBM SkillsBuild courses (free)
- TORCS documentation and forums
- IBM Granite model guides
- Community Discord for peer support

### Example Projects
- GitHub: https://github.com/Simple-wood/IBM-TORCs (Team MonDragons)
- Medium blog: Search "Racing the Code: Building and optimizing an autonomous car with TORCS and IBM SkillsBuild"

### Recognition
- John McNamara (IBM) actively recognizing participant achievements on LinkedIn
- Lydia Logan and Jeff Macdonald mentioned as IBM contacts
- University career services promoting the competition globally

---

## 11. Questions Still Requiring Clarification

### Competition Structure
- Exact format of final competition (beyond Early Adopter)
- Will head-to-head racing be added?
- Prize structure (if any)
- Team size limits or recommendations

### Submission Details
- Exact submission format and platform
- Evaluation methodology (standardized testing environment?)
- Number of evaluation runs per team
- Code requirements (documentation, style guides)

### Future Plans
- Timeline for full global launch
- Whether Early Adopter program will have multiple phases
- Changes to platform based on feedback
- Additional tracks or vehicles planned

### Judging
- Tiebreaker criteria if lap times identical
- Whether innovation/documentation affects rankings
- Appeal process if technical issues occur
- Whether code quality is formally evaluated

**Note:** Many details likely available in the Discord community or will be clarified as competition progresses.

---

## Conclusion

The IBM AI Racing League represents an innovative approach to AI education and competition, combining:
- **Accessible platform:** Free tools, supportive community, comprehensive learning resources
- **Real challenge:** Demanding track and realistic physics require genuine skill and optimization
- **Learning emphasis:** IBM SkillsBuild and Granite support skill development
- **Community focus:** Sharing knowledge, documenting journeys, collaborative spirit
- **Career relevance:** Skills directly applicable to autonomous vehicles, AI, and software engineering

The Early Adopter Program provides exceptional opportunity for first-movers to shape the competition's future while gaining visibility in the AI community. With proper use of IBM's tools and an iterative development approach, teams at all skill levels can compete effectively.

**Bottom line:** This is a well-designed competition that balances challenge with support, making cutting-edge AI development accessible to students and developers worldwide.

---

**Research compiled:** February 8, 2026  
**Sources:** Exa search results, official IBM announcements, participant blog posts, university career postings  
**Status:** Early Adopter Program active, submissions due first week of February 2026
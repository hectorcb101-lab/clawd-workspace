# AI Chips 2025: Practical Buying Guide
## Pricing, Availability & Vendor Recommendations

**Research Date:** January 2026  
**Focus:** Actionable deployment information with specific pricing and procurement paths

---

## Executive Summary

**Key Findings:**
- **H100 pricing dropped 44%** in 2025 due to increased supply
- **Cloud rental is 40-70% cheaper** with specialized providers vs hyperscalers
- **On-premise breakeven:** 14 months for 24/7 usage at current cloud rates
- **AMD MI300X:** Now widely available at $1.50-$6/hr, offering 192GB memory advantage
- **B200 availability:** Limited but expanding, premium pricing ($2.49-$68/hr cloud)

---

## 1. NVIDIA GPU Pricing (H100/H200/B200)

### H100 (Hopper Architecture)
**Purchase Price:**
- **Single GPU:** $25,000 - $40,000 (typically $27K-$30K)
- **8-GPU Server:** $216,000 - $400,000+ (with infrastructure)

**Cloud Rental (Per GPU/Hour):**

| Provider Type | Price Range | Best Options |
|--------------|-------------|--------------|
| **Specialized Providers** | $1.49 - $3.99/hr | RunPod ($1.99), Lambda Labs ($2.99), GMI Cloud ($2.10) |
| **AWS (p5.48xlarge)** | $3.90/hr | Spot: $2.50, Savings Plans: $1.90-$2.10 |
| **GCP (A3-highgpu-1g)** | $3.00/hr | Preemptible: $2.25 |
| **Azure (ND H100 v5)** | $6.98/hr | Spot: $70-$75/hr for 8-GPU VM |
| **Oracle Cloud** | $1.87/hr | (Normalized for 8xH100 at $15/hr total) |

**✅ RECOMMENDED:** Lambda Labs ($2.99/hr) or GMI Cloud ($2.10/hr) for on-demand, AWS Savings Plans ($1.90/hr) for long-term committed workloads.

---

### H200 (Enhanced Hopper)
**Purchase Price:**
- **Single GPU:** $30,000 - $40,000 (15-20% premium over H100)
- **8-GPU Server:** $308,000 - $315,000

**Cloud Rental (Per GPU/Hour):**
- **GMI Cloud:** $3.35 - $3.50/hr (Tier-4 data centers, InfiniBand)
- **Jarvislabs:** $3.80/hr (single GPU rentals available)
- **Google Cloud Spot:** $3.72/hr (preemptible)
- **AWS/Azure:** $10.60/hr

**Key Advantage:** 141GB HBM3e memory (vs 80GB H100) + 4.8 TB/s bandwidth (vs 3.0 TB/s)

**✅ RECOMMENDED:** GMI Cloud for production, Google Cloud Spot for cost-sensitive workloads.

---

### B200 (Blackwell Architecture)
**Purchase Price:**
- **Production Cost:** $6,400 (estimated)
- **Sale Price:** $30,000 - $40,000 per chip
- **Gross Margin:** ~82% for NVIDIA

**Cloud Rental (Per GPU/Hour):**

| Provider | Price | Availability |
|----------|-------|--------------|
| **Lambda Labs** | $2.99/hr (3-yr reserved) | Available |
| **Lambda Labs** | $3.79/hr (on-demand) | Available |
| **Modal** | $6.25/hr (serverless) | Available |
| **RunPod** | $5.99/hr (on-demand) | Available |
| **Baseten** | $9.98/hr (serverless) | Available |
| **AWS** | $14.24/hr (on-demand), $8.14/hr (capacity block) | Limited |

**Key Specs:**
- **VRAM:** 192GB
- **Memory Bandwidth:** 8,000 GB/s
- **FP16 Performance:** 4,500 TFLOPS

**⚠️ Availability Status:** Limited but expanding Q1 2026. Expect 6-12 week lead times for on-premise orders.

**✅ RECOMMENDED:** Lambda Labs for best pricing, Modal/Baseten for serverless flexibility.

---

## 2. AMD MI300X - The High-Memory Alternative

### Pricing & Availability

**Cloud Rental (Per GPU/Hour):**

| Provider | Price | Configuration | Notes |
|----------|-------|---------------|-------|
| **TensorWave** | $1.50/hr | 8x MI300X bare-metal | Best value |
| **Vultr** | $1.85/hr | Chicago region | Self-service |
| **DigitalOcean** | $1.99/hr | Single GPU | Easy deployment |
| **Hot Aisle** | $1.99/hr | Various configs | Flexible |
| **NeevCloud** | $2.20/hr | Pre-reserve supercluster | |
| **RunPod** | $2.99/hr | Community Cloud | |
| **Oracle Cloud** | $6.00/hr | BM.GPU.MI300X.8 | Enterprise support |
| **Azure** | $7.86/hr | ND96isr_MI300X_v5 | Full integration |

**Key Advantage:** 192GB unified HBM3 memory (same as B200, more than H100/H200)

**AMD Developer Cloud Access:**
- **Complimentary:** 25 hours free credit (~$50 value) for qualified developers
- **Pay-As-You-Go:** Instant access with credit card

**✅ RECOMMENDED:** 
- **Cost-conscious:** TensorWave ($1.50) or Vultr ($1.85)
- **Enterprise:** Oracle Cloud ($6.00) for Tier-1 support
- **Testing:** AMD Developer Cloud (25 free hours)

**Procurement Contact:**
- Kyle White, VP of AI Infrastructure Sales, Oracle Cloud

---

## 3. Cloud Pricing Comparison (AWS vs Azure vs GCP)

### H100 Pricing Summary (2025/2026)

| Provider | Instance Type | On-Demand ($/GPU-hr) | Spot/Preemptible | Reserved/Savings |
|----------|---------------|---------------------|------------------|------------------|
| **AWS** | p5.48xlarge (8xH100) | $3.90 | $2.50 | $1.90-$2.10 (1-3yr) |
| **GCP** | A3-highgpu-1g | $3.00 | $2.25 | N/A |
| **Azure** | ND H100 v5 | $6.98 | ~$5.90 | 60% off (reserved) |
| **Oracle** | BM.GPU.H100.8 | $1.87 | N/A | Contact sales |

### Total Cost Examples (8x H100 Node, 30-Day Month)

| Provider | Configuration | Monthly Cost | Annual Cost |
|----------|---------------|--------------|-------------|
| **AWS On-Demand** | 8x H100 @ $3.90/hr | $22,464 | $269,568 |
| **AWS Spot** | 8x H100 @ $2.50/hr | $14,400 | $172,800 |
| **GCP On-Demand** | 8x H100 @ $3.00/hr | $17,280 | $207,360 |
| **Azure On-Demand** | 8x H100 @ $6.98/hr | $40,147 | $481,766 |
| **GMI Cloud** | 8x H100 @ $2.10/hr | $12,096 | $145,152 |

**Key Insight:** Azure is **2-3x more expensive** than AWS/GCP for H100 workloads.

**Hidden Costs to Watch:**
- **Data Egress:** Can add 20-40% to hyperscaler bills
- **Storage:** Persistent volumes add $0.10-$0.30/GB-month
- **Networking:** Inter-region transfer fees
- **Support:** Enterprise support adds 10-15% to base costs

**✅ RECOMMENDED:**
- **AWS:** Best for enterprises with existing AWS commitment, use Savings Plans
- **GCP:** Best on-demand rates among hyperscalers, good for short bursts
- **Specialized Providers (GMI, Lambda):** 40-70% savings for pure GPU workloads

---

## 4. On-Premise vs Cloud TCO Analysis

### Purchase Costs (8x H100 Server)

| Component | Cost Range |
|-----------|------------|
| **8x H100 GPUs** | $216,000 - $320,000 |
| **Server Chassis** | $30,000 - $50,000 |
| **Networking (InfiniBand)** | $20,000 - $40,000 |
| **Power/Cooling Infrastructure** | $50,000 - $100,000 |
| **Installation/Setup** | $10,000 - $20,000 |
| **TOTAL Initial CapEx** | **$326,000 - $530,000** |

### Annual Operating Costs (8x H100)

| Category | Annual Cost |
|----------|-------------|
| **Power (8x H100 @ 700W, $0.12/kWh, 70% utilization)** | $46,482 |
| **Cooling (30% of power cost)** | $13,945 |
| **Maintenance/Support (10% hardware)** | $32,600 |
| **Staff (0.5 FTE DevOps/SRE @ $150K)** | $75,000 |
| **TOTAL Annual OpEx** | **$168,027** |

### Breakeven Analysis (vs Cloud)

**Scenario: 8x H100 @ 24/7 Usage**

| Cloud Provider | $/GPU-hr | Annual Cost | Breakeven (Months) |
|----------------|----------|-------------|-------------------|
| **Lambda Labs** | $2.99 | $209,462 | 20 months |
| **AWS On-Demand** | $3.90 | $273,168 | **14 months** |
| **GCP** | $3.00 | $210,240 | 20 months |
| **Azure** | $6.98 | $489,254 | **8 months** |

**Key Findings:**
- **Break-even at 50% utilization:** 28-40 months
- **Break-even at 100% utilization:** 14-20 months
- **5-Year TCO Savings (on-prem):** 40-60% vs hyperscalers

### When On-Premise Makes Sense

✅ **GO ON-PREMISE IF:**
- Sustained utilization >50% (12+ hours/day)
- Workloads run for 18+ months
- Data gravity concerns (multi-TB datasets)
- Regulatory/compliance requirements (GDPR, HIPAA)
- >1 billion tokens/month processing volume

❌ **STAY CLOUD IF:**
- Bursty/unpredictable workloads
- Experimentation phase (<6 months)
- Small team (<5 people)
- Need instant scalability (10x+ spikes)
- Limited capital budget

### Dell AI Factory TCO Study (July 2025)

**4-Year Comparison:**
- **Dell On-Prem (CapEx):** 63% cheaper than AWS, 61% cheaper than Azure
- **Dell APEX (Subscription):** 62% cheaper than AWS, 60% cheaper than Azure

---

## 5. Enterprise Deployment Guide

### Deployment Options Matrix

| Option | Best For | Typical Cost | Lead Time |
|--------|----------|--------------|-----------|
| **Hyperscaler (AWS/GCP/Azure)** | Enterprises with existing cloud commitment | $3-7/GPU-hr | Instant |
| **Specialized Cloud (Lambda/GMI)** | AI-native startups, cost-conscious teams | $2-4/GPU-hr | Instant-1 week |
| **Bare Metal Cloud (Oracle/CoreWeave)** | High-performance training, multi-node | $2-6/GPU-hr | 1-2 weeks |
| **On-Premise Purchase** | Long-term, sustained workloads | $326K-$530K upfront | 6-12 weeks |
| **Hybrid (Burst-to-Cloud)** | Variable workloads, compliance needs | Base + burst costs | 4-8 weeks setup |

### Procurement Process

#### Cloud (Specialized Providers)
**Timeline: Same Day - 1 Week**

1. **Sign Up:** Create account (Lambda Labs, RunPod, GMI Cloud)
2. **Payment:** Add credit card or request invoice (enterprises)
3. **Select Instance:** Choose GPU type, quantity, region
4. **Deploy:** Spin up in <5 minutes
5. **Scale:** Add/remove GPUs on-demand

**Contacts:**
- Lambda Labs: https://lambdalabs.com/service/gpu-cloud
- GMI Cloud: https://gmicloud.ai/
- RunPod: https://www.runpod.io/

#### Cloud (Hyperscalers)
**Timeline: Instant - 2 Weeks (for quota increases)**

1. **AWS:** Request P5 instance quota increase via AWS Support
2. **GCP:** Enable Compute Engine API, request A3 quota
3. **Azure:** Submit ND H100 v5 quota request

**⚠️ Note:** Initial quotas are often 0-8 GPUs. Large clusters (32+ GPUs) require sales engagement and 2-4 week approval.

#### On-Premise Purchase
**Timeline: 6-12 Weeks**

**Option 1: OEM Direct (NVIDIA Partners)**
- **Supermicro:** https://www.supermicro.com/en/solutions/ai
- **Dell:** https://www.dell.com/en-us/ai-technologies
- **HPE:** https://www.hpe.com/us/en/compute/hpc/ai.html
- **Lead Time:** 8-12 weeks for H100, 12-16 weeks for H200/B200

**Option 2: Turnkey AI Infrastructure**
- **Lambda Labs:** Pre-configured servers with support ($250K+ for 8x H100)
- **NVIDIA DGX:** Official systems, premium support ($400K-$500K for DGX H100)

**Option 3: Build Your Own**
1. Source GPUs from distributors (CDW, Ingram Micro)
2. Select compatible server platform
3. Integrate networking (NVIDIA Spectrum-X, InfiniBand)
4. Deploy orchestration (Kubernetes, Slurm)
5. **Timeline:** 12-16 weeks, requires in-house expertise

### Infrastructure Requirements (On-Premise)

**Per 8x H100 Node:**
- **Power:** 10-12 kW (700W/GPU + overhead)
- **Cooling:** 30-36 kW cooling capacity
- **Network:** 400 Gbps InfiniBand or 400GbE
- **Rack Space:** 4-6U

**Minimum Viable Setup:**
- **1x 8-GPU Node:** $326K-$530K
- **4x 8-GPU Cluster:** $1.3M-$2.1M (for multi-node training)

### Software Stack Considerations

**Model Training/Fine-Tuning:**
- NVIDIA AI Enterprise (included with DGX, $3K-$5K/GPU standalone)
- PyTorch, TensorFlow (free, open-source)
- Hugging Face Transformers (free)

**Orchestration:**
- **Kubernetes + KubeFlow:** Open-source, complex setup
- **Run:ai:** Commercial GPU orchestration ($2K-$5K/GPU annually)
- **Slurm:** Free, HPC-focused

**Monitoring:**
- NVIDIA DCGM (free)
- Prometheus + Grafana (free)

---

## 6. Vendor Recommendations by Use Case

### 🚀 Startup / Experimentation (<$50K/year budget)
**RECOMMENDED:**
1. **Lambda Labs** ($2.99/hr H100) - Academic-friendly, simple UI
2. **RunPod Community Cloud** ($1.99/hr H100) - Cheapest spot pricing
3. **AMD Developer Cloud** (25 free hours) - Testing MI300X

**Why:** No commitment, pay-as-you-go, instant scaling.

---

### 🏢 Enterprise / Production Workloads ($200K-$1M/year budget)
**RECOMMENDED:**
1. **AWS with Savings Plans** ($1.90/hr H100) - Existing AWS footprint
2. **GMI Cloud** ($2.10-$3.50/hr H100/H200) - Specialized AI infrastructure
3. **Oracle Cloud** ($1.87/hr H100, $6.00/hr MI300X) - Bare metal, enterprise support

**Why:** Reliability, SLAs, compliance certifications, dedicated support.

---

### 🔬 Research / Long-Term Training (>18 months, >$500K budget)
**RECOMMENDED:**
1. **On-Premise Dell AI Factory** (63% TCO savings vs cloud over 4 years)
2. **Lambda On-Premise Servers** (Turnkey H100 systems with support)
3. **Hybrid:** On-prem base + AWS burst capacity

**Why:** Lowest TCO for sustained usage, data control, no egress fees.

---

### 💾 Large Memory Workloads (>80GB VRAM)
**RECOMMENDED:**
1. **AMD MI300X via TensorWave** ($1.50/hr, 192GB memory)
2. **H200 via GMI Cloud** ($3.35/hr, 141GB memory)
3. **B200 via Lambda Labs** ($2.99/hr reserved, 192GB memory)

**Why:** Large language models (70B+), scientific computing, large batch inference.

---

### 🌐 Multi-Region / Global Deployment
**RECOMMENDED:**
1. **AWS P5** (available in 5+ regions) - us-east-1, us-west-2, eu-west-1
2. **Azure ND H100 v5** (global presence) - Higher cost, but widest availability
3. **Hybrid Multi-Cloud** - GMI (North America) + Hyperscaler (Asia/EU)

**Why:** Low latency for global user base, compliance with data residency.

---

## 7. Key Takeaways & Action Items

### Pricing Summary (H100 Equivalent)
- **Cheapest Cloud:** TensorWave MI300X @ $1.50/hr
- **Best H100 Value:** GMI Cloud @ $2.10/hr or Oracle @ $1.87/hr
- **Hyperscaler Best:** GCP @ $3.00/hr or AWS Spot @ $2.50/hr
- **On-Premise Breakeven:** 14-20 months @ 24/7 usage

### Availability Status (Q1 2026)
- ✅ **H100:** Widely available, prices dropped 44% in 2025
- ✅ **H200:** Available, 15-20% premium, limited on-premise stock
- ⚠️ **B200:** Limited cloud availability, 12-16 week lead time on-premise
- ✅ **MI300X:** Widely available across 8+ providers, best memory value

### Immediate Action Plan

**1. Define Your Workload Profile (Week 1)**
- Estimate GPU hours/month
- Identify peak vs sustained usage
- Calculate memory requirements

**2. Run Cloud Pilot (Week 2-4)**
- Start with Lambda Labs or RunPod ($2-3/hr)
- Benchmark your models
- Measure actual utilization

**3. Cost Model (Week 4)**
- Project 12-month cloud costs
- Compare to on-premise TCO
- Include hidden costs (egress, storage)

**4. Procurement Decision (Week 5-6)**
- **If <$150K annual:** Stay cloud (Lambda/GMI)
- **If $150K-$500K annual:** Hybrid or reserved cloud
- **If >$500K annual:** Evaluate on-premise

**5. Deploy (Week 6-20)**
- **Cloud:** Instant-1 week
- **On-Premise:** 6-12 weeks for H100, 12-16 weeks for B200

---

## 8. Contact Information & Resources

### Cloud Providers
- **Lambda Labs:** https://lambdalabs.com/service/gpu-cloud
- **GMI Cloud:** https://gmicloud.ai/ | Kyle White (Oracle AI Infrastructure)
- **RunPod:** https://www.runpod.io/
- **TensorWave (MI300X):** https://tensorwave.com/

### On-Premise Hardware
- **Supermicro:** https://www.supermicro.com/en/solutions/ai
- **Dell Technologies:** https://www.dell.com/en-us/ai-technologies
- **NVIDIA DGX:** https://www.nvidia.com/en-us/data-center/dgx-platform/

### Deployment Guides
- **NVIDIA AI Enterprise:** https://docs.nvidia.com/ai-enterprise/deployment/
- **AWS SageMaker:** https://aws.amazon.com/sagemaker/
- **Azure Machine Learning:** https://azure.microsoft.com/en-us/products/machine-learning/

---

**Research Compiled:** January 2026  
**Next Update:** April 2026 (Post-B200 General Availability)

---

## Appendix: Quick Decision Matrix

```
IF total_gpu_hours < 1000/month AND budget_flexible:
    → Lambda Labs ($2.99/hr H100)

ELIF total_gpu_hours > 4000/month AND sustained_18mo+:
    → On-Premise ($326K-$530K upfront)

ELIF memory_requirements > 80GB:
    → TensorWave MI300X ($1.50/hr, 192GB)

ELIF existing_aws_commitment:
    → AWS Savings Plans ($1.90/hr)

ELIF cost_optimized AND flexible_workload:
    → RunPod Spot ($1.99/hr) or Oracle Cloud ($1.87/hr)

ELSE:
    → GMI Cloud ($2.10-$3.50/hr) # Best balance of cost/reliability
```

**Decision Confidence:**
- High: H100 pricing and availability (mature market)
- Medium: H200 pricing (limited data points)
- Low: B200 pricing (early market, fluctuating)

---

*This guide is based on publicly available pricing as of January 2026. Prices are subject to change. Contact vendors directly for enterprise volume discounts and custom configurations.*

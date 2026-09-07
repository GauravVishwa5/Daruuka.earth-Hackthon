# 01 — Project Overview

> **Navigation:** [Index](./00_DOCUMENTATION_INDEX.md) | **Next:** [System Architecture](./02_SYSTEM_ARCHITECTURE.md)

---

## 1. Problem Statement

Across the globe, 40% of agricultural land is degraded, threatening global food security, climate stability, and biological resilience. Landowners, regenerative farmers, agronomic advisors, and conservation managers face compounding ecological crises:

1. **Information Fragmentation:** Scientific guidance is buried inside dense institutional reports (IPCC, IPBES, FAO) and academic papers inaccessible during day-to-day decision-making.
2. **Context-Blind Recommendations:** Generic AI models provide dangerous or counterproductive ecological advice because they fail to correlate multiple environmental variables simultaneously (e.g., advising water-intensive cover crops in semi-arid zones experiencing water deficit).
3. **The "Chatbot Hallucination" Trap:** Standard LLMs hallucinate quantitative impact numbers, claim fabricated yield benefits, or cite non-existent peer-reviewed studies.
4. **Lack of Multi-Metric Synthesis:** Ecological degradation is inherently systemic. Soil organic carbon cannot be solved in isolation from precipitation patterns, thermal stress, or crop monoculture intensity.

---

## 2. The Solution: Darukaa.Earth

**Darukaa.Earth** is an **AI Biodiversity Intelligence and Environmental Decision Engine**. 

Operating as an automated Environmental Scientist, the platform ingests empirical physical telemetry (soil physics, microclimatic data, topology, land use) and applies **evidence-grounded multi-metric reasoning** coupled with scientific literature RAG. It pinpoints ecological vulnerabilities, evaluates trade-offs, and outputs ranked, auditable intervention plans backed by verifiable citations from authoritative bodies (FAO, IPCC, IPBES).

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                       DARUKAA.EARTH                         │
       │                                                             │
       │   Structured Environmental Telemetry (Soil, Climate, Land)  │
       │                              +                              │
       │         Deterministic Multi-Metric Compound Reasoning       │
       │                              +                              │
       │             Authoritative Scientific Literature             │
       │                              +                              │
       │            Post-Generation Claim & Citation Verifier        │
       └─────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                   Auditable, Science-Backed Interventions
                     with Explicit Trade-Offs & Confidence
```

---

## 3. Product Differentiator: Why This is Not a Generic Chatbot

Most AI hackathon projects fall into one of two superficial architectural patterns:
1. **Generic Chatbot:** `User -> LLM -> Answer` (completely ungrounded, highly prone to hallucination, incapable of complex multi-variable threshold logic).
2. **Basic Semantic RAG:** `User -> Embeddings Search -> LLM -> Answer` (retrieves text snippets based on keyword/semantic similarity, but lacks any deterministic ecological calculation or scientific validation).

### The Darukaa.Earth Advantage

| Feature | Generic LLM Chatbot | Basic Naive RAG | Darukaa.Earth |
| :--- | :--- | :--- | :--- |
| **Environmental Reasoning** | Hallucinated heuristics | Naive text stitching | **Deterministic threshold matrix & cross-metric stress calculation** |
| **Input Incompleteness** | Guesses or assumes missing variables | Answers blindly without context | **Proactive slot-filling and targeted clarifying queries** |
| **Data Types** | Unstructured text only | Text chunks only | **Structured telemetry + relational ontology + semantic chunks** |
| **Scientific Grounding** | Imagined citations | Top-k vector snippets | **Hierarchical institutional sources (FAO, IPCC, IPBES) with chunk IDs** |
| **Fact Checking** | None | None | **Automated post-generation claim validation pipeline** |
| **Trade-Off Analysis** | Overly optimistic generalizations | Often omitted | **Explicit matrix showing risk vs ecological vs economic tradeoffs** |
| **Explainability** | Black-box output | Source link dump | **Step-by-step logic trace with confidence scoring (0.0–1.0)** |

---

## 4. Target Users & Core Use Cases

### Target Personas
1. **Regenerative Farmers & Landowners:** Managing 10–5,000 hectares, facing declining soil organic matter, drought stress, and diminishing crop yields.
2. **Agronomic Advisors & Extension Agents:** Requiring rapid, verifiable evidence to formulate multi-year farm transition plans.
3. **Biodiversity & Conservation Officers:** Prioritizing corridor restoration and pollinator habitat interventions based on empirical degradation metrics.
4. **Impact Investors & Carbon Project Developers:** Needing rigorous baseline environmental stress assessments prior to funding ecological restoration projects.

### Primary Use Cases
* **Soil & Water Vulnerability Assessment:** Detecting latent compound stress before crop failure occurs.
* **Evidence-Based Intervention Selection:** Identifying whether legume intercropping, agroforestry strips, biochar amendment, or reduced tillage provides the highest net ecological benefit.
* **Trade-Off & Downside Analysis:** Determining if a water-retaining cover crop will compete with the cash crop for limited moisture during drought periods.
* **Audit-Ready Scientific Justification:** Generating verifiable reports with exact citations for grant applications or regulatory compliance.

---

## 5. End-to-End User Scenario

### Step 1: Incomplete Query
A farmer enters the system:
> *"My soil is turning hard and dusty, and pollinators have disappeared. What should I plant?"*

### Step 2: Clarification & Slot Filling
Rather than dispensing generic advice, Darukaa.Earth notes missing critical parameters and responds:
> *"To provide an ecologically sound recommendation, I need 3 key metrics:
> 1. Your Soil Organic Carbon (SOC) percentage or organic matter level.
> 2. Average annual precipitation (mm).
> 3. Your current cropping system (e.g., continuous wheat, rotation, fallow)."*

### Step 3: Structured Metric Synthesis
The user responds:
> *"SOC is 0.35%, rainfall is 450 mm/year, and we run continuous monoculture winter wheat."*

### Step 4: Multi-Metric Compound Stress Detection
The deterministic engine evaluates the combined parameters:
* `SOC < 0.5%` + `Rainfall < 500mm` + `Monoculture` $\rightarrow$ **Critical Compound Soil-Moisture-Biodiversity Degradation State**.
* Water retention capacity is compromised (< 20mm/m).
* Microbial biomass and floral nectar continuity are near zero.

### Step 5: Ranked & Validated Interventions
The engine returns:
1. **Primary Intervention:** Semi-Arid Legume Intercropping (*Cicer arietinum* / Chickpea or *Vicia sativa* / Vetch).
   * *Target Metrics:* Increases SOC (+0.12%/yr projected), restores nitrogen fixing without depleting deep moisture reserves.
   * *Trade-off:* 8–12% potential moisture competition during dry establishment windows.
   * *Evidence:* FAO Soil Bulletin 80 (2020), Section 4.2; IPCC Land Report (2019) Ch. 4.
   * *Confidence:* **0.91 / 1.0** (Backed by 3 primary field trial citations).
2. **Secondary Intervention:** Windbreak Native Hedgerow Strips on field margins.
   * *Target Metrics:* Pollinator habitat connectivity (+35%), 15% reduction in evapotranspirative wind loss.

---

## 6. Hackathon Scope: MVP vs Non-Goals

### In-Scope (24-Hour MVP)
* **Interactive Conversational UI:** React + TypeScript chat interface with structured environmental profile drawer.
* **Structured Input Engine:** Accepts direct numeric input (SOC, rainfall, pH, temperature, crop type, acreage).
* **Deterministic Reasoning Engine:** Python logic executing cross-variable thresholds and compound risk detection.
* **Hybrid Scientific RAG:** PostgreSQL with `pgvector` index populated with 50+ curated high-authority chunks (FAO, IPCC, IPBES).
* **Multi-Objective Recommendation Ranking:** Algorithmic scoring across fit, scientific evidence, biodiversity gain, and water feasibility.
* **Evidence Validation Pipeline:** Automated check ensuring output claims correspond directly to retrieved chunk metadata.
* **Confidence & Traceability:** Explicit visual display of confidence scores and source citations.

### Non-Goals (Out of Scope for 24h Hackathon)
* Automated live satellite raster ingestion (Copernicus Sentinel-2 API deferred to v2).
* Complex multi-tenant RBAC and billing infrastructures.
* Heavy asynchronous queue architectures (Celery/Kafka).
* Custom deep learning model fine-tuning (standard OpenAI embedding and reasoning models utilized).
* Native mobile applications (responsive web app prioritised).

---

## 7. Cross-Document Navigation

* Next: Explore the high-level and component architecture in [02_SYSTEM_ARCHITECTURE.md](./02_SYSTEM_ARCHITECTURE.md).
* Deep-dive into the core deterministic logic in [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md).
* Inspect the database schema and pgvector implementation in [05_DATABASE_DESIGN.md](./05_DATABASE_DESIGN.md).
* Review the 24-hour delivery schedule in [18_MVP_IMPLEMENTATION_PLAN.md](./18_MVP_IMPLEMENTATION_PLAN.md).

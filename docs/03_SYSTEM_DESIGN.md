# 03 — System Design

> **Navigation:** [Index](./00_DOCUMENTATION_INDEX.md) | **Previous:** [System Architecture](./02_SYSTEM_ARCHITECTURE.md) | **Next:** [Data Architecture](./04_DATA_ARCHITECTURE.md)

---

## 1. System Requirements

### 1.1 Functional Requirements (FR)
* **FR-01 (Multi-Metric Telemetry Ingestion):** Ingest numerical and categorical environmental inputs: Soil Organic Carbon (SOC), soil pH, soil moisture, precipitation, temperature, land use type, regional biome, and crop history.
* **FR-02 (Proactive Incomplete Query Detection):** Detect missing parameters critical to risk calculation and generate clarifying prompts before executing recommendations.
* **FR-03 (Compound Stress Assessment):** Execute deterministic threshold rules across combinations of $\ge 3$ variables (e.g., SOC + Precipitation + Monoculture).
* **FR-04 (Hybrid Scientific RAG):** Retrieve relevant scientific literature chunks using both semantic vector similarity and keyword search against FAO, IPCC, and IPBES publications.
* **FR-05 (Intervention Recommendation & Ranking):** Output ranked agricultural and ecological interventions scored by ecological fit, evidence strength, biodiversity impact, and feasibility.
* **FR-06 (Evidence & Claim Validation):** Cross-reference every draft quantitative claim and assertion against retrieved chunks, removing or adjusting unverified claims.
* **FR-07 (Conversational State Retention):** Preserve user profiles across multi-turn dialogues, updating values dynamically when users provide corrections.

### 1.2 Non-Functional Requirements (NFR)
* **NFR-01 (Latency):** Total end-to-end request latency for standard analysis must be under $3.5$ seconds (p95) on single-node hackathon hardware.
* **NFR-02 (Anti-Hallucination Guardrail):** Zero ungrounded numerical claims in output recommendations. Every quantitative metric must map to a database source chunk ID.
* **NFR-03 (Reliability):** Graceful degradation: if the LLM API experiences transient timeouts, the system returns deterministic rule-based advice with cached evidence chunks.
* **NFR-04 (Portability):** Complete environment deployable via a single `docker-compose up` command within 5 minutes.

---

## 2. End-to-End Processing Pipeline

```mermaid
flowchart TD
    Start([User Message / Profile Input]) --> Ingestion["1. FastAPI Router & Input Sanitization"]
    Ingestion --> ConvContext["2. Conversation Memory Context Assembly"]
    ConvContext --> Extraction["3. Entity Extraction & Slot Filling"]
    
    Extraction --> CheckComplete{Are core metrics\ncomplete?}
    CheckComplete -- No --> Clarification["4a. Formulate Targeted Clarifying Query"]
    Clarification --> ResponseOut([Return Clarification to User])
    
    CheckComplete -- Yes --> StateEngine["4b. Environmental State Engine\n(Normalize & Categorize)"]
    StateEngine --> MultiMetric["5. Multi-Metric Compound Stress Matrix\n(Evaluate Cross-Metric Stress)"]
    MultiMetric --> CandidateGen["6. Candidate Interventions Filter\n(Agronomic Rule Pruning)"]
    
    CandidateGen --> HybridRAG["7. Hybrid Scientific Retrieval\n(pgvector HNSW + PostgreSQL BM25)"]
    HybridRAG --> Scoring["8. Multi-Objective Recommendation Scoring"]
    Scoring --> DraftGen["9. LLM Synthesis Draft with Context & Citations"]
    
    DraftGen --> Validation["10. Evidence Validation Loop\n(Claim-to-Chunk Matching)"]
    Validation --> CheckValid{All claims\nsupported?}
    CheckValid -- No --> Rewrite["11a. Strip / Downgrade Unsupported Claims"]
    Rewrite --> FinalOutput["12. Final Response Assembly"]
    CheckValid -- Yes --> FinalOutput
    
    FinalOutput --> StoreDB[(Save Message & Profile to PostgreSQL)]
    StoreDB --> ResponseOutFinal([Return Final Decision & Profile to User])
```

---

## 3. Sequence Diagrams

### 3.1 Normal Complete Query Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant FE as React Frontend
    participant API as FastAPI Router
    participant CM as Conversation Memory
    participant RE as Reasoning Engine
    participant RAG as RAG Service
    participant DB as PostgreSQL + pgvector
    participant LLM as OpenAI (GPT-4o)
    participant VAL as Evidence Validator

    User->>FE: Submits complete query (SOC 0.35%, 450mm rain, wheat monoculture)
    FE->>API: POST /api/v1/chat {message, session_id}
    API->>CM: Load session history & accumulated profile
    CM-->>API: Context payload
    API->>RE: Run evaluate_environmental_state(profile)
    RE->>RE: Compute compound stress index (High Water Stress + High Biodiversity Risk)
    RE-->>API: Stress diagnostics + candidate interventions
    API->>RAG: Retrieve evidence for (Semi-arid + Low SOC + Legumes)
    RAG->>DB: Hybrid search (HNSW Cosine + tsvector BM25)
    DB-->>RAG: Return top 5 verified chunks (FAO, IPCC)
    RAG-->>API: Scientific context chunks
    API->>LLM: Generate structured draft (Candidates + Evidence + Context)
    LLM-->>API: Draft recommendation JSON
    API->>VAL: Validate claims(draft, chunks)
    VAL-->>API: Verification passed (Confidence 0.91)
    API->>CM: Update session profile & message history
    CM->>DB: Persist state
    API-->>FE: HTTP 200 {response, profile, recommendations, evidence}
    FE-->>User: Displays recommendations, radar metrics, and clickable citations
```

### 3.2 Incomplete Query (Clarification Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant FE as React Frontend
    participant API as FastAPI Router
    participant CM as Conversation Memory
    participant SP as Slot-Filling Parser

    User->>FE: "My soil is degrading and crops look stunted"
    FE->>API: POST /api/v1/chat {message: "My soil is degrading...", session_id}
    API->>CM: Get current profile
    CM-->>API: Profile {soc: null, rainfall: null, land_use: null}
    API->>SP: Check required metric slots
    SP-->>API: Missing: [soc, rainfall, land_use]
    API->>CM: Append user message + system clarifying question
    API-->>FE: HTTP 200 {status: "CLARIFICATION_REQUIRED", message: "To evaluate soil stress accurately, please provide your Soil Organic Carbon (SOC), annual rainfall, and current crop rotation.", missing_fields: ["soc", "rainfall", "land_use"]}
    FE-->>User: Renders chat prompt with highlighted input chips
```

### 3.3 Recommendation Scoring & Evidence Validation Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Recommendation Engine
    participant DB as PostgreSQL (pgvector)
    participant LLM as LLM Synthesizer
    participant Val as Evidence Validator

    Engine->>Engine: Filter candidates by Biome & Constraints
    loop For each candidate intervention
        Engine->>DB: Query similarity chunks for intervention + local biome
        DB-->>Engine: Chunks [ID: fao_ch4, Score: 0.89]
        Engine->>Engine: Calculate Utility Score: Fit(0.85) + Evidence(0.9) + Bio(0.8) - WaterRisk(0.2)
    end
    Engine->>LLM: Synthesize top 2 candidates with chunk citations
    LLM-->>Val: Draft text: "Legume intercropping increases SOC by 0.12%/yr and improves infiltration by 25% (FAO Bulletin 80)"
    Val->>Val: Extract assertions: [SOC_increase: 0.12%, infiltration: 25%]
    Val->>DB: Verify assertions against chunk text
    alt Assertions match chunk text
        Val-->>Engine: Validation OK, set confidence = 0.92
    else Assertion 25% infiltration not in source text
        Val->>Val: Strip quantitative claim "by 25%" -> replace with qualitative "improves infiltration"
        Val-->>Engine: Adjusted text, set confidence = 0.84
    end
```

---

## 4. Failure Handling & Resilience

| Failure Mode | Impact | Mitigation / Fallback Strategy |
| :--- | :--- | :--- |
| **OpenAI API Timeout / Downtime** | LLM draft cannot be generated | Fall back to pre-compiled deterministic templates populated with verified database chunks. The user receives recommendations with a banner: *"Generated via deterministic rule engine (Offline Mode)"*. |
| **Database Connection Loss** | Cannot read session or chunks | In-memory fallback dictionary with top 10 fundamental agricultural interventions and static FAO guidelines. |
| **Conflicting User Input** | e.g., User claims pH = 14 and SOC = 50% | Input validation rejects extreme biological outliers with a friendly error prompt: *"Values outside biological limits. Please check soil test results."* |
| **No Retrieved Chunks ($\text{similarity} < 0.6$)** | Query is outside scientific corpus | System outputs recommendations with a low confidence score ($< 0.4$) and an explicit disclaimer: *"Preliminary agronomic guidance; insufficient peer-reviewed literature for this specific microclimate."* |

---

## 5. Cross-Document Navigation

* To inspect the complete data schemas, see [04_DATA_ARCHITECTURE.md](./04_DATA_ARCHITECTURE.md).
* For the SQL table structures and vector index setup, see [05_DATABASE_DESIGN.md](./05_DATABASE_DESIGN.md).
* For the multi-metric threshold matrices, see [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md).
* For the evidence validation algorithm, see [10_EVIDENCE_VALIDATION.md](./10_EVIDENCE_VALIDATION.md).

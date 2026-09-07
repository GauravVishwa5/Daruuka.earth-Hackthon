# 00 — Master Documentation Index

Welcome to the engineering and architectural documentation for **Darukaa.Earth**, the evidence-grounded AI Biodiversity Intelligence & Environmental Decision Engine.

This documentation suite is organized into 22 modular, implementation-ready specifications designed to take a full-stack engineering team from Hour 0 to a working MVP within a 24-hour hackathon, while establishing an enterprise-grade architectural foundation for production scaling.

---

## 1. Project Overview & Core Differentiator

Darukaa.Earth is an **AI Environmental Scientist / Biodiversity Decision Intelligence Engine**. It does not function as a naive LLM wrapper or simple RAG query bot. It couples empirical environmental metrics (soil physics, microclimate, land topology, species indicators) with deterministic ecological rule engines and peer-reviewed scientific consensus.

```text
[Naive Chatbot]     User ──> LLM ──> Unverified Text
[Basic RAG]         User ──> Semantic Search ──> LLM ──> Hallucination Risk
[Darukaa.Earth]     User ──> Metric Extraction ──> Environmental State Engine ──>
                             Multi-Metric Stress Reasoning ──> Candidate Interventions ──>
                             Hybrid Scientific RAG ──> Algorithmic Ranking ──>
                             Evidence Validation Loop ──> Auditable Decision Output
```

---

## 2. Master Documentation Map

```text
darukaa-earth/docs/
│
├── 00_DOCUMENTATION_INDEX.md           # Master index, navigation, reading guides (You are here)
│
├── System Vision & Design
│   ├── 01_PROJECT_OVERVIEW.md          # Problem statement, differentiators, use cases, MVP boundaries
│   ├── 02_SYSTEM_ARCHITECTURE.md       # C4 context, container & component diagrams, data planes
│   └── 03_SYSTEM_DESIGN.md             # Request lifecycles, execution pipelines, error handling
│
├── Data & Knowledge Engineering
│   ├── 04_DATA_ARCHITECTURE.md         # 4-tier data model: structured, semantic, relational, state
│   ├── 05_DATABASE_DESIGN.md           # PostgreSQL 16 DDL, pgvector schemas, ER diagram, sample data
│   ├── 06_KNOWLEDGE_BASE.md            # Scientific taxonomy (FAO, IPCC, IPBES) & metadata standards
│   └── 07_RAG_ARCHITECTURE.md          # Hybrid search (pgvector + BM25), chunking, reciprocal ranking
│
├── Intelligence & Algorithmic Core
│   ├── 08_REASONING_ENGINE.md          # Deterministic multi-metric matrix, compound stress reasoning
│   ├── 09_RECOMMENDATION_ENGINE.md     # Multi-objective intervention scoring, trade-off analysis
│   ├── 10_EVIDENCE_VALIDATION.md       # Claim extraction, NLI grounding verification, citation tracer
│   └── 11_CONVERSATION_MEMORY.md       # Slot-filling state accumulator, conversational memory manager
│
├── API & Interface
│   ├── 12_API_DESIGN.md                # FastAPI REST endpoints, OpenAPI specs, JSON schemas
│   ├── 13_FRONTEND_ARCHITECTURE.md     # React 18 + TypeScript component tree, state management
│   └── 14_USER_FLOWS.md                # End-to-end user journeys & interaction sequence diagrams
│
├── Operations & Quality
│   ├── 15_DEPLOYMENT_ARCHITECTURE.md   # 24h Hackathon Docker deploy vs AWS ECS/RDS production target
│   ├── 16_SECURITY_RELIABILITY.md      # Input sanitization, prompt safety, audit logging, guardrails
│   └── 17_TESTING_STRATEGY.md          # Unit, integration, & 10 AI multi-metric reasoning test cases
│
└── Execution, Pitch & Roadmap
    ├── 18_MVP_IMPLEMENTATION_PLAN.md   # 24-hour sprint plan, hour-by-hour milestones, priority matrix
    ├── 19_DEMO_SCRIPT.md               # 3-5 minute live hackathon presentation & step-by-step walkthrough
    ├── 20_JUDGE_QA.md                  # 15+ hard technical & scientific questions with honest answers
    └── 21_FUTURE_ROADMAP.md            # Hackathon MVP vs Version 2 (Copernicus/GIS) vs Global Production
```

---

## 3. Fast-Track Reading Guides

Select your path based on your role or hackathon objective:

### Path A: Developer Quick Start (Hour 0 Execution)
1. Read [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) for domain grounding.
2. Review [02_SYSTEM_ARCHITECTURE.md](./02_SYSTEM_ARCHITECTURE.md) to understand component boundaries.
3. Deploy the database using [05_DATABASE_DESIGN.md](./05_DATABASE_DESIGN.md).
4. Implement the backend endpoints in [12_API_DESIGN.md](./12_API_DESIGN.md).
5. Build the core reasoning engine using [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md).
6. Follow the hour-by-hour timetable in [18_MVP_IMPLEMENTATION_PLAN.md](./18_MVP_IMPLEMENTATION_PLAN.md).

### Path B: Hackathon Judge & Evaluator Fast-Track
1. Read [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) for value proposition and differentiators.
2. Review [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md) to see how multi-metric reasoning solves the generic chatbot fallacy.
3. Check [10_EVIDENCE_VALIDATION.md](./10_EVIDENCE_VALIDATION.md) for strict scientific anti-hallucination guardrails.
4. Read [19_DEMO_SCRIPT.md](./19_DEMO_SCRIPT.md) for the end-to-end user story.
5. Review [20_JUDGE_QA.md](./20_JUDGE_QA.md) for direct answers to architectural edge cases.

### Path C: Environmental Scientist / Agronomist Path
1. Review the scientific authority hierarchy in [06_KNOWLEDGE_BASE.md](./06_KNOWLEDGE_BASE.md).
2. Inspect the multi-metric threshold matrices in [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md).
3. Evaluate the ecological intervention scoring algorithms in [09_RECOMMENDATION_ENGINE.md](./09_RECOMMENDATION_ENGINE.md).
4. Verify the claim validation pipeline in [10_EVIDENCE_VALIDATION.md](./10_EVIDENCE_VALIDATION.md).

---

## 4. MVP Priority Matrix (24-Hour Scope)

| Tier | Capabilities | Included in 24h MVP? |
| :--- | :--- | :--- |
| **Must Have** | Structured Metric Input, PostgreSQL + pgvector, FAO/IPCC scientific RAG, Multi-Metric Compound Stress Reasoning, Clarifying Questions, Evidence Validation & Traceability, FastAPI Backend, React Frontend | **YES (Hour 0–16)** |
| **Should Have** | Conversation State Persistence, Interactive Trade-off Matrix, JSON Profile Import/Export, Confidence Scoring | **YES (Hour 16–20)** |
| **Could Have** | Geo-coordinates Lat/Long lookup, PostGIS spatial indexing, External Weather API hooks | **OPTIONAL (Hour 20–22)** |
| **Won't Have** | Microservices, Kubernetes, Kafka, Custom model fine-tuning, Satellite image processing pipelines | **NO (Deferred to v2)** |

---

## 5. Technology Stack Summary

| Layer | Technology | Primary Rationale |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS | High velocity, component reusability, zero runtime overhead |
| **Backend** | FastAPI (Python 3.11), Pydantic v2 | Native async performance, automatic OpenAPI documentation, rich scientific typing |
| **Relational DB** | PostgreSQL 16 | ACID compliance, JSONB environmental profiles, solid relation tracking |
| **Vector DB** | `pgvector` extension | Single datastore simplicity: no cross-database sync or duplicate infrastructure |
| **LLM Orchestration** | OpenAI API (GPT-4o) / LangChain / Native Python | Reliable structured JSON outputs, deterministic reasoning hooks |
| **Embeddings** | `text-embedding-3-small` (1536 dims) | Cost-effective, high semantic retrieval performance on ecological domain |
| **Deployment** | Docker Compose / AWS Lightsail / ECS | 10-minute setup, predictable containerized environment |

---

## 6. Document Cross-Reference Directory

* [01 — Project Overview](./01_PROJECT_OVERVIEW.md)
* [02 — System Architecture](./02_SYSTEM_ARCHITECTURE.md)
* [03 — System Design](./03_SYSTEM_DESIGN.md)
* [04 — Data Architecture](./04_DATA_ARCHITECTURE.md)
* [05 — Database Design](./05_DATABASE_DESIGN.md)
* [06 — Knowledge Base](./06_KNOWLEDGE_BASE.md)
* [07 — RAG Architecture](./07_RAG_ARCHITECTURE.md)
* [08 — Reasoning Engine](./08_REASONING_ENGINE.md)
* [09 — Recommendation Engine](./09_RECOMMENDATION_ENGINE.md)
* [10 — Evidence Validation](./10_EVIDENCE_VALIDATION.md)
* [11 — Conversation Memory](./11_CONVERSATION_MEMORY.md)
* [12 — API Design](./12_API_DESIGN.md)
* [13 — Frontend Architecture](./13_FRONTEND_ARCHITECTURE.md)
* [14 — User Flows](./14_USER_FLOWS.md)
* [15 — Deployment Architecture](./15_DEPLOYMENT_ARCHITECTURE.md)
* [16 — Security and Reliability](./16_SECURITY_RELIABILITY.md)
* [17 — Testing Strategy](./17_TESTING_STRATEGY.md)
* [18 — MVP Implementation Plan](./18_MVP_IMPLEMENTATION_PLAN.md)
* [19 — Demo Script](./19_DEMO_SCRIPT.md)
* [20 — Judge Q&A](./20_JUDGE_QA.md)
* [21 — Future Roadmap](./21_FUTURE_ROADMAP.md)
* [22 — Final Implementation Audit](./22_FINAL_IMPLEMENTATION_AUDIT.md)
* [23 — Hackathon Challenge Compliance](./23_HACKATHON_CHALLENGE_COMPLIANCE.md)
* [24 — Hackathon Gap Fix Plan](./24_HACKATHON_GAP_FIX_PLAN.md)

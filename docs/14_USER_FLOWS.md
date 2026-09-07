# 14 — User Flows & Interaction Journeys

> **Navigation:** [Index](./00_DOCUMENTATION_INDEX.md) | **Previous:** [Frontend Architecture](./13_FRONTEND_ARCHITECTURE.md) | **Next:** [Deployment Architecture](./15_DEPLOYMENT_ARCHITECTURE.md)

---

## 1. Flow Overview

Darukaa.Earth supports both conversational inquiries and direct dashboard data manipulation. Below are the 8 primary user interaction flows.

---

## 2. The 8 Core User Interaction Journeys

### Flow 1: New User First Visit & Onboarding

```mermaid
flowchart TD
    User([New User Lands on App]) --> ViewWelcome["View Empty State with Example Prompts\n('Semi-Arid Wheat', 'Degraded Pasture')"]
    ViewWelcome --> Choice{User Entry Path}
    Choice -- Interactive Chat --> EnterText["Type freeform message into ChatWindow"]
    Choice -- Example Seed --> ClickSeed["Click 'Semi-Arid Wheat Degradation' Preset"]
    EnterText --> TriggerAPI["Submit to POST /api/v1/chat"]
    ClickSeed --> AutoPopulate["Populates Profile & Triggers Multi-Metric Evaluation"]
```

---

### Flow 2: Incomplete Environmental Query (Clarification Loop)

```mermaid
flowchart TD
    Query["User: 'My soil is exhausted and dry'"] --> API["POST /api/v1/chat"]
    API --> SlotCheck{Are SOC, Rainfall & Crop present?}
    SlotCheck -- No --> IssueClarify["Assistant: 'Please provide SOC %, annual rainfall, and crop system.'"]
    IssueClarify --> HighlightUI["Frontend highlights empty profile cards in yellow"]
    HighlightUI --> UserReplies["User: 'SOC is 0.35%, rain 450mm, wheat monoculture'"]
    UserReplies --> SlotCheck
    SlotCheck -- Yes --> TriggerFull["Trigger Multi-Metric Assessment & Recommendations"]
```

---

### Flow 3: Complete Assessment Generation

```mermaid
flowchart TD
    CompleteState["Complete Profile Registered"] --> ComputeStress["Compute Soil, Water & Bio Stress Vectors"]
    ComputeStress --> CheckCompound{Compound Risk > 0.80?}
    CheckCompound -- Yes --> FlagCritical["Flag CRITICAL COMPOUND DESERTIFICATION STATE"]
    CheckCompound -- No --> FlagModerate["Flag MODERATE ECOLOGICAL STRESS"]
    FlagCritical --> RetrieveLit["Hybrid RAG Retrieval against FAO/IPCC Chunks"]
    FlagModerate --> RetrieveLit
    RetrieveLit --> RankRecs["Rank Candidate Interventions"]
    RankRecs --> FactCheck["Claim Validation Loop"]
    FactCheck --> DisplayDashboard["Render Stress Radar, Ranked Action Cards, and Citations"]
```

---

### Flow 4: Conversational Follow-Up & Deep Dive

```mermaid
flowchart TD
    DashboardActive["Active Dashboard with Recommendations"] --> UserQuestion["User: 'Will chickpea intercropping take away too much moisture from my wheat?'"]
    UserQuestion --> ContextPack["Inject Active Profile + Rec #1 Metadata into Context"]
    ContextPack --> TargetRAG["Targeted Vector Search: 'chickpea cereal moisture competition semi-arid'"]
    TargetRAG --> Synthesize["LLM Synthesizes trade-off citing FAO Bulletin 80 Section 4"]
    Synthesize --> RenderReply["Renders direct answer with moisture mitigation sowing instructions"]
```

---

### Flow 5: Scientific Evidence Inspection

```mermaid
flowchart TD
    UserViewsRec["User inspects Recommendation #1 Card"] --> ClickCite["User clicks '[Source: FAO (2021)]' badge"]
    ClickCite --> FetchEvidence["GET /api/v1/evidence/chunk_fao_recarb_v2_p142"]
    FetchEvidence --> OpenModal["Slide-over EvidencePanel Opens"]
    OpenModal --> Display["Shows: Full Title, Authors, DOI Link, Authority Tier 1, Exact Excerpt"]
    Display --> UserVerifies["User audits scientific foundation"]
```

---

### Flow 6: Recommendation Comparison & Trade-Off Matrix

```mermaid
flowchart TD
    User["User clicks 'Compare Interventions'"] --> MatrixView["Renders Comparative Trade-Off Grid"]
    MatrixView --> CompareColumns["Column 1: Legume Intercropping\nColumn 2: Native Hedgerow Buffers"]
    CompareColumns --> Row1["Row 1: SOC Accretion (+0.12%/yr vs +0.02%/yr)"]
    CompareColumns --> Row2["Row 2: Biodiversity Impact (Moderate vs +35% Wild Pollinators)"]
    CompareColumns --> Row3["Row 3: Water Demand Risk (Moderate vs Low)"]
    CompareColumns --> UserSelects["User selects preferred intervention for farm plan"]
```

---

### Flow 7: Direct Structured JSON / Lab Data Import

```mermaid
flowchart TD
    User["User has soil lab test results"] --> ClickImport["Clicks 'Import Profile JSON'"]
    ClickImport --> PasteJSON["Pastes lab metrics payload\n{soc: 0.35, ph: 7.8, rain: 450}"]
    PasteJSON --> PostProfile["POST /api/v1/environmental-profile"]
    PostProfile --> InstantEval["Bypasses conversational parser; executes instant assessment"]
    InstantEval --> UpdateUI["UI instantly updates with computed stress vectors"]
```

---

### Flow 8: Optional Geo-Coordinates Input

```mermaid
flowchart TD
    User["User enters Lat: 32.7157, Long: -102.1678 (Texas High Plains)"] --> API["POST /api/v1/environmental-profile"]
    API --> CoordinateLookup["Resolve regional biome: semi_arid_steppe"]
    CoordinateLookup --> DefaultRainfall["Pre-fill historical climate baseline: 460 mm/yr"]
    DefaultRainfall --> UserConfirms["User confirms or overrides pre-filled rainfall value"]
    UserConfirms --> Proceed["Proceeds to soil metric entry"]
```

---

## 3. Cross-Document Navigation

* To see the deployment architecture running these flows, see [15_DEPLOYMENT_ARCHITECTURE.md](./15_DEPLOYMENT_ARCHITECTURE.md).
* For testing user flows with concrete assertions, see [17_TESTING_STRATEGY.md](./17_TESTING_STRATEGY.md).
* For the exact live demo execution of these flows, see [19_DEMO_SCRIPT.md](./19_DEMO_SCRIPT.md).

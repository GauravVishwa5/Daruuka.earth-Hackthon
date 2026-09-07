# 04 — Data Architecture

> **Navigation:** [Index](./00_DOCUMENTATION_INDEX.md) | **Previous:** [System Design](./03_SYSTEM_DESIGN.md) | **Next:** [Database Design](./05_DATABASE_DESIGN.md)

---

## 1. Multi-Tiered Data Architecture

Ecological intelligence cannot be realized through unstructured text alone. Biological and agronomic decisions require a synthesis of physical telemetry, relational causality, semantic research papers, and conversational context.

Darukaa.Earth organizes all information into **four distinct data tiers**:

```mermaid
flowchart TD
    subgraph Tier1["1. Structured Environmental Telemetry"]
        RawMetrics["Soil, Climate & Land Measurements\n(Numeric & Categorical)"]
        NormEngine["Normalization & Validation Engine"]
        RelationalStore[("PostgreSQL Relational Tables")]
        RawMetrics --> NormEngine --> RelationalStore
    end

    subgraph Tier2["2. Semantic Knowledge Base"]
        LitSource["Scientific PDFs & Reports\n(FAO, IPCC, IPBES)"]
        Chunker["Semantic Chunker (500 tokens)"]
        Embedder["text-embedding-3-small (1536d)"]
        VecStore[("pgvector HNSW Store")]
        LitSource --> Chunker --> Embedder --> VecStore
    end

    subgraph Tier3["3. Relational & Ontological Knowledge"]
        MetricRel["Metric Causality Rules\n(e.g., SOC < 0.5% => Infiltration -40%)"]
        InterventionMap["Intervention Preconditions & Impacts"]
        RuleGraph[("PostgreSQL Relational Ontologies")]
        MetricRel --> RuleGraph
        InterventionMap --> RuleGraph
    end

    subgraph Tier4["4. Conversational State & Accumulated Profiles"]
        SessionHistory["User Chat Dialogue Turns"]
        StateAccumulator["Slot-Filling Profile Accumulator"]
        SessionStore[("JSONB Session Profile Store")]
        SessionHistory --> StateAccumulator --> SessionStore
    end

    RelationalStore --> JointReasoning["Darukaa Unified Reasoning Engine"]
    VecStore --> JointReasoning
    RuleGraph --> JointReasoning
    SessionStore --> JointReasoning
```

---

## 2. Comparison of Data Tiers

| Tier | Nature | Storage Engine | Query Method | Primary Role in Decision Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **1. Structured Telemetry** | Quantitative metrics (SOC %, pH, rainfall mm, temperature °C) | PostgreSQL columns / JSONB | SQL comparison operators (`<`, `>`, `BETWEEN`) | Grounding the current physical state of the land |
| **2. Semantic Knowledge** | Unstructured scientific prose, field trial results, regional guidelines | `pgvector` table (`vector(1536)`) | Cosine distance (`<=>`) + BM25 keyword search | Providing scientific literature citations and experimental proof |
| **3. Relational Ontology** | Cause-and-effect rules, inter-metric correlations, constraint matrices | PostgreSQL relational tables | SQL JOINs & foreign keys | Deterministically identifying compound stress and filtering candidates |
| **4. Conversational State** | Multi-turn chat messages, accumulated profile, user corrections | PostgreSQL relational + JSONB | Primary key session lookup | Maintaining context across turns without repeating questions |

---

## 3. Deep Dive into Data Tiers

### 3.1 Tier 1: Structured Environmental Telemetry

Structured data represents the empirical physical conditions of the landscape under evaluation.

```mermaid
graph LR
    subgraph ObservationInput["Raw Observations"]
        SOC["Soil Organic Carbon: 0.35%"]
        PH["pH: 7.8 (Alkaline)"]
        RAIN["Rainfall: 450 mm/yr"]
        TEMP["Max Temp: 34°C"]
        CROP["Land Use: Wheat Monoculture"]
    end

    subgraph Normalization["Range Normalization"]
        NormSOC["SOC Normalized: 0.07 / 1.0 (Critical)"]
        NormRain["Aridity Index: Semi-Arid (0.32)"]
    end

    subgraph DB["PostgreSQL observation_metrics"]
        Record["Record: obs_98234\nsoil_stress: CRITICAL\nwater_stress: HIGH\nbio_stress: CRITICAL"]
    end

    ObservationInput --> Normalization --> DB
```

Key fields stored:
* **Soil Physics:** Soil Organic Carbon (`soc_percent`), pH (`ph_level`), Soil Moisture (`moisture_percent`), Bulk Density (`bulk_density_g_cm3`).
* **Climate Indicators:** Annual Rainfall (`annual_rainfall_mm`), Mean Temp (`mean_temp_celsius`), Maximum Summer Temp (`max_temp_celsius`), Drought Months (`dry_months_count`).
* **Land & Ecology:** Current Land Use (`cropland_monoculture`, `pasture`, `agroforestry`), Canopy Cover (`canopy_cover_percent`), Field Margin Vegetation (`margin_veg_present`).

---

### 3.2 Tier 2: Semantic Scientific Knowledge

The semantic tier indexes peer-reviewed consensus and institutional field guides.

```mermaid
flowchart TD
    Doc["FAO World Soil Resources Report 106"] --> Chunking["Split by Semantic Section (~500 tokens)"]
    Chunking --> Metatag["Tag Metadata:\n• biome: semi_arid\n• topic: legume_intercropping\n• source: FAO\n• year: 2021\n• evidence_grade: A"]
    Metatag --> Embedding["Generate 1536-dim Vector\n(text-embedding-3-small)"]
    Embedding --> DBInsert[("INSERT INTO evidence_chunks\n(content, embedding, metadata)")]
```

Metadata schema attached to every semantic chunk:
```json
{
  "source_id": "fao_soil_bulletin_80",
  "source_title": "Soil Management for Sustainable Agriculture",
  "organization": "FAO",
  "year": 2020,
  "doi": "10.4060/ca9280en",
  "authority_tier": 1,
  "biome": "semi-arid",
  "target_metrics": ["soc", "soil_moisture", "nitrogen"],
  "recommended_interventions": ["legume_intercropping", "conservation_tillage"]
}
```

---

### 3.3 Tier 3: Relationship & Causality Knowledge

Rather than relying on an LLM to guess the laws of soil physics, Darukaa.Earth encodes validated agronomic causality directly into a relational relationship matrix.

```mermaid
graph TD
    SOC_LOW["Low Soil Organic Carbon (< 0.5%)"]
    INFIL_LOW["Reduced Water Infiltration (-40%)"]
    MICRO_LOW["Microbial Biomass Depletion"]
    DROUGHT_HIGH["High Vulnerability to Drought"]
    BIO_COLLAPSE["Pollinator / Soil Biota Collapse"]

    SOC_LOW -->|"causes"| INFIL_LOW
    SOC_LOW -->|"causes"| MICRO_LOW
    INFIL_LOW -->|"exacerbates"| DROUGHT_HIGH
    MICRO_LOW -->|"triggers"| BIO_COLLAPSE
    DROUGHT_HIGH -->|"accelerates"| BIO_COLLAPSE
```

Database representation in table `metric_relationships`:
* `source_metric`: `soc_percent`
* `operator`: `<`
* `threshold_value`: `0.5`
* `affected_metric`: `water_infiltration_capacity`
* `effect_direction`: `NEGATIVE`
* `impact_factor`: `0.40`
* `scientific_justification`: `"Loss of organic matter destroys aggregate stability, reducing infiltration pores (IPCC SRCCL, 2019)."`

---

### 3.4 Tier 4: Conversational State & Accumulated Profiles

Maintains conversational continuity and dynamic slot-filling across multiple conversational turns.

```mermaid
sequenceDiagram
    participant User
    participant StateEngine as Profile State Engine
    participant SessionDB as PostgreSQL (JSONB)

    User->>StateEngine: Turn 1: "My crop is suffering from dry spells."
    StateEngine->>SessionDB: Update profile: {symptoms: ["drought_stress"]}
    
    User->>StateEngine: Turn 2: "Rainfall is 420mm and soil organic carbon is 0.4%."
    StateEngine->>SessionDB: Update profile: {rainfall: 420, soc: 0.4, symptoms: ["drought_stress"]}
    
    User->>StateEngine: Turn 3: "Actually, carbon was measured at 0.45%."
    StateEngine->>SessionDB: Overwrite profile: {rainfall: 420, soc: 0.45} (Correction preserved)
```

---

## 4. Cross-Document Navigation

* To see the concrete DDL implementation and indexing strategies, see [05_DATABASE_DESIGN.md](./05_DATABASE_DESIGN.md).
* For the institutional sources populating Tier 2, see [06_KNOWLEDGE_BASE.md](./06_KNOWLEDGE_BASE.md).
* For the hybrid retrieval pipeline operating on Tier 2, see [07_RAG_ARCHITECTURE.md](./07_RAG_ARCHITECTURE.md).
* To see how Tier 1 and Tier 3 drive deterministic calculations, see [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md).

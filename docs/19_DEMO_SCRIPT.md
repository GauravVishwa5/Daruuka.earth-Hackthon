# 19 — Live Demo Script & Presentation Playbook

> **Navigation:** [Index](./00_DOCUMENTATION_INDEX.md) | **Previous:** [MVP Implementation Plan](./18_MVP_IMPLEMENTATION_PLAN.md) | **Next:** [Judge Q&A](./20_JUDGE_QA.md)

---

## 1. Presentation Metadata
* **Duration:** 3 Minutes 30 Seconds (+ 1.5 minutes Q&A buffer).
* **Target Audience:** Hackathon Technical Judges, Agronomists, Environmental Investors.
* **Core Takeaway:** *"Darukaa.Earth is an automated Environmental Scientist, not a generic chatbot. It solves ecological collapse through deterministic multi-metric reasoning and audited scientific RAG."*

---

## 2. Timed Presentation Script & Live Clicks

```mermaid
timeline
    title 3.5-Minute Demo Timeline
    00:00 - 00:30 : Problem Pitch (The Chatbot Fallacy)
    00:30 - 01:15 : Incomplete Input & Proactive Clarification
    01:15 - 02:00 : Multi-Metric Compound Stress Calculation
    02:00 - 02:45 : Ranked Interventions & Anti-Hallucination Audit
    02:45 - 03:30 : System Architecture & Wrap-up
```

---

### Act 1: The Problem & The Chatbot Fallacy (00:00 – 00:30)
* **Presenter Spoken Narrative:**
  > *"Judges, 40% of our planet's agricultural soils are severely degraded. If a farmer asks a generic AI chatbot like ChatGPT or a standard RAG bot: 'My land is turning to dust, what should I plant?', it will happily hallucinate: 'Plant high-biomass clover and alfalfa!'
  > In a semi-arid zone, that advice is catastrophic—it drains the remaining subsoil water and kills the next harvest.
  > Ecology is not simple text. It requires physical telemetry, deterministic thresholds, and verifiable scientific evidence. That is why we built **Darukaa.Earth**."*

---

### Act 2: Incomplete Input & Proactive Clarification (00:30 – 01:15)
* **Screen Action:** Presenter opens `http://localhost:3000`. The clean interface shows the chat stream and an empty Environmental Profile drawer.
* **Input Submitted:**
  ```text
  "My wheat yields are declining, soil is hard and dusty, and pollinators have vanished. What should I do?"
  ```
* **Presenter Spoken Narrative:**
  > *"Notice what Darukaa does. It does NOT invent an answer blindly. Because biological decisions require real context, its slot-filling engine notices missing parameters and asks targeted clarifying questions."*
* **System Output Displayed:**
  > *"To evaluate compound soil and biodiversity risk, I need 3 specific metrics:
  > 1. Soil Organic Carbon (SOC) percentage.
  > 2. Average annual rainfall (mm).
  > 3. Your current cropping system."*

---

### Act 3: Multi-Metric Reasoning in Action (01:15 – 02:00)
* **Input Submitted:**
  ```text
  "SOC is 0.35%, annual rainfall is 450 mm, max summer temperature is 34°C, and we grow continuous monoculture winter wheat."
  ```
* **Screen Action:** The Right Pane immediately animates:
  * **SOC Card:** 0.35% (Flashing Red / CRITICAL).
  * **Rainfall Card:** 450 mm (Semi-Arid Aridity Index 0.38).
  * **Stress Radar Chart:** Soil Stress 0.88, Water Stress 0.82, Biodiversity Stress 0.94.
  * **Status Badge:** **CRITICAL COMPOUND COLLAPSE RISK (Score: 1.00 / 1.0)**.
* **Presenter Spoken Narrative:**
  > *"Watch the telemetry drawer update in real-time. Darukaa didn't ask an LLM to guess the laws of soil physics. Our deterministic Python reasoning engine computed that SOC under 0.5% combined with 450mm rainfall creates compound hydrological collapse: the soil has lost its micro-sponge porosity, causing 45% runoff and starving the wheat."*

---

### Act 4: Non-Obvious Interventions & Scientific Audit (02:00 – 02:45)
* **Screen Action:** The Recommendation Panel renders two ranked cards:
  1. **Rank 1:** Legume Intercropping with Chickpea (*Cicer arietinum*) — Confidence: **92% (High)**.
  2. **Rank 2:** Native Vegetative Hedgerow Buffer Strips — Confidence: **88% (High)**.
* **Presenter Spoken Narrative:**
  > *"Notice what the recommendation engine did:
  > 1. It explicitly **banned** water-intensive cover crops because rainfall is under 500mm.
  > 2. It recommended drought-adapted chickpea intercropping, projecting +0.12% SOC per year and 35kg/ha nitrogen fixation.
  > 3. It highlights the exact trade-off: an 8% subsoil moisture competition risk during early flowering, and gives the specific row-spacing mitigation."*
* **Screen Action:** Presenter clicks the **[FAO Soil Bulletin 80]** citation badge on Card #1. A slide-over modal appears showing:
  * Title: *Soil Management for Sustainable Agriculture (FAO, 2020)*
  * DOI: `10.4060/ca9280en`
  * Exact verified excerpt.
* **Presenter Spoken Narrative:**
  > *"Every single number on this screen is traceable to an indexed peer-reviewed chunk in our PostgreSQL pgvector database. Our post-generation Claim Validator ensures zero hallucinated metrics."*

---

### Act 5: Follow-Up & Architecture Wrap-Up (02:45 – 03:30)
* **Input Submitted:**
  ```text
  "Will chickpea intercropping take away too much moisture from my wheat?"
  ```
* **System Output:** System cites FAO Bulletin 80 Section 4.2 explaining alternate 2-row strip sowing at 40cm spacing.
* **Presenter Spoken Narrative:**
  > *"Darukaa maintained the complete accumulated profile and conversation memory seamlessly.
  > Built in 24 hours on a single-node PostgreSQL 16 with pgvector, FastAPI, and React, Darukaa.Earth proves that AI environmental tools can be deterministic, scientific, and audit-ready. Thank you, we are ready for your questions!"*

---

## 3. Demo Backup & Recovery Procedures

| Scenario | Immediate Recovery Action |
| :--- | :--- |
| **Wi-Fi Disconnects During Demo** | Switch browser to pre-cached `http://localhost:3000` running on local Docker Compose. Offline database has 35 seeded chunks ready. |
| **OpenAI API Timeout** | System's automated circuit breaker falls back to deterministic rule-based output with pre-rendered FAO excerpts. |
| **Laptop Hardware Glitch** | Play pre-recorded 1080p MP4 backup video located in `docs/demo_backup.mp4`. |

---

## 4. Cross-Document Navigation

* To prepare for judge technical questions following this demo, see [20_JUDGE_QA.md](./20_JUDGE_QA.md).
* For the technical formulation behind the demo calculations, see [08_REASONING_ENGINE.md](./08_REASONING_ENGINE.md).
* For the complete test cases proving this demo flow, see [17_TESTING_STRATEGY.md](./17_TESTING_STRATEGY.md).

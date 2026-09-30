# System Architecture & Multi-Agent Design

The **Autonomous Multi-Agent E-Commerce Intelligence Platform** is engineered as a distributed, typed decision system that converts ambiguous natural language shopping objectives into structured constraints, gathers multi-source evidence, performs aspect-based review mining, and executes a transparent, deterministic ranking model.

---

## 1. High-Level System Architecture

```
                               ┌─────────────────────────────┐
                               │   React + Vite Frontend     │
                               │  (Research Console Web UI)  │
                               └──────────────┬──────────────┘
                                              │ HTTP / REST / SSE
                                              ▼
                               ┌─────────────────────────────┐
                               │       FastAPI Backend       │
                               │ Telemetry • Auth • Routers  │
                               └──────────────┬──────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
         ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
         │ PostgreSQL+pgvector │   │  Redis Job Queue &  │   │ Extensible LLM Layer│
         │   (or SQLite Core)  │   │  Correlation Store  │   │ (Mock/Gemini/OpenAI)│
         └─────────────────────┘   └──────────┬──────────┘   └─────────────────────┘
                                              │
                                              ▼
                    ┌──────────────────────────────────────────────────┐
                    │       Multi-Agent Orchestrator Pipeline          │
                    │                                                  │
                    │  1. Query Understanding Agent                    │
                    │     └─► Intent, Category, Hard/Soft Constraints  │
                    │  2. Product Discovery Agent                      │
                    │     └─► Candidate SKU Retrieval & Deduplication  │
                    │  3. Specification Validation Agent               │
                    │     └─► Spec Normalization & Compliance Filter   │
                    │  4. Review Intelligence Agent                    │
                    │     └─► Aspect Sentiment Mining (6 Facets)       │
                    │  5. Price & Value Agent                          │
                    │     └─► Budget Delta & Value Index               │
                    │  6. Trust & Evidence Verification Agent          │
                    │     └─► Multi-source Audit & Confidence Scoring  │
                    │  7. Recommendation & Explainability Agent        │
                    │     └─► Narrative Synthesis & Reason Codes       │
                    └─────────────────────────┬────────────────────────┘
                                              │
                                              ▼
                    ┌──────────────────────────────────────────────────┐
                    │        Deterministic Ranking Engine              │
                    │    Score = 0.30×Fit + 0.20×Rev + 0.15×Val +      │
                    │            0.15×Spec + 0.10×Rel + 0.10×Pref      │
                    └──────────────────────────────────────────────────┘
```

---

## 2. Specialized Agents & Typed Contracts

Each agent has a strictly bounded responsibility with typed inputs and outputs:

### 2.1 Query Understanding Agent (`QueryUnderstandingAgent`)
- **Input:** Natural language query string.
- **Output:** `ParsedConstraints` containing:
  - `category`: Detected category (`laptop`, `smartphone`, `monitor`, `audio`).
  - `budget_max`: Extracted maximum price ceiling in INR/USD.
  - `hard_constraints`: Must-have filter requirements (`ram_gb >= 16`, `price <= 90000`).
  - `soft_preferences`: Optimization directions (`battery_life_hours -> MAX`, `weight_kg -> MIN`, `linux_compatibility -> GOOD`).
  - `exclusions`: Brand or attribute exclusions (e.g. "No Dell", "Exclude Apple").
  - `ambiguity_score`: Metric indicating missing constraints (0.0 to 1.0).

### 2.2 Product Discovery Agent (`ProductDiscoveryAgent`)
- **Input:** `ParsedConstraints`
- **Output:** List of candidate product SKUs retrieved from canonical database / external providers.
- **Responsibility:** Pre-filters out excluded brands, attaches multi-source attribute metadata and verified customer reviews.

### 2.3 Specification Agent (`SpecificationAgent`)
- **Input:** Candidate products and hard constraints.
- **Output:** `SpecEvaluation` mapping:
  - Evaluates each hard constraint (`PASS` / `FAIL` / `UNKNOWN`).
  - Assigns `fit_status`: `COMPLIANT`, `PARTIALLY_COMPLIANT`, or `NON_COMPLIANT`.
  - Computes `spec_strength` (0.0 to 1.0) evaluating raw hardware tiers.

### 2.4 Review Intelligence Agent (`ReviewIntelligenceAgent`)
- **Input:** Raw reviews and ratings per candidate.
- **Output:** `ReviewIntelligenceOutput` per candidate:
  - Aspect-level sentiment extraction across 6 key facets: `Performance`, `Battery`, `Build Quality`, `Display`, `Thermals`, `Value`.
  - Clustering of recurring strengths and recurring complaints.
  - Identification of review volume flags or suspicious distributions.

### 2.5 Price / Value Agent (`PriceValueAgent`)
- **Input:** Product prices, target budget ceiling, and hardware spec tiers.
- **Output:** `PriceValueOutput` per candidate:
  - Budget fit ratio and overrun penalties.
  - Category price percentile rank.
  - Feature-to-price value index ($0.7 \times \text{Specs} + 0.3 \times (1 - \text{Percentile})$).

### 2.6 Trust & Evidence Verification Agent (`TrustEvidenceAgent`)
- **Input:** Multi-source records, specifications, and review quotes.
- **Output:** Verifiable `Evidence` records and confidence scoring:
  - Confidence Status: `VERIFIED`, `INFERRED`, `UNCERTAIN`, `UNAVAILABLE`.
  - Reliability Trust Score (0.0 to 1.0) based on source cross-verification.

### 2.7 Recommendation Agent (`RecommendationAgent`)
- **Input:** Deterministically ranked candidates and factor breakdowns.
- **Output:** Comprehensive decision narrative:
  - "Why It Won" thesis for top-ranked winner.
  - Concrete trade-off disclosures (e.g. fan noise on high load, price premium).
  - Categorical reason codes (`FULL_CONSTRAINT_COMPLIANCE`, `OPTIMAL_VALUE_TIER`, `HIGH_SENTIMENT_CONSENSUS`).

---

## 3. Deterministic Ranking & "What-If" Analysis

In adherence to system principles, ranking is **never delegated to stochastic LLM arithmetic**. The multi-criteria score matrix calculates:

$$\text{Final Score} = w_1 \times \text{Fit} + w_2 \times \text{Review} + w_3 \times \text{Value} + w_4 \times \text{Spec} + w_5 \times \text{Reliability} + w_6 \times \text{Preference}$$

- Hard constraints act as strict prerequisites: non-compliant products receive non-linear penalties and are sorted below compliant items.
- The interactive **"What-If" Re-ranking Engine** recalculates all candidate scores dynamically on weight and constraint changes without re-querying models or databases.

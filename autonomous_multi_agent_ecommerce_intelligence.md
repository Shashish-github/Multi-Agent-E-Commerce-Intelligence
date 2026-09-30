# Autonomous Multi-Agent E-Commerce Intelligence Platform

## 1. Project Identity

**Professional title:** Autonomous Multi-Agent E-Commerce Intelligence
Platform\
**Tagline:** A production-oriented multi-agent decision system that
searches products, evaluates evidence, analyzes reviews, compares value,
and produces explainable purchase recommendations.

**Source concept:** The uploaded project list includes "AI Multi Agent
Shopping System." fileciteturn0file0L359-L365

### Resume positioning

This is not a simple shopping website or chatbot. The implementation
must demonstrate: - multi-agent orchestration - tool-using AI agents -
retrieval-augmented generation - structured product/review data -
evidence-aware ranking - asynchronous jobs - explainable
recommendations - secure APIs - production-style frontend/backend
separation - testing, observability, and deployment

------------------------------------------------------------------------

# 2. Problem Statement

Online shopping requires users to manually perform several tasks:
discover relevant products, compare specifications and prices, inspect
reviews, identify review-quality problems, and decide which product
provides the best fit for their constraints.

A conventional keyword search or single recommendation model cannot
reliably perform this complete reasoning workflow.

The system will implement an autonomous set of specialized agents that
collaborate through a controlled orchestration layer. Each agent will
have a narrow responsibility, typed inputs/outputs, explicit tools,
confidence signals, and failure handling.

------------------------------------------------------------------------

# 3. Real-World Motivation

The goal is to reduce decision friction while avoiding opaque "AI says
buy this" recommendations.

The system should answer questions such as: - Which laptop is best for
programming under a specified budget? - Which products satisfy mandatory
specifications? - Which product has the strongest review evidence? - Is
a high rating supported by enough credible reviews? - What trade-offs
exist between price, performance, reliability, and user requirements? -
Why was Product A ranked above Product B?

The final recommendation must be traceable to product attributes and
review evidence.

------------------------------------------------------------------------

# 4. Proposed Solution

Build a web platform in which a user submits a natural-language shopping
objective.

Example:

> "Find a laptop under ₹90,000 for machine learning, at least 16 GB RAM,
> strong battery life, and good Linux compatibility."

The system decomposes the request into constraints and delegates work to
agents:

``` text
User Goal
   ↓
Query Understanding Agent
   ↓
Orchestrator
   ├── Product Discovery Agent
   ├── Specification Agent
   ├── Review Intelligence Agent
   ├── Price/Value Agent
   ├── Trust & Evidence Agent
   └── Recommendation Agent
            ↓
     Evidence Aggregation
            ↓
     Explainable Ranking
            ↓
       Final Results
```

------------------------------------------------------------------------

# 5. Target Users

-   Students researching expensive purchases
-   Technical professionals comparing hardware/software products
-   Consumers with strict budget/specification constraints
-   Researchers demonstrating multi-agent decision systems
-   Internal procurement teams

------------------------------------------------------------------------

# 6. Core Objectives

1.  Convert natural-language shopping goals into structured constraints.
2.  Retrieve candidate products from approved data sources.
3.  Normalize heterogeneous product information.
4.  Analyze reviews using NLP.
5.  Detect contradictory or weak evidence.
6.  Score products using explicit ranking criteria.
7.  Produce an explainable recommendation.
8.  Preserve evidence supporting every important recommendation claim.
9.  Provide robust handling for unavailable tools or incomplete data.
10. Make the system deployable as a real application.

------------------------------------------------------------------------

# 7. Differentiating Features

## 7.1 Multi-Agent Architecture

Each agent performs a clearly bounded task. Agents must not become
generic copies of one another.

## 7.2 Evidence-First Recommendations

Every important recommendation factor should point to: - source/product
record - extracted attribute - review evidence - confidence score -
timestamp where applicable

## 7.3 Constraint-Aware Ranking

Separate: - hard constraints: must be satisfied - soft preferences:
influence ranking - unknowns: reduce confidence rather than inventing
values

## 7.4 Review Intelligence

Extract: - sentiment - aspect-level sentiment - recurring complaints -
recurring strengths - review volume - suspicious/low-quality signals

## 7.5 What-If Analysis

Allow users to modify constraints and immediately see how rankings
change.

Example: - Budget ₹80K → ₹100K - Battery importance: medium → high -
Weight: optional → mandatory

## 7.6 Recommendation Audit Trail

Display which agents contributed to the decision and which evidence
influenced the score.

## 7.7 Confidence-Aware Output

The system must distinguish: - verified - inferred - uncertain -
unavailable

------------------------------------------------------------------------

# 8. Functional Requirements

## FR-01 Authentication

Users can register, log in, refresh sessions, and log out.

## FR-02 Shopping Query

Users can submit natural-language shopping objectives.

## FR-03 Constraint Extraction

The system extracts: - category - budget - minimum/maximum attributes -
preferred attributes - exclusions - geographic/availability constraints

## FR-04 Product Discovery

The discovery layer retrieves candidate products from configured
providers or a controlled local dataset.

## FR-05 Product Normalization

Different provider schemas must map into a canonical product schema.

## FR-06 Review Analysis

Reviews are processed for sentiment, aspects, recurring issues, and
quality signals.

## FR-07 Ranking

Products receive a transparent multi-factor score.

## FR-08 Explanation

The system explains why a product ranked highly.

## FR-09 Comparison

Users can compare several products side-by-side.

## FR-10 Saved Investigations

Users can save searches and recommendations.

## FR-11 What-If Re-ranking

Changing a criterion recalculates ranking without rebuilding unrelated
data.

## FR-12 Export

Allow export of a recommendation report as JSON/CSV and optionally PDF.

## FR-13 Agent Observability

Authorized users can inspect agent execution status, duration, tool
calls, and failures without exposing secrets.

------------------------------------------------------------------------

# 9. Non-Functional Requirements

-   API p95 target: \< 500 ms for ordinary CRUD/read endpoints excluding
    long-running AI jobs.
-   AI investigations must run asynchronously.
-   UI must remain responsive during agent execution.
-   All external calls require timeouts.
-   All mutable resources require authorization.
-   Secrets must never be committed.
-   The system must be horizontally scalable at the API layer.
-   Database queries must use appropriate indexes.
-   Long-running jobs must be retryable and idempotent.
-   Logs must contain correlation/request IDs.
-   Accessibility should target WCAG 2.1 AA principles.

------------------------------------------------------------------------

# 10. Technology Selection

  -----------------------------------------------------------------------
  Technology              Purpose                 Why selected
  ----------------------- ----------------------- -----------------------
  Next.js + TypeScript    Frontend                Strong typed React
                                                  architecture and
                                                  production routing

  Tailwind CSS            Styling                 Consistent design
                                                  tokens without
                                                  excessive component
                                                  boilerplate

  FastAPI + Python        Backend                 Excellent fit for AI/ML
                                                  workloads and typed
                                                  REST APIs

  PostgreSQL              Primary DB              Relational integrity
                                                  for users, products,
                                                  investigations, and
                                                  evidence

  Redis                   Cache/job coordination  Fast ephemeral state
                                                  and queue support

  Celery                  Background jobs         Reliable asynchronous
                                                  agent/inference
                                                  workflows

  pgvector                Vector retrieval        Keeps embeddings close
                                                  to transactional
                                                  product data

  Pydantic                Validation              Typed contracts between
                                                  API and AI components

  LangGraph               Agent orchestration     Explicit stateful
                                                  multi-agent workflows

  Sentence-transformers   Embeddings              Efficient semantic
                                                  retrieval

  LLM provider            Reasoning               Allows controlled model
  abstraction                                     substitution

  Docker                  Packaging               Reproducible deployment

  Pytest                  Testing                 Mature Python test
                                                  framework

  Playwright              E2E                     Browser-level workflow
                                                  testing
  -----------------------------------------------------------------------

Do not add a framework unless it solves a concrete requirement.

------------------------------------------------------------------------

# 11. System Architecture

``` text
Browser
  ↓
Next.js Web App
  ↓
FastAPI REST API
  ↓
Auth + Request Validation
  ↓
Investigation Service
  ↓
Redis Queue
  ↓
Agent Orchestrator
  ├── Query Understanding
  ├── Discovery
  ├── Specification Extraction
  ├── Review Intelligence
  ├── Price/Value
  ├── Trust/Evidence
  └── Recommendation
  ↓
Evidence + Ranking Layer
  ↓
PostgreSQL + pgvector
  ↓
Results API
  ↓
Interactive Recommendation UI
```

------------------------------------------------------------------------

# 12. Agent Architecture

## 12.1 Query Understanding Agent

Input: - natural-language shopping request

Output:

``` json
{
  "category": "laptop",
  "budget_max": 90000,
  "hard_constraints": [],
  "soft_preferences": [],
  "exclusions": []
}
```

Responsibilities: - classify product category - extract constraints -
normalize units - detect ambiguity - assign confidence

It must never silently invent missing constraints.

## 12.2 Product Discovery Agent

Responsibilities: - search configured sources - deduplicate products -
collect source references - return canonical candidate records

## 12.3 Specification Agent

Responsibilities: - normalize CPU/RAM/storage/display/battery/etc. -
detect missing attributes - resolve units - flag contradictory source
values

## 12.4 Review Intelligence Agent

Pipeline:

``` text
Reviews
 ↓
Cleaning
 ↓
Language detection
 ↓
Normalization
 ↓
Sentiment
 ↓
Aspect extraction
 ↓
Topic clustering
 ↓
Quality signals
 ↓
Evidence summary
```

## 12.5 Price/Value Agent

Calculate: - budget fit - feature-to-price ratio - price percentile
among candidates - optional total-cost considerations

## 12.6 Trust & Evidence Agent

Detect: - insufficient evidence - contradictory values - suspicious
review patterns - stale data - unsupported claims

The agent should lower confidence rather than fabricate certainty.

## 12.7 Recommendation Agent

Combines structured outputs and produces: - ranked products - reason
codes - trade-offs - confidence - evidence references

------------------------------------------------------------------------

# 13. Ranking Model

Use a deterministic ranking layer rather than allowing the LLM to
directly invent the order.

Example:

``` text
Final Score =
0.30 × Requirement Fit
+ 0.20 × Review Quality
+ 0.15 × Price Value
+ 0.15 × Specification Strength
+ 0.10 × Reliability Evidence
+ 0.10 × Preference Match
```

Weights must be configurable per investigation.

Hard constraints are applied first.

A product failing a mandatory requirement should be excluded or
explicitly marked as non-compliant.

------------------------------------------------------------------------

# 14. Data Pipeline

``` text
Raw Product Data
 ↓
Schema Validation
 ↓
Deduplication
 ↓
Canonicalization
 ↓
Attribute Extraction
 ↓
Review Processing
 ↓
Embeddings
 ↓
Evidence Storage
 ↓
Ranking Features
 ↓
Recommendation
```

------------------------------------------------------------------------

# 15. Database Design

## users

-   id UUID PK
-   email unique
-   password_hash
-   role
-   created_at
-   updated_at

## products

-   id UUID PK
-   canonical_name
-   category
-   brand
-   normalized_price
-   currency
-   source_count
-   created_at
-   updated_at

Indexes: - category - brand - normalized_price - updated_at

## product_attributes

-   id UUID PK
-   product_id FK
-   attribute_name
-   normalized_value
-   raw_value
-   unit
-   confidence
-   source_id

## sources

-   id UUID PK
-   provider
-   source_url/reference
-   retrieved_at
-   freshness_status

## reviews

-   id UUID PK
-   product_id FK
-   rating
-   review_text
-   language
-   created_at
-   source_id

## review_aspects

-   id UUID PK
-   review_id FK
-   aspect
-   sentiment
-   confidence

## investigations

-   id UUID PK
-   user_id FK
-   original_query
-   parsed_constraints JSONB
-   status
-   created_at
-   completed_at

## investigation_candidates

-   investigation_id FK
-   product_id FK
-   score
-   rank
-   explanation JSONB

## evidence

-   id UUID PK
-   investigation_id FK
-   product_id FK
-   evidence_type
-   source_id
-   claim
-   supporting_text
-   confidence

## agent_runs

-   id UUID PK
-   investigation_id FK
-   agent_name
-   status
-   started_at
-   completed_at
-   error_code
-   token_usage
-   metadata JSONB

------------------------------------------------------------------------

# 16. API Design

## POST /api/v1/auth/register

Purpose: create user.

Authentication: none.

## POST /api/v1/auth/login

Purpose: authenticate user.

Authentication: none.

## POST /api/v1/investigations

Purpose: create shopping investigation.

Authentication: required.

Request:

``` json
{
  "query": "Find a laptop under 90000 for ML with 16GB RAM"
}
```

Response:

``` json
{
  "id": "uuid",
  "status": "queued"
}
```

## GET /api/v1/investigations/{id}

Returns investigation state.

## GET /api/v1/investigations/{id}/results

Returns ranked products and evidence.

## GET /api/v1/investigations/{id}/agents

Returns agent execution metadata for authorized users.

## POST /api/v1/investigations/{id}/rerank

Changes weights/constraints and recalculates ranking.

## GET /api/v1/products/{id}

Returns canonical product information.

## GET /api/v1/products/{id}/reviews

Returns paginated reviews and analysis.

## POST /api/v1/comparisons

Creates a comparison between selected products.

All endpoints must return a consistent error format:

``` json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable message",
    "request_id": "uuid"
  }
}
```

------------------------------------------------------------------------

# 17. Authentication and Authorization

Use short-lived access tokens plus secure refresh-token handling.

Roles: - USER - ADMIN

Users may access only their own investigations.

Admin-only: - provider configuration - system-level agent telemetry -
moderation/configuration tools

Passwords must use Argon2id or another modern password hashing scheme.

Never store raw passwords or API keys.

------------------------------------------------------------------------

# 18. Frontend Architecture

Routes:

``` text
/
 /login
 /register
 /app
 /app/investigate
 /app/investigations/[id]
 /app/compare
 /app/saved
 /app/settings
 /admin/agents
```

State should be separated into: - authentication state - investigation
state - UI state - server/cache state

Use typed API clients generated or maintained from the backend schema.

------------------------------------------------------------------------

# 19. UI/UX Direction

Visual identity: **AI research console + premium commerce intelligence
product.**

Avoid generic e-commerce cards.

### Landing page

Show the problem as an intelligent decision workflow rather than a
product catalog.

### Investigation screen

Use a large natural-language query area with structured constraints
appearing progressively.

### Processing screen

Show live agent stages:

``` text
Understanding request       ✓
Finding candidates          ✓
Analyzing specifications    ✓
Mining reviews              ●
Checking evidence           ○
Ranking products            ○
```

### Results screen

Primary visual hierarchy: 1. recommendation 2. confidence 3. why it won
4. evidence 5. trade-offs 6. alternatives

### Comparison screen

Use synchronized columns with highlighted constraint satisfaction and
evidence quality.

### Responsive behavior

Desktop-first analytical layout, but fully usable on tablet/mobile.

Include loading, empty, error, and partial-result states.

------------------------------------------------------------------------

# 20. Third-Party Integrations

Integrations must sit behind provider interfaces.

Example:

``` python
class ProductProvider(Protocol):
    async def search(self, query: SearchQuery) -> list[RawProduct]:
        ...
```

Possible provider classes: - MockProvider for tests - CSVProvider for
reproducible demo data - ExternalCatalogProvider for approved live
sources

Do not scrape websites in violation of terms or robots policies.

------------------------------------------------------------------------

# 21. Storage

PostgreSQL stores structured data.

Object storage may be used for: - exported reports - large raw
datasets - model artifacts

Vector embeddings live in pgvector unless scale later justifies a
dedicated vector store.

------------------------------------------------------------------------

# 22. Error Handling

Every external call must have: - timeout - retry policy - bounded
retries - structured error - fallback behavior

Agent failure should not automatically destroy the entire investigation.

Example:

``` text
Review Agent failed
       ↓
Mark review evidence unavailable
       ↓
Continue ranking with reduced confidence
       ↓
Show user that review evidence is incomplete
```

------------------------------------------------------------------------

# 23. Security

Implement: - JWT/session security - Argon2id password hashing - strict
CORS - input validation - rate limiting - authorization checks - SQL
injection prevention through ORM/parameterization - XSS-safe rendering -
secure headers - secret management - audit logging - provider credential
isolation

Never allow user-supplied prompts to control privileged tools.

Agent tools must use an explicit allowlist.

------------------------------------------------------------------------

# 24. Performance

Targets: - ordinary API p95 \< 500 ms - cached product reads \< 150 ms
target - paginated reviews - async investigations - bounded concurrent
agent calls - Redis caching for repeated retrievals - database indexes
on high-selectivity fields - batch embedding generation - streaming
investigation status to frontend

------------------------------------------------------------------------

# 25. Testing Strategy

## Unit

Test: - constraint parser - price normalization - ranking - confidence
calculations - deduplication - review preprocessing

## Integration

Test: - API ↔ DB - API ↔ queue - agent ↔ provider interfaces - retrieval
↔ vector store

## AI Tests

Maintain a fixed evaluation set containing shopping requests and
expected structured constraints.

Measure: - constraint extraction accuracy - retrieval recall@K - ranking
consistency - explanation grounding rate

## E2E

Test: 1. Register 2. Login 3. Submit investigation 4. Wait for
completion 5. Inspect recommendation 6. Compare products 7. Save
investigation 8. Change ranking criteria

------------------------------------------------------------------------

# 26. Evaluation Framework

Do not claim AI performance metrics without measurement.

Create an evaluation dataset containing at least: - 100 structured
shopping queries - representative categories - hard constraints - soft
preferences - ambiguous queries - missing-data cases

Compare: - keyword baseline - single-model ranking baseline -
multi-agent pipeline

Report: - constraint extraction F1 - retrieval Recall@K - ranking
NDCG@K - evidence-grounding rate - latency - failure rate

------------------------------------------------------------------------

# 27. Observability

Every investigation receives a correlation ID.

Log: - request ID - user ID where permitted - investigation ID - agent
name - duration - status - error code - model/provider metadata -
token/cost metadata where available

Never log: - passwords - access tokens - provider secrets - unnecessary
sensitive user data

------------------------------------------------------------------------

# 28. Repository Structure

``` text
multi-agent-commerce/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   └── tests/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── investigations/
│   │   ├── products/
│   │   ├── reviews/
│   │   ├── agents/
│   │   ├── ranking/
│   │   ├── providers/
│   │   └── core/
│   └── tests/
├── ml/
│   ├── datasets/
│   ├── preprocessing/
│   ├── embeddings/
│   ├── evaluation/
│   └── models/
├── database/
│   ├── migrations/
│   └── seed/
├── scripts/
├── docs/
├── docker/
├── .env.example
├── docker-compose.yml
├── README.md
├── ARCHITECTURE.md
├── API.md
├── SETUP.md
├── TESTING.md
├── DEPLOYMENT.md
├── ML_PIPELINE.md
├── DATABASE.md
├── SECURITY.md
└── DESIGN_SYSTEM.md
```

------------------------------------------------------------------------

# 29. Development Phases

## Phase 1 --- Foundation

-   repository
-   Docker
-   environment configuration
-   PostgreSQL
-   Redis
-   migrations
-   CI

## Phase 2 --- Core Backend

-   authentication
-   product schema
-   investigation APIs
-   provider interfaces

## Phase 3 --- Data Layer

-   canonical product data
-   review data
-   embeddings
-   search/retrieval

## Phase 4 --- AI Agents

-   query understanding
-   discovery
-   specification
-   review intelligence
-   trust
-   ranking

## Phase 5 --- Orchestration

-   LangGraph state machine
-   retries
-   partial failures
-   observability

## Phase 6 --- Frontend

-   authentication
-   investigation workflow
-   live progress
-   results
-   comparison

## Phase 7 --- Evaluation

-   benchmark dataset
-   baselines
-   metrics
-   error analysis

## Phase 8 --- Productionization

-   security
-   Docker
-   CI/CD
-   monitoring
-   deployment

## Phase 9 --- Polish

-   UX
-   accessibility
-   performance
-   documentation
-   demo scenario

------------------------------------------------------------------------

# 30. Definition of Done

The project is complete only when: - all core agents work - structured
agent contracts are enforced - ranking is deterministic and
explainable - evidence is persisted - partial failures are handled -
authentication works - authorization is tested - API tests pass - ML/AI
evaluation is reproducible - frontend is responsive - no secrets are
hardcoded - Docker deployment works - documentation is complete - no
major placeholder functionality remains

------------------------------------------------------------------------

# 31. Resume-Worthy Technical Highlights

Potential bullets, to be finalized only after measurement:

-   Engineered a multi-agent e-commerce decision platform using typed
    agent workflows, asynchronous orchestration, and evidence-grounded
    product ranking.
-   Built an NLP pipeline for constraint extraction and aspect-level
    review intelligence, integrating semantic retrieval with
    deterministic ranking.
-   Designed a confidence-aware evidence layer that detects
    missing/contradictory product information and prevents unsupported
    recommendation claims.
-   Productionized the system with FastAPI, PostgreSQL, Redis/Celery,
    Docker, automated tests, structured logging, and secure API
    authorization.

Only include numerical performance claims after benchmarking.

------------------------------------------------------------------------

# 32. Antigravity Implementation Rules

1.  Read this specification completely before coding.
2.  Create repository structure first.
3.  Implement backend contracts before UI integration.
4.  Keep agents independently testable.
5.  Never make an LLM responsible for deterministic arithmetic/ranking.
6.  Never fabricate unavailable product data.
7.  Mark uncertain evidence explicitly.
8.  Use mock providers for development and testing.
9.  Do not bypass failed tests.
10. Do not hardcode secrets.
11. Add tests with each major module.
12. Update documentation when architecture changes.
13. Do not add dependencies without a concrete requirement.
14. Do not replace a difficult feature with a fake implementation.
15. Keep provider integrations replaceable.
16. Verify the full investigation workflow before final polish.

------------------------------------------------------------------------

# 33. Originality Requirement

The product identity comes from combining:

**natural-language shopping intent + specialized AI agents + structured
constraints + review intelligence + evidence verification +
deterministic ranking + explainable recommendations.**

Do not reduce the application to a chatbot that returns product names.

The defining question is:

> Can the system demonstrate how and why it reached its recommendation?

If not, the implementation is incomplete.

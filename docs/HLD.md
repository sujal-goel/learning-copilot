# High-Level Design (HLD) Document
## AI Learning Path Copilot

---

## 1. Executive Summary & Design Scope

The **High-Level Design (HLD)** defines the modular decomposition, subsystem boundaries, inter-service communication protocols, and end-to-end data flows for the AI Learning Path Copilot.

The platform's primary goal is to guide learners through a personalized, prerequisite-aware curriculum by marrying **deterministic graph processing** (Skill Trees, Prerequisite Rules) with **probabilistic generative AI** (LLM-based profiling, natural language tutoring, and semantic vector matching).

---

## 2. Subsystem Decomposition & Component Model

The system is decomposed into six logical subsystems operating across three physical tiers (Client, Application, and Persistence).

```mermaid
flowchart TB
    subgraph ClientSubsystem ["1. Client Presentation Subsystem (Next.js 14)"]
        UI_Onboarding["Onboarding & Chat Module"]
        UI_Roadmap["Roadmap Visualizer (React Flow)"]
        UI_Dashboard["Analytics & Next Action Dashboard"]
        UI_Tutor["AI Tutor Overlay & Assistant"]
    end

    subgraph GatewaySubsystem ["2. API Gateway & Security Subsystem"]
        APIGateway["FastAPI Reverse Proxy & Router"]
        AuthMiddleware["JWT Authentication & Rate Limiting"]
    end

    subgraph CoreServices ["3. Application Core Services Subsystem"]
        ProfileService["Learner Profile Service"]
        RecommenderService["Hybrid Recommendation Engine"]
        PathGeneratorService["Learning Path & DAG Generator"]
        AssessmentService["Assessment & Evaluation Service"]
        RAGAssistantService["RAG & Knowledge Assistant Service"]
        MentorService["AI Mentor Service\nFeedback-Driven Roadmap Adaptation"]
    end

    subgraph DataSubsystem ["4. Data & Vector Persistence Subsystem"]
        SQLDB[("PostgreSQL Relational DB<br/>Users, Skills, Nodes, Progress")]
        VectorStore[("pgvector Index<br/>Course & Skill Embeddings")]
    end

    subgraph ExternalSubsystems ["5. External AI Infrastructure"]
        LLMInference["LLM Provider (OpenAI / Gemini)"]
        EmbeddingInference["Embedding Models"]
    end

    ClientSubsystem -->|HTTPS REST and SSE Streams| APIGateway
    APIGateway --> AuthMiddleware
    AuthMiddleware --> CoreServices

    ProfileService -->|Structured Extraction| LLMInference
    ProfileService -->|Save Profile| SQLDB

    RecommenderService -->|Skill Lookup| SQLDB
    RecommenderService -->|Vector Match| VectorStore
    RecommenderService -->|Goal Vector| EmbeddingInference

    PathGeneratorService -->|Prerequisite Validation| SQLDB
    PathGeneratorService -->|Write Path Nodes| SQLDB

    AssessmentService -->|Update Proficiency| SQLDB
    AssessmentService -->|Trigger Mutation| PathGeneratorService

    RAGAssistantService -->|Similarity Retrieval| VectorStore
    RAGAssistantService -->|Grounding Context| LLMInference

    MentorService -->|Read Feedback & Chat History| SQLDB
    MentorService -->|Trigger Roadmap Update| PathGeneratorService
    MentorService -->|Grounding Context| LLMInference

    classDef client fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    classDef gw fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#0f172a;
    classDef svc fill:#f3e8ff,stroke:#9333ea,stroke-width:2px,color:#0f172a;
    classDef db fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#0f172a;
    classDef ext fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#0f172a;

    class UI_Onboarding,UI_Roadmap,UI_Dashboard,UI_Tutor client;
    class APIGateway,AuthMiddleware gw;
    class ProfileService,RecommenderService,PathGeneratorService,AssessmentService,RAGAssistantService,MentorService svc;
    class SQLDB,VectorStore db;
    class LLMInference,EmbeddingInference ext;
```

---

## 3. Subsystem Domain Responsibilities

### 3.1 Client Presentation Subsystem (Next.js)
- **Conversational Onboarding:** Multi-step natural language dialogue capturing learner background, target career roles, available study hours, and current skill confidence.
- **Interactive Roadmap (React Flow):** Visualizes the learning roadmap as a Directed Acyclic Graph (DAG) with custom nodes (Milestones, Courses, Projects, Assessments) and dynamic states (`LOCKED`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`).
- **Dashboard & Next Action:** Aggregates overall curriculum completion percentage, skill mastery radar charts, and renders a high-priority "Next Action Card".
- **AI Tutor Interface:** Persistent floating chat panel supporting real-time streaming markdown, code syntax highlighting, and cited reference chips.

### 3.2 Learner Profile Service
- **Entity Extraction:** Consumes raw onboarding transcripts and leverages LLM Structured Function Calling to output strict Pydantic schemas.
- **Skill Proficiency Tracker:** Maintains continuous proficiency ratings ($0.0 \dots 1.0$) for every known skill in the user's personal inventory.

### 3.3 Hybrid Recommendation Engine
- **Layer 1 (Prerequisite Rule Filter):** Eliminates courses where prerequisite skills have proficiency $< 0.7$, and courses whose topics the student has already mastered ($\ge 0.8$).
- **Layer 2 (Semantic Vector Search):** Employs `pgvector` Cosine Distance matching between the learner's goal vector and pre-indexed course embeddings.
- **Layer 3 (Skill-Gap Scoring):** Ranks candidate resources using:
  $$\text{PriorityScore} = W_{\text{goal}} \times (1.0 - \text{Proficiency}_{\text{current}}) \times (1.0 + \sum \text{PrerequisiteWeight})$$

### 3.4 Learning Path Generator
- **DAG Construction:** Topologically orders recommended modules to guarantee prerequisite integrity.
- **Milestone Chunking:** Organizes nodes into weekly/monthly sprints based on the learner's time commitment budget (e.g., 8 hours/week).

### 3.5 Assessment & Evaluation Service
- **Quiz Engine:** Generates targeted concept assessments and records submission scores.
- **Path Mutation Dispatcher:** Emits events when scores cross thresholds:
  - $\ge 85\%$: Fast-tracks the learner by tagging downstream introductory nodes as `SKIPPED`.
  - $< 50\%$: Dynamically queries the Recommender Service and splices remedial exercise nodes into the active graph.

### 3.6 RAG & AI Assistant Service
- **Vector Retrieval:** Performs similarity search across chunked course syllabi, documentation, and skill taxonomy.
- **Grounded Prompt Synthesis:** Injects retrieved context into system prompts with strict anti-hallucination instructions.

### 3.7 AI Mentor Service (`mentor_service.py`)
- **Feedback Processing:** Reads submitted `feedback` records (difficulty level + free text) after a user completes a node.
- **Proactive Adaptation:** If `difficulty_level == TOO_HARD`, calls `PathGeneratorService` to splice remedial nodes. If `TOO_EASY`, fast-tracks.
- **Context-Aware Chat:** Injects chat history + active node context into every LLM call so the mentor maintains conversational continuity across sessions.
- **Roadmap Recalibration:** When the user updates study hours (`PUT /profile/me`), recalculates milestone timelines without regenerating the full roadmap.

---

## 4. End-to-End Dynamic Data Flows

### 4.1 Onboarding & Initial Roadmap Generation Flow

```mermaid
sequenceDiagram
    autonumber
    actor Learner as Learner Client
    participant UI as Next.js Onboarding UI
    participant API as FastAPI Gateway
    participant ProfSvc as Learner Profile Svc
    participant RecSvc as Recommendation Svc
    participant PathSvc as Path Generator Svc
    participant DB as PostgreSQL and pgvector
    participant AI as LLM / Embeddings API

    Learner->>UI: Types goal: "Want backend internship in 6 months, know Java basics"
    UI->>API: POST /profile/onboard (chat_history)
    API->>ProfSvc: extract_profile(chat_history)
    ProfSvc->>AI: LLM Structured JSON Extraction
    AI-->>ProfSvc: Parsed Profile JSON (Java: 0.8, SQL: 0.6, Spring: 0.0)
    ProfSvc->>DB: Save User Profile and Initial Skills
    
    ProfSvc->>RecSvc: generate_recommendations(profile_id)
    RecSvc->>DB: Query Skill Graph Requirements for Backend Role
    DB-->>RecSvc: Required Skill Tree and Prerequisite Nodes
    RecSvc->>AI: Vectorize Learner Goal
    AI-->>RecSvc: 1536-dim Goal Vector
    RecSvc->>DB: pgvector Cosine Search on Course Catalog
    DB-->>RecSvc: Top Candidate Courses
    RecSvc->>RecSvc: Execute 3-Layer Filter and Skill-Gap Ranking
    
    RecSvc->>PathSvc: build_roadmap(ranked_courses, user_constraints)
    PathSvc->>PathSvc: Topological Sort and Milestone Chunking
    PathSvc->>DB: Persist LearningPath and LearningPathNodes
    PathSvc-->>API: Active Roadmap DAG Payload
    API-->>UI: Return 201 Created with Roadmap JSON
    UI-->>Learner: Render Interactive Canvas in React Flow
```

---

### 4.3 User Feedback & Roadmap Update Flow

```mermaid
sequenceDiagram
    autonumber
    actor Learner as Learner Client
    participant UI as Next.js Dashboard
    participant API as FastAPI Gateway
    participant MentorSvc as Mentor Service
    participant PathSvc as Path Generator Svc
    participant DB as PostgreSQL Database
    participant LLM as LLM API

    Learner->>UI: Submits feedback: "Too theoretical, need more practice" + difficulty: TOO_HARD
    UI->>API: POST /feedback (node_id, feedback_text, difficulty_level)
    API->>DB: Save feedback record
    API->>MentorSvc: process_feedback_and_adapt(user_id, feedback_id)

    MentorSvc->>DB: Load feedback + recent chat_history + active learning path
    MentorSvc->>LLM: Generate mentor response with context
    LLM-->>MentorSvc: Adaptation suggestion + explanation

    alt difficulty_level == TOO_HARD
        MentorSvc->>PathSvc: trigger_remediation(user_id, weak_node_id)
        PathSvc->>DB: Splice hands-on project/exercise nodes before next milestone
    else difficulty_level == TOO_EASY
        MentorSvc->>PathSvc: trigger_fast_track(user_id, skill_id)
        PathSvc->>DB: Mark redundant beginner nodes as SKIPPED
    end

    MentorSvc->>DB: Save mentor reply to chat_history (role=ASSISTANT)
    PathSvc-->>API: Updated roadmap DAG
    API-->>UI: 201 Created + mentor reply + updated path summary
    UI-->>Learner: Toast notification + animated roadmap update on canvas
```



### 4.2 Assessment Evaluation & Adaptive Roadmap Mutation Flow

```mermaid
sequenceDiagram
    autonumber
    actor Learner as Learner Client
    participant UI as Next.js Dashboard
    participant API as FastAPI Gateway
    participant AssessSvc as Assessment Service
    participant PathSvc as Path Generator Svc
    participant DB as PostgreSQL Database

    Learner->>UI: Submits Module Assessment Quiz
    UI->>API: POST /assessment/submit (assessment_id, answers)
    API->>AssessSvc: grade_assessment(user_id, answers)
    AssessSvc->>AssessSvc: Calculate Score and Concept Breakdown
    AssessSvc->>DB: Record Score and Update Skill Proficiency
    
    alt Score >= 85% (Advanced Mastery)
        AssessSvc->>PathSvc: trigger_fast_track(user_id, skill_id)
        PathSvc->>DB: Update downstream beginner nodes to SKIPPED
        PathSvc->>DB: Recalculate estimated completion date
        PathSvc-->>API: Mutated Roadmap DAG (Bypassed Nodes)
    else Score < 50% (Remedial Needed)
        AssessSvc->>PathSvc: trigger_remediation(user_id, weak_concepts)
        PathSvc->>DB: Insert remedial exercise nodes before next milestone
        PathSvc-->>API: Mutated Roadmap DAG (Spliced Nodes)
    else Standard Passing (50% to 84%)
        AssessSvc->>PathSvc: mark_completed(node_id)
        PathSvc->>DB: Update node status to COMPLETED
        PathSvc-->>API: Updated Progress Payload
    end
    
    API-->>UI: 200 OK with Updated DAG
    UI-->>Learner: Animate DAG changes on canvas & toast feedback
```

---

## 5. Non-Functional Architecture & Resilience

```mermaid
flowchart LR
    subgraph ResiliencePatterns ["Resilience & Reliability Patterns"]
        CB["Circuit Breakers on LLM APIs (Tenacity)"]
        Pool["PgBouncer Connection Pooling (Postgres)"]
        Cache["In-Memory LRU / Redis Query Cache"]
        Retry["Exponential Backoff with Jitter"]
    end

    subgraph OperationalMetrics ["Observability & Metrics"]
        Prometheus["Structured JSON Logs & Prometheus Metrics"]
        HealthCheck["FastAPI /healthz & /readyz probes"]
    end

    classDef res fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#0f172a;
    classDef obs fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#0f172a;

    class CB,Pool,Cache,Retry res;
    class Prometheus,HealthCheck obs;
```

### 5.1 High-Availability & Scalability
- **Stateless Application Servers:** All FastAPI worker containers are stateless. Sessions are authenticated via cryptographically signed JWTs, allowing horizontal pod autoscaling behind load balancers.
- **Connection Management:** Connection pooling via PgBouncer prevents PostgreSQL socket exhaustion during peak concurrent API invocations.
- **LLM Rate-Limit Resilience:** External AI calls are wrapped with `tenacity` retry decorators using exponential backoff with random jitter to gracefully handle provider 429 rate limit spikes.

---

## 6. Detailed AI Workflows & State Machines

### 6.1 Onboarding State Machine

```mermaid
stateDiagram-v2
    [*] --> UNAUTHENTICATED

    UNAUTHENTICATED --> REGISTERING : User clicks "Sign Up"
    UNAUTHENTICATED --> AUTHENTICATING : User clicks "Login"
    UNAUTHENTICATED --> AUTHENTICATING_OAUTH : User clicks "Continue with Google"

    REGISTERING --> AUTHENTICATING : Registration success (auto-login)
    REGISTERING --> UNAUTHENTICATED : Registration error (duplicate email, etc.)

    AUTHENTICATING --> AUTHENTICATED : JWT issued
    AUTHENTICATING --> UNAUTHENTICATED : Invalid credentials

    AUTHENTICATING_OAUTH --> AUTHENTICATED : Google OAuth callback success
    AUTHENTICATING_OAUTH --> UNAUTHENTICATED : OAuth error / denied

    AUTHENTICATED --> CHECK_PROFILE : Frontend checks GET /profile/me
    CHECK_PROFILE --> ONBOARDING_CHAT : 404 — No profile exists
    CHECK_PROFILE --> DASHBOARD : 200 — Profile exists

    ONBOARDING_CHAT --> ONBOARDING_REVIEW : User completes conversation
    ONBOARDING_REVIEW --> PROFILE_SAVING : User confirms extracted profile
    ONBOARDING_REVIEW --> ONBOARDING_CHAT : User requests re-do

    PROFILE_SAVING --> ROADMAP_GENERATING : Profile saved (201)
    ROADMAP_GENERATING --> DASHBOARD : Roadmap ready
    ROADMAP_GENERATING --> ERROR : Generation failure

    ERROR --> ONBOARDING_CHAT : Retry
```

### 6.2 AI Tutor Chat Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Learner
    participant FE as Next.js (AI Tutor Panel)
    participant API as FastAPI Gateway
    participant ChatRoute as Chat Router
    participant MentorSvc as Mentor Service
    participant DB as PostgreSQL
    participant LLM as LLM Provider (RAG)

    User->>FE: Types "Why do I need SQL before JPA?"
    FE->>API: POST /api/v1/chat { query, current_node_id?, session_id? }
    API->>ChatRoute: Validate JWT → get current_user

    Note over ChatRoute, DB: Step 1 — Save User Message
    ChatRoute->>DB: INSERT chat_history (role=USER, message=query, session_id)

    Note over ChatRoute, LLM: Step 2 — Get AI Response
    ChatRoute->>MentorSvc: get_mentor_response(user_id, query, current_node_id)
    MentorSvc->>DB: Load chat_history (context window)
    MentorSvc->>DB: Load active learning_path + current node metadata
    MentorSvc->>LLM: RAG prompt with retrieved context
    LLM-->>MentorSvc: { reply, citations[], roadmap_mutation }

    Note over ChatRoute, DB: Step 3 — Save AI Response
    ChatRoute->>DB: INSERT chat_history (role=ASSISTANT, message=reply)
    ChatRoute->>DB: COMMIT transaction

    ChatRoute-->>FE: { reply, session_id, citations, roadmap_mutation }
    FE-->>User: Render AI response with citations
```

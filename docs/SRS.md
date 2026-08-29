# Software Requirements Specification (SRS)
## AI Learning Path Copilot

---

## 1. Project Overview & Problem Statement

### 1.1 Purpose
This Software Requirements Specification (SRS) documents the detailed functional and non-functional requirements for the **AI Learning Path Copilot**. 

### 1.2 Problem Statement
Learners are often overwhelmed by the sheer volume of educational content available online. Generic learning paths ("learn Python → learn ML → learn AI") fail to account for a learner's existing skills, specific career goals, and unique learning pace. Without a structured, personalized, and adaptive guide, learners lose motivation and waste time on redundant or overly advanced materials.

### 1.3 Solution
This project aims to build an **AI Learning Path Copilot** that provides personalized, prerequisite-aware, and adaptive learning recommendations. By utilizing Large Language Models (LLMs) for natural onboarding and RAG-based tutoring, combined with deterministic skill-graph algorithms for precise pathing, the system ensures learners always know their exact "next best action."

---

## 2. Functional Requirements (FR)

The system functionality is divided into core domains that represent the user journey.

### 2.1 Conversational Onboarding & Learner Profiling
**Description:** The system must capture the learner's initial state without forcing them to fill out long forms.
- **FR-1.01:** The system shall provide a conversational chat interface for initial user onboarding.
- **FR-1.02:** The system shall use NLP/LLMs to parse the conversation and extract the following entities:
  - Target Career Goal (e.g., "Full Stack Developer")
  - Target Duration (e.g., "6 months")
  - Current Skills and estimated proficiency levels
  - Special Interests (e.g., "Interested in FinTech")
- **FR-1.03:** The system shall allow users to manually review and edit the AI-extracted profile before saving.
- **FR-1.04:** The system shall store the finalized profile in a structured JSON format mapped to relational database tables.

#### 2.1.1 Conversation Design Script
The onboarding chatbot follows a guided conversation script with five core questions. All conversation happens client-side; the full transcript is sent to the backend only when the user finishes.

| Step | Bot Message | Extraction Target | Required |
| :---: | :--- | :--- | :---: |
| 1 | "👋 Welcome! I'm your learning copilot. What career role or skill are you working towards?" | `goal` | ✅ |
| 2 | "Great choice! What programming languages, frameworks, or tools do you already know? Rate your comfort level if you can." | `skills[]` + `proficiency` | ✅ |
| 3 | "How would you describe your overall experience level?" *(Offer: Beginner / Intermediate / Advanced)* | `experience_level` | ✅ |
| 4 | "How many hours per week can you dedicate to learning?" | `study_hours_per_week` | ✅ |
| 5 | "What's your target timeline? (e.g., 3 months, 6 months, 1 year)" | `timeline_months` | ✅ |
| 6 | *(Optional)* "Any special interests or industry focus? (e.g., FinTech, HealthTech, Gaming)" | `interests` | ❌ |

### 2.2 Skill-Gap Analysis
**Description:** The system must determine exactly what the user needs to learn.
- **FR-2.01:** The system shall maintain a centralized "Skill Graph" defining all skills and their dependencies/prerequisites.
- **FR-2.02:** The system shall compare the user's current skills against the target goal's required skills.
- **FR-2.03:** The system shall calculate a mathematical "Skill Gap Score" for each missing or underdeveloped skill.
- **FR-2.04:** The system shall assign a priority to each skill gap based on whether the skill is a prerequisite for other required skills.

### 2.3 Hybrid Recommendation Engine
**Description:** The system must find the optimal learning resources (courses, projects, docs) to fill the identified skill gaps.
- **FR-3.01:** The system shall execute a rule-based filter to exclude resources that require prerequisites the user does not possess.
- **FR-3.02:** The system shall execute a rule-based filter to exclude resources teaching skills the user has already mastered.
- **FR-3.03:** The system shall perform semantic similarity vector searches (using `pgvector`) to match the user's interests with resource descriptions.
- **FR-3.04:** The system shall rank the filtered, matched resources according to the priority of the skill gap they address.

### 2.4 Learning Path Generation
**Description:** The system must arrange the recommended resources into a chronological roadmap.
- **FR-4.01:** The system shall generate a Directed Acyclic Graph (DAG) representing the learning path, strictly obeying prerequisite rules.
- **FR-4.02:** The system shall group path nodes into chronological milestones (e.g., "Month 1: Foundations").
- **FR-4.03:** The system shall provide an interactive visual representation of this path to the user (e.g., using React Flow).

### 2.5 Assessment & Adaptive Roadmap
**Description:** The system must react when a learner overperforms or underperforms.
- **FR-5.01:** The system shall provide multiple-choice or practical assessments for core skills.
- **FR-5.02:** The system shall record assessment scores and update the user's skill proficiency levels accordingly.
- **FR-5.03:** **Positive Adaptation:** If a user scores above a predefined threshold (e.g., >85%), the system shall automatically mark beginner/introductory nodes for that skill as "Skipped" in the active learning path.
- **FR-5.04:** **Negative Adaptation:** If a user scores below a predefined threshold (e.g., <50%), the system shall automatically insert remedial/additional practice nodes into the active learning path before allowing progression.

### 2.6 AI Tutor (RAG)
**Description:** An ever-present assistant that explains the "why" behind the system's choices and helps with blockers.
- **FR-6.01:** The system shall provide a chat interface accessible from any point in the learning path.
- **FR-6.02:** The AI Tutor shall answer questions regarding the learning path (e.g., "Why am I learning REST APIs before Authentication?").
- **FR-6.03:** The AI Tutor shall utilize Retrieval-Augmented Generation (RAG) by retrieving data from the internal course catalog and skill graph to prevent hallucinating non-existent courses.
- **FR-6.04:** The AI Tutor shall accept commands to modify constraints (e.g., "I only have 5 hours a week now") and trigger a recalculation of the roadmap timeline.

### 2.7 Learner Dashboard
**Description:** The home screen providing an at-a-glance overview of the user's journey.
- **FR-7.01:** The dashboard shall display a global progress bar (percentage complete).
- **FR-7.02:** The dashboard shall list recently completed skills and milestones.
- **FR-7.03:** The dashboard shall highlight identified "weak areas" based on recent low assessment scores.
- **FR-7.04:** The dashboard shall prominently display a single "Next Action" card, directing the user to the exact next resource they should consume.

### 2.8 User Feedback & Roadmap Adaptation
**Description:** The system must allow learners to signal difficulty and receive an adapted roadmap in response.
- **FR-8.01:** After completing or abandoning a roadmap node, the system shall prompt the user for optional feedback (difficulty level: `TOO_EASY`, `JUST_RIGHT`, `TOO_HARD`, and free-text comments).
- **FR-8.02:** The system shall persist all submitted feedback linked to the user and the specific roadmap node.
- **FR-8.03:** Upon receiving a `TOO_HARD` feedback, the AI Mentor Service shall automatically splice supplemental practice nodes into the active learning path before the next milestone.
- **FR-8.04:** Upon receiving a `TOO_EASY` feedback, the AI Mentor Service shall mark redundant beginner nodes as `SKIPPED` to fast-track the user.
- **FR-8.05:** The system shall return an updated roadmap summary and a natural-language mentor explanation in the feedback response.

---

## 3. Non-Functional Requirements (NFR)

### 3.1 Performance Requirements
- **NFR-1.01 (Latency):** API responses for standard CRUD operations must complete within 200ms.
- **NFR-1.02 (LLM Latency):** Conversational AI responses and path generation utilizing external LLMs shall respond within 5 seconds (or stream tokens immediately).
- **NFR-1.03 (Vector Search):** Semantic matching queries using `pgvector` on the course catalog must complete within 100ms.

### 3.2 Scalability & Reliability
- **NFR-2.01 (Concurrency):** The backend architecture shall support at least 1,000 concurrent active users without performance degradation.
- **NFR-2.02 (Availability):** The application shall maintain a 99.9% uptime target.
- **NFR-2.03 (Statelessness):** The backend API shall be stateless, relying on JWT tokens for session management to allow horizontal scaling.

### 3.3 Security & Privacy
- **NFR-3.01 (Authentication):** All user endpoints (except public landing pages) must be secured via JWT-based authentication over HTTPS.
- **NFR-3.02 (Authorization):** Strict tenant isolation must be enforced; a user cannot access another user's profile, path, or assessment scores.
- **NFR-3.03 (Data Encryption):** Passwords must be hashed using bcrypt or Argon2 before database storage.
- **NFR-3.04 (Prompt Injection):** The AI systems must implement system-level prompt constraints to resist malicious prompt injections intended to bypass the RAG sandbox.
- **NFR-3.05 (Google OAuth2):** The system shall support social login via Google OAuth2. Google-authenticated users shall receive the same JWT-based session as password-authenticated users. Accounts created via Google shall have `password_hash = NULL` and cannot use password login.

### 3.4 Usability & Accessibility
- **NFR-4.01 (Responsiveness):** The web application UI must be fully responsive and functional on both desktop (1920x1080) and mobile (375x667) viewports.
- **NFR-4.02 (Accessibility):** The UI shall conform to WCAG 2.1 AA standards (color contrast, screen reader compatibility, keyboard navigation).
- **NFR-4.03 (Feedback):** The system must provide non-blocking visual feedback (toast notifications, skeletons, spinners) for any action taking longer than 1 second.

### 3.5 Maintainability
- **NFR-5.01 (Documentation):** All backend API endpoints must be automatically documented using OpenAPI (Swagger).
- **NFR-5.02 (Logging):** The system must implement structured JSON logging for all API requests and LLM interactions for debugging and observability.

---

## 4. User Roles

| Role | Permissions & Capabilities |
| :--- | :--- |
| **Learner** | - Can register and complete onboarding.<br>- Can view and interact with their personalized dashboard and learning path.<br>- Can take assessments and mark resources as completed.<br>- Can chat with the AI Tutor. |
| **Admin** *(Future)* | - Can manage the global Skill Graph (add/edit skills and prerequisites).<br>- Can manage the Course Catalog (add/edit learning resources).<br>- Can view anonymized platform usage metrics. |

---

## 5. Constraints & Assumptions

1. **Domain Scope:** The MVP will be constrained to the Computer Science / Software Engineering / Data Science domains. Expanding to other fields requires significant data entry for new Skill Graphs.
2. **Third-Party APIs:** The system relies entirely on external providers (e.g., OpenAI or Google Gemini) for LLM processing and embeddings. Network instability or API rate limits from these providers will degrade the user experience.
3. **Cold Start Problem:** Deep learning-based collaborative filtering (e.g., "users like you also took...") is excluded from the MVP because it requires a large historical dataset of user interactions which currently does not exist. The rule-based + semantic vector hybrid engine will suffice until data is collected.

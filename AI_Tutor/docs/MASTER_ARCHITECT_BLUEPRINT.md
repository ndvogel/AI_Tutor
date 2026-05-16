# 📜 MASTER_ARCHITECT_BLUEPRINT.md (v1.6)

## 1. Master System Overview

The Adaptive Learning Engine is a closed-loop pedagogical system designed to decouple **Subject Matter Knowledge** from **Instructional Delivery**. The system operates in a four-stage continuous loop, tracking state dynamically to ensure personalized, high-retention mastery.

```
[Student Input / Onboarding]
          │
          ▼
┌─────────────────────────┐   Generates Curriculum   ┌─────────────────────────┐
│   1. Knowledge Architect├─────────────────────────>│   2. Dynamic Profiler   │
│   (Deconstructs Subject)│                           │  (Tracks State & Trait) │
└───────────▲─────────────┘                           └────────────┬────────────┘
            │                                                      │
            │  Triggers Interventions            Passes Profile On │
            │  On High Friction                  & Target Node     │
            │                                                      ▼
┌───────────┴─────────────┐   Renders Lesson         ┌─────────────────────────┐
│   4. Evaluation Loop    │<─────────────────────────┤   3. Contextual Anchor  │
│ (Assessments & Prompts) │                           │   (Translates Concepts) │
└─────────────────────────┘                           └─────────────────────────┘
```

---

## 2. Onboarding & Student Input Fields (The UI Data Layer)

Regardless of implementation medium (CLI, Web UI, Mobile), the system must collect and map the following inputs from the user during initial setup:

| Field Name | Data Type | Purpose / AI Instruction Guideline | Example Input |
| :--- | :--- | :--- | :--- |
| `student_name` | String | Personalization and conversational tone. | "Nathan" |
| `target_subject` | String | The macro-concept or skill the user wants to master. | "Web APIs" |
| `generational_bracket` | String | Sets tone, slang parameters, and historical touchstones. | "Gen X / Millennial Crossover" |
| `core_interests` | Array (Strings) | Max capacity: 5. Primary mental models used to build structural analogies. | `["basketball", "cooking"]` |
| `preferred_delivery` | String | Primary instructional modality preferred. | "Interactive Dialog" |

---

## 3. Sub-System Deep Dive

### Sub-System A: The Knowledge Architect (The "What")
- **Role:** Takes the `target_subject` and decomposes it into an ordered list of micro-lessons structured as a Directed Acyclic Graph (DAG).
- **Data Boundary:** Independent of user identity. Focuses strictly on subject logic and prerequisite mapping.
- **Logic:** Outputs a structural progression. Step N+1 cannot be unlocked until Step N is verified.

### Sub-System B: The Dynamic Profiler (The "Who")
- **Role:** Holds the persistent state of the learner.
- **Data Boundary:** Merges static onboarding inputs with real-time tracking data (`attempts`, `success_rate`, `friction_score`, `custom_mental_models`).

### Sub-System C: The Contextual Anchor (The Delivery)
- **Role:** The translator. Blends raw technical concepts from Sub-System A with personal vectors from Sub-System B.
- **Formula:** `Lesson Output = Concept + (Interests + Generation)`.
- **Constraint:** Select exactly ONE interest from the user's core interests profile per lesson node. Do not cross-contaminate analogies into confusing hybrid topics.

### Sub-System D: The Evaluation & Intervention Loop (The Guardrail)
- **Role:** Tests the user via active recall and manages cognitive block protocols.
- **Standard Mode:** Issues micro-assessments. If passed, updates Sub-System B and unlocks the next node in Sub-System A.
- **Friction Mode:** Triggered automatically if local node failures criteria are met.

---

## 4. System Safeguards & Control Logic

### 4.1 The Circuit Breaker (Anti-Loop Guardrail)
- Each node maintains a tracking integer: `friction_cycle_count`.
- **RULE 1:** If a user fails 3 consecutive assessments on a single node, the node triggers Friction Mode. If they fail 3 more times inside Friction Mode (6 total consecutive failures), the Orchestrator MUST:
  1. Force-lock the current node.
  2. Regress the user to the immediate prerequisite node for a review cycle.
  3. Instruct the Knowledge Architect to split the failing node into two smaller, simpler sub-nodes.
- **RULE 2:** `friction_cycle_count` only increments during *active lesson node delivery*. It is entirely decoupled from Onboarding Diagnostics and Micro-Gates to prevent locking an unvisited node.

### 4.2 The Token Conservation Protocol (Financial Optimization)
- Raw chat conversation logs are ephemeral and truncated or cleared every 5 turns.
- Persistent state is strictly maintained and passed via the flat JSON profile.
- **Payload Budget:** `Payload = [System Prompt] + [Condensed JSON State] + [Current Node Content] + [Last 3 Chat Turns]`.
- **Cache Limiter:** Cap the active JSON `custom_mental_models` cache to the top 3 most recently utilized models. Any model not explicitly related to the current active module is moved to secondary storage to protect the token context length.

### 4.3 Analogy Sanity Check & Collaborative Modeling
- **RULE 1: The Analogy Fork (Interest Re-Routing):** If the Contextual Anchor determines that a primary interest creates a weak or technically inaccurate analogy for a node, it queries the Dynamic Profiler for alternative interests and prompts the user: *"This concept doesn't map perfectly to [Interest A]. Are you comfortable if we look at it through the lens of [Interest B] instead?"*
- **RULE 2: Socratic Verification (The Rebound Rule):** If the AI constructs a domain analogy but lacks 100% real-world mechanical confidence, it is forbidden from stating it as fact. It must issue an inquiry prompt: *"In [User Interest], does a mechanism exist where [Concept Mechanic]? If so, that is exactly how [Technical Concept] works because..."* User validation is parsed and saved to `custom_mental_models`.
- **RULE 3: The Interest Cap & Eviction Protocol:** The `core_interests` array has a strict upper limit of 5 entries. If a new interest is uncovered via dialogue or explicitly added when the array is full, the system MUST halt automated updates and prompt the user: *"You've hit your maximum of 5 core interests. Would you like to replace one of your current interests to make room for this new one, or should we skip storing it?"* The system will display the current 5 interests as a selectable list for eviction.

---

## 5. Onboarding & Diagnostic Placement Architecture

### 5.1 Adaptive Tree-Pruning Protocol (Macro-Assessment)
- The system generates a maximum of 3 high-level, scenario-based diagnostic questions mapping to the main pillars of the target subject.
- If competency is demonstrated, child nodes are structurally marked as `conditionally_skipped`.

### 5.2 Micro-Gate Verification (Just-In-Time Assessment)
- **RULE:** A user cannot begin an advanced node if the preceding nodes are marked `conditionally_skipped`.
- Before delivering the advanced lesson, the Evaluation Loop issues a single, highly targeted technical query.
- *Pass Condition:* Child nodes convert from `conditionally_skipped` to `mastered`.
- *Fail Condition:* Child nodes revert to `unlocked` (active), and the Orchestrator routes the user to the beginning of the missed foundational elements.

---

## 6. Future Engineering Roadmap & Scalability

### 6.1 Migration to Vector-Driven RAG (Long-Term Memory)
- **Target State:** Implement a localized vector database (e.g., ChromaDB or LanceDB) to handle "Pedagogical Memory Retrieval."
- **Mechanism:** Convert historical learning logs into vector embeddings. When friction occurs, use semantic similarity search to retrieve successful past instructional strategies, maintaining structural efficiency without blowing past context windows.

---

## 7. Software Architecture & Coding Standards

To maintain clean, maintainable code and prevent file bloat during AI-assisted generation, the codebase must strictly adhere to a modular, decoupled architecture.

### 7.1 Module Isolation Rules
*   **No API Leakage:** All LLM API interaction (initializing the Google GenAI SDK, setting system instructions, managing parameters) must live strictly inside `src/agents.py`. No other file is permitted to make direct API calls.
*   **No Raw Storage Calls:** Reading and writing `.json` files must live strictly inside `src/utils.py`. The rest of the application must interact with data via helper functions (e.g., `load_profile()`, `save_progress()`).
*   **No State in Main:** `src/main.py` is exclusively the operational runtime loop (the conductor). It coordinates data from `utils.py`, passes it to `agents.py`, and orchestrates the user interface.

### 7.2 Directory Reference Guide for AI Agents
When generating or modifying code, adhere strictly to this functional allocation mapping:

| File Path | Explicit Responsibility | Forbidden Content |
| :--- | :--- | :--- |
| `src/agents.py` | Initializing LLM clients; executing prompts; handling retry logic. | Direct file saving (`open()`, `json.dump()`); terminal menus. |
| `src/utils.py` | JSON loading/saving; data schema validation; system paths. | Importing LLM SDKs; running prompts; handling runtime logic. |
| `src/main.py` | Managing the state loop; print statements; routing the menu logic. | Complex JSON mutations; direct API handling. |

# 📜 MASTER_ARCHITECT_BLUEPRINT.md (v1.7)

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
---

## 8. Data Architecture & State Management (Stress-Test Additions)

*This section was added after architectural review to close gaps identified in the v1.6 spec before code generation begins.*

---

### 8.1 Canonical Node Schema

Every lesson node in the DAG must conform to this exact structure when stored in `learning_progress.json`. No code may write a node object that omits required fields.

```json
{
  "node_id": "string (e.g., 'api_basics_01')",
  "title": "string",
  "prerequisites": ["node_id", "node_id"],
  "status": "locked | unlocked | conditionally_skipped | mastered | force_locked",
  "friction_cycle_count": 0,
  "consecutive_failures": 0,
  "attempts": 0,
  "success_rate": 0.0,
  "active_interest_used": "string (the interest selected for this node's analogy)",
  "last_updated": "ISO 8601 timestamp"
}
```

**Where it lives:** `learning_progress.json` under a top-level `nodes` key, indexed by `node_id`.
**Who writes it:** Only `src/utils.py` via a dedicated `save_node()` function. No other file may mutate node objects directly.

---

### 8.2 Legal Node State Transitions (State Machine)

Not all status changes are valid. The Orchestrator in `main.py` must reject any transition not listed here. This prevents the race condition between the Micro-Gate promotion logic (Section 5.2) and the Circuit Breaker regression logic (Section 4.1).

| From Status | Legal Transitions To | Triggered By |
| :--- | :--- | :--- |
| `locked` | `unlocked` | Prerequisite node reaches `mastered` |
| `unlocked` | `conditionally_skipped`, `mastered`, `force_locked` | Diagnostic pass, assessment pass, Circuit Breaker |
| `conditionally_skipped` | `mastered`, `unlocked` | Micro-Gate pass, Micro-Gate fail |
| `mastered` | `unlocked` | Circuit Breaker regression only |
| `force_locked` | `unlocked` | Manual instructor override OR node split complete |

**Priority Rule:** If two subsystems attempt conflicting transitions simultaneously, the Circuit Breaker (Section 4.1) always wins. A `force_locked` status cannot be overridden by Micro-Gate logic.

---

### 8.3 Turn Buffer Management (Clarifying Section 4.2 vs. Section 7)

Section 4.2 defines a 5-turn truncation and 3-turn payload window. Section 7.1 assigns state loop management to `main.py` but forbids complex JSON mutation there. This section resolves that conflict explicitly.

**Rule:** `src/utils.py` owns the turn buffer via two functions:

```python
def append_turn(role: str, content: str) -> None:
    """Appends a turn to last_3_turns, evicts oldest if buffer exceeds 3."""

def increment_turn_count() -> bool:
    """Increments session_turn_count. Returns True if truncation threshold (5) is reached."""
```

`src/main.py` calls these functions after every exchange. It does not manipulate the buffer array directly.

---

### 8.4 Contextual Anchor Fallback Protocol (Closing the No-Match Gap)

Section 4.3 defines behavior when a primary interest produces a weak analogy, but does not define what happens if all 5 interests fail to map to a node.

**Fallback Chain (executed in order):**

1. Attempt primary interest analogy.
2. If weak, query Dynamic Profiler for alternatives per Section 4.3 Rule 1.
3. If all 5 interests are exhausted without a valid mapping, the Contextual Anchor switches to **Neutral Mode**: deliver the concept using plain language with no domain analogy, and log the node ID to a `no_analogy_nodes` list in `student_profile.json`.
4. After the session, prompt the user: *"I had trouble finding a good analogy for [Node Title] using your current interests. Would you like to add a new interest that might help with topics like this?"*

This ensures the lesson always delivers rather than stalling, while surfacing the gap for the user to address.

---

### 8.5 Updated `learning_progress.json` Full Schema

```json
{
  "current_node_id": null,
  "nodes": {},
  "friction_cycle_count": 0,
  "session_turn_count": 0,
  "last_3_turns": [
    { "role": "user | assistant", "content": "string" }
  ]
}
```

### 8.6 Updated `student_profile.json` Full Schema

```json
{
  "student_name": "",
  "target_subject": "",
  "generational_bracket": "",
  "core_interests": [],
  "preferred_delivery": "",
  "custom_mental_models": [],
  "no_analogy_nodes": []
}
```
## Appendix C: Architectural Decision Records (ADR)

### ADR-001: Dynamic Remediation and User Agency
* **Date:** May 16, 2026
* **Status:** Approved (Pre-Implementation Stress Test Passed)
* **Context:** The core assessment engine defaults to a 2-out-of-3 threshold for node mastery. However, a rigid binary pass/fail mechanics prevents deep reinforcement of nuanced weak spots and limits user learning choices.
* **Decision:** Implement an isolated, branching "Micro-Remediation Loop". If a student meets the pass threshold but misses a sub-topic, the system triggers an optional branching choice allowing the user to initiate a single-topic deep dive.
* **Guardrails & Constraints:**
  1. **Data Isolation:** Remediation state must live inside a temporary, optional `"remediation": {}` tracking block within the existing node record. It must NOT alter the canonical 9-field schema framework.
  2. **Circuit Breaker:** Max 1 attempt for micro-remediation modules to prevent recursive execution loops.
  3. **No Retroactive Locks:** Failing a micro-remediation module cannot revoke a previously granted `mastered` status or re-lock downstream nodes.
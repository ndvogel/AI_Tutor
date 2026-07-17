# AI_Tutor — Project Constitution

This file is read automatically at the start of every Claude Code session in this
repo. It defines how work gets done here: the coding baseline, the agent roster,
and the approval gates. If an instruction elsewhere conflicts with this file,
this file wins.

## 1. What this project is

AI_Tutor is an adaptive learning engine (Python + Streamlit UI, Gemini API via
`google-genai`, JSON-file persistence). Four sub-systems drive it: Knowledge
Architect (curriculum DAG), Contextual Anchor (lesson generation), Evaluation
Loop (grading), Micro-Remediation (gap-filling). See `docs/MASTER_ARCHITECT_BLUEPRINT.md`
for the full design.

## 2. Coding baseline

Every agent that writes code follows these, in order of priority:

**SOLID, applied practically to Python (not academic dogma):**
- **Single Responsibility** — a function or class does one job. If you're
  describing it with "and," split it.
- **Open/Closed** — prefer adding a new function/branch over rewriting an
  existing one that already works and is tested.
- **Liskov Substitution** — if it walks like a `dict`-shaped node record, it
  should behave like one everywhere; don't special-case callers.
- **Interface Segregation** — small, focused function signatures over one
  function that takes a dozen optional flags.
- **Dependency Inversion** — the API call (`agents.py`) should be swappable
  without touching the business logic in `utils.py`, and vice versa.

**Python-specific standards:**
- PEP 8 formatting; type hints on all new function signatures.
- Docstrings on every public function (one-line summary minimum).
- No bare `except:` — catch specific exceptions.
- Prefer pure functions where possible; isolate side effects (file I/O, API
  calls) at the edges, matching the existing `utils.py` / `agents.py` split.
- Every new function that has meaningful logic gets a corresponding test.

## 3. Agent roster (v1)

Four specialized workers, coordinated by you and an orchestrating skill. Each
agent has a narrow job and stays in its lane — that separation is what makes
review possible.

| Agent | Job | Can write code? | Can run tests? |
|---|---|---|---|
| **Researcher** | Maps the relevant code before any work starts; reports what exists, what it touches, and what could break | No — read-only | No |
| **Builder** | Writes new code and refines existing code, following this file's coding baseline | Yes | No |
| **Edge-Case Writer** | Designs test cases, especially edge cases, for whatever the Builder just wrote or touched | Yes (tests only) | No |
| **Validator** | Runs the tests the Edge-Case Writer wrote, reports pass/fail and any gaps found — never fixes anything itself | No | Yes |
| **Scribe** | Writes the commit message, CHANGELOG.md entry, and GitHub PR description once validation passes — never fixes or merges anything itself | Docs only | No |

Planned additions once v1 is comfortable: **Branch Manager** (currently folded
into the orchestrator below) and **Refiner** (currently the Builder's second
job) can split out into their own agents without restructuring anything else.

## 4. Approval gates

You are learning the SDLC through this process, so checkpoints are
intentionally visible right now — not buried in a log you have to go dig for.

1. **Plan approval** — before the Builder writes anything, you see the
   Researcher's findings + a short plan, and approve or redirect it.
2. **Validator report review** — before anything is documented or merged,
   you see the Validator's pass/fail report and any flagged gaps.
3. **Commit, PR, and merge approval** — you see the Scribe's commit
   message, CHANGELOG entry, and PR description together, and approve all
   of it plus the merge in one step. Nothing gets pushed, opened as a PR,
   or merged into `main` without this.

Agents work freely *within* a branch between these checkpoints — you are not
asked before every file edit. As you get comfortable, checkpoint 1 can be
skipped for small, low-risk changes; checkpoints 2 and 3 stay mandatory
regardless of experience level, since they're the actual safety net.

## 5. Git workflow

- Never commit directly to `main`.
- One branch per unit of work, named `feature/<short-description>` or
  `fix/<short-description>`.
- The orchestrator (acting as branch manager for now) creates the branch,
  hands it to Builder → Edge-Case Writer → Validator → Scribe in sequence,
  then stops and waits for your approval.
- This repo mirrors a real team workflow: work happens on a branch, gets
  pushed to GitHub, and merges through an actual Pull Request — not a
  silent local merge. Requires GitHub CLI (`gh`) installed and
  authenticated.
- On approval: commit with Scribe's message, append the CHANGELOG entry,
  push the branch, open a real PR via `gh pr create` using Scribe's
  description, then merge the PR and sync local `main` (`git pull`).
- Re-run the full test suite against the synced `main` after merging to
  confirm nothing else broke (this is the "reconciliation" or
  *integration* step).
- Delete the feature branch, locally and remotely, after a successful
  merge.

## 6. Handoff format between agents

Each agent ends its turn with a short structured summary (what it did, what
it found, what it recommends next) rather than a wall of text — the next
agent, and you, should be able to scan it in a few seconds.

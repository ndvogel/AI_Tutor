# AI_Tutor — Adaptive Learning Engine

A closed-loop pedagogical system that decouples **Subject Matter Knowledge** from **Instructional Delivery**, using a four-stage continuous loop to deliver personalized, high-retention learning.

## Architecture Overview

See [`docs/MASTER_ARCHITECT_BLUEPRINT.md`](docs/MASTER_ARCHITECT_BLUEPRINT.md) for the full system design.

## Project Structure

```
AI_Tutor/
├── docs/
│   └── MASTER_ARCHITECT_BLUEPRINT.md   # Full system design spec
├── config/
│   ├── student_profile.json            # Learner identity & interests
│   └── learning_progress.json          # Node state & session tracking
├── src/
│   ├── __init__.py
│   ├── main.py                         # Entry point
│   ├── agents.py                       # Four sub-system agents
│   └── utils.py                        # Shared utilities
├── .env.example                        # Environment variable template
├── .gitignore
└── README.md
```

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/AI_Tutor.git
cd AI_Tutor

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run
python src/main.py
```

## Sub-Systems

| Agent | Role |
| :--- | :--- |
| Knowledge Architect | Deconstructs the target subject into a DAG of micro-lessons |
| Dynamic Profiler | Maintains persistent learner state and trait data |
| Contextual Anchor | Translates concepts using the learner's interests and generation |
| Evaluation Loop | Runs assessments, manages friction, and unlocks next nodes |

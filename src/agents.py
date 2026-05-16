# agents.py
# Sub-system agent definitions:
#   - KnowledgeArchitect  (Sub-System A)
#   - DynamicProfiler     (Sub-System B)
#   - ContextualAnchor    (Sub-System C)
#   - EvaluationLoop      (Sub-System D)

import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

_KNOWLEDGE_ARCHITECT_SYSTEM = """
You are the Knowledge Architect sub-system of an Adaptive Learning Engine.

Your sole responsibility is to take a target subject and decompose it into an
ordered Directed Acyclic Graph (DAG) of micro-lessons. You focus strictly on
subject matter logic and prerequisite mapping — you are entirely independent of
the learner's identity, interests, or delivery style.

You MUST respond with ONLY a valid JSON array. No explanation, no markdown, no code fences.
Each object must have exactly these three fields:
  "node_id"       – snake_case string (e.g. "http_basics")
  "title"         – short descriptive lesson title
  "prerequisites" – array of node_id strings; empty array [] for the root node

Rules:
- Order nodes from foundational to advanced
- Every prerequisite node_id must appear earlier in the array
- Aim for 6–10 nodes
- Return raw JSON only — the output is passed directly to json.loads()
""".strip()


def generate_curriculum(profile_data: dict) -> list:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found. Check your .env file.")

    client = genai.Client(api_key=api_key)
    subject = profile_data.get("target_subject", "Unknown Subject")

    prompt = (
        f"Decompose the subject '{subject}' into an ordered DAG of micro-lessons. "
        "Return only the JSON array."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_KNOWLEDGE_ARCHITECT_SYSTEM,
        ),
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    nodes = json.loads(raw)

    for node in nodes:
        node["status"] = "unlocked" if not node.get("prerequisites") else "locked"

    return nodes

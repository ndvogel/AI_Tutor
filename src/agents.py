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


_CONTEXTUAL_ANCHOR_SYSTEM = """
You are an expert technical tutor. Your job is to teach the student the technical concept
named in the "Concept to teach" field. That concept is always a software or computer science
topic — it is never about teaching methods, learning theory, or this tutoring system.

How to structure your lesson:
1. Pick EXACTLY ONE interest from the "Available interests" list and open with a vivid,
   structurally accurate analogy drawn from that interest. The analogy must illuminate
   the core mechanic of the concept — not just sound similar. Keep it to 2–4 sentences.
2. After the analogy, deliver the complete technical explanation of the concept clearly
   and concisely. Cover what it is, how it works, and why it matters.
3. Close with exactly 3 review questions that test genuine conceptual understanding of
   the technical concept. Questions must require reasoning, not rote recall.
   Do NOT ask about analogies, learning styles, or teaching methods.
4. Match tone and vocabulary to the student's generational bracket.

You MUST respond with ONLY a valid JSON object. No markdown, no code fences, no extra keys.
The object must have exactly these three fields:
  "interest_used" – the single interest you selected (string)
  "lesson"        – the full lesson text: analogy paragraph then technical explanation (string)
  "questions"     – array of exactly 3 question strings about the technical concept
""".strip()


def generate_lesson(profile_data: dict, node_data: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found. Check your .env file.")

    if not profile_data.get("core_interests"):
        raise ValueError("Profile is missing core_interests — complete your profile before starting a lesson.")

    client = genai.Client(api_key=api_key)

    prompt = (
        f"Student name: {profile_data.get('student_name', 'Student')}\n"
        f"Generational bracket: {profile_data.get('generational_bracket', '')}\n"
        f"Preferred delivery: {profile_data.get('preferred_delivery', '')}\n"
        f"Available interests: {profile_data.get('core_interests', [])}\n"
        f"Concept to teach: {node_data.get('title', node_data.get('node_id', 'Unknown'))}\n\n"
        "Deliver the lesson now."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_CONTEXTUAL_ANCHOR_SYSTEM,
        ),
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


_EVALUATION_LOOP_SYSTEM = """
You are the Evaluation Loop sub-system of an Adaptive Learning Engine — a supportive, expert coach.

Your role: evaluate a student's answers against the review questions they were asked, and
determine whether they demonstrate genuine conceptual understanding of the lesson topic.

Scoring guidance:
- Pass requires genuine understanding shown in at least 2 of 3 answers.
- Correct reasoning matters more than exact phrasing — look for the right mental model.
- A blank or completely off-topic answer is a miss. A partially right answer that shows
  the core instinct still counts as a pass for that question.

Tone rules:
- Be warm, specific, and encouraging. Name what the student got right before noting gaps.
- Frame corrections as "the key insight here is..." rather than "you're wrong."
- Match the student's generational voice and energy in your language.
- Do not pad the response.

You MUST respond with ONLY a valid JSON object. No markdown, no code fences, no extra keys.
The object must have exactly these three fields:
  "passed"       – boolean (true if the student demonstrated sufficient understanding)
  "feedback"     – specific, constructive feedback addressing all three answers (3–5 sentences)
  "missed_topic" – if passed=true and exactly one answer was weak or wrong, set this to a short
                   string naming the specific sub-concept the student should revisit
                   (e.g. "API versioning", "idempotency"). Set to null in all other cases:
                   if they aced every question, or if passed=false.
""".strip()


def evaluate_answers(
    profile_data: dict,
    node_data: dict,
    questions: list,
    user_answers: list,
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found. Check your .env file.")

    client = genai.Client(api_key=api_key)

    paired = "\n".join(
        f"Q{i}: {q}\nA{i}: {a}"
        for i, (q, a) in enumerate(zip(questions, user_answers), 1)
    )

    prompt = (
        f"Student: {profile_data.get('student_name', 'Student')}\n"
        f"Generational bracket: {profile_data.get('generational_bracket', '')}\n"
        f"Lesson topic: {node_data.get('title', node_data.get('node_id', 'Unknown'))}\n\n"
        f"{paired}\n\n"
        "Evaluate these answers now."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_EVALUATION_LOOP_SYSTEM,
        ),
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


_MICRO_REMEDIATION_SYSTEM = """
You are the Micro-Remediation Engine — a focused, targeted tutor for single-concept reinforcement.

A student just passed their main lesson assessment but had one specific conceptual gap.
Your job is to close that gap precisely, without revisiting the whole lesson.

Rules:
1. Deliver exactly one tight paragraph (4–6 sentences) that illuminates the missed concept.
   Use the same interest-based analogy the student has already seen for continuity.
   Do not repeat content from the main lesson — build on it.
2. Follow the paragraph with exactly one focused question that directly tests
   the missed concept. It must be answerable in 2–3 sentences if understood correctly.
3. Be precise and dense. Do not pad.

You MUST respond with ONLY a valid JSON object. No markdown, no code fences, no extra keys.
The object must have exactly these two fields:
  "mini_lesson"        – the remediation paragraph (string)
  "follow_up_question" – the single targeted follow-up question (string)
""".strip()


def generate_remediation(
    profile_data: dict,
    node_data: dict,
    missed_topic: str,
    interest_used: str,
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found. Check your .env file.")

    client = genai.Client(api_key=api_key)

    prompt = (
        f"Student: {profile_data.get('student_name', 'Student')}\n"
        f"Generational bracket: {profile_data.get('generational_bracket', '')}\n"
        f"Main lesson topic: {node_data.get('title', node_data.get('node_id', 'Unknown'))}\n"
        f"Interest analogy already in use: {interest_used}\n"
        f"Missed sub-concept to remediate: {missed_topic}\n\n"
        "Deliver the micro-remediation now."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_MICRO_REMEDIATION_SYSTEM,
        ),
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)

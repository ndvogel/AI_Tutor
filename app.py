import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
from utils import (
    load_profile, load_progress, update_student_profile,
    save_node, unlock_dependents, save_remediation,
)
from agents import generate_lesson, evaluate_answers, generate_remediation

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Tutor",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global reset ── */
*, *::before, *::after { border-radius: 0 !important; box-shadow: none !important; }
html, body, [class*="css"] { font-family: 'Courier New', Courier, monospace; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #f0f0f0;
    border-right: 3px solid #000000;
    min-width: 280px;
}

/* ── Headings ── */
h1 { font-weight: 900 !important; font-size: 2rem !important; letter-spacing: -1px;
     text-transform: uppercase; border-bottom: 4px solid #000; padding-bottom: 0.4rem;
     margin-bottom: 0.5rem !important; }
h2, h3 { font-weight: 800 !important; font-size: 0.75rem !important;
          letter-spacing: 0.15em; text-transform: uppercase;
          border-bottom: 2px solid #000; padding-bottom: 0.2rem;
          margin-top: 1.25rem !important; margin-bottom: 0.5rem !important; color: #000; }
hr { border: none; border-top: 2px solid #000 !important; margin: 0.75rem 0; }

/* ── Buttons ── */
.stButton > button {
    background-color: #000 !important; color: #fff !important;
    border: 2px solid #000 !important; border-radius: 0 !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    letter-spacing: 0.08em !important; padding: 0.4rem 1.25rem !important;
    transition: background-color 0.08s, color 0.08s;
}
.stButton > button:hover { background-color: #F5C400 !important; color: #000 !important; }

/* ── Text inputs & text areas ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 2px solid #000 !important; border-radius: 0 !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.85rem !important; background: #fff !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #F5C400 !important; outline: none !important;
}

/* ── Status badges ── */
.badge { display: inline-block; padding: 1px 7px; font-size: 0.65rem; font-weight: 700;
         letter-spacing: 0.1em; text-transform: uppercase; white-space: nowrap;
         font-family: 'Courier New', Courier, monospace; border: 1px solid #000; }
.badge-locked            { background: #d6d6d6; color: #555; border-color: #aaa; }
.badge-unlocked          { background: #F5C400; color: #000; border-color: #000; }
.badge-mastered          { background: #000;    color: #fff; border-color: #000; }
.badge-conditionally_skipped { background: #ccc; color: #333; border-color: #888; }
.badge-force_locked      { background: #c00;    color: #fff; border-color: #800; }

/* ── Sidebar profile ── */
.profile-block { font-size: 0.82rem; line-height: 1.6; }
.field-label { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.15em;
               text-transform: uppercase; color: #777; display: block; margin-top: 0.5rem; }
.field-value { font-weight: 600; color: #000; }
.interest-tag { display: inline-block; border: 2px solid #000; padding: 1px 8px;
                margin: 2px 3px 2px 0; font-size: 0.75rem; font-weight: 700; background: #fff; }

/* ── Sidebar node rows ── */
.node-row { display: flex; align-items: center; justify-content: space-between;
            padding: 5px 0; border-bottom: 1px solid #ccc; gap: 6px; }
.node-title-text { font-size: 0.78rem; font-weight: 500; flex: 1; white-space: nowrap;
                   overflow: hidden; text-overflow: ellipsis;
                   font-family: 'Courier New', Courier, monospace; }

/* ── Dashboard panels ── */
.panel       { border: 2px solid #000; padding: 1.25rem 1.5rem; background: #fff; margin-bottom: 1rem; }
.panel-accent{ border: 3px solid #000; padding: 1.25rem 1.5rem; background: #F5C400; margin-bottom: 0.5rem; }
.panel-muted { border: 2px solid #ccc; padding: 1.25rem 1.5rem; background: #f7f7f7; margin-bottom: 1rem; }
.panel-label { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.15em;
               text-transform: uppercase; color: #555; margin-bottom: 0.35rem; }
.panel-title { font-size: 1.6rem; font-weight: 900; letter-spacing: -0.5px;
               margin: 0.1rem 0 0.3rem; line-height: 1.2; }
.panel-sub   { font-size: 0.78rem; color: #333; margin: 0; }
.stat-number { font-size: 2rem; font-weight: 900; line-height: 1; }
.stat-label  { font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: #555; }

/* ── Lesson stage ── */
.lesson-box {
    border: 3px solid #000; padding: 1.5rem 1.75rem;
    background: #fff; margin-bottom: 1.25rem;
}
.lesson-text { font-size: 0.95rem; line-height: 1.75; color: #111; margin-top: 0.75rem; }

/* ── Assessment stage ── */
.question-block {
    border-left: 4px solid #000; padding: 0.6rem 1rem;
    background: #f9f9f9; margin-bottom: 0.4rem; font-size: 0.9rem; font-weight: 500;
}
.q-num {
    display: inline-block; background: #000; color: #fff;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    padding: 1px 6px; margin-right: 0.5rem;
}

/* ── Feedback panels ── */
.feedback-panel { border: 2px solid #000; padding: 1.25rem 1.5rem; margin-bottom: 1rem; font-size: 0.9rem; line-height: 1.65; }
.feedback-pass  { background: #e8f5e8; border-color: #2d6a2d; }
.feedback-fail  { background: #fff8e8; border-color: #a07000; }
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("active_node", None)
ss.setdefault("ui_stage", None)
ss.setdefault("edit_profile", False)


# ── Data (fresh every re-run) ──────────────────────────────────────────────────
try:
    profile = load_profile()
except FileNotFoundError:
    profile = {}

try:
    progress = load_progress()
except FileNotFoundError:
    progress = {"nodes": {}}

nodes = progress.get("nodes", {})


# ── Helpers ────────────────────────────────────────────────────────────────────
_STATUS_LABELS = {
    "locked":                "○ Locked",
    "unlocked":              "→ Unlocked",
    "mastered":              "✓ Mastered",
    "conditionally_skipped": "~ Skipped",
    "force_locked":          "✗ Locked",
}

def _badge(status: str) -> str:
    label = _STATUS_LABELS.get(status, status.upper())
    return f'<span class="badge badge-{status}">{label}</span>'

def _reset():
    for k in ["active_node", "ui_stage", "lesson_result",
              "evaluation_result", "remediation_result", "newly_unlocked"]:
        ss.pop(k, None)
    ss.edit_profile = False


# ── Sidebar (always rendered) ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ◈ AI TUTOR")
    st.markdown("### Student")

    name       = profile.get("student_name")        or "—"
    subject    = profile.get("target_subject")      or "—"
    generation = profile.get("generational_bracket") or "—"
    delivery   = profile.get("preferred_delivery")  or "—"
    interests  = profile.get("core_interests", [])

    st.markdown(f"""
    <div class="profile-block">
        <span class="field-label">Name</span><span class="field-value">{name}</span>
        <span class="field-label">Subject</span><span class="field-value">{subject}</span>
        <span class="field-label">Persona</span><span class="field-value">{generation}</span>
        <span class="field-label">Style</span><span class="field-value">{delivery}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Interests")
    if interests:
        st.markdown(
            "".join(f'<span class="interest-tag">{i}</span>' for i in interests),
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<span style="font-size:0.78rem;color:#999;">No interests set.</span>',
                    unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Edit Profile", key="btn_edit_profile"):
        ss.edit_profile = not ss.edit_profile
        st.rerun()

    st.markdown("### Curriculum")
    if not nodes:
        st.markdown('<span style="font-size:0.78rem;color:#999;">No curriculum loaded.</span>',
                    unsafe_allow_html=True)
    else:
        rows = ""
        for node in nodes.values():
            title  = node.get("title", node["node_id"])
            status = node.get("status", "locked")
            rows  += f"""<div class="node-row">
                <span class="node-title-text" title="{title}">{title}</span>
                {_badge(status)}</div>"""
        st.markdown(rows, unsafe_allow_html=True)


# ── Main area ─────────────────────────────────────────────────────────────────

# ── 1. Edit Profile ────────────────────────────────────────────────────────────
_GENERATIONAL_OPTIONS = [
    "Gen Z (born 1997–2012)",
    "Millennial (born 1981–1996)",
    "Gen X / Millennial Crossover (born ~1978–1985)",
    "Gen X (born 1965–1980)",
    "Boomer (born 1946–1964)",
]
_DELIVERY_OPTIONS = [
    "Interactive Dialog",
    "Lecture Style",
    "Socratic Method",
    "Example-Driven",
]

if ss.edit_profile:
    st.markdown("# Edit Profile")

    current_gen      = profile.get("generational_bracket", "")
    current_delivery = profile.get("preferred_delivery", "")

    gen_index = _GENERATIONAL_OPTIONS.index(current_gen) if current_gen in _GENERATIONAL_OPTIONS else 0
    del_index = _DELIVERY_OPTIONS.index(current_delivery) if current_delivery in _DELIVERY_OPTIONS else 0

    with st.form("profile_form"):
        new_name = st.text_input("Name", value=profile.get("student_name", ""))
        new_subject = st.text_input("Target Subject", value=profile.get("target_subject", ""))
        new_generation = st.selectbox(
            "Generational Bracket",
            options=_GENERATIONAL_OPTIONS,
            index=gen_index,
        )
        new_delivery = st.selectbox(
            "Preferred Delivery Style",
            options=_DELIVERY_OPTIONS,
            index=del_index,
        )
        new_interests_raw = st.text_input(
            "Core Interests — comma-separated, max 5",
            value=", ".join(profile.get("core_interests", [])),
        )
        col_s, col_c, _ = st.columns([1, 1, 4])
        with col_s:
            submitted = st.form_submit_button("Save Changes")
        with col_c:
            cancelled = st.form_submit_button("Cancel")

    if submitted:
        interests_parsed = [i.strip() for i in new_interests_raw.split(",") if i.strip()][:5]
        update_student_profile({
            "student_name":         new_name.strip(),
            "target_subject":       new_subject.strip(),
            "generational_bracket": new_generation,
            "preferred_delivery":   new_delivery,
            "core_interests":       interests_parsed,
        })
        ss.edit_profile = False
        st.rerun()

    if cancelled:
        ss.edit_profile = False
        st.rerun()


# ── 2. Lesson Presentation ─────────────────────────────────────────────────────
elif ss.ui_stage == "presentation":
    node_id   = ss.active_node
    node_data = nodes.get(node_id, {})

    st.markdown(f"# {node_data.get('title', node_id)}")

    if "lesson_result" not in ss:
        try:
            with st.spinner("Generating your personalised lesson — please wait…"):
                ss.lesson_result = generate_lesson(profile, node_data)
        except ValueError as e:
            st.error(f"Profile incomplete: {e}")
            if st.button("← Go to Edit Profile"):
                ss.edit_profile = True
                _reset()
                st.rerun()
            st.stop()
        st.rerun()

    lr = ss.lesson_result
    lesson_html = lr["lesson"].replace("\n", "<br/>")

    st.markdown(f"""
    <div class="lesson-box">
        <div class="panel-label">Lesson · Interest anchor: {lr.get("interest_used", "—")}</div>
        <div class="lesson-text">{lesson_html}</div>
    </div>""", unsafe_allow_html=True)

    if st.button("Proceed to Assessment →"):
        ss.ui_stage = "assessment"
        st.rerun()


# ── 3. Assessment ──────────────────────────────────────────────────────────────
elif ss.ui_stage == "assessment":
    node_id   = ss.active_node
    node_data = nodes.get(node_id, {})
    questions = ss.get("lesson_result", {}).get("questions", [])

    st.markdown(f"# Assessment · {node_data.get('title', node_id)}")

    prior_eval = ss.get("evaluation_result")
    if prior_eval and not prior_eval["passed"]:
        st.markdown(f"""
        <div class="feedback-panel feedback-fail">
            <div class="panel-label">Previous Attempt · Coach Feedback</div>
            {prior_eval["feedback"]}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="panel-label" style="margin-bottom:0.6rem">Answer each question, then submit.</div>',
                unsafe_allow_html=True)

    answers = []
    for i, q in enumerate(questions):
        st.markdown(f"""
        <div class="question-block">
            <span class="q-num">Q{i + 1}</span>{q}
        </div>""", unsafe_allow_html=True)
        ans = st.text_area(
            label=f"Answer {i + 1}",
            key=f"answer_{i}",
            label_visibility="collapsed",
            height=85,
            placeholder="Your answer…",
        )
        answers.append(ans)

    st.markdown("")
    if st.button("Submit Answers →"):
        with st.spinner("Evaluating your answers…"):
            result = evaluate_answers(profile, node_data, questions, answers)
        ss.evaluation_result = result

        if result["passed"]:
            node_data["status"]             = "mastered"
            node_data["consecutive_failures"] = 0
            node_data["attempts"]           = node_data.get("attempts", 0) + 1
            node_data["active_interest_used"] = ss.get("lesson_result", {}).get("interest_used")
            save_node(node_id, node_data)
            ss.newly_unlocked = unlock_dependents(node_id)
            ss.ui_stage = "remediation" if result.get("missed_topic") else "result"
        else:
            node_data["attempts"]           = node_data.get("attempts", 0) + 1
            node_data["consecutive_failures"] = node_data.get("consecutive_failures", 0) + 1
            save_node(node_id, node_data)

        st.rerun()


# ── 4. Result (clean pass, no missed topic) ────────────────────────────────────
elif ss.ui_stage == "result":
    node_id        = ss.active_node
    node_data      = nodes.get(node_id, {})
    evaluation     = ss.get("evaluation_result", {})
    newly_unlocked = ss.get("newly_unlocked", [])

    st.markdown(f"# ✓ Passed: {node_data.get('title', node_id)}")

    st.markdown(f"""
    <div class="feedback-panel feedback-pass">
        <div class="panel-label">Coach Feedback</div>
        {evaluation.get("feedback", "")}
    </div>""", unsafe_allow_html=True)

    if newly_unlocked:
        items = "".join(
            f"<li>{nodes.get(nid, {}).get('title', nid)}</li>"
            for nid in newly_unlocked
        )
        st.markdown(f"""
        <div class="panel">
            <div class="panel-label">Next Lessons Unlocked</div>
            <ul style="margin:0.3rem 0 0 1rem;font-size:0.9rem;line-height:1.9">{items}</ul>
        </div>""", unsafe_allow_html=True)

    if st.button("← Return to Dashboard"):
        _reset()
        st.rerun()


# ── 5. Remediation (pass + one missed sub-topic) ───────────────────────────────
elif ss.ui_stage == "remediation":
    node_id        = ss.active_node
    node_data      = nodes.get(node_id, {})
    evaluation     = ss.get("evaluation_result", {})
    missed_topic   = evaluation.get("missed_topic", "")
    interest_used  = ss.get("lesson_result", {}).get("interest_used", "")
    newly_unlocked = ss.get("newly_unlocked", [])

    st.markdown(f"# ✓ Passed · Quick Deep-Dive: {missed_topic}")

    st.markdown(f"""
    <div class="feedback-panel feedback-pass">
        <div class="panel-label">Coach Feedback (Assessment)</div>
        {evaluation.get("feedback", "")}
    </div>""", unsafe_allow_html=True)

    if "remediation_result" not in ss:
        with st.spinner(f"Generating focused deep-dive on '{missed_topic}'…"):
            ss.remediation_result = generate_remediation(
                profile, node_data, missed_topic, interest_used
            )
        st.rerun()

    rr = ss.remediation_result
    mini_html = rr["mini_lesson"].replace("\n", "<br/>")

    st.markdown(f"""
    <div class="lesson-box">
        <div class="panel-label">Micro-Lesson · {missed_topic}</div>
        <div class="lesson-text">{mini_html}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="question-block" style="margin-bottom:0.75rem">
        <span class="q-num">Q</span>{rr["follow_up_question"]}
    </div>""", unsafe_allow_html=True)

    rem_answer = st.text_area(
        "Your answer",
        key="remediation_answer",
        label_visibility="collapsed",
        height=100,
        placeholder="Your answer…",
    )

    if newly_unlocked:
        items = "".join(
            f"<li>{nodes.get(nid, {}).get('title', nid)}</li>"
            for nid in newly_unlocked
        )
        st.markdown(f"""
        <div class="panel">
            <div class="panel-label">Next Lessons Unlocked</div>
            <ul style="margin:0.3rem 0 0 1rem;font-size:0.9rem;line-height:1.9">{items}</ul>
        </div>""", unsafe_allow_html=True)

    col_submit, col_skip, _ = st.columns([1, 1, 4])
    with col_submit:
        if st.button("Submit & Finish"):
            save_remediation(node_id, {
                "topic":               missed_topic,
                "mini_lesson":         rr["mini_lesson"],
                "follow_up_question":  rr["follow_up_question"],
                "user_answer":         rem_answer,
                "status":              "completed",
                "attempts":            1,
            })
            _reset()
            st.rerun()
    with col_skip:
        if st.button("Skip Deep-Dive →"):
            save_remediation(node_id, {
                "topic":    missed_topic,
                "status":   "skipped",
                "attempts": 0,
            })
            _reset()
            st.rerun()


# ── 6. Dashboard (default) ─────────────────────────────────────────────────────
else:
    st.markdown("# Active Learning Hub")

    unlocked_nodes = [n for n in nodes.values() if n.get("status") == "unlocked"]
    mastered_nodes = [n for n in nodes.values() if n.get("status") == "mastered"]
    total          = len(nodes)

    col_main, col_stats = st.columns([3, 1], gap="medium")

    with col_main:
        if not nodes:
            st.markdown("""
            <div class="panel-muted">
                <div class="panel-label">Status</div>
                No curriculum found. Run onboarding from the terminal
                (<code>python src/main.py</code>) to generate your learning path.
            </div>""", unsafe_allow_html=True)

        elif unlocked_nodes:
            st.markdown(
                f'<div class="panel-label" style="margin-bottom:0.75rem">'
                f'{len(unlocked_nodes)} lesson(s) ready · '
                f'{len(mastered_nodes)} of {total} mastered</div>',
                unsafe_allow_html=True,
            )
            for node in unlocked_nodes:
                st.markdown(f"""
                <div class="panel-accent">
                    <div class="panel-label">Unlocked</div>
                    <div class="panel-title">{node["title"]}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Launch Lesson →", key=f"launch_{node['node_id']}"):
                    ss.active_node = node["node_id"]
                    ss.ui_stage    = "presentation"
                    for k in ["lesson_result", "evaluation_result", "remediation_result"]:
                        ss.pop(k, None)
                    st.rerun()

        elif total and all(n.get("status") == "mastered" for n in nodes.values()):
            st.markdown("""
            <div class="panel">
                <div class="panel-label">Status</div>
                <div class="panel-title">Curriculum Complete.</div>
                <div class="panel-sub">All nodes mastered. Well done.</div>
            </div>""", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="panel-muted">
                <div class="panel-label">Status</div>
                No lessons currently unlocked.
                Complete prerequisites to advance to the next node.
            </div>""", unsafe_allow_html=True)

    with col_stats:
        if total:
            n_unlocked = len(unlocked_nodes)
            n_locked   = sum(1 for n in nodes.values() if n.get("status") == "locked")
            n_mastered = len(mastered_nodes)

            st.markdown(f"""
            <div class="panel">
                <div class="panel-label">Progress</div>
                <div class="stat-number">{n_mastered}<span style="font-size:1rem;font-weight:400"> / {total}</span></div>
                <div class="stat-label">nodes mastered</div>
                <hr style="border-top:2px solid #000;margin:0.6rem 0"/>
                <div style="font-size:0.78rem;line-height:1.9">
                    {_badge("unlocked")} &nbsp;{n_unlocked}<br/>
                    {_badge("locked")}   &nbsp;{n_locked}<br/>
                    {_badge("mastered")} &nbsp;{n_mastered}
                </div>
            </div>""", unsafe_allow_html=True)

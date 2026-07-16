# main.py
# Entry point for the AI_Tutor Adaptive Learning Engine.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import initialize_storage, load_profile, save_profile, save_node, load_progress, unlock_dependents, save_remediation, update_student_profile
from agents import generate_curriculum, generate_lesson, evaluate_answers, generate_remediation

GENERATIONAL_OPTIONS = [
    "Gen Z (born 1997–2012)",
    "Millennial (born 1981–1996)",
    "Gen X / Millennial Crossover (born ~1978–1985)",
    "Gen X (born 1965–1980)",
    "Boomer (born 1946–1964)",
]

DELIVERY_OPTIONS = [
    "Interactive Dialog",
    "Lecture Style",
    "Socratic Method",
    "Example-Driven",
]


def _prompt_choice(prompt: str, options: list) -> str:
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("Enter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  Please enter a number between 1 and {len(options)}.")


def run_onboarding() -> None:
    print("\n=== AI Tutor — Student Onboarding ===\n")

    name = input("What's your name? ").strip()
    while not name:
        print("  Name cannot be empty.")
        name = input("What's your name? ").strip()

    subject = input("What subject do you want to master? ").strip()
    while not subject:
        print("  Subject cannot be empty.")
        subject = input("What do you want to master? ").strip()

    generation = _prompt_choice(
        "Which generational bracket fits you best?", GENERATIONAL_OPTIONS
    )

    delivery = _prompt_choice(
        "What's your preferred learning style?", DELIVERY_OPTIONS
    )

    print("\nEnter up to 5 core interests (press Enter with no input to stop):")
    interests = []
    while len(interests) < 5:
        entry = input(f"  Interest {len(interests) + 1}: ").strip()
        if not entry:
            if not interests:
                print("  Please enter at least one interest.")
                continue
            break
        interests.append(entry)

    profile = load_profile()
    profile["student_name"] = name
    profile["target_subject"] = subject
    profile["generational_bracket"] = generation
    profile["preferred_delivery"] = delivery
    profile["core_interests"] = interests
    save_profile(profile)

    print(f"\nProfile saved. Welcome, {name}!")
    print(f"  Subject   : {subject}")
    print(f"  Generation: {generation}")
    print(f"  Delivery  : {delivery}")
    print(f"  Interests : {', '.join(interests)}")


def run_curriculum_generation() -> None:
    profile = load_profile()
    print("\nGenerating curriculum — please wait...")
    nodes = generate_curriculum(profile)
    for node in nodes:
        save_node(node["node_id"], node)
    print(f"Curriculum saved: {len(nodes)} nodes written to learning_progress.json")
    for node in nodes:
        prereqs = ", ".join(node["prerequisites"]) or "none"
        print(f"  [{node['status']:8}] {node['node_id']} — {node['title']} (prereqs: {prereqs})")


def change_profile_context() -> None:
    while True:
        profile = load_profile()
        print("\n=== Update Profile Context ===")
        print(f"  Delivery style : {profile.get('preferred_delivery', '(none)')}")
        interests = profile.get("core_interests", [])
        print(f"  Interests ({len(interests)}/5): {', '.join(interests) or '(none)'}")

        action = _prompt_choice(
            "What would you like to update?",
            ["Change delivery style", "Add an interest", "Remove an interest", "Back"],
        )

        if action == "Back":
            break

        elif action == "Change delivery style":
            new_delivery = _prompt_choice("Choose your new delivery style:", DELIVERY_OPTIONS)
            updated = update_student_profile({"preferred_delivery": new_delivery})
            print(f"  Saved. Delivery style is now: {updated['preferred_delivery']}")

        elif action == "Add an interest":
            if len(interests) >= 5:
                print("  You already have 5 interests (the maximum). Remove one first.")
            else:
                entry = input("  New interest: ").strip()
                if not entry:
                    print("  Nothing entered — no change made.")
                elif entry in interests:
                    print(f"  '{entry}' is already in your interests.")
                else:
                    updated = update_student_profile({"core_interests": interests + [entry]})
                    print(f"  Saved. Interests: {', '.join(updated['core_interests'])}")

        elif action == "Remove an interest":
            if not interests:
                print("  No interests to remove.")
            else:
                to_remove = _prompt_choice("Which interest to remove?", interests)
                updated_interests = [i for i in interests if i != to_remove]
                updated = update_student_profile({"core_interests": updated_interests})
                remaining = ", ".join(updated["core_interests"]) or "(none)"
                print(f"  '{to_remove}' removed. Remaining: {remaining}")


def run_remediation(node_id: str, node_data: dict, missed_topic: str, interest_used: str) -> None:
    profile = load_profile()
    print(f"\n--- Micro-Remediation: {missed_topic} ---")
    print("Generating focused deep-dive — please wait...")
    result = generate_remediation(profile, node_data, missed_topic, interest_used)

    print(f"\n{result['mini_lesson']}")
    print(f"\nFollow-up question: {result['follow_up_question']}")
    answer = input("\nYour answer: ").strip()

    save_remediation(node_id, {
        "topic": missed_topic,
        "mini_lesson": result["mini_lesson"],
        "follow_up_question": result["follow_up_question"],
        "user_answer": answer,
        "status": "completed",
        "attempts": 1,
    })
    print("\nLogged. Your mastered status is unchanged — that gap is now on record for future review.")


def run_lesson(node_id: str) -> None:
    profile = load_profile()
    progress = load_progress()

    node_data = progress["nodes"].get(node_id)
    if not node_data:
        print(f"Node '{node_id}' not found in learning_progress.json.")
        return
    if node_data["status"] != "unlocked":
        print(f"Node '{node_id}' is {node_data['status']} — prerequisites not yet met.")
        return

    print(f"\nGenerating lesson for: {node_data['title']} — please wait...")
    result = generate_lesson(profile, node_data)

    print("\n" + "=" * 60)
    print(f"  LESSON: {node_data['title']}")
    print("=" * 60)
    print(result["lesson"])

    questions = result["questions"]
    print("\n--- Review Questions ---")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print("-" * 60)

    print("\nAnswer each question below. Press Enter to submit.\n")
    user_answers = []
    for i, q in enumerate(questions, 1):
        print(f"  Q{i}: {q}")
        answer = input("  Your answer: ").strip()
        user_answers.append(answer)
        print()

    print("Evaluating your answers — please wait...")
    evaluation = evaluate_answers(profile, node_data, questions, user_answers)

    print("\n--- Coach Feedback ---")
    print(evaluation["feedback"])

    node_data["active_interest_used"] = result.get("interest_used")
    node_data["attempts"] = node_data.get("attempts", 0) + 1

    if evaluation["passed"]:
        node_data["status"] = "mastered"
        node_data["consecutive_failures"] = 0
        save_node(node_id, node_data)
        newly_unlocked = unlock_dependents(node_id)
        print(f"\nPASSED — '{node_data['title']}' marked as mastered.")
        if newly_unlocked:
            for nid in newly_unlocked:
                next_title = load_progress()["nodes"][nid]["title"]
                print(f"  Next lesson unlocked: {next_title} ({nid})")
        else:
            print("  No further nodes to unlock.")

        missed_topic = evaluation.get("missed_topic")
        if missed_topic:
            print(f"\n  One gap spotted: '{missed_topic}'.")
            choice = input("  Take a quick 2-minute deep-dive on that? (y/n): ").strip().lower()
            if choice == "y":
                run_remediation(node_id, node_data, missed_topic, result.get("interest_used", ""))
            else:
                save_remediation(node_id, {
                    "topic": missed_topic,
                    "status": "skipped",
                    "attempts": 0,
                })
                print("  Skipped — logged for future reference.")
    else:
        node_data["consecutive_failures"] = node_data.get("consecutive_failures", 0) + 1
        save_node(node_id, node_data)
        print(f"\nNot quite yet — node stays unlocked. Give it another shot!")
        print(f"  Attempts: {node_data['attempts']}  |  Consecutive misses: {node_data['consecutive_failures']}")


def view_progress() -> None:
    """Prints every curriculum node's title and status from learning_progress.json."""
    progress = load_progress()
    nodes = progress["nodes"]
    if not nodes:
        print("No curriculum nodes found. Run option 1 first.")
        return
    print("\n=== Curriculum Progress ===")
    for node_id, node in nodes.items():
        title = node.get("title", "Unknown Concept")
        status = node.get("status", "unknown")
        print(f"  [{status:8}] {node_id} — {title}")


if __name__ == "__main__":
    initialize_storage()

    print("\n=== AI Tutor — Dev Menu ===")
    print("  1. Onboarding + Curriculum Generation")
    print("  2. Run Lesson  (first unlocked node)")
    print("  3. Update Profile Context")
    print("  4. View Progress")
    choice = input("Select option: ").strip()

    if choice == "1":
        run_onboarding()
        run_curriculum_generation()
    elif choice == "2":
        progress = load_progress()
        unlocked = [
            nid for nid, n in progress["nodes"].items() if n["status"] == "unlocked"
        ]
        if not unlocked:
            print("No unlocked nodes found. Run option 1 first.")
        else:
            run_lesson(unlocked[0])
    elif choice == "3":
        change_profile_context()
    elif choice == "4":
        view_progress()
    else:
        print("Invalid choice.")

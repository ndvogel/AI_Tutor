# main.py
# Entry point for the AI_Tutor Adaptive Learning Engine.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import initialize_storage, load_profile, save_profile, save_node
from agents import generate_curriculum

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


if __name__ == "__main__":
    initialize_storage()
    run_onboarding()
    run_curriculum_generation()

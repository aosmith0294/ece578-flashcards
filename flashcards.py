import json
import random
from pathlib import Path
from typing import List, Dict, Any


def load_cards_from_json(path: str = "Questions/flashcards.json") -> List[Dict[str, Any]]:
    """Load parsed multiple-choice questions from JSON."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {file_path.resolve()}")

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("flashcards.json must contain a list of questions")

    cards = []
    for idx, raw in enumerate(data, start=1):
        question = raw.get("question", "").strip()
        choices = raw.get("choices") or []
        correct_letter = (raw.get("correct_letter") or "").lower() or None

        if not question or not choices:
            print(f"Skipping malformed card #{idx} (missing question or choices)")
            continue

        # Normalize choices (letters + text)
        norm_choices = []
        for ch in choices:
            letter = (ch.get("letter") or "").lower()
            text = (ch.get("text") or "").strip()
            if not letter or not text:
                continue
            norm_choices.append({"letter": letter, "text": text})

        if not norm_choices:
            print(f"Skipping card #{idx} (no valid choices)")
            continue

        # Map correct letter to index if possible
        letter_to_index = {c["letter"]: i for i, c in enumerate(norm_choices)}
        correct_index = letter_to_index.get(correct_letter) if correct_letter else None

        card = {
            "id": raw.get("id"),
            "source_file": raw.get("source_file"),
            "question": question,
            "choices": norm_choices,
            "correct_letter": correct_letter,
            "correct_index": correct_index,
        }
        cards.append(card)

    if not cards:
        raise ValueError("No valid cards loaded from JSON.")

    print(f"Loaded {len(cards)} cards from {file_path.name}")
    return cards


def run_flashcards(cards: List[Dict[str, Any]]) -> None:
    """Main flashcard / quiz loop."""

    # Randomize order of cards once per session
    random.shuffle(cards)

    total = len(cards)
    seen = 0
    answered = 0
    correct = 0

    print("\nFlashcard session started.")
    print("For each question:")
    print("  - Type a letter (a/b/c/...) to answer")
    print("  - Or just press Enter to reveal without answering")
    print("  - Type 'q' to quit\n")

    for i, card in enumerate(cards, start=1):
        print("=" * 70)
        print(f"Question {i}/{total}")  # <-- This stays sequential, but cards are random
        print(card["question"])
        print()

        for ch in card["choices"]:
            print(f"  {ch['letter']}) {ch['text']}")

        user_input = input("\nYour answer (letter, Enter to skip, 'q' to quit): ").strip().lower()

        if user_input == "q":
            break

        seen += 1

        correct_letter = card.get("correct_letter")
        correct_index = card.get("correct_index")
        correct_choice_text = None
        if correct_index is not None:
            correct_choice_text = card["choices"][correct_index]["text"]

        valid_letters = {c["letter"] for c in card["choices"]}

        if user_input in valid_letters:
            answered += 1
            if correct_letter and user_input == correct_letter:
                correct += 1
                print("\n✅ Correct!")
            else:
                print("\n❌ Incorrect.")
        else:
            if user_input:
                print("\n(Invalid input — showing answer)")

        print("\nCorrect answer:")
        print(f"  {correct_letter}) {correct_choice_text}")

        input("\n[Enter] to continue...")

    # Summary
    print("\nSession summary:")
    print(f"  Questions seen:    {seen}")
    print(f"  Questions answered:{answered}")
    print(f"  Correct answers:   {correct}")
    if answered > 0:
        pct = correct / answered * 100
        print(f"  Score:             {correct}/{answered} ({pct:.1f}%)")
    print("Done.\n")


def main():
    # If you want to prompt for path instead, uncomment these two lines:
    # json_path = input("Enter path to flashcards.json (or press Enter for default): ").strip() or "flashcards.json"
    # cards = load_cards_from_json(json_path)

    cards = load_cards_from_json()
    run_flashcards(cards)


if __name__ == "__main__":
    main()

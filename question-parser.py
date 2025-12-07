import json
import re
from pathlib import Path
from typing import List, Dict, Any


QUESTION_RE = re.compile(r"^(\d+)\.\s*(.*)$")
CHOICE_RE = re.compile(r"^(\*?)([a-zA-Z])\.\s*(.*)$")


def parse_question_file(path: Path) -> List[Dict[str, Any]]:
    """
    Parse a single text file of questions in the format:

    1. Question text ...
    a. option
    *b. correct option
    c. ...

    Returns a list of question dicts.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="cp1252")
    lines = [ln.rstrip("\n") for ln in text.splitlines()]

    questions = []
    current = None  # current question dict
    last_type = None  # "question" or "choice"

    for line in lines:
        stripped = line.strip()

        # Skip totally blank lines
        if not stripped:
            continue

        # New question?
        m_q = QUESTION_RE.match(stripped)
        if m_q:
            # Finalize previous question
            if current is not None:
                questions.append(current)

            q_number = m_q.group(1)
            q_text = m_q.group(2).strip()

            current = {
                "id": f"{path.stem}_{q_number}",
                "source_file": path.name,
                "question": q_text,
                "choices": [],
                "correct_letter": None,
                "correct_index": None,
            }
            last_type = "question"
            continue

        # New choice (answer option)?
        m_c = CHOICE_RE.match(stripped)
        if m_c and current is not None:
            star = m_c.group(1)
            letter = m_c.group(2).lower()
            text_part = m_c.group(3).strip()

            choice_index = len(current["choices"])
            current["choices"].append({
                "letter": letter,
                "text": text_part
            })

            if star == "*":
                current["correct_letter"] = letter
                current["correct_index"] = choice_index

            last_type = "choice"
            continue

        # If it's not a question or a choice, treat it as a continuation line
        if current is not None:
            if last_type == "question":
                # Continuation of question text
                current["question"] += " " + stripped
            elif last_type == "choice" and current["choices"]:
                # Continuation of last choice text
                current["choices"][-1]["text"] += " " + stripped

    # Finalize last question in file
    if current is not None:
        questions.append(current)

    # Basic sanity check: warn if any question has no marked answer
    for q in questions:
        if q["correct_index"] is None:
            print(f"WARNING: No correct answer marked in {path.name} for question id {q['id']}")

    return questions


def load_questions_from_directory(dir_path: Path) -> List[Dict[str, Any]]:
    """
    Iterate through all .txt files in the given directory and parse questions.
    """
    if not dir_path.exists() or not dir_path.is_dir():
        raise NotADirectoryError(f"{dir_path} is not a valid directory")

    all_questions: List[Dict[str, Any]] = []

    txt_files = sorted(dir_path.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {dir_path}")
        return all_questions

    print(f"Found {len(txt_files)} .txt files. Parsing...")

    for txt_file in txt_files:
        print(f"  Parsing {txt_file.name}...")
        file_questions = parse_question_file(txt_file)
        print(f"    -> {len(file_questions)} questions found")
        all_questions.extend(file_questions)

    print(f"Total questions loaded: {len(all_questions)}")
    return all_questions


def save_questions_to_json(questions: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Save all questions to a JSON file.
    """
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(questions)} questions to {output_path}")


def main():
    # 1) Prompt user for directory
    dir_input = input("Enter the directory path containing your question .txt files: ").strip()
    dir_path = Path(dir_input).expanduser().resolve()

    # 2) Load & parse all questions
    questions = load_questions_from_directory(dir_path)
    if not questions:
        print("No questions parsed. Exiting.")
        return

    # 3) Save to JSON
    output_path = dir_path / "flashcards.json"
    save_questions_to_json(questions, output_path)


if __name__ == "__main__":
    main()

VALID_CHOICES = ("A", "B", "C", "D")
MIN_EXPLANATION_LENGTH = 10

QUESTION_BANK = [
    {
        "id": "Q1",
        "question": (
            "Ticket T001 is open and unassigned. A user tries to move it "
            "to in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove ticket",
        },
        "correct": "B",
        "feedback": (
            "An unassigned open ticket cannot enter in_progress. The action "
            "is rejected and the ticket must stay exactly as it was."
        ),
    },
    {
        "id": "Q2",
        "question": "The app has zero tickets. What should resolution percentage display?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "correct": "C",
        "feedback": (
            "resolved / total would divide by zero, so an empty dataset is "
            "handled as a special case and reports 0%."
        ),
    },
    {
        "id": "Q3",
        "question": (
            "Filter title='wifi', category='Network', status='open'. "
            "Which records should match?"
        ),
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "correct": "B",
        "feedback": (
            "Filters combine with AND: a ticket must satisfy every supplied "
            "filter. OR would return unrelated tickets."
        ),
    },
    {
        "id": "Q4",
        "question": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "correct": "C",
        "feedback": (
            "Only open or in_progress tickets accept notes. A resolved ticket "
            "must be reopened first, and its earlier notes are kept."
        ),
    },
    {
        "id": "Q5",
        "question": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "correct": "C",
        "feedback": (
            "The whole file is validated first. If any record is invalid, the "
            "load is rejected and current memory is left untouched."
        ),
    },
    {
        "id": "Q6",
        "question": (
            "A PR changes validation but has no negative-case tests. "
            "Best review action?"
        ),
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "correct": "B",
        "feedback": (
            "Code that runs is not proof it rejects bad input. A good review "
            "asks for specific negative tests and the reasoning behind them."
        ),
    },
]


def normalize_choice(raw):
    """Return 'A'-'D' for valid input (any case, spaces ignored), else None."""
    if not isinstance(raw, str):
        return None
    choice = raw.strip().upper()
    return choice if choice in VALID_CHOICES else None


def score_answers(questions, answers):
    score = 0
    for question in questions:
        submitted = normalize_choice(answers.get(question["id"]))
        if submitted is not None and submitted == question["correct"]:
            score += 1
    return score


def is_valid_explanation(text):
    return isinstance(text, str) and len(text.strip()) >= MIN_EXPLANATION_LENGTH


def ask_question(question, input_fn=input, output_fn=print):
    output_fn("")
    output_fn(f"{question['id']}. {question['question']}")
    for letter in VALID_CHOICES:
        output_fn(f"  {letter}. {question['options'][letter]}")

    while True:
        choice = normalize_choice(input_fn("Your answer (A/B/C/D): "))
        if choice is not None:
            return choice
        output_fn("Invalid choice. Please enter A, B, C or D.")


def collect_explanations(questions, answers, count=2,
                         input_fn=input, output_fn=print):
    count = min(count, len(questions))
    ids = [question["id"] for question in questions]
    explanations = {}

    output_fn("")
    output_fn(f"Choose {count} questions and explain your answer in your own words.")

    while len(explanations) < count:
        raw = input_fn(f"Question number to explain (1-{len(questions)}): ").strip()
        if not raw.isdigit() or not 1 <= int(raw) <= len(questions):
            output_fn(f"Please enter a number from 1 to {len(questions)}.")
            continue

        question_id = ids[int(raw) - 1]
        if question_id in explanations:
            output_fn("You already explained that one. Choose a different question.")
            continue

        while True:
            text = input_fn(f"Why is your answer ({answers[question_id]}) for {question_id} correct? ")
            if is_valid_explanation(text):
                explanations[question_id] = text.strip()
                break
            output_fn(
                f"Please write at least {MIN_EXPLANATION_LENGTH} characters "
                "explaining your reasoning."
            )

    return explanations


def run_check(questions=None, input_fn=input, output_fn=print,
              explanation_count=2):
    if questions is None:
        questions = QUESTION_BANK

    output_fn("===== Engineering Understanding Check =====")
    answers = {}

    for question in questions:
        answers[question["id"]] = ask_question(question, input_fn, output_fn)
        if answers[question["id"]] == question["correct"]:
            output_fn("Correct.")
        else:
            output_fn(f"Not quite. The correct answer is {question['correct']}.")
        output_fn(question["feedback"])

    score = score_answers(questions, answers)
    output_fn("")
    output_fn(f"Final score: {score}/{len(questions)}")

    explanations = collect_explanations(
        questions, answers, explanation_count, input_fn, output_fn
    )
    output_fn("Explanations recorded for mentor discussion (not auto-graded).")

    return {
        "score": score,
        "total": len(questions),
        "answers": answers,
        "explanations": explanations,
    }


def save_explanations(path, engineer_label, result, questions=None):
    """Append a learner's score and explanations to a local notes file."""
    if questions is None:
        questions = QUESTION_BANK
    by_id = {question["id"]: question for question in questions}

    lines = [
        f"## {engineer_label}",
        f"Score: {result['score']}/{result['total']}",
        "",
    ]
    for question_id, text in result["explanations"].items():
        lines.append(f"### {question_id}: {by_id[question_id]['question']}")
        lines.append(f"Submitted answer: {result['answers'][question_id]}")
        lines.append(f"Explanation (not auto-graded): {text}")
        lines.append("")

    with open(path, "a", encoding="utf-8") as notes_file:
        notes_file.write("\n".join(lines) + "\n")
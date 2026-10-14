## Engineering Understanding Check.

# A six-question multiple-choice check about how CampusFlow behaves.
# The question bank (QUESTIONS) is kept separate from the scoring logic
# (score_answers) so that both can be tested independently, per the
# project guide.


# Question bank
QUESTIONS = [
    {
        "id": "Q1",
        "prompt": (
            "Ticket T001 is open and unassigned. A user tries to move it "
            "to in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept the change",
            "B": "Reject the change and preserve all data",
            "C": "Resolve the ticket automatically",
            "D": "Remove the ticket",
        },
        "correct": "B",
        "explanation": (
            "An unassigned ticket must not enter in_progress. The operation "
            "is rejected and the ticket collection is left unchanged."
        ),
    },
    {
        "id": "Q2",
        "prompt": "The app has zero tickets. What should resolution percentage display?",
        "options": {
            "A": "Crash with an error",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one with no explanation",
        },
        "correct": "C",
        "explanation": (
            "With no tickets there is nothing resolved, so the percentage is 0%. "
            "The code must guard against division by zero."
        ),
    },
    {
        "id": "Q3",
        "prompt": (
            "Filters: title='wifi', category='Network', status='open'. "
            "Which records should match?"
            ),
        "options": {
            "A": "Any record matching at least one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "correct": "B",
        "explanation": (
            "Supplied search filters combine with AND: a ticket must match "
            "every filter to be returned."
        ),
    },
    {
        "id": "Q4",
        "prompt": "A resolved ticket receives an 'Add note' request. What should happen?",
        "options": {
            "A": "Append the note anyway",
            "B": "Delete the old notes first",
            "C": "Reject until the ticket is reopened",
            "D": "Silently change the status",
        },
        "correct": "C",
        "explanation": (
            "Resolved tickets are locked. Notes can only be added while a "
            "ticket is open or in_progress. Reopen it first."
        ),
    },
    {
        "id": "Q5",
        "prompt": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both tickets",
            "B": "Replace memory with the duplicates",
            "C": "Reject the load and keep current memory unchanged",
            "D": "Rename the IDs silently",
        },
        "correct": "C",
        "explanation": (
            "Validation happens before memory is replaced. Duplicate IDs make "
            "the file unsafe, so the load is rejected and current data is kept."
        ),
    },
    {
        "id": "Q6",
        "prompt": (
            "A PR changes validation but has no negative-case tests. "
            "What is the best review action?"
        ),
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "correct": "B",
        "explanation": (
            "Validation changes need negative tests to prove invalid input is "
            "rejected. Requesting them is the reviewer's job."
        ),
    },
]

# Scoring logic
def score_answers(submitted, questions=QUESTIONS):
    #Score a list of submitted answers against the question bank.
    #submitted: list of strings, one per question, in the same order as
    # `questions`. Each entry should be "A", "B", "C" or "D".
    # Missing or unknown entries are treated as incorrect. 
    # Returns a tuple:
        # (score, per_question)
        # - score: int, number of correct answers (0..len(questions))
        # - per_question: list of dicts, one per question, each containing:
        #       id           -> the question id
        #       submitted    -> the letter the user gave (or None)
        #       correct      -> the correct letter
        #       is_correct   -> bool
        #       explanation  -> the question's explanation text
    score = 0
    per_question = []

    for index, question in enumerate(questions):
        # Safely fetch the submitted answer for this position
        submitted_letter = None
        if index < len(submitted):
            raw = submitted[index]
            if raw is not None:
                submitted_letter = str(raw).strip().upper()

        expected = question["correct"]
        is_correct = submitted_letter == expected

        if is_correct:
            score += 1

        per_question.append(
            {
                "id": question["id"],
                "submitted": submitted_letter,
                "correct": expected,
                "is_correct": is_correct,
                "explanation": question["explanation"],
            }
        )

    return score, per_question
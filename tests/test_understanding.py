import os
import tempfile
import unittest

from campusflow.understanding_check import (
    QUESTION_BANK,
    VALID_CHOICES,
    ask_question,
    collect_explanations,
    is_valid_explanation,
    normalize_choice,
    run_check,
    save_explanations,
    score_answers,
)

CORRECT_ANSWERS = {"Q1": "B", "Q2": "C", "Q3": "B", "Q4": "C", "Q5": "C", "Q6": "B"}
GOOD_EXPLANATION_1 = "Unassigned tickets are rejected so the dictionary stays unchanged."
GOOD_EXPLANATION_2 = "Duplicate IDs fail validation so memory is never replaced."


class ScriptedInput:
    def __init__(self, replies):
        self.replies = list(replies)

    def __call__(self, prompt=""):
        if not self.replies:
            raise AssertionError("The program asked for more input than the test supplied.")
        return self.replies.pop(0)


class OutputCollector:
    """Replaces print(): stores every line for assertions."""

    def __init__(self):
        self.lines = []

    def __call__(self, text=""):
        self.lines.append(text)

    def text(self):
        return "\n".join(self.lines)


def full_run_inputs(answer_letters, explanation_numbers=("1", "5")):
    """Build scripted input: six answers, then two (number, explanation) pairs."""
    return list(answer_letters) + [
        explanation_numbers[0], GOOD_EXPLANATION_1,
        explanation_numbers[1], GOOD_EXPLANATION_2,
    ]


class TestQuestionBank(unittest.TestCase):
    def test_bank_has_six_questions(self):
        self.assertEqual(len(QUESTION_BANK), 6)

    def test_every_question_is_well_formed(self):
        ids = [question["id"] for question in QUESTION_BANK]
        self.assertEqual(len(set(ids)), 6)
        for question in QUESTION_BANK:
            self.assertEqual(tuple(question["options"].keys()), VALID_CHOICES)
            self.assertIn(question["correct"], VALID_CHOICES)
            self.assertTrue(question["question"].strip())
            self.assertTrue(question["feedback"].strip())

    def test_bank_answers_match_business_rules(self):
        submitted = {q["id"]: q["correct"] for q in QUESTION_BANK}
        self.assertEqual(submitted, CORRECT_ANSWERS)


class TestScoring(unittest.TestCase):
    def test_all_correct_scores_six(self):
        self.assertEqual(score_answers(QUESTION_BANK, CORRECT_ANSWERS), 6)

    def test_all_wrong_scores_zero(self):
        wrong = {"Q1": "A", "Q2": "A", "Q3": "A", "Q4": "A", "Q5": "A", "Q6": "A"}
        self.assertEqual(score_answers(QUESTION_BANK, wrong), 0)

    def test_partial_score_counts_one_point_per_correct_answer(self):
        answers = dict(CORRECT_ANSWERS)
        answers["Q1"] = "A"
        answers["Q4"] = "D"
        self.assertEqual(score_answers(QUESTION_BANK, answers), 4)

    def test_missing_and_invalid_answers_earn_no_point(self):
        answers = {"Q1": "B", "Q2": "Z", "Q3": None}
        self.assertEqual(score_answers(QUESTION_BANK, answers), 1)

    def test_lowercase_answer_is_scored_correctly(self):
        self.assertEqual(score_answers(QUESTION_BANK, {"Q1": "b"}), 1)

    def test_scoring_works_with_a_different_question_bank(self):
        # Proves scoring is separate from the stored questions.
        custom_bank = [{"id": "X1", "correct": "D"}, {"id": "X2", "correct": "A"}]
        self.assertEqual(score_answers(custom_bank, {"X1": "D", "X2": "B"}), 1)

    def test_scoring_does_not_modify_answers(self):
        answers = dict(CORRECT_ANSWERS)
        score_answers(QUESTION_BANK, answers)
        self.assertEqual(answers, CORRECT_ANSWERS)


class TestNormalizeChoice(unittest.TestCase):
    def test_valid_choices_in_any_case(self):
        self.assertEqual(normalize_choice("a"), "A")
        self.assertEqual(normalize_choice(" D "), "D")

    def test_invalid_choices_return_none(self):
        for bad in ("E", "", "  ", "AB", "1", "yes", None, 3):
            self.assertIsNone(normalize_choice(bad), repr(bad))


class TestInvalidAnswersAreRejected(unittest.TestCase):
    """Acceptance case 14: invalid answer rejected, scoring correct."""

    def test_invalid_input_reprompts_until_valid(self):
        out = OutputCollector()
        fake_input = ScriptedInput(["E", "", "7", "AB", "c"])

        choice = ask_question(QUESTION_BANK[0], fake_input, out)

        self.assertEqual(choice, "C")
        self.assertEqual(fake_input.replies, [])  # all five replies were consumed
        self.assertEqual(out.text().count("Invalid choice"), 4)

    def test_invalid_answers_do_not_change_the_score(self):
        out = OutputCollector()
       
        inputs = full_run_inputs(["X", "?", "B", "C", "B", "C", "C", "B"])

        result = run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        self.assertEqual(result["score"], 6)
        self.assertEqual(result["answers"], CORRECT_ANSWERS)

    def test_first_valid_answer_is_the_one_recorded(self):
        out = OutputCollector()
       
        inputs = full_run_inputs(["A", "C", "B", "C", "C", "B"])

        result = run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        self.assertEqual(result["answers"]["Q1"], "A")
        self.assertEqual(result["score"], 5)
        self.assertIn("Not quite. The correct answer is B.", out.text())


class TestRunCheck(unittest.TestCase):
    def test_perfect_run_scores_six_and_shows_final_score(self):
        out = OutputCollector()
        inputs = full_run_inputs(["B", "C", "B", "C", "C", "B"])

        result = run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        self.assertEqual(result["score"], 6)
        self.assertEqual(result["total"], 6)
        self.assertIn("Final score: 6/6", out.text())

    def test_all_wrong_run_scores_zero(self):
        out = OutputCollector()
        inputs = full_run_inputs(["A", "A", "A", "A", "A", "A"])

        result = run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        self.assertEqual(result["score"], 0)
        self.assertIn("Final score: 0/6", out.text())

    def test_feedback_is_shown_after_each_question(self):
        out = OutputCollector()
        inputs = full_run_inputs(["B", "C", "B", "C", "C", "B"])

        run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        for question in QUESTION_BANK:
            self.assertIn(question["feedback"], out.text())

    def test_result_contains_two_explanations(self):
        out = OutputCollector()
        inputs = full_run_inputs(["B", "C", "B", "C", "C", "B"])

        result = run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        self.assertEqual(
            result["explanations"],
            {"Q1": GOOD_EXPLANATION_1, "Q5": GOOD_EXPLANATION_2},
        )


class TestExplanations(unittest.TestCase):
    def setUp(self):
        self.answers = dict(CORRECT_ANSWERS)
        self.out = OutputCollector()

    def test_too_short_or_blank_explanation_is_rejected(self):
        fake_input = ScriptedInput(
            ["1", "", "ok", GOOD_EXPLANATION_1, "2", GOOD_EXPLANATION_2]
        )

        result = collect_explanations(QUESTION_BANK, self.answers, 2, fake_input, self.out)

        self.assertEqual(result, {"Q1": GOOD_EXPLANATION_1, "Q2": GOOD_EXPLANATION_2})
        self.assertEqual(self.out.text().count("Please write at least"), 2)

    def test_invalid_question_number_is_rejected(self):
        fake_input = ScriptedInput(
            ["0", "7", "abc", "", "1", GOOD_EXPLANATION_1, "2", GOOD_EXPLANATION_2]
        )

        result = collect_explanations(QUESTION_BANK, self.answers, 2, fake_input, self.out)

        self.assertEqual(sorted(result), ["Q1", "Q2"])
        self.assertEqual(self.out.text().count("Please enter a number"), 4)

    def test_same_question_cannot_be_explained_twice(self):
        fake_input = ScriptedInput(
            ["3", GOOD_EXPLANATION_1, "3", "4", GOOD_EXPLANATION_2]
        )

        result = collect_explanations(QUESTION_BANK, self.answers, 2, fake_input, self.out)

        self.assertEqual(sorted(result), ["Q3", "Q4"])
        self.assertIn("already explained", self.out.text())

    def test_explanation_is_not_auto_graded(self):
    
        out = OutputCollector()
        inputs = ["A", "C", "B", "C", "C", "B", "1", "accept reject unchanged preserve", "2",
                  "zero percent because of reasons"]

        result = run_check(input_fn=ScriptedInput(inputs), output_fn=out)

        self.assertEqual(result["score"], 5) 

    def test_is_valid_explanation(self):
        self.assertTrue(is_valid_explanation("Rejected so data stays unchanged."))
        self.assertFalse(is_valid_explanation("short"))
        self.assertFalse(is_valid_explanation("          "))
        self.assertFalse(is_valid_explanation(None))


class TestSaveExplanations(unittest.TestCase):
    def test_notes_file_contains_score_answer_and_explanation(self):
        result = {
            "score": 5,
            "total": 6,
            "answers": dict(CORRECT_ANSWERS),
            "explanations": {"Q1": GOOD_EXPLANATION_1, "Q5": GOOD_EXPLANATION_2},
        }

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "notes.md")
            save_explanations(path, "Engineer B", result)
            with open(path, encoding="utf-8") as notes_file:
                content = notes_file.read()

        self.assertIn("Engineer B", content)
        self.assertIn("Score: 5/6", content)
        self.assertIn("### Q1", content)
        self.assertIn(GOOD_EXPLANATION_1, content)
        self.assertIn(GOOD_EXPLANATION_2, content)
        self.assertIn("not auto-graded", content)

    def test_saving_appends_instead_of_overwriting(self):
        result = {"score": 6, "total": 6, "answers": dict(CORRECT_ANSWERS),
                  "explanations": {"Q2": GOOD_EXPLANATION_1}}

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "notes.md")
            save_explanations(path, "Engineer A", result)
            save_explanations(path, "Engineer B", result)
            with open(path, encoding="utf-8") as notes_file:
                content = notes_file.read()

        self.assertIn("Engineer A", content)
        self.assertIn("Engineer B", content)


if __name__ == "__main__":
    unittest.main()
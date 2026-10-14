import unittest
import os
import sys

# Allow the test runner to resolve the campusflow package from the repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from campusflow.understanding_check import QUESTIONS, score_answers


class TestQuizScoringEngine(unittest.TestCase):

    def test_perfect_run_returns_maximum_score(self):
        # A list of 6 perfect answers matching the QUESTIONS bank exactly
        perfect_run = ["B", "C", "B", "C", "C", "B"]
        score, per_question = score_answers(perfect_run)

        self.assertEqual(score, 6)
        self.assertTrue(per_question[0]["is_correct"])
        self.assertEqual(per_question[0]["submitted"], "B")

    def test_incomplete_or_partial_submissions_evaluated_safely(self):
        # Only 2 answers submitted: Q1 correct, Q2 wrong, rest missing
        short_run = ["B", "A"]
        score, per_question = score_answers(short_run)

        self.assertEqual(score, 1)
        self.assertTrue(per_question[0]["is_correct"])
        self.assertFalse(per_question[1]["is_correct"])
        self.assertIsNone(per_question[2]["submitted"])

    def test_all_wrong_scores_zero(self):
        score, _ = score_answers(["A", "A", "A", "A", "A", "A"])
        self.assertEqual(score, 0)

    def test_lowercase_answers_are_accepted(self):
        # The runner uppercases before submitting, but the scorer must too
        score, _ = score_answers(["b", "c", "b", "c", "c", "b"])
        self.assertEqual(score, 6)

    def test_whitespace_around_answers_is_trimmed(self):
        score, _ = score_answers([" B ", "C\n", " b", "C", " C", "B\t"])
        self.assertEqual(score, 6)

    def test_unknown_letter_is_wrong_not_crash(self):
        score, _ = score_answers(["B", "Z", "B", "C", "C", "B"])
        self.assertEqual(score, 5)

    def test_none_answer_is_wrong_not_crash(self):
        score, detail = score_answers(["B", None, "B", "C", "C", "B"])
        self.assertEqual(score, 5)
        self.assertIsNone(detail[1]["submitted"])

    def test_empty_submission_scores_zero(self):
        score, detail = score_answers([])
        self.assertEqual(score, 0)
        self.assertEqual(len(detail), 6)

    def test_empty_questions_list_returns_zero(self):
        score, detail = score_answers([], questions=[])
        self.assertEqual(score, 0)
        self.assertEqual(detail, [])


class TestQuestionBankShape(unittest.TestCase):
   #Guards the data, not the code -- catches typos before the demo.

    def test_bank_has_six_questions(self):
        self.assertEqual(len(QUESTIONS), 6)

    def test_every_question_has_required_keys(self):
        required = {"id", "prompt", "options", "correct", "explanation"}
        for q in QUESTIONS:
            self.assertEqual(set(q.keys()), required, f"bad keys on {q.get('id')}")

    def test_every_question_has_four_options_a_to_d(self):
        for q in QUESTIONS:
            self.assertEqual(
                set(q["options"].keys()), {"A", "B", "C", "D"},
                f"bad options on {q['id']}",
            )

    def test_correct_letter_is_a_real_option(self):
        for q in QUESTIONS:
            self.assertIn(q["correct"], q["options"],
                          f"correct letter not in options for {q['id']}")

    def test_question_ids_are_unique(self):
        ids = [q["id"] for q in QUESTIONS]
        self.assertEqual(len(ids), len(set(ids)))


class TestPerQuestionDetail(unittest.TestCase):
    #The return contract: every entry has the right shape and flags.

    def test_detail_entry_has_expected_keys(self):
        _, detail = score_answers(["B", "C", "B", "C", "C", "B"])
        expected = {"id", "submitted", "correct", "is_correct", "explanation"}
        for entry in detail:
            self.assertEqual(set(entry.keys()), expected)

    def test_detail_flags_all_correct(self):
        _, detail = score_answers(["B", "C", "B", "C", "C", "B"])
        for entry in detail:
            self.assertTrue(entry["is_correct"])
            self.assertEqual(entry["submitted"], entry["correct"])

    def test_detail_flags_all_wrong(self):
        _, detail = score_answers(["A", "A", "A", "A", "A", "A"])
        for entry in detail:
            self.assertFalse(entry["is_correct"])
            self.assertNotEqual(entry["submitted"], entry["correct"])


if __name__ == "__main__":
    unittest.main()
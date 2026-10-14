import unittest
import os
import sys

# Allow the test runner to resolve the campusflow package from the repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from campusflow.search import search_tickets


def make_tickets():
    return [
        {"id": "T001", "title": "Wi-Fi down in ICT", "category": "Network", "urgency": "high", "affected_users": 12, "priority": "critical", "status": "open", "assigned_to": None},
        {"id": "T002", "title": "Projector not working", "category": "Hardware", "urgency": "low", "affected_users": 1,  "priority": "low", "status": "open", "assigned_to": "Wade"},
        {"id": "T003", "title": "VS Code down in cluster two", "category": "Software", "urgency": "medium", "affected_users": 4,  "priority": "medium", "status": "in_progress", "assigned_to": "Keith"},
        {"id": "T004", "title": "Chair broken", "category": "Other", "urgency": "low", "affected_users": 1, "priority": "low", "status": "resolved", "assigned_to": "Fermin"},
    ]


class TestSearchTickets(unittest.TestCase):

    def setUp(self):
        # Fresh fixture before each test so no test can leak state into another
        self.tickets = make_tickets()

    def test_title_match_is_case_insensitive_substring(self):
    # "wi-fi" must match "Wi-Fi" after casefold; only T001 contains it.
        results = search_tickets(self.tickets, search_word="wi-fi")
        ids = [t["id"] for t in results]
        self.assertEqual(ids, ["T001"])

    def test_title_match_uppercase_query(self):
    # Uppercase query must behave the same as lowercase after casefolding
        results = search_tickets(self.tickets, search_word="WI-FI")
        ids = [t["id"] for t in results]
        self.assertEqual(ids, ["T001"])

    def test_combined_filters_use_and(self):
    # All three filters must match; T001 is the only Wi-Fi + Network + open ticket.
        results = search_tickets(
            self.tickets,
            search_word="wi-fi",
            category="Network",
            status="open",
        )
        ids = [t["id"] for t in results]
        self.assertEqual(ids, ["T001"])

    def test_filter_with_no_matches_returns_empty_list(self):
    # No ticket in the fixture contains "printer", so result is empty
        results = search_tickets(self.tickets, search_word="printer", status="open")
        self.assertEqual(results, [])

    def test_no_filters_returns_all_tickets(self):
    # Passing None to every filter means "do not filter on this field", so the full collection comes back unchanged.
        results = search_tickets(
            self.tickets,
            search_word=None,
            category=None,
            status=None,
            priority=None,
        )
        self.assertEqual(len(results), len(self.tickets))

    def test_category_filter_is_case_insensitive(self):
    # User types lowercase "network"; stored value is "Network". Only T001 is Network in the new fixture.
        results = search_tickets(self.tickets, category="network")
        ids = [t["id"] for t in results]
        self.assertEqual(ids, ["T001"])

    def test_search_does_not_modify_collection(self):
    # Search must be read-only: same tickets, same order, same values
        snapshot = [dict(t) for t in self.tickets]
        search_tickets(self.tickets, search_word="wi-fi", status="open")
        self.assertEqual(self.tickets, snapshot)

    def test_priority_filter_matches_exact_value(self):
    # Exact priority match; T002 and T004 are both "low"
        results = search_tickets(self.tickets, priority="low")
        ids = [t["id"] for t in results]
        self.assertEqual(ids, ["T002", "T004"])


if __name__ == "__main__":
    unittest.main()

import copy
import unittest

from campusflow.search import (
    normalize_filter,
    search_tickets,
    sort_results_by_priority,
    VALID_CATEGORIES,
    VALID_STATUSES,
)


def make_ticket(ticket_id, title, category, status, priority):
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": "Staff A",
        "notes": [],
    }


def sample_tickets():
    return [
        make_ticket("T001", "Wifi down in library", "Network", "open", "high"),
        make_ticket("T002", "WIFI slow in hostel", "Network", "resolved", "medium"),
        make_ticket("T003", "Laptop wifi adapter broken", "Hardware", "open", "low"),
        make_ticket("T004", "Install Python on lab PCs", "Software", "in_progress", "critical"),
    ]


def ids(tickets):
    return [ticket["id"] for ticket in tickets]


class TestTitleSearch(unittest.TestCase):
    def setUp(self):
        self.tickets = sample_tickets()

    def test_title_search_ignores_case(self):
        self.assertEqual(ids(search_tickets(self.tickets, "wifi")), ["T001", "T002", "T003"])
        self.assertEqual(ids(search_tickets(self.tickets, "WIFI")), ["T001", "T002", "T003"])
        self.assertEqual(ids(search_tickets(self.tickets, "WiFi")), ["T001", "T002", "T003"])

    def test_title_search_matches_substring_anywhere(self):
        self.assertEqual(ids(search_tickets(self.tickets, "pyth")), ["T004"])
        self.assertEqual(ids(search_tickets(self.tickets, "in library")), ["T001"])

    def test_title_search_trims_query_whitespace(self):
        self.assertEqual(ids(search_tickets(self.tickets, "  python  ")), ["T004"])

    def test_title_search_no_match_returns_empty_list(self):
        self.assertEqual(search_tickets(self.tickets, "printer"), [])

    def test_search_does_not_promise_fuzzy_matching(self):
        self.assertEqual(search_tickets(self.tickets, "wi-fi"), [])


class TestCombinedFilters(unittest.TestCase):
    """Acceptance case 09: all supplied filters must match (AND)."""

    def setUp(self):
        self.tickets = sample_tickets()

    def test_title_category_status_use_and(self):
        result = search_tickets(self.tickets, "wifi", "Network", "open")
        self.assertEqual(ids(result), ["T001"])

    def test_and_is_stricter_than_any_single_filter(self):
        by_title = search_tickets(self.tickets, "wifi")
        combined = search_tickets(self.tickets, "wifi", "Network", "open")
        self.assertGreater(len(by_title), len(combined))
        # Never a record that only matches one condition:
        self.assertNotIn("T003", ids(combined))  # title ok, wrong category
        self.assertNotIn("T002", ids(combined))  # title+category ok, wrong status

    def test_priority_filter_combines_with_others(self):
        result = search_tickets(self.tickets, "wifi", priority="low")
        self.assertEqual(ids(result), ["T003"])

    def test_filters_with_no_common_record_return_empty(self):
        self.assertEqual(search_tickets(self.tickets, "python", "Network"), [])

    def test_empty_filters_mean_do_not_filter(self):
        self.assertEqual(len(search_tickets(self.tickets)), 4)
        self.assertEqual(len(search_tickets(self.tickets, "", "", "", "")), 4)
        self.assertEqual(len(search_tickets(self.tickets, None, None, None, None)), 4)

    def test_filter_input_is_normalised(self):
        result = search_tickets(self.tickets, "", " network ", "OPEN")
        self.assertEqual(ids(result), ["T001"])
        result = search_tickets(self.tickets, "", "", "in progress")
        self.assertEqual(ids(result), ["T004"])


class TestInvalidFilters(unittest.TestCase):
    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(sample_tickets(), "wifi", category="Banana")

    def test_invalid_status_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(sample_tickets(), status="closed")

    def test_invalid_priority_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(sample_tickets(), priority="urgent")

    def test_non_text_filter_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(sample_tickets(), category=5)

    def test_normalize_filter_blank_returns_none(self):
        self.assertIsNone(normalize_filter("", VALID_CATEGORIES))
        self.assertIsNone(normalize_filter("   ", VALID_STATUSES))
        self.assertIsNone(normalize_filter(None, VALID_STATUSES))

    def test_normalize_filter_returns_canonical_value(self):
        self.assertEqual(normalize_filter("network", VALID_CATEGORIES), "Network")
        self.assertEqual(normalize_filter("In Progress", VALID_STATUSES), "in_progress")


class TestSearchIsReadOnly(unittest.TestCase):
    def test_search_does_not_modify_tickets_or_list(self):
        tickets = sample_tickets()
        before = copy.deepcopy(tickets)

        search_tickets(tickets, "wifi", "Network", "open", "high")
        search_tickets(tickets, "zzz")
        search_tickets(tickets)

        self.assertEqual(tickets, before)

    def test_search_returns_new_list_not_the_original(self):
        tickets = sample_tickets()
        result = search_tickets(tickets)
        self.assertIsNot(result, tickets)

    def test_failed_search_does_not_modify_tickets(self):
        tickets = sample_tickets()
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            search_tickets(tickets, "wifi", category="Banana")
        self.assertEqual(tickets, before)


class TestSortResultsByPriority(unittest.TestCase):
    def test_sorts_by_priority_then_ticket_id(self):
        result = sort_results_by_priority(sample_tickets())
        # critical T004, high T001, medium T002, low T003
        self.assertEqual(ids(result), ["T004", "T001", "T002", "T003"])

    def test_ties_use_numeric_id_not_text_id(self):
        tickets = [
            make_ticket("T10", "Ten", "Network", "open", "high"),
            make_ticket("T2", "Two", "Network", "open", "high"),
        ]
        # Text sort would give ['T10', 'T2']; numeric sort must give T2 first.
        self.assertEqual(ids(sort_results_by_priority(tickets)), ["T2", "T10"])

    def test_sort_does_not_reorder_original_list(self):
        tickets = sample_tickets()
        original_order = ids(tickets)
        sort_results_by_priority(tickets)
        self.assertEqual(ids(tickets), original_order)

    def test_sort_empty_list(self):
        self.assertEqual(sort_results_by_priority([]), [])


if __name__ == "__main__":
    unittest.main()
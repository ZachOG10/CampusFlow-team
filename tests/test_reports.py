import unittest

from campusflow.reports import (
    generate_ticket_report,
    count_by_category,
    resolution_percentage,
    generate_detailed_report
)

def make_tickets():
    #Known fixture: 4 tickets covering every status, priority and category.
    return [
        {"id": "T001", "title": "Wi-Fi down", "category": "Network", "urgency": "high", "affected_users": 12, "priority": "critical", "status": "open", "assigned_to": None},
        {"id": "T002", "title": "Projector broken", "category": "Hardware", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": "Wade"},
        {"id": "T003", "title": "VS Code crash", "category": "Software", "urgency": "medium", "affected_users": 4, "priority": "medium", "status": "in_progress", "assigned_to": "Keith"},
        {"id": "T004", "title": "Chair broken", "category": "Other", "urgency": "low", "affected_users": 1, "priority": "low", "status": "resolved", "assigned_to": "Fermin"},
    ]


class TestTicketReports(unittest.TestCase):

    def test_generate_ticket_report(self):
        tickets = [
            {
                "id": 1,
                "status": "open",
                "priority": "critical",
            },
            {
                "id": 2,
                "status": "in_progress",
                "priority": "high",
            },
            {
                "id": 3,
                "status": "resolved",
                "priority": "medium",
            },
            {
                "id": 4,
                "status": "open",
                "priority": "low",
            },
        ]

        report = generate_ticket_report(tickets)

        self.assertEqual(report["total_tickets"], 4)
        self.assertEqual(report["open"], 2)
        self.assertEqual(report["in_progress"], 1)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["critical"], 1)
        self.assertEqual(report["high"], 1)
        self.assertEqual(report["medium"], 1)
        self.assertEqual(report["low"], 1)

    def test_empty_ticket_list(self):
        report = generate_ticket_report([])

        self.assertEqual(report["total_tickets"], 0)
        self.assertEqual(report["open"], 0)
        self.assertEqual(report["in_progress"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["critical"], 0)
        self.assertEqual(report["high"], 0)
        self.assertEqual(report["medium"], 0)
        self.assertEqual(report["low"], 0)

    def test_all_tickets_have_same_status_and_priority(self):
        tickets = [
            {
                "id": 1,
                "status": "open",
                "priority": "high",
            },
            {
                "id": 2,
                "status": "open",
                "priority": "high",
            },
        ]

        report = generate_ticket_report(tickets)

        self.assertEqual(report["total_tickets"], 2)
        self.assertEqual(report["open"], 2)
        self.assertEqual(report["in_progress"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["high"], 2)

    def test_report_does_not_modify_tickets(self):
        tickets = [
            {
                "id": 1,
                "status": "resolved",
                "priority": "critical",
            }
        ]

        original_tickets = [ticket.copy() for ticket in tickets]

        generate_ticket_report(tickets)

        self.assertEqual(tickets, original_tickets)

# added tests
class TestCountByCategory(unittest.TestCase):

    def test_counts_correct_categories(self):
        counts = count_by_category(make_tickets())
        self.assertEqual(counts["Network"], 1)
        self.assertEqual(counts["Hardware"], 1)
        self.assertEqual(counts["Software"], 1)
        self.assertEqual(counts["Other"], 1)

    def test_counts_are_case_insensitive(self):
        tickets = [
            {"category": "network"},
            {"category": "NETWORK"},
            {"category": " network "},
        ]
        counts = count_by_category(tickets)
        self.assertEqual(counts["Network"], 3)

    def test_missing_category_falls_into_other(self):
        tickets = [{"category": None}, {}]
        counts = count_by_category(tickets)
        self.assertEqual(counts["Other"], 2)

    def test_unknown_category_gets_its_own_bucket(self):
       # Non-canonical values are preserved, not silently swallowed
        tickets = [{"category": "Wi-Fi"}]
        counts = count_by_category(tickets)
        self.assertEqual(counts["Wi-Fi"], 1)


class TestResolutionPercentage(unittest.TestCase):

    def test_empty_report_has_zero_percentage(self):
       # Required case #10: no tickets -> 0.0, no ZeroDivisionError
        self.assertEqual(resolution_percentage([]), 0.0)

    def test_percentage_matches_fixture(self):
       # 1 of 4 resolved -> 25.0
        self.assertEqual(resolution_percentage(make_tickets()), 25.0)

    def test_percentage_rounds_to_one_decimal(self):
       # 1 of 3 resolved -> 33.333... -> 33.3
        tickets = [
            {"status": "resolved"},
            {"status": "open"},
            {"status": "open"},
        ]
        self.assertEqual(resolution_percentage(tickets), 33.3)

    def test_percentage_is_numeric_not_string(self):
        # Regression guard: must return a number so user can do math on it
        self.assertIsInstance(resolution_percentage(make_tickets()), float)


class TestGenerateDetailedReport(unittest.TestCase):

    def test_detailed_report_includes_new_fields(self):
        report = generate_detailed_report(make_tickets())
        self.assertIn("unresolved_tickets", report)
        self.assertIn("resolved_tickets", report)
        self.assertIn("categories", report)
        self.assertIn("resolution_percentage", report)

    def test_unresolved_count_is_open_plus_in_progress(self):
        report = generate_detailed_report(make_tickets())
        self.assertEqual(report["unresolved_tickets"], 3)   # 2 open + 1 in_progress

    def test_counts_agree_after_resolve(self):
       # Required case #11: counts must follow the CURRENT status
        tickets = make_tickets()
        tickets[0]["status"] = "resolved"   # T001 moves open -> resolved
        report = generate_detailed_report(tickets)
        self.assertEqual(report["open"], 1)
        self.assertEqual(report["resolved"], 2)
        self.assertEqual(report["unresolved_tickets"], 2)   # 1 open + 1 in_progress
        self.assertEqual(report["resolution_percentage"], 50.0)  # 2 of 4

    def test_empty_report_through_detailed_view(self):
        # Required case #10 via the composed view
        report = generate_detailed_report([])
        self.assertEqual(report["total_tickets"], 0)
        self.assertEqual(report["unresolved_tickets"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)


class TestOriginalReportRegression(unittest.TestCase):
    #Guards that adding new helpers did not change the original report's shape.

    def test_original_report_has_no_new_keys(self):
        report = generate_ticket_report(make_tickets())
        self.assertEqual(set(report.keys()), {"total_tickets", "open", "in_progress", 
        "resolved", "critical", "high", "medium", "low"})


if __name__ == "__main__":
    unittest.main()
import copy
import unittest

from campusflow.reports import (
    calculate_resolution_percentage,
    format_report,
    generate_ticket_report,
)


def make_ticket(ticket_id, status, priority, category="Network"):
    """Fixture helper: only the fields reports read."""
    return {
        "id": ticket_id,
        "status": status,
        "priority": priority,
        "category": category,
    }


def known_fixture():
    return [
        make_ticket("T001", "open", "critical", "Network"),
        make_ticket("T002", "open", "high", "Hardware"),
        make_ticket("T003", "in_progress", "high", "Software"),
        make_ticket("T004", "resolved", "medium", "Network"),
        make_ticket("T005", "resolved", "low", "Other"),
        make_ticket("T006", "resolved", "low", "Network"),
    ]


class TestOriginalReportBehaviour(unittest.TestCase):

    def test_generate_ticket_report(self):
        tickets = [
            {"id": 1, "status": "open", "priority": "critical"},
            {"id": 2, "status": "in_progress", "priority": "high"},
            {"id": 3, "status": "resolved", "priority": "medium"},
            {"id": 4, "status": "open", "priority": "low"},
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

    def test_all_tickets_have_same_status_and_priority(self):
        tickets = [
            {"id": 1, "status": "open", "priority": "high"},
            {"id": 2, "status": "open", "priority": "high"},
        ]

        report = generate_ticket_report(tickets)

        self.assertEqual(report["total_tickets"], 2)
        self.assertEqual(report["open"], 2)
        self.assertEqual(report["in_progress"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["high"], 2)

    def test_report_does_not_modify_tickets(self):
        tickets = [make_ticket("T001", "resolved", "critical")]
        before = copy.deepcopy(tickets)

        generate_ticket_report(tickets)

        self.assertEqual(tickets, before)


class TestEmptyReport(unittest.TestCase):
    """Acceptance case 10: empty report returns 0%, no crash."""

    def test_empty_ticket_list_has_all_zero_counts(self):
        report = generate_ticket_report([])

        for key in (
            "total_tickets", "open", "in_progress", "resolved",
            "critical", "high", "medium", "low", "unresolved",
        ):
            self.assertEqual(report[key], 0, key)
        self.assertEqual(
            report["by_category"],
            {"Network": 0, "Hardware": 0, "Software": 0, "Other": 0},
        )

    def test_empty_ticket_list_resolution_is_zero_percent(self):
        report = generate_ticket_report([])
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_percentage_helper_with_zero_total_does_not_divide(self):
        self.assertEqual(calculate_resolution_percentage(0, 0), 0.0)

    def test_empty_report_can_be_formatted(self):
        text = format_report(generate_ticket_report([]))
        self.assertIn("Total tickets: 0", text)
        self.assertIn("Resolution rate: 0.0%", text)


class TestReportCounts(unittest.TestCase):

    def setUp(self):
        self.tickets = known_fixture()
        self.report = generate_ticket_report(self.tickets)

    def test_total_and_status_counts(self):
        self.assertEqual(self.report["total_tickets"], 6)
        self.assertEqual(self.report["open"], 2)
        self.assertEqual(self.report["in_progress"], 1)
        self.assertEqual(self.report["resolved"], 3)

    def test_priority_counts(self):
        self.assertEqual(self.report["critical"], 1)
        self.assertEqual(self.report["high"], 2)
        self.assertEqual(self.report["medium"], 1)
        self.assertEqual(self.report["low"], 2)

    def test_category_counts(self):
        self.assertEqual(
            self.report["by_category"],
            {"Network": 3, "Hardware": 1, "Software": 1, "Other": 1},
        )

    def test_unresolved_is_open_plus_in_progress(self):
        self.assertEqual(self.report["unresolved"], 3)
        self.assertEqual(
            self.report["unresolved"],
            self.report["open"] + self.report["in_progress"],
        )

    def test_in_progress_ticket_counts_as_unresolved_not_resolved(self):
        report = generate_ticket_report([make_ticket("T001", "in_progress", "low")])
        self.assertEqual(report["unresolved"], 1)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_resolution_percentage(self):
        self.assertEqual(self.report["resolution_percentage"], 50.0)

    def test_percentage_is_rounded_to_two_decimals(self):
        tickets = [
            make_ticket("T001", "resolved", "low"),
            make_ticket("T002", "open", "low"),
            make_ticket("T003", "open", "low"),
        ]
        self.assertEqual(generate_ticket_report(tickets)["resolution_percentage"], 33.33)

    def test_all_resolved_is_100_percent(self):
        tickets = [make_ticket("T001", "resolved", "low"), make_ticket("T002", "resolved", "high")]
        self.assertEqual(generate_ticket_report(tickets)["resolution_percentage"], 100.0)

    def test_no_double_counting_across_statuses_priorities_categories(self):
        total = self.report["total_tickets"]
        self.assertEqual(
            self.report["open"] + self.report["in_progress"] + self.report["resolved"],
            total,
        )
        self.assertEqual(
            sum(self.report[p] for p in ("critical", "high", "medium", "low")),
            total,
        )
        self.assertEqual(sum(self.report["by_category"].values()), total)
        self.assertEqual(
            self.report["unresolved"] + self.report["resolved"],
            total,
        )


class TestResolveAndReopenCounts(unittest.TestCase):

    def test_resolving_moves_ticket_between_status_counts(self):
        tickets = known_fixture()
        tickets[0]["status"] = "resolved"  

        report = generate_ticket_report(tickets)

        self.assertEqual(report["open"], 1)
        self.assertEqual(report["resolved"], 4)
        self.assertEqual(report["unresolved"], 2)
        self.assertEqual(report["total_tickets"], 6)
        self.assertEqual(report["resolution_percentage"], 66.67)

    def test_reopened_ticket_counts_as_open_not_resolved(self):
        tickets = known_fixture()
        tickets[3]["status"] = "open"  

        report = generate_ticket_report(tickets)

        self.assertEqual(report["open"], 3)
        self.assertEqual(report["resolved"], 2)
        self.assertEqual(report["total_tickets"], 6)
        self.assertEqual(report["resolution_percentage"], 33.33)

    def test_resolve_then_reopen_returns_to_original_counts(self):
        tickets = known_fixture()
        before = generate_ticket_report(tickets)

        tickets[0]["status"] = "resolved"
        tickets[0]["status"] = "open"

        self.assertEqual(generate_ticket_report(tickets), before)

    def test_priority_and_category_counts_unchanged_by_status_changes(self):
        tickets = known_fixture()
        before = generate_ticket_report(tickets)

        tickets[1]["status"] = "resolved"
        after = generate_ticket_report(tickets)

        for key in ("critical", "high", "medium", "low", "by_category"):
            self.assertEqual(after[key], before[key], key)


class TestReportRobustness(unittest.TestCase):
    def test_ticket_without_category_is_left_out_of_category_counts_only(self):
        tickets = [{"id": "T001", "status": "open", "priority": "low"}]
        report = generate_ticket_report(tickets)

        self.assertEqual(report["total_tickets"], 1)
        self.assertEqual(report["open"], 1)
        self.assertEqual(sum(report["by_category"].values()), 0)

    def test_report_does_not_modify_tickets_with_new_fields(self):
        tickets = known_fixture()
        before = copy.deepcopy(tickets)

        report = generate_ticket_report(tickets)
        format_report(report)

        self.assertEqual(tickets, before)


class TestFormatReport(unittest.TestCase):
    def test_format_report_shows_every_required_figure(self):
        text = format_report(generate_ticket_report(known_fixture()))

        self.assertIn("Total tickets: 6", text)
        self.assertIn("Open: 2", text)
        self.assertIn("In progress: 1", text)
        self.assertIn("Critical: 1", text)
        self.assertIn("Network: 3", text)
        self.assertIn("Unresolved (open + in progress): 3", text)
        self.assertIn("Resolution rate: 50.0%", text)

    def test_format_report_returns_text_and_does_not_print(self):
        self.assertIsInstance(format_report(generate_ticket_report([])), str)


if __name__ == "__main__":
    unittest.main()
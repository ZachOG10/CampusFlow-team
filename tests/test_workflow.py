import unittest
from unittest.mock import patch
from campusflow.workflow import (
    assign_ticket,
    update_ticket_status,
    reopen_ticket,
    get_work_queue
)


class TestTicketWorkflow(unittest.TestCase):

    def setUp(self):
        """Create fresh sample tickets before each test."""

        self.tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "status": "open",
                "assigned_to": None
            },
            {
                "id": "T002",
                "title": "Laptop won't start",
                "status": "open",
                "assigned_to": "David"
            },
            {
                "id": "T003",
                "title": "Software problem",
                "status": "in_progress",
                "assigned_to": "Sarah"
            },
            {
                "id": "T004",
                "title": "Projector failure",
                "status": "resolved",
                "assigned_to": "John"
            }
        ]

    def test_assign_ticket(self):
        with patch("builtins.input", side_effect=["T001", "David"]):
            assign_ticket(self.tickets)

        self.assertEqual(self.tickets[0]["assigned_to"], "David")

    def test_reassign_ticket(self):
        with patch("builtins.input", side_effect=["T002", "Sarah"]):
            assign_ticket(self.tickets)

        self.assertEqual(self.tickets[1]["assigned_to"], "Sarah")

    def test_reject_empty_staff_name(self):
        with patch("builtins.input", side_effect=["T001", "   ", "David"]):
            assign_ticket(self.tickets)

        self.assertEqual(self.tickets[0]["assigned_to"], "David")

    def test_reject_unknown_ticket_assignment(self):
        with patch("builtins.input", side_effect=["T999"]):
            assign_ticket(self.tickets)

        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_unassigned_ticket_cannot_start(self):
        with patch("builtins.input", side_effect=["T001", "1"]):
            update_ticket_status(self.tickets)

        self.assertEqual(self.tickets[0]["status"], "open")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_assigned_ticket_can_start(self):
        with patch("builtins.input", side_effect=["T002", "1"]):
            update_ticket_status(self.tickets)

        self.assertEqual(self.tickets[1]["status"], "in_progress")

    def test_in_progress_ticket_can_be_resolved(self):
        with patch("builtins.input", side_effect=["T003", "2"]):
            update_ticket_status(self.tickets)

        self.assertEqual(self.tickets[2]["status"], "resolved")

    def test_resolved_ticket_cannot_skip_reopening(self):
        with patch("builtins.input", side_effect=["T004", "1"]):
            update_ticket_status(self.tickets)

        self.assertEqual(self.tickets[3]["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        with patch("builtins.input", side_effect=["T004"]):
            reopen_ticket(self.tickets)

        self.assertEqual(self.tickets[3]["status"], "open")

    def test_resolved_ticket_cannot_be_reassigned(self):
        with patch("builtins.input", side_effect=["T004", "Mary"]):
            assign_ticket(self.tickets)

        self.assertEqual(self.tickets[3]["assigned_to"], "John")

    def test_non_resolved_ticket_cannot_be_reopened(self):
        with patch("builtins.input", side_effect=["T002"]):
            reopen_ticket(self.tickets)

        self.assertEqual(self.tickets[1]["status"], "open")

    def test_unknown_ticket_cannot_be_reopened(self):
        with patch("builtins.input", side_effect=["T999"]):
            reopen_ticket(self.tickets)

        self.assertEqual(self.tickets[3]["status"], "resolved")


if __name__ == "__main__":
    unittest.main(verbosity=2)
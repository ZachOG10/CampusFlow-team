import unittest
import tempfile
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets

class TestTicketStoragePersistence(unittest.TestCase):

    def test_save_and_reload_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "in_progress",
                "assigned_to": "Ada",
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "tickets.json"

            save_tickets(tickets, file_path)
            loaded_tickets = load_tickets(file_path)

        self.assertEqual(loaded_tickets, tickets)

    def test_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "missing.json"

            loaded_tickets = load_tickets(file_path)

        self.assertEqual(loaded_tickets, [])

    def test_malformed_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "tickets.json"
            file_path.write_text("{invalid json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                load_tickets(file_path)

    def test_json_must_contain_a_list(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "tickets.json"
            file_path.write_text(
                '{"id": "T001"}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "list of tickets"):
                load_tickets(file_path)

    def test_json_list_must_contain_ticket_dictionaries(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "tickets.json"
            file_path.write_text(
                '["not a ticket dictionary"]',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "dictionary"):
                load_tickets(file_path)

if __name__ == "__main__":
    unittest.main()
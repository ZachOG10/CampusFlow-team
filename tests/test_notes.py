import unittest
from campusflow.notes import add_note, validate_note_author, validate_note_message
from campusflow.ticket import Ticket  

class TestNotes(unittest.TestCase):
    
    def setUp(self):
        self.ticket = Ticket(
            ticket_id="T001",
            title="Server Connection Failure",
            description="Unable to connect to the primary database server.",
            category="Network",
            urgency="high",
            affected_users=10,
            status="open"
        )

    def test_validate_author_valid(self):
        self.assertEqual(validate_note_author("Alice"), "Alice")

    def test_validate_author_invalid(self):
        with self.assertRaises(ValueError):
            validate_note_author("")
        with self.assertRaises(ValueError):
            validate_note_author("   ")

    def test_validate_message_valid(self):
        msg = "Checking the router configurations now."
        self.assertEqual(validate_note_message(msg), msg)

    def test_validate_message_bounds(self):
        """Ensure messages outside the 5-300 character limit are rejected."""
        with self.assertRaises(ValueError):
            validate_note_message("Test")
        with self.assertRaises(ValueError):
            validate_note_message("A" * 301)

    def test_add_note_success(self):
        note = add_note(self.ticket, author="Alice", message="Investigating switch logs.")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Alice")
        self.assertIn(note, self.ticket.notes)

    def test_add_note_status_restriction(self):
        self.ticket.status = "resolved"
        with self.assertRaises(ValueError):
            add_note(self.ticket, author="Bob", message="Attempting to comment on resolved ticket.")

    def test_failed_note_does_not_consume_id(self):
        note1 = add_note(self.ticket, author="Alice", message="First update.")
        self.assertEqual(note1["note_id"], "N001")
        
        with self.assertRaises(ValueError):
            add_note(self.ticket, author="", message="Bad author note.")
        
        note2 = add_note(self.ticket, author="Charlie", message="Second update.")
        self.assertEqual(note2["note_id"], "N002")

if __name__ == "__main__":
    unittest.main()
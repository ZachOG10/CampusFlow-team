import copy
import json
import unittest
import campusflow.notes
from campusflow.notes import add_note, next_note_id, validate_note_author, validate_note_message
from campusflow.tickets import create_ticket  

class TestNotes(unittest.TestCase):
    
    def setUp(self):
        campusflow.notes.note_count = 1  
        self.ticket = create_ticket(
            title="Server Connection Failure",
            category="Network",
            urgency="high",
            affected_users=10
        )

    def test_validate_author_valid(self):
        self.assertEqual(validate_note_author("Alice"), "Alice")

    def test_validate_author_invalid(self):
        with self.assertRaises(ValueError):
            validate_note_author("")
        with self.assertRaises(ValueError):
            validate_note_author("   ")

    def test_validate_message_valid(self):
        message = "Checking the router configurations now."
        self.assertEqual(validate_note_message(message), message)

    def test_validate_message_bounds(self):
        with self.assertRaises(ValueError):
            validate_note_message("Test")
        with self.assertRaises(ValueError):
            validate_note_message("A" * 301)

    def test_add_note_success(self):
        note = add_note(self.ticket, author="Alice", message="Investigating switch logs.")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Alice")
        self.assertIn(note, self.ticket["notes"])

    def test_add_note_status_restriction(self):
        self.ticket["status"] = "resolved"
        with self.assertRaises(ValueError):
            add_note(self.ticket, author="Bob", message="Attempting to comment on resolved ticket.")

    def test_failed_note_does_not_consume_id(self):
        note1 = add_note(self.ticket, author="Alice", message="First update.")
        self.assertEqual(note1["note_id"], "N001")
        
        with self.assertRaises(ValueError):
            add_note(self.ticket, author="", message="Bad author note.")
        
        note2 = add_note(self.ticket, author="Charlie", message="Second update.")
        self.assertEqual(note2["note_id"], "N002")

    def test_note_ids_are_per_ticket(self):
        other = create_ticket("Printer jam", "Hardware", "low", 1)
        first = add_note(self.ticket, "Alice", "Checking the router.")
        second = add_note(other, "Bob", "Replacing the toner.")
        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N001")

    def test_note_ids_continue_after_save_and_reload(self):
        add_note(self.ticket, "Alice", "First update.")
        add_note(self.ticket, "Bob", "Second update.")
        reloaded = json.loads(json.dumps(self.ticket))
        note = add_note(reloaded, "Carol", "Third update.")
        self.assertEqual(note["note_id"], "N003")

    def test_message_length_is_checked_after_trimming(self):
        before = copy.deepcopy(self.ticket)
        with self.assertRaises(ValueError):
            add_note(self.ticket, "Alice", "   hi   ")
        self.assertEqual(self.ticket, before)
        note = add_note(self.ticket, "Alice", "   hello   ")
        self.assertEqual(note["message"], "hello")

    def test_in_progress_ticket_accepts_notes(self):
        self.ticket["status"] = "in_progress"
        note = add_note(self.ticket, "Alice", "Working on it now.")
        self.assertEqual(note["note_id"], "N001")

    def test_rejected_note_leaves_ticket_unchanged(self):
        add_note(self.ticket, "Alice", "First update.")
        self.ticket["status"] = "resolved"
        before = copy.deepcopy(self.ticket)
        with self.assertRaises(ValueError):
            add_note(self.ticket, "Bob", "Too late to comment.")
        self.assertEqual(self.ticket, before)

    def test_resolve_reopen_keeps_notes_and_numbering(self):
        add_note(self.ticket, "Mentor A", "Wi-Fi router reboot attempted")
        add_note(self.ticket, "Mentor B", "Investigating switch ports")
        self.ticket["status"] = "resolved"
        with self.assertRaises(ValueError):
            add_note(self.ticket, "Mentor A", "Trying to add a third note")
        self.ticket["status"] = "open"
        note = add_note(self.ticket, "Mentor A", "Back on this one")
        self.assertEqual(note["note_id"], "N003")
        self.assertEqual(len(self.ticket["notes"]), 3)

    def test_next_note_id_for_ticket_without_notes_key(self):
        self.assertEqual(next_note_id({"status": "open"}), "N001")

if __name__ == "__main__":
    unittest.main()
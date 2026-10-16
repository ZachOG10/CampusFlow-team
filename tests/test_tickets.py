import unittest
from campusflow.tickets import create_ticket  

class TestTickets(unittest.TestCase):
    
    def test_valid_tickets(self):
        test_ticket = create_ticket("WI-FI not working", "network", "HIGH", 20)
        self.assertIsInstance(test_ticket, dict)
        self.assertEqual(test_ticket["priority"], "critical")
        self.assertEqual(test_ticket["status"], "open")
        self.assertEqual(test_ticket["urgency"], "high")
        self.assertEqual(test_ticket["category"], "Network")

    def test_invalid_category(self):
        test_category = create_ticket("Printer broken", "cooking", "low", 2)
        self.assertIsNone(test_category)
    
    def test_invalid_urgency(self):
        test_urgency = create_ticket("Printer broken", "Hardware", "urgent", 2)
        self.assertIsNone(test_urgency)

    def test_blank_title(self):
        test_title = create_ticket("", "Hardware", "medium", 3)
        self.assertIsNone(test_title)

    def test_zero_affected_users(self):
        test_affected_users = create_ticket("Wifi", "Network", "medium", 0)
        self.assertIsNone(test_affected_users)

    def test_negative_affected_users(self):
        test_negative_users = create_ticket("Wifi", "Network", "medium", -3)
        self.assertIsNone(test_negative_users)

    def test_boolean_affected_users_rejected(self):
        test_bool_true = create_ticket("Wifi", "Network", "medium", True)
        test_bool_false = create_ticket("Wifi", "Network", "medium", False)
        self.assertIsNone(test_bool_true)
        self.assertIsNone(test_bool_false)

    def test_high_priority(self):
        test_priority = create_ticket("wifi", "network", "high", 4)
        self.assertEqual(test_priority["priority"], "high")

    def test_medium_priority(self):
        test_medium = create_ticket("wifi", "Network", "medium", 2)
        self.assertEqual(test_medium["priority"], "medium")

    def test_low_priority(self):
        test_low = create_ticket("wifi", "network", "low", 2)
        self.assertEqual(test_low["priority"], "low")

    def test_new_ticket_continues_after_highest_existing_id(self):
        existing = [{"id": "T001"}, {"id": "T005"}]
        ticket = create_ticket("Projector broken", "Hardware", "low", 1, existing)
        self.assertEqual(ticket["id"], "T006")

    def test_first_ticket_with_empty_existing_list_is_t001(self):
        ticket = create_ticket("Projector broken", "Hardware", "low", 1, [])
        self.assertEqual(ticket["id"], "T001")

    def test_id_does_not_repeat_after_restart(self):
        import campusflow.tickets
        campusflow.tickets.count = 1
        saved = [create_ticket("Wifi down", "Network", "high", 12, [])]
        campusflow.tickets.count = 1 
        new = create_ticket("Printer jam", "Hardware", "low", 1, saved)
        self.assertNotEqual(new["id"], saved[0]["id"])

    def test_new_ticket_has_empty_notes_and_trimmed_title(self):
        ticket = create_ticket("  Wifi down  ", "Network", "high", 12)
        self.assertEqual(ticket["notes"], [])
        self.assertEqual(ticket["title"], "Wifi down")

if __name__ == "__main__":
    unittest.main()
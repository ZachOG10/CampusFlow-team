import unittest
from campusflow.tickets import create_ticket 

class TestTickets(unittest.TestCase):
    def test_valid_tickets(self):
        test_ticket = create_ticket("WI-FI not working", "Network", "high", 20)
        self.assertIsInstance(test_ticket, dict)
        self.assertEqual(test_ticket["priority"], "critical")
        self.assertEqual(test_ticket["status"], "open")
        self.assertEqual(test_ticket["urgency"], "high")
        
if __name__ == "__main__": 
    unittest.main()
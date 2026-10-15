import unittest
from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_urgency,
)

class TestValidation(unittest.TestCase):
    
    def test_validate_affected_users_valid(self):
        self.assertEqual(validate_affected_users(5), 5)
        self.assertEqual(validate_affected_users(1), 1)

    def test_validate_affected_users_booleans_rejected(self):
        with self.assertRaises((ValueError, TypeError)):
            validate_affected_users(True)
        with self.assertRaises((ValueError, TypeError)):
            validate_affected_users(False)

    def test_validate_affected_users_invalid_types(self):
        with self.assertRaises((ValueError, TypeError)):
            validate_affected_users("10")
        with self.assertRaises((ValueError, TypeError)):
            validate_affected_users(2.5)

    def test_validate_affected_users_zero_or_negative(self):
        with self.assertRaises(ValueError):
            validate_affected_users(0)
        with self.assertRaises(ValueError):
            validate_affected_users(-3)

    def test_validate_category_valid(self):
        self.assertEqual(validate_category("network"), "Network")
        self.assertEqual(validate_category("  hardware "), "Hardware")
        self.assertEqual(validate_category("Software"), "Software")
        self.assertEqual(validate_category("other"), "Other")

    def test_validate_category_invalid(self):
        with self.assertRaises(ValueError):
            validate_category("PowerOutage")

    def test_validate_urgency_valid(self):
        self.assertEqual(validate_urgency("LOW"), "low")
        self.assertEqual(validate_urgency("  medium  "), "medium")
        self.assertEqual(validate_urgency("High"), "high")

    def test_validate_urgency_invalid(self):
        with self.assertRaises(ValueError):
            validate_urgency("critical_emergency")

if __name__ == "__main__":
    unittest.main()
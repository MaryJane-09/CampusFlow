import unittest
from unittest.mock import patch
from datetime import datetime, timezone

from campusflow.tickets import GenerateID
from campusflow.sla import is_overdue
from campusflow.queues import SLAAttentionQueue

class TestCampusFlowRegression(unittest.TestCase):

    def test_generate_id_strict_validation(self):
        """Test that GenerateID rejects non-dictionary elements with ValueError."""
        class MockCampus:
            tickets = ["malformed_string"]

        with patch("campusflow.tickets.campus", MockCampus()), \
             patch("campusflow.tickets.load_json", return_value=None):
            
            with self.assertRaises(ValueError):
                GenerateID()

    def test_is_overdue_type_guard(self):
        """Test that is_overdue safely handles non-dictionary items without crashing."""
        now = datetime.now(timezone.utc)
        self.assertFalse(is_overdue("not_a_dict", now))

    @patch("campusflow.queues.load_json")
    def test_sla_attention_queue_skips_malformed(self, mock_load):
        """Test that SLAAttentionQueue ignores strings in the ticket list."""
        class MockCampus:
            tickets = [
                "rogue_string_entry",
                {
                    "id": "T001",
                    "title": "Test Ticket",
                    "status": "open",
                    "priority": "High",
                    "due_at": "2030-01-01T00:00:00+00:00"
                }
            ]

        with patch("campusflow.queues.campus", MockCampus()):
            try:
                SLAAttentionQueue()
            except AttributeError as e:
                self.fail(f"Queue crashed on legacy string entry: {e}")

if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from campusflow.tickets import GenerateID
from campusflow.sla import is_overdue
from campusflow.queues import SLAAttentionQueue, DisplayMetrics

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

    
    @patch("campusflow.queues.load_json")
    def test_display_metrics_counts_tickets(self, mock_load):
        """Verify status and priority metrics are calculated correctly."""
        class MockCampus:
            tickets = [
                {
                    "id": "T001",
                    "status": "open",
                    "priority": "critical",
                    "due_at": "2030-01-01T00:00:00+00:00",
                },
                {
                    "id": "T002",
                    "status": "in_progress",
                    "priority": "high",
                    "due_at": "2030-01-01T00:00:00+00:00",
                },
                {
                    "id": "T003",
                    "status": "resolved",
                    "priority": "low",
                    "due_at": "2030-01-01T00:00:00+00:00",
                },
            ]

        with patch("campusflow.queues.campus", MockCampus()):
            with patch("builtins.print") as mock_print:
                DisplayMetrics()

        output = "\n".join(
            str(call.args[0])
            for call in mock_print.call_args_list
            if call.args
        )

        self.assertIn("Open Tickets:", output)
        self.assertIn("In-Progress Tickets:", output)
        self.assertIn("Resolved Tickets:", output)
        self.assertIn("Critical", output)
        self.assertIn("High", output)
        self.assertIn("Low", output)


if __name__ == "__main__":
    unittest.main()
import unittest
from copy import deepcopy
from unittest.mock import patch

from campusflow import queues, storage
from campus_test_support import CampusTestSetup


class TestQueues(CampusTestSetup, unittest.TestCase):
    def test_sla_attention_queue_rejects_corrupt_file(self):
        self.prepare_ticket()
        storage.load_json(queues.campus)
        old_tickets = deepcopy(queues.campus.tickets)
        old_events = deepcopy(queues.campus.events)
        self.write_data([self.ticket, "rogue_string"], self.events)
        before = self.read_data()
        with patch("builtins.print") as output:
            queues.SLAAttentionQueue()
        # Corruption must be reported, rather than silently skipped.
        self.assertIn("dictionary", str(output.call_args_list))
        self.assertEqual(queues.campus.tickets, old_tickets)
        self.assertEqual(queues.campus.events, old_events)
        self.assertEqual(self.read_data(), before)

    def test_display_metrics_counts_tickets(self):
        self.prepare_ticket()
        before = self.read_data()
        with patch("builtins.print") as output:
            queues.DisplayMetrics()
        text = "\n".join(" ".join(map(str, call.args)) for call in output.call_args_list)
        self.assertRegex(text, r"Open Tickets:\s*1\b")
        self.assertRegex(text, r"In-Progress Tickets:\s*0\b")
        self.assertRegex(text, r"Resolved Tickets:\s*0\b")
        self.assertIn("Critical", text)
        self.assertIn("High", text)
        self.assertIn("Low", text)
        self.assertEqual(self.read_data(), before)


if __name__ == "__main__":
    unittest.main()
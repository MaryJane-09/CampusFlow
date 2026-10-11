import json
import os
import tempfile
import unittest
from unittest.mock import patch

from campusflow import workflow


class TestWorkQueueAndWorkFlow(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ticket_file = os.path.join(self.temp_dir.name, "ticket.json")
        self.patcher = patch.object(workflow, "FilePath", self.ticket_file)
        self.patcher.start()

        self.tickets = [
            {
                "id": "T001",
                "title": "Slow network",
                "priority": "Low",
                "status": "open",
                "assigned_to": "None",
            },
            {
                "id": "T002",
                "title": "Server down",
                "priority": "Critical",
                "status": "open",
                "assigned_to": "Alex",
            },
            {
                "id": "T003",
                "title": "Old issue",
                "priority": "High",
                "status": "resolved",
                "assigned_to": "Sam",
            },
            {
                "id": "T004",
                "title": "Login error",
                "priority": "High",
                "status": "in_progress",
                "assigned_to": "Jamie",
            },
        ]

        self.save_tickets()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def save_tickets(self):
        with open(self.ticket_file, "w") as file:
            json.dump(self.tickets, file)

    def read_tickets(self):
        with open(self.ticket_file, "r") as file:
            return json.load(file)

    # WorkQueue tests

    def test_queue_shows_active_tickets(self):
        with patch("builtins.print") as mock_print:
            workflow.WorkQueue()

        output = "\n".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("T001", output)
        self.assertIn("T002", output)
        self.assertIn("T004", output)
        self.assertNotIn("T003", output)

    def test_queue_sorts_by_priority(self):
        with patch("builtins.print") as mock_print:
            workflow.WorkQueue()

        output = "\n".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertLess(output.index("T002"), output.index("T004"))
        self.assertLess(output.index("T004"), output.index("T001"))

    def test_queue_shows_unassigned_tickets(self):
        with patch("builtins.print") as mock_print:
            workflow.WorkQueue()

        output = "\n".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Unassigned", output)

    def test_queue_handles_missing_file(self):
        os.remove(self.ticket_file)

        with patch("builtins.print") as mock_print:
            workflow.WorkQueue()

        mock_print.assert_called_with(
            "Error: Tickets file is empty or missing."
        )

    def test_queue_handles_empty_file(self):
        open(self.ticket_file, "w").close()

        with patch("builtins.print") as mock_print:
            workflow.WorkQueue()

        mock_print.assert_called_with(
            "Error: Tickets file is empty or missing."
        )

    # WorkFlow tests

    @patch("builtins.input", side_effect=["T001", "in_progress"])
    def test_open_ticket_can_be_started_when_assigned(self, mock_input):
        self.tickets[0]["assigned_to"] = "Alex"
        self.save_tickets()

        workflow.WorkFlow()

        tickets = self.read_tickets()
        self.assertEqual(tickets[0]["status"], "in_progress")

    @patch("builtins.input", side_effect=["T001", "in_progress"])
    def test_unassigned_ticket_cannot_be_started(self, mock_input):
        with patch("builtins.print") as mock_print:
            workflow.WorkFlow()

        mock_print.assert_called_with(
            "Error: Ticket has not been assigned."
        )
        self.assertEqual(self.read_tickets()[0]["status"], "open")

    @patch("builtins.input", side_effect=["T004", "resolved"])
    def test_in_progress_ticket_can_be_resolved(self, mock_input):
        workflow.WorkFlow()

        self.assertEqual(self.read_tickets()[3]["status"], "resolved")

    @patch("builtins.input", side_effect=["T003", "open"])
    def test_resolved_ticket_can_be_reopened(self, mock_input):
        workflow.WorkFlow()

        self.assertEqual(self.read_tickets()[2]["status"], "open")

    @patch("builtins.input", side_effect=["T001", "resolved"])
    def test_open_ticket_cannot_skip_to_resolved(self, mock_input):
        with patch("builtins.print") as mock_print:
            workflow.WorkFlow()

        mock_print.assert_called_with("Error: Must follow workflow.")
        self.assertEqual(self.read_tickets()[0]["status"], "open")

    @patch("builtins.input", side_effect=["T003", "in_progress"])
    def test_resolved_ticket_must_be_reopened_first(self, mock_input):
        with patch("builtins.print") as mock_print:
            workflow.WorkFlow()

        mock_print.assert_called_with(
            "Error: Reopen the ticket first."
        )
        self.assertEqual(self.read_tickets()[2]["status"], "resolved")

    @patch("builtins.input", side_effect=["UNKNOWN", "open"])
    def test_unknown_ticket_id_is_rejected(self, mock_input):
        with patch("builtins.print") as mock_print:
            workflow.WorkFlow()

        mock_print.assert_called_with("Error: No match found")

    @patch("builtins.input", side_effect=["T001", "invalid"])
    def test_invalid_status_is_rejected(self, mock_input):
        with patch("builtins.print") as mock_print:
            workflow.WorkFlow()

        mock_print.assert_called_with("Error: Unrecognized workflow.")
        self.assertEqual(self.read_tickets()[0]["status"], "open")


if __name__ == "__main__":
    unittest.main()
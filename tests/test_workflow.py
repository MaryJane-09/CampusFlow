import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

CampusFlow = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CampusFlow))

# Change this import if your module has a different filename.
from campusflow import workflow as status_module


class TestWorkFlow(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
        )
        self.temp_file.close()

        status_module.FilePath = self.temp_file.name
        status_module.campus.tickets = []

        self.ticket = {
            "id": "T001",
            "title": "Campus Wi-Fi is down",
            "category": "network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "Critical",
            "status": "open",
            "assigned_to": None,
        }

        self.save_tickets()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def save_tickets(self):
        with open(status_module.FilePath, "w") as file:
            json.dump([self.ticket.copy()], file, indent=4)

    def read_ticket(self):
        with open(status_module.FilePath, "r") as file:
            return json.load(file)[0]

    def run_status_update(self, ticket_id, new_status):
        with patch(
            "builtins.input",
            side_effect=[ticket_id, new_status],
        ):
            status_module.WorkFlow()

    def test_open_ticket_moves_to_in_progress_when_assigned(self):
        self.ticket["assigned_to"] = "Mary"
        self.save_tickets()

        self.run_status_update("T001", "in_progress")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "in_progress")

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        self.run_status_update("T001", "in_progress")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "open")

    def test_in_progress_ticket_can_be_resolved(self):
        self.ticket["status"] = "in_progress"
        self.save_tickets()

        self.run_status_update("T001", "resolved")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        self.ticket["status"] = "resolved"
        self.save_tickets()

        self.run_status_update("T001", "open")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "open")

    def test_open_ticket_cannot_be_resolved_directly(self):
        self.run_status_update("T001", "resolved")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "open")

    def test_resolved_ticket_cannot_move_directly_to_in_progress(self):
        self.ticket["status"] = "resolved"
        self.save_tickets()

        self.run_status_update("T001", "in_progress")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "resolved")

    def test_ticket_cannot_be_moved_to_unrecognized_status(self):
        self.run_status_update("T001", "pending")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "open")

    def test_ticket_id_must_match(self):
        self.run_status_update("T999", "in_progress")

        saved = self.read_ticket()
        self.assertEqual(saved["id"], "T001")
        self.assertEqual(saved["status"], "open")

    def test_ticket_id_is_case_sensitive_currently(self):
        self.run_status_update("t001", "in_progress")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "open")

    def test_ticket_already_open_remains_open(self):
        self.run_status_update("T001", "open")

        saved = self.read_ticket()
        self.assertEqual(saved["status"], "open")

    def test_missing_ticket_file_is_handled(self):
        os.remove(status_module.FilePath)

        with patch("builtins.input") as mock_input:
            status_module.WorkFlow()

        mock_input.assert_not_called()

    def test_empty_ticket_file_is_handled(self):
        with open(status_module.FilePath, "w") as file:
            file.write("")

        with patch("builtins.input") as mock_input:
            status_module.WorkFlow()

        mock_input.assert_not_called()


if __name__ == "__main__":
    unittest.main()

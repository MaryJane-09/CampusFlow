import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

CampusFlow = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CampusFlow))

# Change this import if your module has a different filename.
from campusflow import workflow as queue_module


class TestWorkQueue(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
        )
        self.temp_file.close()

        queue_module.FilePath = self.temp_file.name
        queue_module.campus.tickets = []

        self.tickets = [
            {
                "id": "T003",
                "title": "Software bug",
                "priority": "Medium",
                "status": "open",
                "assigned_to": "Mary",
            },
            {
                "id": "T002",
                "title": "Server failure",
                "priority": "Critical",
                "status": "in_progress",
                "assigned_to": "John",
            },
            {
                "id": "T001",
                "title": "Wi-Fi issue",
                "priority": "High",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T004",
                "title": "Old issue",
                "priority": "Critical",
                "status": "resolved",
                "assigned_to": "Jane",
            },
            {
                "id": "T005",
                "title": "Minor issue",
                "priority": "Low",
                "status": "open",
                "assigned_to": "Alex",
            },
        ]

        self.save_tickets(self.tickets)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def save_tickets(self, tickets):
        with open(queue_module.FilePath, "w") as file:
            json.dump(tickets, file, indent=4)

    def run_work_queue(self):
        output = StringIO()

        with redirect_stdout(output):
            queue_module.WorkQueue()

        return output.getvalue()

    def test_active_tickets_are_displayed(self):
        output = self.run_work_queue()

        self.assertIn("T001", output)
        self.assertIn("T002", output)
        self.assertIn("T003", output)
        self.assertIn("T005", output)

    def test_resolved_tickets_are_excluded(self):
        output = self.run_work_queue()

        self.assertNotIn("T004", output)
        self.assertNotIn("Old issue", output)

    def test_tickets_are_sorted_by_priority(self):
        output = self.run_work_queue()

        critical_position = output.index("T002")
        high_position = output.index("T001")
        medium_position = output.index("T003")
        low_position = output.index("T005")

        self.assertLess(critical_position, high_position)
        self.assertLess(high_position, medium_position)
        self.assertLess(medium_position, low_position)

    def test_same_priority_is_sorted_by_ticket_id(self):
        tickets = [
            {
                "id": "T010",
                "title": "Issue ten",
                "priority": "High",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T002",
                "title": "Issue two",
                "priority": "High",
                "status": "open",
                "assigned_to": None,
            },
        ]

        self.save_tickets(tickets)
        output = self.run_work_queue()

        self.assertLess(output.index("T002"), output.index("T010"))

    def test_unassigned_ticket_displays_unassigned(self):
        output = self.run_work_queue()

        self.assertIn("Unassigned", output)

    def test_in_progress_tickets_are_included(self):
        output = self.run_work_queue()

        self.assertIn("Server failure", output)

    def test_no_active_tickets_displays_message(self):
        tickets = [
            {
                "id": "T001",
                "title": "Resolved issue",
                "priority": "High",
                "status": "resolved",
                "assigned_to": "Mary",
            }
        ]

        self.save_tickets(tickets)
        output = self.run_work_queue()

        self.assertIn("No active tickets in the work queue.", output)

    def test_missing_ticket_file_is_handled(self):
        os.remove(queue_module.FilePath)

        output = self.run_work_queue()

        self.assertIn("Error: Tickets file is empty or missing.", output)

    def test_empty_ticket_file_is_handled(self):
        with open(queue_module.FilePath, "w") as file:
            file.write("")

        output = self.run_work_queue()

        self.assertIn("Error: Tickets file is empty or missing.", output)

    def test_priority_sorting_is_case_insensitive(self):
        tickets = [
            {
                "id": "T001",
                "title": "High priority issue",
                "priority": "HIGH",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T002",
                "title": "Critical issue",
                "priority": "CRITICAL",
                "status": "open",
                "assigned_to": None,
            },
        ]

        self.save_tickets(tickets)
        output = self.run_work_queue()

        self.assertLess(output.index("T002"), output.index("T001"))


if __name__ == "__main__":
    unittest.main()

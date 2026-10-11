
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

from campusflow.show_ticket import CampusFlow
from campusflow.list_view import list_ticket, view_ticket


class TestCampusFlowF2(unittest.TestCase):

    def setUp(self):
        self.campus = CampusFlow()

        self.campus.ticket = [
            {
                "ID": "T001",
                "title": "Wi-Fi Problem",
                "category": "Network",
                "urgency": "high",
                "affected_users": 20,
                "priority": "critical",
                "status": "open",
                "assigned_to": None
            },
            {
                "ID": "T002",
                "title": "Broken Laptop",
                "category": "Hardware",
                "urgency": "medium",
                "affected_users": 1,
                "priority": "medium",
                "status": "in_progress",
                "assigned_to": "Daniel"
            },
            {
                "ID": "T003",
                "title": "Platform Error",
                "category": "Platform",
                "urgency": "low",
                "affected_users": 2,
                "priority": "low",
                "status": "resolved",
                "assigned_to": "Andrew"
            }
        ]

    # Helper to capture LIST output
    def capture_list(self):
        output = StringIO()

        with redirect_stdout(output):
            list_ticket(self.campus)

        return output.getvalue()

    # Helper to simulate user input and capture VIEW output
    def capture_view(self, ticket_id):
        output = StringIO()

        with patch("builtins.input", return_value=ticket_id):
            with redirect_stdout(output):
                view_ticket(self.campus)

        return output.getvalue()

    # TEST 1: Empty ticket collection
    def test_list_empty(self):
        self.campus.ticket = []

        output = self.capture_list()

        self.assertIn("no", output.lower())
        self.assertIn("recorded", output.lower())

    # TEST 2: List all tickets
    def test_list_all(self):
        output = self.capture_list()

        self.assertIn("T001", output)
        self.assertIn("T002", output)
        self.assertIn("T003", output)

    # TEST 3: Check ticket information
    def test_list_ticket_details(self):
        output = self.capture_list()

        self.assertIn("Wi-Fi Problem", output)
        self.assertIn("Broken Laptop", output)
        self.assertIn("Platform Error", output)
        self.assertIn("critical", output)
        self.assertIn("in_progress", output)

    # TEST 4: View an existing ticket
    def test_view_existing(self):
        output = self.capture_view("T002")

        self.assertIn("T002", output)
        self.assertIn("Broken Laptop", output)
        self.assertIn("Daniel", output)
        self.assertNotIn("Ticket not found", output)

    # TEST 5: View a nonexistent ticket
    def test_view_unknown(self):
        output = self.capture_view("T999")

        self.assertIn("Ticket not found", output)

    # TEST 6: Lowercase ticket ID
    def test_view_lowercase(self):
        output = self.capture_view("t001")

        self.assertIn("T001", output)
        self.assertIn("Wi-Fi Problem", output)

    # TEST 7: Extra spaces around ticket ID
    def test_view_spaces(self):
        output = self.capture_view("  T003  ")

        self.assertIn("T003", output)
        self.assertIn("Platform Error", output)

    # TEST 8: Empty ticket ID
    def test_view_empty_input(self):
        output = self.capture_view("   ")

        self.assertIn("empty", output.lower())
        self.assertNotIn("Ticket not found", output)

    # TEST 9: Ensure VIEW displays only the matching ticket
    def test_view_only_one_ticket(self):
        output = self.capture_view("T002")

        self.assertIn("Broken Laptop", output)
        self.assertNotIn("Wi-Fi Problem", output)
        self.assertNotIn("Platform Error", output)


if __name__ == "__main__":
    unittest.main()

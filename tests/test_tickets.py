
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

CampusFlow = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CampusFlow))

from campusflow import tickets


class TestTicketCreation(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
        )
        self.temp_file.close()

        tickets.FilePath = self.temp_file.name
        tickets.campus.tickets = []

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def read_tickets(self):
        with open(tickets.FilePath, "r") as file:
            return json.load(file)

    def test_generate_first_ticket_id(self):
        self.assertEqual(tickets.GenerateID(), "T001")

    def test_generate_next_ticket_id(self):
        existing_tickets = [
            {"id": "T001"},
            {"id": "T002"},
        ]

        with open(tickets.FilePath, "w") as file:
            json.dump(existing_tickets, file)

        self.assertEqual(tickets.GenerateID(), "T003")

    def test_save_ticket(self):
        ticket = tickets.Ticket(
            id="T001",
            title="Network issue",
            category="network",
            urgency="high",
            affected_users=12,
            priority="Critical",
        )

        tickets.SaveTicket(ticket)

        saved = self.read_tickets()

        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["id"], "T001")
        self.assertEqual(saved[0]["title"], "Network issue")
        self.assertEqual(saved[0]["category"], "network")

    def test_create_ticket_with_valid_input(self):
        user_input = [
            "Network failure",
            "Network",
            "High",
            "12",
        ]

        with patch("builtins.input", side_effect=user_input):
            tickets.CreateTickets()

        saved = self.read_tickets()

        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["id"], "T001")
        self.assertEqual(saved[0]["priority"], "Critical")
        self.assertEqual(saved[0]["status"], "Open")

    def test_invalid_category_does_not_create_ticket(self):
        user_input = [
            "Network failure",
            "InvalidCategory",
        ]

        with patch("builtins.input", side_effect=user_input):
            tickets.CreateTickets()

        self.assertEqual(os.path.getsize(tickets.FilePath), 0)
        self.assertEqual(tickets.campus.tickets, [])

    def test_invalid_urgency_does_not_create_ticket(self):
        user_input = [
            "Network failure",
            "Network",
            "Urgent",
        ]

        with patch("builtins.input", side_effect=user_input):
            tickets.CreateTickets()

        self.assertEqual(os.path.getsize(tickets.FilePath), 0)
        self.assertEqual(tickets.campus.tickets, [])

    def test_non_numeric_affected_users_is_rejected(self):
        user_input = [
            "Network failure",
            "Network",
            "High",
            "many",
        ]

        with patch("builtins.input", side_effect=user_input):
            tickets.CreateTickets()

        self.assertEqual(os.path.getsize(tickets.FilePath), 0)
        self.assertEqual(tickets.campus.tickets, [])

    def test_zero_affected_users_is_rejected(self):
        user_input = [
            "Network failure",
            "Network",
            "High",
            "0",
        ]

        with patch("builtins.input", side_effect=user_input):
            tickets.CreateTickets()

        self.assertEqual(os.path.getsize(tickets.FilePath), 0)
        self.assertEqual(tickets.campus.tickets, [])


class TestTicketAssignment(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
        )
        self.temp_file.close()

        tickets.FilePath = self.temp_file.name
        tickets.campus.tickets = []

        self.ticket = {
            "id": "T001",
            "title": "Network failure",
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
        with open(tickets.FilePath, "w") as file:
            json.dump([self.ticket.copy()], file, indent=4)

    def read_ticket(self):
        with open(tickets.FilePath, "r") as file:
            return json.load(file)[0]

    def run_assignment(self, ticket_id, technician):
        with patch(
            "builtins.input",
            side_effect=[ticket_id, technician],
        ):
            tickets.AssignTicket()

    def test_assign_open_ticket(self):
        self.run_assignment("T001", "Mary")

        saved = self.read_ticket()

        self.assertEqual(saved["assigned_to"], "Mary")
        self.assertEqual(saved["status"], "open")

    def test_ticket_id_is_case_insensitive(self):
        self.run_assignment("t001", "Mary")

        saved = self.read_ticket()

        self.assertEqual(saved["assigned_to"], "Mary")

    def test_blank_technician_is_rejected(self):
        self.run_assignment("T001", "   ")

        saved = self.read_ticket()

        self.assertIsNone(saved["assigned_to"])

    def test_missing_ticket_is_rejected(self):
        self.run_assignment("T999", "Mary")

        saved = self.read_ticket()

        self.assertEqual(saved["id"], "T001")
        self.assertIsNone(saved["assigned_to"])

    def test_resolved_ticket_cannot_be_assigned(self):
        self.ticket["status"] = "resolved"
        self.save_tickets()

        self.run_assignment("T001", "Mary")

        saved = self.read_ticket()

        self.assertIsNone(saved["assigned_to"])
        self.assertEqual(saved["status"], "resolved")


if __name__ == "__main__":
    unittest.main()

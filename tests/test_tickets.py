import unittest
from copy import deepcopy
from unittest.mock import patch

from campusflow import tickets, storage
from campus_test_support import CampusTestSetup


class TestTicketCreation(CampusTestSetup, unittest.TestCase):
    def test_generate_first_ticket_id(self):
        self.assertEqual(tickets.GenerateID(), "T001")

    def test_generate_next_ticket_id(self):
        self.prepare_ticket()
        second = deepcopy(self.ticket)
        second["ID"] = "T002"
        second_event = deepcopy(self.events[0])
        second_event.update(event_id="E002", ticket_id="T002")
        self.write_data([self.ticket, second], self.events + [second_event])
        storage.load_json(tickets.campus)
        self.assertEqual(tickets.GenerateID(), "T003")
        self.assertEqual([t["ID"] for t in tickets.campus.tickets], ["T001", "T002"])

    def test_save_ticket(self):
        ticket = tickets.Ticket(**self.ticket)
        self.assertTrue(tickets.SaveTicket(ticket, "Test Operator"))
        data = self.read_data()
        self.assertEqual(data["tickets"], [self.ticket])
        self.assertEqual(len(data["events"]), 1)
        event = data["events"][0]
        self.assertEqual(event["event_type"], "CREATE")
        self.assertEqual(event["timestamp"], ticket.created_at)
        self.assertEqual(event["actor"], "Test Operator")

    def test_create_ticket_with_valid_input(self):
        answers = ["Network failure", "Network", "High", "12", "Test Operator"]
        with patch.object(tickets, "confirm_ticket_creation", return_value=True) as confirm:
            with patch("builtins.input", side_effect=answers):
                tickets.CreateTickets(now=self.now)
        confirm.assert_called_once_with("Network failure", "network")
        data = self.read_data()
        self.assertEqual(len(data["tickets"]), 1)
        self.assertEqual(data["tickets"][0]["ID"], "T001")
        self.assertEqual(data["tickets"][0]["priority"], "Critical")
        self.assertEqual(data["tickets"][0]["status"], "Open")
        self.assertEqual(data["events"][0]["timestamp"], self.now.isoformat())

    def check_rejected_input(self, answers):
        before = self.read_data()
        with patch("builtins.input", side_effect=answers):
            tickets.CreateTickets(now=self.now)
        self.assert_state(before)

    def test_invalid_category_does_not_create_ticket(self):
        self.check_rejected_input(["Network failure", "InvalidCategory"])

    def test_invalid_urgency_does_not_create_ticket(self):
        self.check_rejected_input(["Network failure", "Network", "Urgent"])

    def test_non_numeric_affected_users_is_rejected(self):
        self.check_rejected_input(["Network failure", "Network", "High", "many"])

    def test_zero_affected_users_is_rejected(self):
        self.check_rejected_input(["Network failure", "Network", "High", "0"])

    def test_cancel_duplicate_creates_nothing(self):
        self.prepare_ticket()
        storage.load_json(tickets.campus)
        before = self.read_data()
        with patch.object(tickets, "confirm_ticket_creation", return_value=False) as confirm:
            with patch("builtins.input", side_effect=["Network issue", "network", "high", "12"]):
                tickets.CreateTickets(now=self.now)
        confirm.assert_called_once()
        self.assert_state(before)

    def test_save_failure_restores_memory(self):
        before = self.read_data()
        with patch.object(storage, "save_json", side_effect=OSError("Disk failure")) as save:
            self.assertFalse(tickets.SaveTicket(tickets.Ticket(**self.ticket), "Test Operator"))
        save.assert_called_once()
        self.assert_state(before)

    def test_creation_with_missing_file(self):
        import os
        os.remove(storage.FilePath)
        self.assertTrue(tickets.SaveTicket(tickets.Ticket(**self.ticket), "Test Operator"))
        self.assertEqual(self.read_data()["tickets"][0]["ID"], "T001")


class TestTicketAssignment(CampusTestSetup, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.prepare_ticket()

    def run_assignment(self, ticket_id, technician):
        with patch("builtins.input", side_effect=[ticket_id, technician, "Test Operator"]):
            with patch("builtins.print") as output:
                tickets.AssignTicket(now=self.now)
        return output

    def test_assign_open_ticket(self):
        self.run_assignment("T001", "Mary")
        data = self.read_data()
        self.assertEqual(data["tickets"][0]["assigned_to"], "Mary")
        self.assertEqual(data["tickets"][0]["status"], "Open")
        self.assertEqual(data["tickets"][0]["updated_at"], self.now.isoformat())
        self.assertEqual(len(data["events"]), 2)
        self.assertEqual(data["events"][-1]["timestamp"], self.now.isoformat())
        self.assertEqual(data["events"][-1]["event_type"], "ASSIGN")

    def test_ticket_id_is_case_insensitive(self):
        self.run_assignment("t001", "Mary")
        self.assertEqual(self.read_data()["tickets"][0]["assigned_to"], "Mary")

    def test_blank_technician_is_rejected(self):
        before = self.read_data()
        output = self.run_assignment("T001", "   ")
        output.assert_any_call("Error: Technician name cannot be blank.")
        self.assert_state(before)

    def test_missing_ticket_is_rejected(self):
        before = self.read_data()
        output = self.run_assignment("T999", "Mary")
        output.assert_any_call("Error: Ticket T999 not found.")
        self.assert_state(before)

    def test_resolved_ticket_cannot_be_assigned(self):
        self.prepare_ticket("resolved")
        before = self.read_data()
        output = self.run_assignment("T001", "Mary")
        output.assert_any_call("Error: Reopen the ticket before assigning it.")
        self.assert_state(before)


if __name__ == "__main__":
    unittest.main()
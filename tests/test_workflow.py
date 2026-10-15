import os
import unittest
from copy import deepcopy
from unittest.mock import patch

from campusflow import workflow, storage
from campus_test_support import CampusTestSetup


class TestWorkQueueAndWorkFlow(CampusTestSetup, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.prepare_ticket()

    def run_workflow(self, answers):
        with patch("builtins.input", side_effect=answers):
            with patch("builtins.print") as output:
                workflow.WorkFlow(now=self.now)
        return output

    def queue_output(self):
        with patch("builtins.print") as output:
            workflow.WorkQueue()
        return str(output.call_args_list)

    def check_event(self, kind, old_events):
        data = self.read_data()
        self.assertEqual(len(data["events"]), len(old_events) + 1)
        self.assertEqual(data["events"][:-1], old_events)
        event = data["events"][-1]
        self.assertEqual(event["event_type"], kind)
        self.assertEqual(event["actor"], "Test Operator")
        self.assertEqual(event["timestamp"], self.now.isoformat())

    def test_queue_shows_only_open_tickets(self):
        self.assertIn("T001", self.queue_output())
        self.prepare_ticket("in_progress")
        self.assertNotIn("T001", self.queue_output())
        # Rebuild a separate valid resolved fixture.
        self.ticket["status"] = "resolved"
        self.ticket["updated_at"] = "2026-10-15T10:30:00+00:00"
        self.add_event("RESOLVE", "in_progress", "resolved", self.ticket["updated_at"])
        self.write_data([self.ticket], self.events)
        self.assertNotIn("T001", self.queue_output())

    def test_queue_sorts_by_priority(self):
        second = deepcopy(self.ticket)
        second.update(ID="T002", priority="Low", urgency="low", affected_users=1,
                      due_at="2026-10-17T10:00:00+00:00")
        event = deepcopy(self.events[0])
        event.update(event_id="E002", ticket_id="T002")
        self.write_data([second, self.ticket], self.events + [event])
        output = self.queue_output()
        self.assertLess(output.index("T001"), output.index("T002"))

    def test_queue_breaks_ties_by_id(self):
        second = deepcopy(self.ticket)
        second["ID"] = "T002"
        event = deepcopy(self.events[0])
        event.update(event_id="E002", ticket_id="T002")
        self.write_data([second, self.ticket], self.events + [event])
        output = self.queue_output()
        self.assertLess(output.index("T001"), output.index("T002"))

    def test_queue_shows_unassigned_tickets(self):
        self.assertIn("Unassigned", self.queue_output())

    def test_queue_handles_missing_file(self):
        os.remove(storage.FilePath)
        self.assertIn("Error: Tickets file is empty or missing.", self.queue_output())

    def test_queue_handles_empty_file(self):
        with open(storage.FilePath, "w"):
            pass
        self.assertIn("Error: Tickets file is empty or missing.", self.queue_output())

    def test_queue_rejects_malformed_string_tickets(self):
        storage.load_json(workflow.campus)
        before_tickets = deepcopy(workflow.campus.tickets)
        before_events = deepcopy(workflow.campus.events)
        self.write_data([self.ticket, "rogue_string"], self.events)
        before_file = self.read_data()
        self.assertIn("Could not load tickets:", self.queue_output())
        self.assertEqual(workflow.campus.tickets, before_tickets)
        self.assertEqual(workflow.campus.events, before_events)
        self.assertEqual(self.read_data(), before_file)

    def test_open_ticket_can_be_started_when_assigned(self):
        self.prepare_ticket(assigned=True)
        self.run_workflow(["T001", "in_progress", "Test Operator"])
        self.assertEqual(self.read_data()["tickets"][0]["status"], "in_progress")
        self.check_event("START", self.events)

    def test_in_progress_ticket_can_be_resolved(self):
        self.prepare_ticket("in_progress")
        self.run_workflow(["T001", "resolved", "Test Operator"])
        self.assertEqual(self.read_data()["tickets"][0]["status"], "resolved")
        self.check_event("RESOLVE", self.events)

    def test_resolved_ticket_can_be_reopened(self):
        self.prepare_ticket("resolved")
        self.run_workflow(["T001", "open", "Test Operator"])
        ticket = self.read_data()["tickets"][0]
        self.assertEqual(ticket["status"], "open")
        self.assertEqual(ticket["created_at"], self.ticket["created_at"])
        self.assertEqual(ticket["updated_at"], self.now.isoformat())
        self.assertEqual(ticket["due_at"], "2026-10-16T11:00:00+00:00")
        self.assertEqual(ticket["escalation_cycle"], 1)
        self.assertIsNone(ticket["escalated_cycle"])
        self.check_event("REOPEN", self.events)

    def check_rejection(self, answers, message):
        before = self.read_data()
        output = self.run_workflow(answers)
        output.assert_any_call(message)
        self.assert_state(before)

    def test_unassigned_ticket_cannot_be_started(self):
        self.check_rejection(["T001", "in_progress"], "Error: Ticket has not been assigned.")

    def test_open_ticket_cannot_skip_to_resolved(self):
        self.check_rejection(["T001", "resolved"], "Error: Must follow workflow.")

    def test_resolved_ticket_must_be_reopened_first(self):
        self.prepare_ticket("resolved")
        self.check_rejection(["T001", "in_progress"], "Error: Reopen the ticket first.")

    def test_unknown_ticket_id_is_rejected(self):
        self.check_rejection(["UNKNOWN"], "Error: No match found.")

    def test_invalid_status_is_rejected(self):
        self.check_rejection(["T001", "invalid"], "Error: Unrecognized workflow.")

    def test_save_failure_restores_state(self):
        self.prepare_ticket("resolved")
        before = self.read_data()
        with patch.object(storage, "save_json", side_effect=OSError("Disk failure")) as save:
            output = self.run_workflow(["T001", "open", "Test Operator"])
        save.assert_called_once()
        output.assert_any_call("Transition failed; changes rolled back: Disk failure")
        self.assert_state(before)


if __name__ == "__main__":
    unittest.main()
import json
import os
import tempfile
import unittest
from copy import deepcopy
from unittest.mock import patch

from campusflow.show_ticket import CampusFlow
from campusflow.storage import load_json, save_json


class TestCampusFlowPersistence(unittest.TestCase):

    def setUp(self):
        self.original_directory = os.getcwd()
        self.temp_directory = tempfile.TemporaryDirectory()

        self.addCleanup(self.temp_directory.cleanup)
        self.addCleanup(os.chdir, self.original_directory)
        os.chdir(self.temp_directory.name)

        self.path_patch = patch(
            "campusflow.storage.FilePath", "ticket.json"
        )
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

        self.campus = CampusFlow()

        self.sample_tickets = [
            {
                "ID": "T001",
                "title": "Wi-Fi Problem",
                "category": "network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "Critical",
                "status": "open",
                "assigned_to": None,
                "created_at": "2026-10-15T10:00:00+00:00",
                "updated_at": "2026-10-15T10:00:00+00:00",
                "due_at": "2026-10-15T11:00:00+00:00",
                "escalation_cycle": 0,
                "escalated_cycle": None,
            },
            {
                "ID": "T002",
                "title": "Broken Laptop",
                "category": "hardware",
                "urgency": "low",
                "affected_users": 1,
                "priority": "Low",
                "status": "open",
                "assigned_to": None,
                "created_at": "2026-10-15T10:00:00+00:00",
                "updated_at": "2026-10-15T10:00:00+00:00",
                "due_at": "2026-10-17T10:00:00+00:00",
                "escalation_cycle": 0,
                "escalated_cycle": None,
            },
        ]

        self.sample_events = [
            {
                "event_id": f"E{number:03d}",
                "ticket_id": ticket["ID"],
                "event_type": "CREATE",
                "actor": "Test Operator",
                "timestamp": ticket["created_at"],
                "before_status": None,
                "after_status": "open",
                "details": "Ticket created",
            }
            for number, ticket in enumerate(
                self.sample_tickets, start=1
            )
        ]

    def populate_state(self):
        self.campus.tickets = deepcopy(self.sample_tickets)
        self.campus.events = deepcopy(self.sample_events)

    def snapshot(self):
        return deepcopy((self.campus.tickets, self.campus.events))

    def test_missing_json_file(self):
        self.populate_state()
        before = self.snapshot()

        with self.assertRaises(FileNotFoundError):
            load_json(self.campus)

        self.assertEqual(self.snapshot(), before)

    def test_save_tickets(self):
        self.populate_state()

        save_json(self.campus)

        self.assertTrue(os.path.exists("ticket.json"))

        with open("ticket.json", "r", encoding="utf-8") as file:
            saved = json.load(file)

        self.assertEqual(saved["schema_version"], 2)
        self.assertEqual(saved["tickets"], self.sample_tickets)
        self.assertEqual(saved["events"], self.sample_events)

    def test_reload_tickets(self):
        self.populate_state()
        save_json(self.campus)

        new_campus = CampusFlow()
        load_json(new_campus)

        self.assertEqual(new_campus.tickets, self.sample_tickets)
        self.assertEqual(new_campus.events, self.sample_events)

    def test_malformed_json(self):
        with open("ticket.json", "w", encoding="utf-8") as file:
            file.write("{invalid JSON")

        with self.assertRaises(ValueError):
            load_json(self.campus)

    def test_preserve_existing_tickets(self):
        self.populate_state()
        before = self.snapshot()

        with open("ticket.json", "w", encoding="utf-8") as file:
            file.write("{invalid JSON")

        with self.assertRaises(ValueError):
            load_json(self.campus)

        self.assertEqual(self.snapshot(), before)

    def test_duplicate_ticket_ids(self):
        self.populate_state()
        before = self.snapshot()

        duplicate_tickets = deepcopy(self.sample_tickets)
        duplicate_tickets[1]["ID"] = duplicate_tickets[0]["ID"]

        data = {
            "schema_version": 2,
            "tickets": duplicate_tickets,
            "events": [],
        }

        with open("ticket.json", "w", encoding="utf-8") as file:
            json.dump(data, file)

        with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
            load_json(self.campus)

        self.assertEqual(self.snapshot(), before)

    def test_invalid_save_preserves_good_file(self):
        self.populate_state()
        save_json(self.campus)

        with open("ticket.json", "rb") as file:
            original_file = file.read()

        self.campus.tickets[0]["created_at"] = "2026-10-15T10:00:00"

        with self.assertRaises(ValueError):
            save_json(self.campus)

        with open("ticket.json", "rb") as file:
            current_file = file.read()

        self.assertEqual(current_file, original_file)
        self.assertFalse(os.path.exists("ticket.json.tmp"))

    def test_replace_failure_preserves_good_file(self):
        self.populate_state()
        save_json(self.campus)

        with open("ticket.json", "rb") as file:
            original_file = file.read()

        self.campus.tickets[0]["title"] = "Updated Wi-Fi Problem"
        memory_before_save = self.snapshot()

        with patch(
            "campusflow.storage.os.replace",
            side_effect=OSError("Replacement failed"),
        ) as replace:
            with self.assertRaises(OSError):
                save_json(self.campus)

        replace.assert_called_once_with(
            "ticket.json.tmp", "ticket.json"
        )

        with open("ticket.json", "rb") as file:
            self.assertEqual(file.read(), original_file)

        self.assertEqual(self.snapshot(), memory_before_save)
        self.assertFalse(os.path.exists("ticket.json.tmp"))

    def test_invalid_cycle_markers_are_rejected(self):
        invalid_markers = [
            (-1, None),
            (True, None),
            (0, True),
            (0, 1),
            (1, 0),
        ]

        for cycle, escalated in invalid_markers:
            with self.subTest(cycle=cycle, escalated=escalated):
                self.populate_state()

                self.campus.tickets[0]["escalation_cycle"] = cycle
                self.campus.tickets[0]["escalated_cycle"] = escalated

                with self.assertRaisesRegex(ValueError, "cycle"):
                    save_json(self.campus)

    def test_invalid_cycle_load_preserves_memory(self):
        self.populate_state()
        before = self.snapshot()

        bad_data = {
            "schema_version": 2,
            "tickets": deepcopy(self.sample_tickets),
            "events": deepcopy(self.sample_events),
        }

        bad_data["tickets"][0]["escalation_cycle"] = -1

        with open("ticket.json", "w", encoding="utf-8") as file:
            json.dump(bad_data, file)

        with self.assertRaisesRegex(ValueError, "cycle"):
            load_json(self.campus)

        self.assertEqual(self.snapshot(), before)

    def test_invalid_priority_and_status_are_rejected(self):
        invalid_values = [
            ("priority", "urgent"),
            ("priority", None),
            ("status", "closed"),
            ("status", 123),
        ]

        for field, value in invalid_values:
            with self.subTest(field=field, value=value):
                self.populate_state()
                self.campus.tickets[0][field] = value

                with self.assertRaisesRegex(ValueError, field):
                    save_json(self.campus)

    def test_reopened_ticket_survives_restart(self):
        self.populate_state()
        ticket = self.campus.tickets[0]

        ticket.update({
            "status": "open",
            "assigned_to": "Alex",
            "updated_at": "2026-10-16T10:00:00+00:00",
            "due_at": "2026-10-16T11:00:00+00:00",
            "escalation_cycle": 1,
            "escalated_cycle": None,
        })

        changes = [
            (
                "E003", "ASSIGN", "open", "open",
                "2026-10-15T10:05:00+00:00",
            ),
            (
                "E004", "START", "open", "in_progress",
                "2026-10-15T10:10:00+00:00",
            ),
            (
                "E005", "RESOLVE", "in_progress", "resolved",
                "2026-10-15T10:30:00+00:00",
            ),
            (
                "E006", "REOPEN", "resolved", "open",
                "2026-10-16T10:00:00+00:00",
            ),
        ]

        for event_id, kind, before, after, timestamp in changes:
            self.campus.events.append({
                "event_id": event_id,
                "ticket_id": "T001",
                "event_type": kind,
                "actor": "Test Operator",
                "timestamp": timestamp,
                "before_status": before,
                "after_status": after,
                "details": f"{kind} completed.",
            })

        expected = self.snapshot()
        save_json(self.campus)

        restarted = CampusFlow()
        load_json(restarted)

        self.assertEqual(
            (restarted.tickets, restarted.events),
            expected,
        )

    def test_duplicate_escalation_history_is_rejected(self):
        self.populate_state()
        before = self.snapshot()

        data = {
            "schema_version": 2,
            "tickets": deepcopy(self.sample_tickets),
            "events": deepcopy(self.sample_events),
        }

        data["tickets"][0]["escalated_cycle"] = 0

        for event_id, timestamp in (
            ("E003", "2026-10-15T11:01:00+00:00"),
            ("E004", "2026-10-15T11:02:00+00:00"),
        ):
            data["events"].append({
                "event_id": event_id,
                "ticket_id": "T001",
                "event_type": "ESCALATE",
                "actor": "Test Operator",
                "timestamp": timestamp,
                "before_status": "open",
                "after_status": "open",
                "details": "Overdue escalation for SLA cycle 0",
            })

        with open("ticket.json", "w", encoding="utf-8") as file:
            json.dump(data, file)

        with self.assertRaisesRegex(
            ValueError, "Multiple escalation events"
        ):
            load_json(self.campus)

        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
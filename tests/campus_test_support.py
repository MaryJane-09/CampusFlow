import json
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import patch

from campusflow import storage
from campusflow.show_ticket import campus


class CampusTestSetup:
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = os.path.join(directory.name, "ticket.json")
        path_patch = patch.object(storage, "FilePath", path)
        path_patch.start()
        self.addCleanup(path_patch.stop)
        for name in ("tickets", "events"):
            state_patch = patch.object(campus, name, [])
            state_patch.start()
            self.addCleanup(state_patch.stop)
        self.now = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)
        self.ticket = {
            "ID": "T001", "title": "Network issue", "category": "network",
            "urgency": "high", "affected_users": 12, "priority": "Critical",
            "status": "Open", "assigned_to": None,
            "created_at": "2026-10-15T10:00:00+00:00",
            "updated_at": "2026-10-15T10:00:00+00:00",
            "due_at": "2026-10-15T11:00:00+00:00",
            "escalation_cycle": 0, "escalated_cycle": None,
        }
        self.events = []
        self.add_event("CREATE", None, "Open", self.ticket["created_at"])
        self.write_data([], [])

    def add_event(self, kind, before, after, timestamp):
        self.events.append({
            "event_id": f"E{len(self.events) + 1:03d}", "ticket_id": "T001",
            "event_type": kind, "actor": "Test Operator", "timestamp": timestamp,
            "before_status": before, "after_status": after, "details": kind,
        })

    def prepare_ticket(self, status="open", assigned=False):
        if assigned or status != "open":
            self.ticket["assigned_to"] = "Alex"
            self.ticket["updated_at"] = "2026-10-15T10:05:00+00:00"
            self.add_event("ASSIGN", "Open", "Open", self.ticket["updated_at"])
        if status in ("in_progress", "resolved"):
            self.ticket["status"] = "in_progress"
            self.ticket["updated_at"] = "2026-10-15T10:10:00+00:00"
            self.add_event("START", "Open", "in_progress", self.ticket["updated_at"])
        if status == "resolved":
            self.ticket["status"] = "resolved"
            self.ticket["updated_at"] = "2026-10-15T10:30:00+00:00"
            self.add_event("RESOLVE", "in_progress", "resolved", self.ticket["updated_at"])
        self.write_data([self.ticket], self.events)

    def write_data(self, tickets, events):
        with open(storage.FilePath, "w", encoding="utf-8") as file:
            json.dump({"schema_version": 2, "tickets": tickets, "events": events}, file)

    def read_data(self):
        with open(storage.FilePath, encoding="utf-8") as file:
            return json.load(file)

    def assert_state(self, expected):
        self.assertEqual(self.read_data(), expected)
        self.assertEqual(campus.tickets, expected["tickets"])
        self.assertEqual(campus.events, expected["events"])
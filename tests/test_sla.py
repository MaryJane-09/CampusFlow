import unittest
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import Mock
from campusflow.sla import calculate_due_at, is_overdue, escalate_overdue


class SLATest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 10, 14, 10, tzinfo=timezone.utc)
        self.now = datetime(2026, 10, 15, 12, 1, tzinfo=timezone.utc)
        self.ticket = {
            "ID": "T001", "status": "Open", "priority": "Critical",
            "assigned_to": None, "due_at": "2026-10-15T12:00:00+00:00",
            "escalation_cycle": 0, "escalated_cycle": None,
        }
        self.events = []

    def test_critical_due_at(self):
        self.assertEqual(calculate_due_at("critical", self.start), datetime(2026, 10, 14, 11, tzinfo=timezone.utc))

    def test_high_due_at(self):
        self.assertEqual(calculate_due_at("high", self.start), datetime(2026, 10, 14, 14, tzinfo=timezone.utc))

    def test_medium_due_at(self):
        self.assertEqual(calculate_due_at("medium", self.start), datetime(2026, 10, 15, 10, tzinfo=timezone.utc))

    def test_low_due_at(self):
        self.assertEqual(calculate_due_at("low", self.start), datetime(2026, 10, 16, 10, tzinfo=timezone.utc))

    def test_not_overdue_at_deadline(self):
        self.assertFalse(is_overdue(self.ticket, self.now.replace(minute=0)))

    def test_overdue_after_deadline(self):
        self.assertTrue(is_overdue(self.ticket, self.now))

    def test_resolved_ticket_not_overdue(self):
        self.ticket["status"] = "Resolved"
        self.assertFalse(is_overdue(self.ticket, self.now))

    def test_invalid_ticket_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "dictionary"):
            is_overdue("not_a_dict", self.now)

    def test_already_escalated_ticket_is_unchanged(self):
        self.ticket["escalated_cycle"] = 0
        before = deepcopy(self.ticket)
        recorder = Mock()
        result = escalate_overdue([self.ticket], self.events, self.now, "Engineer A", event_recorder=recorder)
        self.assertEqual(result, {"newly_escalated": 0, "already_escalated": 1})
        self.assertEqual(self.ticket, before)
        self.assertEqual(self.events, [])
        recorder.assert_not_called()

    def test_escalation_happens_once_per_cycle(self):
        before = deepcopy(self.ticket)
        def append_event(**values):
            event = {key: value for key, value in values.items() if key != "now"}
            event["event_id"] = "E001"
            event["timestamp"] = values["now"].isoformat()
            self.events.append(event)
            return event
        recorder = Mock(side_effect=append_event)
        first = escalate_overdue([self.ticket], self.events, self.now, "Engineer A", event_recorder=recorder)
        self.assertEqual(first, {"newly_escalated": 1, "already_escalated": 0})
        expected = deepcopy(before)
        expected["escalated_cycle"] = 0
        self.assertEqual(self.ticket, expected)
        saved_events = deepcopy(self.events)
        later = self.now.replace(hour=13)
        second = escalate_overdue([self.ticket], self.events, later, "Engineer A", event_recorder=recorder)
        self.assertEqual(second, {"newly_escalated": 0, "already_escalated": 1})
        self.assertEqual(self.events, saved_events)
        self.assertEqual(len(self.events), 1)
        recorder.assert_called_once_with(
            ticket_id="T001", event_type="ESCALATE", actor="Engineer A",
            before_status="Open", after_status="Open",
            details="Overdue escalation for SLA cycle 0", now=self.now,
        )

    def test_recorder_failure_leaves_state_unchanged(self):
        before = deepcopy(self.ticket)
        def fail(**values):
            self.events.append({"partial": True})
            raise RuntimeError("Recording failed")
        recorder = Mock(side_effect=fail)
        with self.assertRaisesRegex(RuntimeError, "Recording failed"):
            escalate_overdue([self.ticket], self.events, self.now, "Engineer A", event_recorder=recorder)
        self.assertEqual(self.ticket, before)
        self.assertEqual(self.events, [])
        recorder.assert_called_once()


if __name__ == "__main__":
    unittest.main()
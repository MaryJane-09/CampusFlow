import unittest
from campusflow.sla import calculate_due_at, is_overdue, escalate_overdue
from datetime import timezone, datetime
from unittest.mock import Mock

class SLATest(unittest.TestCase):
    def test_critical_due_at(self):
        cycle_start = datetime(year=2026, month=10, day=14, hour=10, minute=0, tzinfo=timezone.utc)
        expected_due_at = datetime(year=2026, month=10, day=14, hour=11, minute=0, tzinfo=timezone.utc)
        sla = calculate_due_at('critical', cycle_start)
        self.assertEqual(sla, expected_due_at)

    def test_high_due_at(self):
        cycle_start = datetime(year=2026, month=10, day=14, hour=10, minute=0, tzinfo=timezone.utc)
        expected_due_at = datetime(year=2026, month=10, day=14, hour=14, minute=0, tzinfo=timezone.utc)
        sla = calculate_due_at('high', cycle_start)
        self.assertEqual(sla, expected_due_at)

    def test_medium_due_at(self):
        cycle_start = datetime(year=2026, month=10, day=14, hour=10, minute=0, tzinfo=timezone.utc)
        expected_due_at = datetime(year=2026, month=10, day=15, hour=10, minute=0, tzinfo=timezone.utc)
        sla = calculate_due_at('medium', cycle_start)
        self.assertEqual(sla, expected_due_at)

    def test_low_due_at(self):
        cycle_start = datetime(year=2026, month=10, day=14, hour=10, minute=0, tzinfo=timezone.utc)
        expected_due_at = datetime(year=2026, month=10, day=16, hour=10, minute=0, tzinfo=timezone.utc)
        sla = calculate_due_at('low', cycle_start)
        self.assertEqual(sla, expected_due_at)


    def test_not_overdue_at_deadline(self):
        ticket = {
            "status": "open",
            "due_at": "2026-10-15T12:00:00+00:00"
        }
    
        now = datetime(year=2026, month=10, day=15, hour=12, minute=0, microsecond=0, tzinfo=timezone.utc)
    
        result = is_overdue(ticket, now)
    
        self.assertFalse(result)

    def test_overdue_after_deadline(self):
        ticket = {
            "status": "open",
            "due_at": "2026-10-15T12:00:00+00:00"
        }

        now = datetime(year=2026, month=10, day=15, hour=12, minute=1, microsecond=0, tzinfo=timezone.utc)
        result = is_overdue(ticket, now)
        self.assertTrue(result)

    def test_resolved_ticket_not_overdue(self):
        ticket = {
            "status": "Resolved",
            "due_at": "2026-10-15T12:00:00+00:00"
        }

        now = datetime(year=2026, month=10, day=15, hour=12, minute=1, microsecond=0, tzinfo=timezone.utc)
        result = is_overdue(ticket, now)
        self.assertFalse(result)

    def test_already_escalated_ticket_is_unchanged(self):
        ticket = {
            "id": "T001",
            "status": "Open",
            "due_at": "2026-10-15T12:00:00+00:00",
            "escalation_cycle": 0,
            "escalated_cycle": 0,
        }
        tickets = [ticket]
        events = []
        original_ticket = ticket.copy()
    
        now = datetime(
            year=2026, month=10, day=15,
            hour=12, minute=1, tzinfo=timezone.utc,
        )
    
        recorder = Mock()

        result = escalate_overdue(
            tickets,
            events,
            now,
            "Engineer A",
            event_recorder=recorder,
        )

        recorder.assert_not_called()
    
        self.assertEqual(result["newly_escalated"], 0)
        self.assertEqual(result["already_escalated"], 1)
        self.assertEqual(tickets, [original_ticket])
        self.assertEqual(events, [])


    def test_escalation_happens_once_per_cycle(self):
        ticket = {
            "id": "T001",
            "status": "Open",
            "priority": "Critical",
            "assigned_to": None,
            "due_at": "2026-10-15T12:00:00+00:00",
            "escalation_cycle": 0,
            "escalated_cycle": None,
        }
        events = []
        original_ticket = ticket.copy()

        now = datetime(
            year=2026, month=10, day=15,
            hour=12, minute=1, tzinfo=timezone.utc,
        )

        event = {
            "event_id": "E001",
            "ticket_id": "T001",
            "event_type": "ESCALATE",
            "actor": "Engineer A",
            "timestamp": now.isoformat(),
            "before_status": "Open",
            "after_status": "Open",
            "details": "Overdue escalation for SLA cycle 0",
        }
        recorder = Mock(return_value=event)

        first_result = escalate_overdue(
            [ticket], events, now, "Engineer A",
            event_recorder=recorder,
        )

        self.assertEqual(
            first_result,
            {"newly_escalated": 1, "already_escalated": 0},
        )
        self.assertEqual(events, [event])

        expected_ticket = original_ticket.copy()
        expected_ticket["escalated_cycle"] = 0
        self.assertEqual(ticket, expected_ticket)

        second_result = escalate_overdue(
            [ticket], events, now, "Engineer A",
            event_recorder=recorder,
        )

        self.assertEqual(
            second_result,
            {"newly_escalated": 0, "already_escalated": 1},
        )
        self.assertEqual(events, [event])
        self.assertEqual(ticket, expected_ticket)
        recorder.assert_called_once_with(
            events=events,
            ticket_id="T001",
            event_type="ESCALATE",
            actor="Engineer A",
            before_status="Open",
            after_status="Open",
            details="Overdue escalation for SLA cycle 0",
            now=now,
        )

    def test_recorder_failure_leaves_state_unchanged(self):
        ticket = {
            "id": "T001",
            "status": "Open",
            "due_at": "2026-10-15T12:00:00+00:00",
            "escalation_cycle": 0,
            "escalated_cycle": None,
        }
        events = []
        original_ticket = ticket.copy()
    
        now = datetime(
            year=2026, month=10, day=15,
            hour=12, minute=1, tzinfo=timezone.utc,
        )
    
        recorder = Mock(side_effect=RuntimeError("Recording failed"))
    
        with self.assertRaisesRegex(RuntimeError, "Recording failed"):
            escalate_overdue(
                [ticket], events, now, "Engineer A",
                event_recorder=recorder,
            )
    
        self.assertEqual(ticket, original_ticket)
        self.assertEqual(events, [])
        recorder.assert_called_once()
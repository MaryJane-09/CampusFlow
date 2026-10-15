import unittest
from campusflow.sla import calculate_due_at, is_overdue
from datetime import timezone, datetime

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
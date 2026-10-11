import re
import unittest
from contextlib import redirect_stdout
from io import StringIO

from campusflow.show_ticket import CampusFlow
from campusflow.reports import generate_report


class TestCampusFlowReports(unittest.TestCase):
    def setUp(self):
        self.campus = CampusFlow()

    def make_ticket(self, ticket_id, status, priority):
        return {
            "ID": ticket_id,
            "title": f"Issue {ticket_id}",
            "category": "Network",
            "urgency": "medium",
            "affected_users": 1,
            "priority": priority,
            "status": status,
            "assigned_to": None,
        }

    def get_report_output(self):
        output = StringIO()
        with redirect_stdout(output):
            generate_report(self.campus)
        return output.getvalue()

    def assert_report_counts(self, expected):
        output = self.get_report_output()
        for label, expected_count in expected.items():
            match = re.search(
                rf"^{re.escape(label)}:\s*(\d+)\s*$", output, flags=re.MULTILINE
            )
            self.assertIsNotNone(match, f"Missing '{label}' in report:\n{output}")
            self.assertEqual(
                int(match.group(1)), expected_count,
                f"Incorrect {label} count in report:\n{output}",
            )

    def test_empty_tickets(self):
        self.assert_report_counts({
            "Total Tickets": 0,
            "Open": 0,
            "In Progress": 0,
            "Resolved": 0,
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
        })

    def test_single_open_critical_ticket(self):
        self.campus.ticket = [self.make_ticket("T001", "open", "critical")]
        self.assert_report_counts({
            "Total Tickets": 1,
            "Open": 1,
            "In Progress": 0,
            "Resolved": 0,
            "Critical": 1,
            "High": 0,
            "Medium": 0,
            "Low": 0,
        })

    def test_five_mixed_tickets(self):
        self.campus.ticket = [
            self.make_ticket("T001", "open", "critical"),
            self.make_ticket("T002", "in_progress", "high"),
            self.make_ticket("T003", "resolved", "medium"),
            self.make_ticket("T004", "open", "high"),
            self.make_ticket("T005", "resolved", "low"),
        ]
        self.assert_report_counts({
            "Total Tickets": 5,
            "Open": 2,
            "In Progress": 1,
            "Resolved": 2,
            "Critical": 1,
            "High": 2,
            "Medium": 1,
            "Low": 1,
        })

    def test_all_tickets_resolved(self):
        self.campus.ticket = [
            self.make_ticket("T001", "resolved", "high"),
            self.make_ticket("T002", "resolved", "medium"),
            self.make_ticket("T003", "resolved", "low"),
        ]
        self.assert_report_counts({
            "Total Tickets": 3,
            "Open": 0,
            "In Progress": 0,
            "Resolved": 3,
            "Critical": 0,
            "High": 1,
            "Medium": 1,
            "Low": 1,
        })

    def test_all_tickets_critical(self):
        self.campus.ticket = [
            self.make_ticket("T001", "open", "critical"),
            self.make_ticket("T002", "in_progress", "critical"),
            self.make_ticket("T003", "resolved", "critical"),
            self.make_ticket("T004", "open", "critical"),
        ]
        self.assert_report_counts({
            "Total Tickets": 4,
            "Open": 2,
            "In Progress": 1,
            "Resolved": 1,
            "Critical": 4,
            "High": 0,
            "Medium": 0,
            "Low": 0,
        })

    def test_report_does_not_modify_tickets(self):
        self.campus.ticket = [
            self.make_ticket("T001", "open", "high"),
            self.make_ticket("T002", "resolved", "low"),
        ]
        import copy
        original_tickets = copy.deepcopy(self.campus.ticket)
        self.get_report_output()
        self.assertEqual(self.campus.ticket, original_tickets)


if __name__ == "__main__":
    unittest.main()
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from campusflow.tickets import GenerateID
from campusflow.sla import is_overdue


class TestCampusFlowRegression(unittest.TestCase):
    def test_generate_id_strict_validation(self):
        state = SimpleNamespace(tickets=["malformed_string"])
        with patch("campusflow.tickets.campus", state):
            with self.assertRaises(ValueError):
                GenerateID()

    def test_is_overdue_type_guard(self):
        now = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "dictionary"):
            is_overdue("not_a_dict", now)


if __name__ == "__main__":
    unittest.main()
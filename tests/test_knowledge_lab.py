import unittest
from unittest.mock import patch
from campusflow.knowledge_lab import QUESTIONS

class TestEngineerBModuleFiles(unittest.TestCase):

    def test_lab_file_question_bank_completeness(self):
        """Verify all 10 official Knowledge Bank questions are fully defined."""
        self.assertEqual(len(QUESTIONS), 10)
        for q in QUESTIONS:
            self.assertIn("id", q)
            self.assertIn("topic", q)
            self.assertIn("options", q)
            self.assertIn("answer", q)
            self.assertIn("revision", q)


if __name__ == "__main__":
    unittest.main()
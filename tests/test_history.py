import unittest
from unittest.mock import patch
import campusflow.history as history  
class TestHistory(unittest.TestCase):

    def test_record_and_show_history(self):
        class MockCampus:
            tickets = [{"ID": "T001"}]
            events = []

        with patch.object(history, "campus", MockCampus()):
            history.record_event("T001", "CREATE", "Admin", None, "open", "Created.")
            
            with patch("builtins.input", return_value="T001"), \
                 patch("builtins.print") as mock_print:
                history.show_history()

            output = "".join(str(c) for c in mock_print.call_args_list)
            self.assertIn("E001", output)
            self.assertIn("CREATE", output)

if __name__ == "__main__":
    unittest.main()
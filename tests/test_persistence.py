
import os
import json
import tempfile
import unittest

from campusflow.storage import load_json, save_json
from campusflow.show_ticket import CampusFlow


class TestCampusFlowPersistence(unittest.TestCase):

    def setUp(self):
        # Create an isolated folder for each test.
        self.original_directory = os.getcwd()
        self.temp_directory = tempfile.TemporaryDirectory()
        os.chdir(self.temp_directory.name)

        self.campus = CampusFlow()

        self.sample_tickets = [
            {"ID": "T001", "title": "Wi-Fi Problem"},
            {"ID": "T002", "title": "Broken Laptop"}
        ]

    def tearDown(self):
        # Restore the original working directory.
        os.chdir(self.original_directory)

        # Remove temporary test files.
        self.temp_directory.cleanup()

    # TEST 1: Missing JSON file
    def test_missing_json_file(self):
        load_json(self.campus)

        self.assertEqual(self.campus.ticket, [])

    # TEST 2: Save tickets to JSON
    def test_save_tickets(self):
        self.campus.ticket = self.sample_tickets

        save_json(self.campus)

        self.assertTrue(os.path.exists("ticket.json"))

        with open("ticket.json", "r") as file:
            saved_tickets = json.load(file)

        self.assertEqual(saved_tickets, self.sample_tickets)

    # TEST 3: Reload saved tickets
    def test_reload_tickets(self):
        self.campus.ticket = self.sample_tickets
        save_json(self.campus)

        new_campus = CampusFlow()
        load_json(new_campus)

        self.assertEqual(new_campus.ticket, self.sample_tickets)

    # TEST 4: Reject malformed JSON
    def test_malformed_json(self):
        with open("ticket.json", "w") as file:
            file.write("{invalid JSON")

        with self.assertRaises(ValueError):
            load_json(self.campus)

    # TEST 5: Failed loading preserves existing tickets
    def test_preserve_existing_tickets(self):
        self.campus.ticket = self.sample_tickets.copy()

        with open("ticket.json", "w") as file:
            file.write("{invalid JSON")

        with self.assertRaises(ValueError):
            load_json(self.campus)

        self.assertEqual(
            self.campus.ticket,
            self.sample_tickets
        )

    # TEST 6: Reject duplicate ticket IDs
    def test_duplicate_ticket_ids(self):
        duplicate_tickets = [
            {"ID": "T001"},
            {"ID": "T001"}
        ]

        with open("ticket.json", "w") as file:
            json.dump(duplicate_tickets, file)

        with self.assertRaises(ValueError):
            load_json(self.campus)


if __name__ == "__main__":
    unittest.main()

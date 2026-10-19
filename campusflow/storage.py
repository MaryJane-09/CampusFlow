import json
import os

from .show_ticket import CampusFlow
from .validation import validate_data


FilePath = "ticket.json"


def load_json(campus: CampusFlow):
    try:
        with open(FilePath, "r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(
            "Ticket file was not found. Current data was not changed."
        ) from None

    except json.JSONDecodeError:
        raise ValueError(
            "Ticket file is empty or corrupted. Current data was not changed."
        ) from None

    validate_data(data)

    campus.tickets = data["tickets"]
    campus.events = data["events"]


def save_json(campus: CampusFlow):
    data = {
        "schema_version": 2,
        "tickets": campus.tickets,
        "events": campus.events,
    }

    validate_data(data)

    target_file = str(FilePath)
    temp_file = target_file + ".tmp"

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, allow_nan=False)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_file, target_file)

    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass
import json
import os

from .validation import validate_data


FilePath = "ticket.json"


def load_json(campus_instance):
    try:
        with open(FilePath, "r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"{FilePath} was not found; current data was not changed."
        ) from error

    except json.JSONDecodeError as error:
        raise ValueError(
            "JSON file is empty or corrupted; current data was not changed."
        ) from error

    validate_data(data)

    campus_instance.tickets = data["tickets"]
    campus_instance.events = data["events"]


def save_json(campus_instance):
    data = {
        "schema_version": 2,
        "tickets": campus_instance.tickets,
        "events": campus_instance.events,
    }

    validate_data(data)

    target_file = os.fspath(FilePath)
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
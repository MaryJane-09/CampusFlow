import json
import os

from .validation import validate_data

FilePath = "ticket.json"

def load_json(campus_instance):
    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        campus_instance.tickets = []
        campus_instance.events = []
        return

    try:
        with open(FilePath, "r") as file:
            data = json.load(file)
            
        if isinstance(data, dict):
            campus_instance.tickets = data.get("tickets", [])
            campus_instance.events = data.get("events", [])
        elif isinstance(data, list):
            campus_instance.tickets = data
            campus_instance.events = []
        else:
            raise ValueError("JSON root must be a dictionary or list object.")
            
    except json.JSONDecodeError:
        raise ValueError("JSON file was corrupted.")



def save_json(campus: CampusFlow):
  target_filename = "ticket.json"
  temp_filename = "ticket.json.tmp"

  try:
    output_data = {
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
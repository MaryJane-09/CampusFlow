import json
from .show_ticket import CampusFlow
import os


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
        "tickets": campus.tickets,
        "events": campus.events,
    }

    with open(temp_filename, "w") as file:
      json.dump(output_data, file, indent=4)
      file.flush()
      os.fsync(file.fileno())

    os.replace(temp_filename, target_filename)

  except (TypeError, OSError):
    if os.path.exists(temp_filename):
      try:
        os.remove(temp_filename)
      except OSError:
        pass

    raise
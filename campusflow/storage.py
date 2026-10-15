import json
from .show_ticket import CampusFlow
import os


def load_json(campus: CampusFlow):
  try:
    with open("ticket.json", "r") as file:
      data = json.load(file)

      if not isinstance(data, dict):
        raise ValueError("JSON root must be a dictionary object")

      if data.get("schema_version") != 2:
        raise ValueError("Unsupported or missing schema_version (expected 2)")

      tickets_list = data.get("tickets")
      events_list = data.get("events")

      if not isinstance(tickets_list, list):
        raise ValueError("'tickets' field must be a list")
      if not isinstance(events_list, list):
        raise ValueError("'events' field must be a list")


      seen_ticket_ids = set()
      for ticket in tickets_list:
        if not isinstance(ticket, dict):
          raise ValueError("Each ticket record must be a dictionary")

        ticket_id = ticket.get("id", ticket.get("ID"))
        if not ticket_id:
          raise ValueError("Missing ID field in ticket record")
        if ticket_id in seen_ticket_ids:
          raise ValueError(f"Duplicate ticket ID found: {ticket_id}")
        seen_ticket_ids.add(ticket_id)

      seen_event_ids = set()
      for event in events_list:
        if not isinstance(event, dict):
          raise ValueError("Each event record must be a dictionary")

        event_id = event.get("event_id")
        if not event_id:
          raise ValueError("Missing event_id field in event record")
        if event_id in seen_event_ids:
          raise ValueError(f"Duplicate event ID found: {event_id}")
        seen_event_ids.add(event_id)

      campus.tickets = tickets_list
      campus.events = events_list

  except FileNotFoundError:
    campus.tickets = []
    campus.events = []
  except json.JSONDecodeError:
    raise ValueError("This file is malformed or invalid JSON")


import json
import os
from .show_ticket import CampusFlow


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
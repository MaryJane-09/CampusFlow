import json
from .show_ticket import CampusFlow

def load_json(campus: CampusFlow):
    try:
        with open("ticket.json", "r") as file:
            existing_file = json.load(file)
            if not isinstance(existing_file, list):
                raise ValueError("file must be inside a list")
            for existing in existing_file:
                if not isinstance(existing, dict):
                    raise ValueError("each ticket record must be a dictionary")
            
            seen_id = set()
            for record in existing_file:
                
                record_id = record.get("id", record.get("ID"))

                if record_id is None or record_id == "":
                    raise ValueError("Missing ID field in record")

                
                if record_id in seen_id:
                    raise ValueError("Already exist")
                seen_id.add(record_id)

            campus.tickets = existing_file
    except FileNotFoundError:
        campus.tickets = []
    except json.JSONDecodeError:
        raise ValueError("this file is malformed or invalid")


def save_json(campus: CampusFlow):
    try:
        with open("ticket.json", "w") as file:
            json.dump(campus.tickets, file, indent=4)
    except TypeError as e:
        raise TypeError(f"Failed to serialize ticket data to JSON. Original error: {e}") from e
    except OSError as e:
        raise OSError(f"System error while writing 'ticket.json'. Original error: {e}") from e

        
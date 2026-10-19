from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from .show_ticket import campus


@dataclass
class Event:
    event_id: str
    ticket_id: str
    event_type: str
    actor: str
    timestamp: str
    before_status: str | None
    after_status: str
    details: str


def GenerateEventID(prefix="E"):
    numbers = []

    for event in campus.events:
        if not isinstance(event, dict):
            raise ValueError("Each event must be a dictionary.")

        event_id = event.get("event_id")

        if not isinstance(event_id, str):
            raise ValueError("Event ID must be text.")

        if not event_id.startswith(prefix):
            raise ValueError(f"Invalid event ID: {event_id}")

        number_text = event_id[len(prefix):]

        if not number_text.isascii():
            raise ValueError(f"Invalid event ID: {event_id}")

        if not number_text.isdigit():
            raise ValueError(f"Invalid event ID: {event_id}")

        number = int(number_text)

        if number < 1:
            raise ValueError(f"Invalid event ID: {event_id}")

        expected_id = prefix + str(number).zfill(3)

        if event_id != expected_id:
            raise ValueError(f"Invalid event ID format: {event_id}")

        if number in numbers:
            raise ValueError(f"Duplicate event ID: {event_id}")

        numbers.append(number)

    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1

    return prefix + str(next_number).zfill(3)


def record_event(
    ticket_id,
    event_type,
    actor,
    before_status,
    after_status,
    details,
    *,
    now=None,
):
    if not isinstance(actor, str):
        raise ValueError("Operator name must be text.")

    operator_name = actor.strip()

    if operator_name == "":
        raise ValueError("Operator name cannot be empty.")

    if now is None:
        now = datetime.now(timezone.utc)

    if not isinstance(now, datetime):
        raise ValueError("Event time must be a datetime.")

    if now.utcoffset() is None:
        raise ValueError("Event time must include a timezone.")

    event_id = GenerateEventID()
    event_time = now.astimezone(timezone.utc).isoformat()

    new_event = Event(
        event_id=event_id,
        ticket_id=ticket_id,
        event_type=event_type,
        actor=operator_name,
        timestamp=event_time,
        before_status=before_status,
        after_status=after_status,
        details=details,
    )

    event_data = asdict(new_event)
    campus.events.append(event_data)

    return event_data


def history_order(event):
    event_time = datetime.fromisoformat(event["timestamp"])
    event_number = int(event["event_id"][1:])

    return event_time, event_number


def show_history():
    ticket_id = input("Input Ticket ID to view history: ").strip().upper()

    ticket_exists = False

    for ticket in campus.tickets:
        if ticket["ID"].strip().upper() == ticket_id:
            ticket_exists = True
            break

    if not ticket_exists:
        print(f"Error: Ticket {ticket_id} not found.")
        return

    ticket_events = []

    for event in campus.events:
        event_ticket_id = event["ticket_id"].strip().upper()

        if event_ticket_id == ticket_id:
            ticket_events.append(event)

    if not ticket_events:
        print("No history logs or events found for this ticket.")
        return

    ticket_events.sort(key=history_order)

    print(f"\n--- Chronological History for Ticket: {ticket_id} ---")

    for event in ticket_events:
        old_status = event["before_status"]
        new_status = event["after_status"]

        print(f"\nEvent ID:     {event['event_id']}")
        print(f"Action:       {event['event_type']}")
        print(f"Operator:     {event['actor']}")
        print(f"Timestamp:    {event['timestamp']}")
        print(f"Status:       {old_status} → {new_status}")
        print(f"Details:      {event['details']}")
        print("-" * 45)
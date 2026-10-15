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
        events_id = event.get("event_id", "")

        if not events_id.startswith(prefix):
            raise ValueError(
            f"Database Corruption: Event ID '{events_id}' does not start with prefix '{prefix}'."
        )

        numeric_part = events_id[len(prefix):]

        if numeric_part.isdigit() and len(numeric_part) == 3:
            numbers.append(int(numeric_part))
        else:
            raise ValueError(
            f"Database Corruption: Invalid numeric sequence in Event ID '{events_id}'."
        )

    max_num = max(numbers) if numbers else 0
    max_num += 1

    return f"{prefix}{max_num:03d}"


def record_event(ticket_id, event_type, actor, before_status, after_status, details, *, now=None,):
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Operator name cannot be empty.")

    if now is None:
        now = datetime.now(timezone.utc)

    if (
        not isinstance(now, datetime)
        or now.tzinfo is None
        or now.utcoffset() is None
    ):
        raise ValueError("Event time must include a timezone.")

    new_event = Event(
        event_id=GenerateEventID(),
        ticket_id=ticket_id,
        event_type=event_type,
        actor=actor.strip(),
        timestamp=now.astimezone(timezone.utc).isoformat(),
        before_status=before_status,
        after_status=after_status,
        details=details,
    )

    event = asdict(new_event)
    campus.events.append(event)
    return event


def show_history():
  ticket_id_input = input("Input Ticket ID to view history: ").upper().strip()

  ticket_exists = False
  for ticket in campus.tickets:
    current_id = str(ticket.get("id", ticket.get("ID", ""))).strip().upper()
    if current_id == ticket_id_input:
      ticket_exists = True
      break

  if not ticket_exists:
    print(f"Error: Ticket {ticket_id_input} not found.")
    return

  matching_events = []

  for event in campus.events:
    if isinstance(event, dict):
      event_ticket_id = str(event.get("ticket_id", "")).strip().upper()
    else:
      event_ticket_id = str(getattr(event, "ticket_id", "")).strip().upper()

    if event_ticket_id == ticket_id_input:
      matching_events.append(event)

  if not matching_events:
    print("No history logs or events found for this ticket.")
    return

  matching_events.sort(
      key=lambda e: (
          e.get("timestamp", "")
          if isinstance(e, dict)
          else getattr(e, "timestamp", "")
      )
  )

  print(f"\n--- Chronological History for Ticket: {ticket_id_input} ---")

  for event in matching_events:
    if isinstance(event, dict):
      e_id = event.get("event_id")
      e_type = event.get("event_type")
      e_actor = event.get("actor")
      e_time = event.get("timestamp")
      e_before = event.get("before_status")
      e_after = event.get("after_status")
      e_details = event.get("details")
    else:
      e_id = getattr(event, "event_id", "")
      e_type = getattr(event, "event_type", "")
      e_actor = getattr(event, "actor", "")
      e_time = getattr(event, "timestamp", "")
      e_before = getattr(event, "before_status", "None")
      e_after = getattr(event, "after_status", "")
      e_details = getattr(event, "details", "")

    before_str = "None" if e_before is None else str(e_before)
    after_str = "None" if e_after is None else str(e_after)

    print(f"\nEvent ID:     {e_id}")
    print(f"Action:       {e_type}")
    print(f"Operator:     {e_actor}")
    print(f"Timestamp:    {e_time}")
    print(f"Status:       {before_str} → {after_str}")
    print(f"Details:      {e_details}")
    print("-" * 45)
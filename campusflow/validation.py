from datetime import datetime, timedelta

from .history_validation import validate_history
from .sla import calculate_due_at


PRIORITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "resolved")
CATEGORIES = ("network", "hardware", "software", "platform")

EVENT_TRANSITIONS = {
    "CREATE": ((None, "open"),),
    "ASSIGN": (
        ("open", "open"),
        ("in_progress", "in_progress"),
    ),
    "START": (("open", "in_progress"),),
    "RESOLVE": (("in_progress", "resolved"),),
    "REOPEN": (("resolved", "open"),),
    "ESCALATE": (
        ("open", "open"),
        ("in_progress", "in_progress"),
    ),
}


def require_fields(record, fields):
    if not isinstance(record, dict):
        raise ValueError("Each record must be a dictionary.")

    for field in fields:
        if field not in record:
            raise ValueError(f"Missing field: {field}")


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")


def validate_id(value, prefix):
    require_text(value, "ID")
    number = value[len(prefix):]

    if (
        not value.startswith(prefix)
        or not number.isascii()
        or not number.isdigit()
    ):
        raise ValueError(f"Invalid ID: {value}")

    if int(number) < 1 or value != f"{prefix}{int(number):03d}":
        raise ValueError(f"Invalid ID format: {value}")


def validate_utc_timestamp(value, field_name):
    require_text(value, field_name)

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be a valid ISO-8601 timestamp."
        ) from error

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone.")

    if parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must use UTC.")

    return parsed


def validate_ticket_fields(ticket):
    require_fields(ticket, (
        "ID", "title", "category", "urgency", "affected_users",
        "priority", "status", "assigned_to", "created_at",
        "updated_at", "due_at", "escalation_cycle", "escalated_cycle",
    ))

    for field in ("title", "category", "urgency", "priority", "status"):
        require_text(ticket[field], field)

    validate_id(ticket["ID"], "T")


def validate_ticket_values(ticket):
    choices = {
        "category": CATEGORIES,
        "urgency": ("high", "medium", "low"),
        "priority": PRIORITIES,
        "status": STATUSES,
    }

    for field, allowed in choices.items():
        if ticket[field].strip().lower() not in allowed:
            raise ValueError(f"Invalid ticket {field}.")

    users = ticket["affected_users"]
    if type(users) is not int or users < 1:
        raise ValueError("affected_users must be a positive integer.")

    urgency = ticket["urgency"].strip().lower()

    if urgency == "high" and users >= 10:
        expected = "critical"
    elif urgency == "high" or users >= 10:
        expected = "high"
    elif urgency == "medium" or users >= 3:
        expected = "medium"
    else:
        expected = "low"

    if ticket["priority"].strip().lower() != expected:
        raise ValueError("Ticket priority does not match its inputs.")


def validate_assignment(ticket):
    assignee = ticket["assigned_to"]

    if assignee is not None and not isinstance(assignee, str):
        raise ValueError("assigned_to must be text or None.")

    unassigned = (
        assignee is None or assignee.strip().lower() in ("", "none")
    )
    status = ticket["status"].strip().lower()

    if status in ("in_progress", "resolved") and unassigned:
        raise ValueError("Started or resolved tickets need an assignee.")


def validate_ticket_cycle(ticket):
    cycle = ticket["escalation_cycle"]
    escalated = ticket["escalated_cycle"]

    if type(cycle) is not int or cycle < 0:
        raise ValueError("escalation_cycle must be a non-negative integer.")

    if escalated is not None:
        if type(escalated) is not int or escalated != cycle:
            raise ValueError(
                "escalated_cycle must be None or the current cycle."
            )


def validate_ticket_times(ticket):
    created = validate_utc_timestamp(ticket["created_at"], "created_at")
    updated = validate_utc_timestamp(ticket["updated_at"], "updated_at")
    deadline = validate_utc_timestamp(ticket["due_at"], "due_at")

    if updated < created:
        raise ValueError("updated_at cannot precede created_at.")

    if deadline <= created:
        raise ValueError("due_at must follow created_at.")

    if ticket["escalation_cycle"] == 0:
        priority = ticket["priority"].strip().lower()
        expected = calculate_due_at(priority, created)

        if deadline != expected:
            raise ValueError("due_at does not match the first SLA cycle.")


def validate_ticket(ticket):
    validate_ticket_fields(ticket)
    validate_ticket_values(ticket)
    validate_assignment(ticket)
    validate_ticket_cycle(ticket)
    validate_ticket_times(ticket)


def validate_event_transition(event):
    before = event["before_status"]
    after = event["after_status"].strip().lower()

    if before is not None:
        before = before.strip().lower()

    allowed = EVENT_TRANSITIONS[event["event_type"]]

    if (before, after) not in allowed:
        raise ValueError(
            f"Invalid status transition for {event['event_type']}."
        )


def validate_event(event, ticket_ids):
    require_fields(event, (
        "event_id", "ticket_id", "event_type", "actor",
        "timestamp", "before_status", "after_status", "details",
    ))

    validate_id(event["event_id"], "E")
    require_text(event["ticket_id"], "ticket_id")
    require_text(event["actor"], "actor")
    require_text(event["details"], "details")
    require_text(event["event_type"], "event_type")
    validate_utc_timestamp(event["timestamp"], "event timestamp")

    if event["ticket_id"] not in ticket_ids:
        raise ValueError("Event references a ticket that does not exist.")

    if event["event_type"] not in EVENT_TRANSITIONS:
        raise ValueError("Invalid event_type.")

    before = event["before_status"]
    after = event["after_status"]

    if event["event_type"] == "CREATE":
        if before is not None:
            raise ValueError("CREATE before_status must be None.")
    else:
        require_text(before, "before_status")

        if before.strip().lower() not in STATUSES:
            raise ValueError("Invalid before_status.")

    require_text(after, "after_status")

    if after.strip().lower() not in STATUSES:
        raise ValueError("Invalid after_status.")

    validate_event_transition(event)


def validate_data(data):
    require_fields(data, ("schema_version", "tickets", "events"))

    version = data["schema_version"]
    if type(version) is not int or version != 2:
        raise ValueError("schema_version must be the integer 2.")

    if not isinstance(data["tickets"], list):
        raise ValueError("'tickets' must be a list.")

    if not isinstance(data["events"], list):
        raise ValueError("'events' must be a list.")

    ticket_ids = set()

    for ticket in data["tickets"]:
        validate_ticket(ticket)

        if ticket["ID"] in ticket_ids:
            raise ValueError(f"Duplicate ticket ID found: {ticket['ID']}")

        ticket_ids.add(ticket["ID"])

    event_ids = set()

    for event in data["events"]:
        validate_event(event, ticket_ids)

        if event["event_id"] in event_ids:
            raise ValueError(
                f"Duplicate event ID found: {event['event_id']}"
            )

        event_ids.add(event["event_id"])
    validate_history(data["tickets"], data["events"])
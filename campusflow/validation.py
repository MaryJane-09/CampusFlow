from datetime import datetime, timedelta

from .history_validation import validate_history
from .sla import calculate_due_at


PRIORITIES = ["critical", "high", "medium", "low"]
STATUSES = ["open", "in_progress", "resolved"]
CATEGORIES = ["network", "hardware", "software", "platform"]
EVENT_TYPES = ["CREATE", "ASSIGN", "START", "RESOLVE", "REOPEN", "ESCALATE"]


def require_fields(record, fields):
    if not isinstance(record, dict):
        raise ValueError("Each record must be a dictionary.")

    for field in fields:
        if field not in record:
            raise ValueError(f"Missing field: {field}")


def require_text(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be non-empty text.")

    if value.strip() == "":
        raise ValueError(f"{field} must be non-empty text.")


def validate_id(value, prefix):
    require_text(value, "ID")

    if not value.startswith(prefix):
        raise ValueError(f"Invalid ID: {value}")

    number_text = value[len(prefix):]

    if not number_text.isascii():
        raise ValueError(f"Invalid ID: {value}")

    if not number_text.isdigit():
        raise ValueError(f"Invalid ID: {value}")

    number = int(number_text)

    if number < 1:
        raise ValueError(f"Invalid ID format: {value}")

    expected_id = prefix + str(number).zfill(3)

    if value != expected_id:
        raise ValueError(f"Invalid ID format: {value}")


def validate_utc_timestamp(value, field_name):
    require_text(value, field_name)

    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"{field_name} must be a valid ISO-8601 timestamp."
        ) from None

    offset = timestamp.utcoffset()

    if offset is None:
        raise ValueError(f"{field_name} must include a timezone.")

    if offset != timedelta(0):
        raise ValueError(f"{field_name} must use UTC.")

    return timestamp


def validate_ticket_fields(ticket):
    fields = [
        "ID",
        "title",
        "category",
        "urgency",
        "affected_users",
        "priority",
        "status",
        "assigned_to",
        "created_at",
        "updated_at",
        "due_at",
        "escalation_cycle",
        "escalated_cycle",
    ]

    require_fields(ticket, fields)

    text_fields = [
        "title", "category", "urgency", "priority", "status"
    ]

    for field in text_fields:
        require_text(ticket[field], field)

    validate_id(ticket["ID"], "T")


def validate_ticket_values(ticket):
    category = ticket["category"].strip().lower()
    urgency = ticket["urgency"].strip().lower()
    priority = ticket["priority"].strip().lower()
    status = ticket["status"].strip().lower()
    users = ticket["affected_users"]

    if category not in CATEGORIES:
        raise ValueError("Invalid ticket category.")

    if urgency not in ["high", "medium", "low"]:
        raise ValueError("Invalid ticket urgency.")

    if priority not in PRIORITIES:
        raise ValueError("Invalid ticket priority.")

    if status not in STATUSES:
        raise ValueError("Invalid ticket status.")

    if type(users) is not int:
        raise ValueError("affected_users must be a positive integer.")

    if users < 1:
        raise ValueError("affected_users must be a positive integer.")

    if urgency == "high" and users >= 10:
        expected_priority = "critical"
    elif urgency == "high" or users >= 10:
        expected_priority = "high"
    elif urgency == "medium" or users >= 3:
        expected_priority = "medium"
    else:
        expected_priority = "low"

    if priority != expected_priority:
        raise ValueError("Ticket priority does not match its inputs.")


def validate_assignment(ticket):
    assignee = ticket["assigned_to"]
    status = ticket["status"].strip().lower()

    if assignee is None:
        unassigned = True
    else:
        if not isinstance(assignee, str):
            raise ValueError("assigned_to must be text or None.")

        name = assignee.strip().lower()

        if name == "" or name == "none":
            unassigned = True
        else:
            unassigned = False

    if status == "in_progress" or status == "resolved":
        if unassigned:
            raise ValueError(
                "Started or resolved tickets need an assignee."
            )


def validate_ticket_cycle(ticket):
    cycle = ticket["escalation_cycle"]
    escalated = ticket["escalated_cycle"]

    if type(cycle) is not int:
        raise ValueError(
            "escalation_cycle must be a non-negative integer."
        )

    if cycle < 0:
        raise ValueError(
            "escalation_cycle must be a non-negative integer."
        )

    if escalated is not None:
        if type(escalated) is not int:
            raise ValueError(
                "escalated_cycle must be None or the current cycle."
            )

        if escalated != cycle:
            raise ValueError(
                "escalated_cycle must be None or the current cycle."
            )


def validate_ticket_times(ticket):
    created = validate_utc_timestamp(
        ticket["created_at"], "created_at"
    )
    updated = validate_utc_timestamp(
        ticket["updated_at"], "updated_at"
    )
    deadline = validate_utc_timestamp(
        ticket["due_at"], "due_at"
    )

    if updated < created:
        raise ValueError("updated_at cannot precede created_at.")

    if deadline <= created:
        raise ValueError("due_at must follow created_at.")

    if ticket["escalation_cycle"] == 0:
        priority = ticket["priority"].strip().lower()
        expected_deadline = calculate_due_at(priority, created)

        if deadline != expected_deadline:
            raise ValueError(
                "due_at does not match the first SLA cycle."
            )


def validate_ticket(ticket):
    validate_ticket_fields(ticket)
    validate_ticket_values(ticket)
    validate_assignment(ticket)
    validate_ticket_cycle(ticket)
    validate_ticket_times(ticket)


def validate_event_transition(event):
    event_type = event["event_type"]
    before = event["before_status"]
    after = event["after_status"].strip().lower()

    if before is not None:
        before = before.strip().lower()

    valid = False

    if event_type == "CREATE":
        if before is None and after == "open":
            valid = True

    elif event_type == "ASSIGN" or event_type == "ESCALATE":
        if before == "open" or before == "in_progress":
            if after == before:
                valid = True

    elif event_type == "START":
        if before == "open" and after == "in_progress":
            valid = True

    elif event_type == "RESOLVE":
        if before == "in_progress" and after == "resolved":
            valid = True

    elif event_type == "REOPEN":
        if before == "resolved" and after == "open":
            valid = True

    if not valid:
        raise ValueError(
            f"Invalid status transition for {event_type}."
        )


def validate_event(event, ticket_ids):
    fields = [
        "event_id",
        "ticket_id",
        "event_type",
        "actor",
        "timestamp",
        "before_status",
        "after_status",
        "details",
    ]

    require_fields(event, fields)

    validate_id(event["event_id"], "E")
    require_text(event["ticket_id"], "ticket_id")
    require_text(event["event_type"], "event_type")
    require_text(event["actor"], "actor")
    require_text(event["details"], "details")

    validate_utc_timestamp(event["timestamp"], "event timestamp")

    if event["ticket_id"] not in ticket_ids:
        raise ValueError(
            "Event references a ticket that does not exist."
        )

    if event["event_type"] not in EVENT_TYPES:
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
    require_fields(data, ["schema_version", "tickets", "events"])

    version = data["schema_version"]

    if type(version) is not int:
        raise ValueError("schema_version must be the integer 2.")

    if version != 2:
        raise ValueError("schema_version must be the integer 2.")

    tickets = data["tickets"]
    events = data["events"]

    if not isinstance(tickets, list):
        raise ValueError("'tickets' must be a list.")

    if not isinstance(events, list):
        raise ValueError("'events' must be a list.")

    ticket_ids = []

    for ticket in tickets:
        validate_ticket(ticket)
        ticket_id = ticket["ID"]

        if ticket_id in ticket_ids:
            raise ValueError(
                f"Duplicate ticket ID found: {ticket_id}"
            )

        ticket_ids.append(ticket_id)

    event_ids = []

    for event in events:
        validate_event(event, ticket_ids)
        event_id = event["event_id"]

        if event_id in event_ids:
            raise ValueError(
                f"Duplicate event ID found: {event_id}"
            )

        event_ids.append(event_id)

    validate_history(tickets, events)
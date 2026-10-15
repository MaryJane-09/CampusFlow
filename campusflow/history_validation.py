from datetime import datetime

from .sla import calculate_due_at


def event_order(event):
    timestamp = datetime.fromisoformat(event["timestamp"])
    event_number = int(event["event_id"][1:])
    return timestamp, event_number


def check_ticket_history(ticket, events):
    if not events:
        raise ValueError(f"Ticket {ticket['ID']} has no history.")

    events = sorted(events, key=event_order)

    created_at = datetime.fromisoformat(ticket["created_at"])
    updated_at = datetime.fromisoformat(ticket["updated_at"])
    priority = ticket["priority"].strip().lower()

    first = events[0]

    if first["event_type"] != "CREATE":
        raise ValueError("Ticket history must begin with CREATE.")

    if datetime.fromisoformat(first["timestamp"]) != created_at:
        raise ValueError("CREATE timestamp must match created_at.")

    status = "open"
    cycle = 0
    cycle_start = created_at
    escalated = False

    for event in events[1:]:
        event_type = event["event_type"]
        timestamp = datetime.fromisoformat(event["timestamp"])

        if event_type == "CREATE":
            raise ValueError("A ticket cannot have multiple CREATE events.")

        before = event["before_status"].strip().lower()
        after = event["after_status"].strip().lower()

        if before != status:
            raise ValueError(
                f"Event {event['event_id']} does not match previous status."
            )

        if event_type == "REOPEN":
            cycle += 1
            cycle_start = timestamp
            escalated = False

        elif event_type == "ESCALATE":
            deadline = calculate_due_at(priority, cycle_start)

            if timestamp <= deadline:
                raise ValueError("Escalation must happen after the deadline.")

            if escalated:
                raise ValueError(
                    "Multiple escalation events in the same SLA cycle."
                )

            escalated = True

        if event_type != "ESCALATE" and timestamp > updated_at:
            raise ValueError("updated_at precedes a successful ticket change.")

        status = after

    if ticket["status"].strip().lower() != status:
        raise ValueError("Ticket status does not match its history.")

    if ticket["escalation_cycle"] != cycle:
        raise ValueError("escalation_cycle does not match REOPEN history.")

    expected_marker = cycle if escalated else None

    if ticket["escalated_cycle"] != expected_marker:
        raise ValueError("escalated_cycle does not match escalation history.")

    expected_deadline = calculate_due_at(priority, cycle_start)
    actual_deadline = datetime.fromisoformat(ticket["due_at"])

    if actual_deadline != expected_deadline:
        raise ValueError("due_at does not match the current SLA cycle.")


def validate_history(tickets, events):
    history_by_ticket = {}

    for ticket in tickets:
        history_by_ticket[ticket["ID"]] = []

    for event in events:
        history_by_ticket[event["ticket_id"]].append(event)

    for ticket in tickets:
        check_ticket_history(
            ticket,
            history_by_ticket[ticket["ID"]],
        )
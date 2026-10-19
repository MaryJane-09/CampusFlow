from datetime import datetime

from .sla import calculate_due_at


def event_order(event):
    event_time = datetime.fromisoformat(event["timestamp"])
    event_number = int(event["event_id"][1:])

    return event_time, event_number


def check_ticket_history(ticket, events):
    if not events:
        raise ValueError(f"Ticket {ticket['ID']} has no history.")

    ordered_events = sorted(events, key=event_order)

    created_at = datetime.fromisoformat(ticket["created_at"])
    updated_at = datetime.fromisoformat(ticket["updated_at"])
    priority = ticket["priority"].strip().lower()

    first_event = ordered_events[0]
    first_time = datetime.fromisoformat(first_event["timestamp"])

    if first_event["event_type"] != "CREATE":
        raise ValueError("Ticket history must begin with CREATE.")

    if first_time != created_at:
        raise ValueError("CREATE timestamp must match created_at.")

    current_status = "open"
    current_cycle = 0
    cycle_start = created_at
    already_escalated = False

    for position in range(1, len(ordered_events)):
        event = ordered_events[position]

        event_type = event["event_type"]
        event_time = datetime.fromisoformat(event["timestamp"])
        before_status = event["before_status"]
        after_status = event["after_status"]

        if event_type == "CREATE":
            raise ValueError("A ticket cannot have multiple CREATE events.")

        before_status = before_status.strip().lower()
        after_status = after_status.strip().lower()

        if before_status != current_status:
            raise ValueError(
                f"Event {event['event_id']} does not match previous status."
            )

        if event_type == "REOPEN":
            current_cycle += 1
            cycle_start = event_time
            already_escalated = False

        elif event_type == "ESCALATE":
            deadline = calculate_due_at(priority, cycle_start)

            if event_time <= deadline:
                raise ValueError("Escalation must happen after the deadline.")

            if already_escalated:
                raise ValueError(
                    "Multiple escalation events in the same SLA cycle."
                )

            already_escalated = True

        if event_type != "ESCALATE":
            if event_time > updated_at:
                raise ValueError(
                    "updated_at precedes a successful ticket change."
                )

        current_status = after_status

    saved_status = ticket["status"].strip().lower()

    if saved_status != current_status:
        raise ValueError("Ticket status does not match its history.")

    if ticket["escalation_cycle"] != current_cycle:
        raise ValueError("escalation_cycle does not match REOPEN history.")

    if already_escalated:
        expected_marker = current_cycle
    else:
        expected_marker = None

    if ticket["escalated_cycle"] != expected_marker:
        raise ValueError("escalated_cycle does not match escalation history.")

    expected_deadline = calculate_due_at(priority, cycle_start)
    saved_deadline = datetime.fromisoformat(ticket["due_at"])

    if saved_deadline != expected_deadline:
        raise ValueError("due_at does not match the current SLA cycle.")


def validate_history(tickets, events):
    for ticket in tickets:
        ticket_events = []

        for event in events:
            if event["ticket_id"] == ticket["ID"]:
                ticket_events.append(event)

        check_ticket_history(ticket, ticket_events)
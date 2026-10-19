from copy import deepcopy
import os

from . import storage
from .show_ticket import campus
from .history import record_event
from .sla import calculate_due_at, utc_time


def apply_transition(ticket, event_type, actor, before, after, details, now):
    ticket_backup = deepcopy(ticket)
    events_backup = deepcopy(campus.events)

    try:
        ticket["status"] = after
        ticket["updated_at"] = now.isoformat()

        if event_type == "REOPEN":
            deadline = calculate_due_at(ticket["priority"], now)
            new_cycle = ticket["escalation_cycle"] + 1

            ticket["due_at"] = deadline.isoformat()
            ticket["escalation_cycle"] = new_cycle
            ticket["escalated_cycle"] = None

            details = f"Ticket reopened. SLA cycle {new_cycle} started."

        record_event(
            ticket_id=ticket["ID"],
            event_type=event_type,
            actor=actor,
            before_status=before,
            after_status=after,
            details=details,
            now=now,
        )

        expected_count = len(events_backup) + 1

        if len(campus.events) != expected_count:
            raise ValueError("Recorder must append exactly one event.")

        for position in range(len(events_backup)):
            if campus.events[position] != events_backup[position]:
                raise ValueError("Recorder changed existing history.")

        storage.save_json(campus)

    except Exception as error:
        ticket.clear()
        ticket.update(ticket_backup)

        campus.events.clear()
        campus.events.extend(events_backup)

        if isinstance(error, (OSError, TypeError, ValueError, KeyError)):
            print(f"Transition failed; changes rolled back: {error}")
            return False

        raise

    return True


def WorkQueue():
    path = storage.FilePath

    if not os.path.exists(path):
        print("Error: Tickets file is empty or missing.")
        return

    if os.path.getsize(path) == 0:
        print("Error: Tickets file is empty or missing.")
        return

    try:
        storage.load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Could not load tickets: {error}")
        return

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    open_tickets = []

    for ticket in campus.tickets:
        status = ticket["status"].strip().lower()

        if status == "open":
            open_tickets.append(ticket)

    def queue_order(ticket):
        priority = ticket["priority"].strip().lower()
        priority_number = priority_order[priority]
        ticket_number = int(ticket["ID"][1:])

        return priority_number, ticket_number

    open_tickets.sort(key=queue_order)

    if not open_tickets:
        print("No open tickets in the work queue.")
        return

    print(
        f"\n{'ID':<6} {'Title':<20} {'Priority':<10} "
        f"{'Status':<12} {'Assigned To':<15}"
    )
    print("-" * 65)

    for ticket in open_tickets:
        assignee = ticket.get("assigned_to")

        if not assignee:
            assignee = "Unassigned"
        else:
            name = str(assignee).strip().lower()

            if name == "" or name == "none":
                assignee = "Unassigned"

        print(
            f"{ticket['ID']:<6} "
            f"{ticket['title']:<20} "
            f"{ticket['priority']:<10} "
            f"{ticket['status']:<12} "
            f"{assignee:<15}"
        )


def WorkFlow(now=None):
    try:
        storage.load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Could not load tickets: {error}")
        return

    if not campus.tickets:
        print("Error: No tickets found to edit.")
        return

    ticket_id = input("Ticket ID: ").strip().upper()
    target = None

    for ticket in campus.tickets:
        if ticket["ID"].upper() == ticket_id:
            target = ticket
            break

    if target is None:
        print("Error: No match found.")
        return

    new_status = input("Ticket Status: ").strip().lower()
    current_status = target["status"].strip().lower()

    if current_status == "open" and new_status == "open":
        print("Ticket is already open.")
        return

    if current_status == "open" and new_status == "in_progress":
        assignee = target.get("assigned_to")

        if not assignee:
            print("Error: Ticket has not been assigned.")
            return

        name = str(assignee).strip().lower()

        if name == "" or name == "none":
            print("Error: Ticket has not been assigned.")
            return

        event_type = "START"

    elif current_status == "in_progress" and new_status == "resolved":
        event_type = "RESOLVE"

    elif current_status == "resolved" and new_status == "open":
        event_type = "REOPEN"

    elif current_status == "open" and new_status == "resolved":
        print("Error: Must follow workflow.")
        return

    elif current_status == "resolved" and new_status == "in_progress":
        print("Error: Reopen the ticket first.")
        return

    else:
        print("Error: Unrecognized workflow.")
        return

    actor = input("Enter Operator Name: ").strip()

    if not actor:
        print("Error: Operator name cannot be empty.")
        return

    try:
        now = utc_time(now)
    except ValueError as error:
        print(f"Error: {error}")
        return

    details = f"Status changed to {new_status}."

    success = apply_transition(
        target,
        event_type,
        actor,
        current_status,
        new_status,
        details,
        now,
    )

    if success:
        print(f"Ticket {ticket_id} changed to {new_status}.")


if __name__ == "__main__":
    WorkFlow()
    WorkQueue()
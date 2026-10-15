from copy import deepcopy
import os

from . import storage
from .show_ticket import campus
from .history import record_event
from .sla import calculate_due_at, utc_time


def apply_transition(ticket, event_type, actor, before, after, details, now):
    old_ticket = deepcopy(ticket)
    old_events = deepcopy(campus.events)

    try:
        changes = {
            "status": after,
            "updated_at": now.isoformat(),
        }

        if event_type == "REOPEN":
            deadline = calculate_due_at(ticket["priority"], now)
            cycle = ticket["escalation_cycle"] + 1

            changes["due_at"] = deadline.isoformat()
            changes["escalation_cycle"] = cycle
            changes["escalated_cycle"] = None
            details = f"Ticket reopened. SLA cycle {cycle} started."

        record_event(
            ticket_id=ticket["ID"],
            event_type=event_type,
            actor=actor,
            before_status=before,
            after_status=after,
            details=details,
            now=now,
        )

        if len(campus.events) != len(old_events) + 1:
            raise ValueError("Recorder must append exactly one event.")

        if campus.events[:-1] != old_events:
            raise ValueError("Recorder changed existing history.")

        ticket.update(changes)
        storage.save_json(campus)

    except Exception as error:
        ticket.clear()
        ticket.update(old_ticket)
        campus.events[:] = old_events

        if isinstance(error, (OSError, TypeError, ValueError, KeyError)):
            print(f"Transition failed; changes rolled back: {error}")
            return False

        raise

    return True


def WorkQueue():
    path = storage.FilePath

    if not os.path.exists(path) or os.path.getsize(path) == 0:
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

    open_tickets = [
        ticket for ticket in campus.tickets
        if ticket["status"].strip().lower() == "open"
    ]

    def queue_order(ticket):
        priority = ticket["priority"].strip().lower()
        number = int(ticket["ID"][1:])
        return priority_order[priority], number

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

        if (
            not assignee
            or str(assignee).strip().lower() in ("", "none")
        ):
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

        if (not assignee or str(assignee).strip().lower() in ("", "none")):
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

    success = apply_transition(target, event_type, actor, current_status, new_status, f"Status changed to {new_status}.", now,)

    if success:
        print(f"Ticket {ticket_id} changed to {new_status}.")


if __name__ == "__main__":
    WorkFlow()
    WorkQueue()
from .show_ticket import campus
from .history import record_event
from .storage import load_json, save_json
from copy import deepcopy
import json
import os

FilePath = "ticket.json"


def apply_transition(ticket, event_type, actor, before, after, details):
    previous_status = ticket.get("status")
    previous_events = deepcopy(campus.events)

    try:
        ticket["status"] = after

        record_event(
            ticket.get("id", ticket.get("ID")),
            event_type,
            actor,
            before,
            after,
            details,
        )

        save_json(campus)

    except (OSError, TypeError, ValueError) as error:
        ticket["status"] = previous_status
        campus.events = previous_events
        print(f"Transition failed; changes rolled back: {error}")
        return False

    return True


def WorkQueue():
    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        print("Error: Tickets file is empty or missing.")
        return

    with open(FilePath, "r") as file:
        campus.tickets = json.load(file)

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    active_tickets = [
        ticket for ticket in campus.tickets
        if str(ticket.get("status", "")).lower().strip() in ("open", "in_progress")
    ]

    sorted_tickets = sorted(
        active_tickets,
        key=lambda ticket: (
            priority_order.get(str(ticket.get("priority", "")).lower().strip(), 4),
            int(str(ticket.get("id", ticket.get("ID", "T0")))[1:])
        )
    )

    if not sorted_tickets:
        print("No active tickets in the work queue.")
        return

    print(f"\n{'ID':<6} {'Title':<15} {'Priority':<10} {'Status':<12} {'Assigned To':<15}")
    print("-" * 60)
    for ticket in sorted_tickets:
        assignee = ticket.get("assigned_to")

        if not assignee or assignee == "None":
            assignee = "Unassigned"

        print(
            f"{ticket.get('id', ticket.get('ID')):<6} "
            f"{ticket.get('title'):<15} "
            f"{ticket.get('priority'):<10} "
            f"{ticket.get('status'):<12} "
            f"{assignee:<15}"
        )



def WorkFlow():
    try:
        load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Could not load tickets: {error}")
        return

    if not campus.tickets:
        print("Error: No tickets found to edit.")
        return

    ticket_id = input("Ticket ID: ").strip().upper()
    target_ticket = None

    for ticket in campus.tickets:
        current_id = str(
            ticket.get("id", ticket.get("ID", ""))
        ).strip().upper()

        if current_id == ticket_id:
            target_ticket = ticket
            break

    if target_ticket is None:
        print("Error: No match found.")
        return

    new_status = input("Ticket Status: ").strip().lower()
    current_status = str(
        target_ticket.get("status", "")
    ).strip().lower()

    if current_status == "open" and new_status == "open":
        print("Ticket is already open.")
        return

    if current_status == "open" and new_status == "in_progress":
        assignee = target_ticket.get("assigned_to")

        if not assignee or str(assignee).strip().lower() == "none":
            print("Error: Ticket has not been assigned.")
            return

        event_type = "START"
        details = "Ticket moved to in_progress."

    elif current_status == "in_progress" and new_status == "resolved":
        event_type = "RESOLVE"
        details = "Ticket resolved."

    elif current_status == "resolved" and new_status == "open":
        event_type = "REOPEN"
        details = "Ticket reopened."

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

    success = apply_transition(
        target_ticket,
        event_type,
        actor,
        current_status,
        new_status,
        details,
    )

    if success:
        print(f"Ticket {ticket_id} changed to {new_status}.")

if __name__ == "__main__":
    WorkFlow()
    WorkQueue()
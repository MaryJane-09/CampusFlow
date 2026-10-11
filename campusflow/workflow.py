from .show_ticket import campus
<<<<<<< HEAD
import os
import json

FilePath = "ticket.json"

def WorkFlow():

    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        print("Error: No tickets file found to edit.")
=======
import json
import os

FilePath = "ticket.json"

def WorkQueue():
    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        print("Error: Tickets file is empty or missing.")
>>>>>>> main
        return

    with open(FilePath, "r") as file:
        campus.tickets = json.load(file)

<<<<<<< HEAD
    target_ticket =  None
    ticket_id = input("Ticket ID: ")
    for ticket in campus.tickets:
        if ticket.get("id") == ticket_id:
            target_ticket = ticket
            break
    if target_ticket is None:
        print("Error: No match found")
        return
    
    new_status = input("Ticket Status: ").lower().strip()

    if target_ticket.get("status") == "open" and new_status == "open":
        print("Ticket is already open")

    elif target_ticket.get("status") == "open" and new_status == "in_progress":
        if target_ticket.get("assigned_to") is None:
            print("Error: Ticket has not been assigned.")
            return
        target_ticket["status"] = "in_progress"

    elif target_ticket.get("status") == "in_progress" and new_status == "resolved":
        target_ticket["status"] = "resolved"

    elif target_ticket.get("status") == "resolved" and new_status == "open":
        target_ticket["status"] = "open"

    elif target_ticket.get("status") == "open" and new_status == "resolved":
        print("Error: Must follow workflow.")
        return

    elif target_ticket.get("status") == "resolved" and new_status == "in_progress":
        print("Error: Reopen the ticket first.")
        return

    else:
        print("Error: Unrecognized workflow.")
        return

    with open(FilePath, "w") as file:
        json.dump(campus.tickets, file, indent=4)

if __name__ == "__main__":
    WorkFlow()
=======
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
            int(str(ticket.get("id", "T0"))[1:])
        )
    )

    if not sorted_tickets:
        print("No active tickets in the work queue.")
        return

    print(f"\n{'ID':<6} {'Title':<15} {'Priority':<10} {'Status':<12} {'Assigned To':<15}")
    print("-" * 60)
    for ticket in sorted_tickets:
        assignee = ticket.get("assigned_to") or "Unassigned"
        print(f"{ticket.get('id'):<6} {ticket.get('title'):<15} {ticket.get('priority'):<10} {ticket.get('status'):<12} {assignee:<15}")

>>>>>>> main

from .show_ticket import campus
import json
import os

FilePath = "ticket.json"

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


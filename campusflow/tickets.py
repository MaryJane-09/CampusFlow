from dataclasses import asdict, dataclass
from .show_ticket import campus
import os
import json
from copy import deepcopy
from datetime import datetime, timezone
from .sla import calculate_due_at
from .duplicate import confirm_ticket_creation 
from .storage import load_json, save_json
from .history import record_event

FilePath = "ticket.json"

@dataclass
class Ticket:
    ID: str
    title: str
    category: str
    urgency: str
    affected_users: int
    priority: str
    created_at: str
    updated_at: str
    due_at: str                       
    status: str = "Open"
    assigned_to: str | None = "None"
    escalation_cycle: int = 0
    escalated_cycle: int | None = "None"


def SaveTicket(tickets: Ticket):
    try:
        load_json(campus)

        ticket_data = asdict(tickets)
        campus.tickets.append(ticket_data)

        record_event(
            ticket_id=ticket_data.get("id", ticket_data.get("ID")),
            event_type="CREATE",
            actor="System",
            before_status=None,
            after_status=ticket_data.get("status", "open"),
            details="Ticket created.",
        )

        save_json(campus)

    except (ValueError, OSError, TypeError) as error:
        print(f"Unable to save ticket: {error}")
        return False

    return True




def GenerateID(prefix="T"):
    numbers = []

    for ticket in campus.tickets:
        if not isinstance(ticket, dict):
            raise ValueError(
                f"Invalid ticket data: expected a dictionary, "
                f"got {type(ticket).__name__}"
            )

        ticket_id = ticket.get("id", ticket.get("ID", ""))

        if not isinstance(ticket_id, str) or not ticket_id.startswith(prefix):
            raise ValueError(f"Unexpected ticket ID: {ticket_id}")

        number = ticket_id[len(prefix):]

        if not number.isascii() or not number.isdigit():
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        numbers.append(int(number))

    next_number = max(numbers, default=0) + 1
    return f"{prefix}{next_number:03d}"




def CreateTickets():
    title_input = input("Problem Title: ").strip()
    if not title_input:
        print("Problem title cannot be blank.")
        return

    category_input = input(
        "Category (Network/Hardware/Software/Platform): "
    ).lower().strip()

    if category_input not in ("network", "hardware", "software", "platform"):
        print("Invalid Category.")
        return

    if not confirm_ticket_creation(title_input, category_input):
        return

    urgency_input = input("Urgency (High/Medium/Low): ").lower().strip()
    if urgency_input not in ("high", "medium", "low"):
        print("Invalid Urgency.")
        return
    
    try:
        affected_user_input = int(input("Affected Users: "))
    except ValueError:
        print("Invalid input for users.")
        return

    if affected_user_input <= 0:
        print("Users cannot be less than 1.")
        return

    if urgency_input == "high" and affected_user_input >= 10:
        priority = "Critical"
    elif urgency_input == "high" or affected_user_input >= 10:
        priority = "High"
    elif urgency_input == "medium" or affected_user_input >= 3:
        priority = "Medium"
    else:
        priority = "Low"

    ticket_id = GenerateID()

    created_time = datetime.now(timezone.utc)
    deadline = calculate_due_at(priority.lower(), created_time)
    created_timestamp = created_time.isoformat()

    tickets = Ticket(
        ID=ticket_id,
        title=title_input,
        category=category_input,
        urgency=urgency_input,
        affected_users=affected_user_input,
        priority=priority,
        created_at=created_timestamp,
        updated_at=created_timestamp,
        due_at=deadline.isoformat(),
        escalation_cycle=0,
    )

    SaveTicket(tickets)
    if not SaveTicket(tickets):
        return

    print("\nTicket Created:")
    print(f"ID:             {tickets.ID}")
    print(f"Title:          {tickets.title}")
    print(f"Category:       {tickets.category}")
    print(f"Urgency:        {tickets.urgency}")
    print(f"Affected Users: {tickets.affected_users}")
    print(f"Priority:       {tickets.priority}")
    print(f"Status:         {tickets.status}")
    print(f"Assigned To:    {tickets.assigned_to}")
    print(f"Created At:     {tickets.created_at}")
    print(f"Updated At:     {tickets.updated_at}")
    print(f"Due At:         {tickets.due_at}")
    print(f"SLA Cycle:      {tickets.escalation_cycle}")



def AssignTicket():
    try:
        load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return

    ticket_id = input("Enter Ticket ID to assign (e.g., T001): ").strip().upper()

    target_ticket = None
    for ticket in campus.tickets:
        if not isinstance(ticket, dict):
            continue
            
        current_id = str(
            ticket.get("id", ticket.get("ID", ""))
        ).strip().upper()

        if current_id == ticket_id:
            target_ticket = ticket
            break

    if target_ticket is None:
        print(f"Error: Ticket {ticket_id} not found.")
        return

    if str(target_ticket.get("status", "")).strip().lower() == "resolved":
        print("Error: Reopen the ticket before assigning it.")
        return

    technician = input("Enter Technician Name: ").strip()
    if not technician:
        print("Error: Technician name cannot be blank.")
        return
    actor = input("Enter your name (operator): ").strip()

    if not actor:
        print("Error: Operator name cannot be blank.")
        return

    previous_assignee = target_ticket.get("assigned_to")
    previous_updated_at = target_ticket.get("updated_at")
    previous_events = deepcopy(campus.events)

    try:
        target_ticket["assigned_to"] = technician
        target_ticket["updated_at"] = datetime.now(timezone.utc).isoformat()

        record_event(
            ticket_id=target_ticket.get("id", target_ticket.get("ID")),
            event_type="ASSIGN",
            actor=actor,
            before_status=target_ticket.get("status", "open"),
            after_status=target_ticket.get("status", "open"),
            details=f"Ticket assigned to {technician}.",
        )

        save_json(campus)

    except (OSError, TypeError, ValueError) as error:
        target_ticket["assigned_to"] = previous_assignee

        if previous_updated_at is None:
            target_ticket.pop("updated_at", None)
        else:
            target_ticket["updated_at"] = previous_updated_at

        campus.events = previous_events
        print(f"Assignment failed; changes rolled back: {error}")
        return

    print(f"Ticket {ticket_id} assigned to {technician}.")

if __name__ == "__main__":
    CreateTickets()
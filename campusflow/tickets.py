from dataclasses import asdict, dataclass
from .show_ticket import campus
import os
import json
from datetime import datetime, timezone
from .sla import calculate_due_at

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
    escalated_cycle: int | None = None

def SaveTicket(tickets: Ticket):
    if os.path.exists(FilePath) and os.path.getsize(FilePath) > 0:
        try:
            with open(FilePath, "r") as file:
                campus.tickets = json.load(file)
        except json.JSONDecodeError:
            print("Warning: JSON file was corrupted.")
            return
    campus.tickets.append(asdict(tickets))
    with open(FilePath, "w") as file:
        json.dump(campus.tickets, file, indent=4)


def GenerateID(prefix="T"):
    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        return f"{prefix}001"
    with open(FilePath, "r") as file:
        campus.tickets = json.load(file)

    numbers = []
    for ticket in campus.tickets:
        tickets_id = ticket.get("ID", "")
        try:
            numeric_part = int(tickets_id[1:])
            numbers.append(numeric_part)
        except ValueError:
            pass

    max_num = max(numbers) if numbers else 0
    max_num += 1

    return f"{prefix}{max_num:03d}"


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
    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        print("Error: Tickets file is empty or missing.")
        return

    with open(FilePath, "r") as file:
        campus.tickets = json.load(file)

    ticket_id = input("Enter Ticket ID to assign (e.g., T001): ").strip().upper()
    technician = input("Enter Technician Name: ").strip()

    if not technician:
        print("Error: Technician name cannot be blank.")
        return

    target_ticket = None
    for ticket in campus.tickets:
        if str(ticket.get("ID")).upper() == ticket_id:
            target_ticket = ticket
            break

    if not target_ticket:
        print(f"Error: Ticket {ticket_id} not found.")
        return
    
    if str(target_ticket.get("status", "")).lower().strip() == "resolved":
        print("Error: Reopen the ticket before assigning it.")
        return


    target_ticket["assigned_to"] = technician

    with open(FilePath, "w") as file:
        json.dump(campus.tickets, file, indent=4)
    print("Changes saved successfully!")

if __name__ == "__main__":
    CreateTickets()
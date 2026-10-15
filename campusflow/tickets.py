from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime

from . import storage
from .show_ticket import campus
from .duplicate import confirm_ticket_creation
from .history import record_event
from .sla import calculate_due_at, utc_time


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
    assigned_to: str | None = None
    escalation_cycle: int = 0
    escalated_cycle: int | None = None


def load_for_creation():
    try:
        storage.load_json(campus)
    except FileNotFoundError:
        # Only a genuinely fresh, empty application may start a new file.
        if campus.tickets or campus.events:
            raise ValueError("Saved file is missing while memory contains data.")


def GenerateID(prefix="T"):
    numbers = set()
    for ticket in campus.tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")
        ticket_id = ticket.get("ID")
        if not isinstance(ticket_id, str) or not ticket_id.startswith(prefix):
            raise ValueError(f"Invalid ticket ID: {ticket_id}")
        suffix = ticket_id[len(prefix):]
        if not suffix.isascii() or not suffix.isdigit():
            raise ValueError(f"Invalid ticket ID: {ticket_id}")
        number = int(suffix)
        if number < 1 or ticket_id != f"{prefix}{number:03d}":
            raise ValueError(f"Invalid ticket ID: {ticket_id}")
        if number in numbers:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")
        numbers.add(number)
    return f"{prefix}{max(numbers, default=0) + 1:03d}"


def SaveTicket(ticket, actor):
    old_tickets = deepcopy(campus.tickets)
    old_events = deepcopy(campus.events)
    try:
        load_for_creation()
        data = asdict(ticket)
        created = utc_time(datetime.fromisoformat(data["created_at"]))
        campus.tickets.append(data)
        record_event(
            ticket_id=data["ID"], event_type="CREATE", actor=actor,
            before_status=None, after_status=data["status"],
            details="Ticket created.", now=created,
        )
        storage.save_json(campus)
    except Exception as error:
        campus.tickets[:] = old_tickets
        campus.events[:] = old_events
        if isinstance(error, (ValueError, OSError, TypeError, KeyError)):
            print(f"Unable to save ticket: {error}")
            return False
        raise
    return True


def CreateTickets(now=None):
    title = input("Problem Title: ").strip()
    if not title:
        print("Problem title cannot be blank.")
        return
    category = input("Category (Network/Hardware/Software/Platform): ").strip().lower()
    if category not in ("network", "hardware", "software", "platform"):
        print("Invalid Category.")
        return
    urgency = input("Urgency (High/Medium/Low): ").strip().lower()
    if urgency not in ("high", "medium", "low"):
        print("Invalid Urgency.")
        return
    try:
        users = int(input("Affected Users: "))
    except ValueError:
        print("Invalid input for users.")
        return
    if users < 1:
        print("Users cannot be less than 1.")
        return
    try:
        load_for_creation()
        if not confirm_ticket_creation(title, category):
            return
        ticket_id = GenerateID()
        created = utc_time(now)
    except (ValueError, OSError) as error:
        print(f"Unable to create ticket: {error}")
        return
    actor = input("Enter your name (operator): ").strip()
    if not actor:
        print("Error: Operator name cannot be blank.")
        return
    if urgency == "high" and users >= 10:
        priority = "Critical"
    elif urgency == "high" or users >= 10:
        priority = "High"
    elif urgency == "medium" or users >= 3:
        priority = "Medium"
    else:
        priority = "Low"
    ticket = Ticket(
        ID=ticket_id, title=title, category=category, urgency=urgency,
        affected_users=users, priority=priority,
        created_at=created.isoformat(), updated_at=created.isoformat(),
        due_at=calculate_due_at(priority, created).isoformat(),
    )
    if SaveTicket(ticket, actor):
        print("\nTicket Created:")
        for field, value in asdict(ticket).items():
            print(f"{field}: {value}")


def AssignTicket(now=None):
    try:
        storage.load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return
    ticket_id = input("Enter Ticket ID to assign: ").strip().upper()
    target = next((t for t in campus.tickets if t["ID"].upper() == ticket_id), None)
    if target is None:
        print(f"Error: Ticket {ticket_id} not found.")
        return
    if target["status"].strip().lower() == "resolved":
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
    old_ticket = deepcopy(target)
    old_events = deepcopy(campus.events)
    try:
        now = utc_time(now)
        target["assigned_to"] = technician
        target["updated_at"] = now.isoformat()
        record_event(
            ticket_id=target["ID"], event_type="ASSIGN", actor=actor,
            before_status=target["status"], after_status=target["status"],
            details=f"Ticket assigned to {technician}.", now=now,
        )
        storage.save_json(campus)
    except Exception as error:
        target.clear()
        target.update(old_ticket)
        campus.events[:] = old_events
        if isinstance(error, (OSError, TypeError, ValueError, KeyError)):
            print(f"Assignment failed; changes rolled back: {error}")
            return
        raise
    print(f"Ticket {ticket_id} assigned to {technician}.")
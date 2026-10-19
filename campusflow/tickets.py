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
        if campus.tickets or campus.events:
            raise ValueError(
                "Saved file is missing while memory contains data."
            )


def GenerateID(prefix="T"):
    numbers = []

    for ticket in campus.tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")

        ticket_id = ticket.get("ID")

        if not isinstance(ticket_id, str):
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        if not ticket_id.startswith(prefix):
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        number_text = ticket_id[len(prefix):]

        if not number_text.isascii():
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        if not number_text.isdigit():
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        number = int(number_text)

        if number < 1:
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        expected_id = prefix + str(number).zfill(3)

        if ticket_id != expected_id:
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        if number in numbers:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")

        numbers.append(number)

    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1

    return prefix + str(next_number).zfill(3)


def SaveTicket(ticket, actor):
    saved_tickets = deepcopy(campus.tickets)
    saved_events = deepcopy(campus.events)

    try:
        load_for_creation()

        ticket_data = asdict(ticket)

        created_time = datetime.fromisoformat(
            ticket_data["created_at"]
        )
        created_time = utc_time(created_time)

        campus.tickets.append(ticket_data)

        record_event(
            ticket_id=ticket_data["ID"],
            event_type="CREATE",
            actor=actor,
            before_status=None,
            after_status=ticket_data["status"],
            details="Ticket created.",
            now=created_time,
        )

        storage.save_json(campus)

    except Exception as error:
        campus.tickets.clear()
        campus.tickets.extend(saved_tickets)

        campus.events.clear()
        campus.events.extend(saved_events)

        if isinstance(error, (ValueError, OSError, TypeError, KeyError)):
            print(f"Unable to save ticket: {error}")
            return False

        raise

    return True


def CreateTickets(now=None):
    title = input("Problem Title: ").strip()

    if title == "":
        print("Problem title cannot be blank.")
        return

    category = input(
        "Category (Network/Hardware/Software/Platform): "
    ).strip().lower()

    if category not in ["network", "hardware", "software", "platform"]:
        print("Invalid Category.")
        return

    urgency = input("Urgency (High/Medium/Low): ").strip().lower()

    if urgency not in ["high", "medium", "low"]:
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

        confirmed = confirm_ticket_creation(title, category)

        if not confirmed:
            return

        ticket_id = GenerateID()
        created_time = utc_time(now)

    except (ValueError, OSError) as error:
        print(f"Unable to create ticket: {error}")
        return

    operator_name = input("Enter your name (operator): ").strip()

    if operator_name == "":
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

    deadline = calculate_due_at(priority, created_time)
    created_text = created_time.isoformat()
    deadline_text = deadline.isoformat()

    ticket = Ticket(
        ID=ticket_id,
        title=title,
        category=category,
        urgency=urgency,
        affected_users=users,
        priority=priority,
        created_at=created_text,
        updated_at=created_text,
        due_at=deadline_text,
    )

    saved = SaveTicket(ticket, operator_name)

    if saved:
        print("\nTicket Created:")

        ticket_data = asdict(ticket)

        for field in ticket_data:
            print(f"{field}: {ticket_data[field]}")


def AssignTicket(now=None):
    try:
        storage.load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return

    ticket_id = input("Enter Ticket ID to assign: ").strip().upper()
    selected_ticket = None

    for ticket in campus.tickets:
        if ticket["ID"].upper() == ticket_id:
            selected_ticket = ticket
            break

    if selected_ticket is None:
        print(f"Error: Ticket {ticket_id} not found.")
        return

    status = selected_ticket["status"].strip().lower()

    if status == "resolved":
        print("Error: Reopen the ticket before assigning it.")
        return

    technician = input("Enter Technician Name: ").strip()

    if technician == "":
        print("Error: Technician name cannot be blank.")
        return

    operator_name = input("Enter your name (operator): ").strip()

    if operator_name == "":
        print("Error: Operator name cannot be blank.")
        return

    saved_ticket = deepcopy(selected_ticket)
    saved_events = deepcopy(campus.events)

    try:
        update_time = utc_time(now)

        selected_ticket["assigned_to"] = technician
        selected_ticket["updated_at"] = update_time.isoformat()

        record_event(
            ticket_id=selected_ticket["ID"],
            event_type="ASSIGN",
            actor=operator_name,
            before_status=selected_ticket["status"],
            after_status=selected_ticket["status"],
            details=f"Ticket assigned to {technician}.",
            now=update_time,
        )

        storage.save_json(campus)

    except Exception as error:
        selected_ticket.clear()
        selected_ticket.update(saved_ticket)

        campus.events.clear()
        campus.events.extend(saved_events)

        if isinstance(error, (OSError, TypeError, ValueError, KeyError)):
            print(f"Assignment failed; changes rolled back: {error}")
            return

        raise

    print(f"Ticket {ticket_id} assigned to {technician}.")
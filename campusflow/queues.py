from datetime import datetime, timezone

from .sla import is_overdue
from .show_ticket import campus
from .storage import load_json


def SLAAttentionQueue():
    try:
        load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load SLA data: {error}")
        return

    now = datetime.now(timezone.utc)
    unresolved_tickets = []

    for ticket in campus.tickets:
        status = ticket["status"].strip().lower()

        if status == "open" or status == "in_progress":
            unresolved_tickets.append(ticket)

    def queue_order(ticket):
        if is_overdue(ticket, now):
            attention_order = 0
        else:
            attention_order = 1

        deadline = datetime.fromisoformat(ticket["due_at"])
        ticket_number = int(ticket["ID"][1:])

        return attention_order, deadline, ticket_number

    unresolved_tickets.sort(key=queue_order)

    if not unresolved_tickets:
        print("No unresolved tickets in SLA Attention Queue.")
        return

    print(
        f"\n{'Attention':<12} {'ID':<6} {'Title':<15} "
        f"{'Priority':<10} {'Status':<12} {'Due At':<25}"
    )
    print("-" * 80)

    for ticket in unresolved_tickets:
        if is_overdue(ticket, now):
            attention = "OVERDUE [!]"
        else:
            attention = "On Track"

        print(
            f"{attention:<12} "
            f"{ticket['ID']:<6} "
            f"{ticket['title']:<15} "
            f"{ticket['priority']:<10} "
            f"{ticket['status']:<12} "
            f"{ticket['due_at']:<25}"
        )


def DisplayMetrics():
    try:
        load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load SLA data: {error}")
        return

    now = datetime.now(timezone.utc)

    open_count = 0
    in_progress_count = 0
    resolved_count = 0
    overdue_count = 0
    escalated_count = 0

    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for ticket in campus.tickets:
        status = ticket["status"].strip().lower()
        priority = ticket["priority"].strip().lower()

        if status == "open":
            open_count += 1
        elif status == "in_progress":
            in_progress_count += 1
        elif status == "resolved":
            resolved_count += 1

        if status == "open" or status == "in_progress":
            if is_overdue(ticket, now):
                overdue_count += 1

        current_cycle = ticket["escalation_cycle"]
        escalated_cycle = ticket["escalated_cycle"]

        if escalated_cycle is not None:
            if escalated_cycle == current_cycle:
                escalated_count += 1

        priority_counts[priority] += 1

    print("\n--- Service Desk Metrics & Analytics ---")
    print(f"Open Tickets:                  {open_count}")
    print(f"In-Progress Tickets:           {in_progress_count}")
    print(f"Resolved Tickets:              {resolved_count}")
    print(f"Overdue Unresolved Tickets:    {overdue_count}")
    print(f"Escalated in Current Cycle:    {escalated_count}")
    print("-" * 40)

    print("Priority Breakdown:")

    for priority in priority_counts:
        name = priority.capitalize()
        count = priority_counts[priority]
        print(f"  - {name:<10}: {count}")

    print("----------------------------------------")
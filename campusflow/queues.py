from datetime import datetime, timezone
from .sla import is_overdue
from .show_ticket import campus
from .storage import load_json

FilePath = "ticket.json"

def SLAAttentionQueue():
    try:
        load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load SLA data: {error}")
        return
    now = datetime.now(timezone.utc)

    unresolved_tickets = []
    for ticket in campus.tickets:
        if not isinstance(ticket, dict):
            continue
        if str(ticket.get("status", "")).lower().strip() in ("open", "in_progress"):
            unresolved_tickets.append(ticket)

    def sla_sort_key(ticket):
        # 1. Overdue status first (False/Not overdue = 0, True/Overdue = 1 -> inverted so overdue is 0)
        overdue_flag = 0 if is_overdue(ticket, now) else 1

        # 2. Ascending due_at timestamp
        due_at_str = ticket.get("due_at")
        if due_at_str:
            try:
                due_time = datetime.fromisoformat(due_at_str)
            except ValueError:
                due_time = datetime.max.replace(tzinfo=timezone.utc)
        else:
            due_time = datetime.max.replace(tzinfo=timezone.utc)

        raw_id = str(ticket.get("id", ticket.get("ID", "T0")))
        digits = "".join(filter(str.isdigit, raw_id))
        id_num = int(digits) if digits else 0

        return (overdue_flag, due_time, id_num)

    sorted_sla_tickets = sorted(unresolved_tickets, key=sla_sort_key)

    if not sorted_sla_tickets:
        print("No unresolved tickets in SLA Attention Queue.")
        return

    print(f"\n{'Attention':<12} {'ID':<6} {'Title':<15} {'Priority':<10} {'Status':<12} {'Due At':<25}")
    print("-" * 80)
    for ticket in sorted_sla_tickets:
        overdue = is_overdue(ticket, now)
        attention_label = "OVERDUE [!]" if overdue else "On Track"
        
        t_id = ticket.get("id", ticket.get("ID", ""))
        title = ticket.get("title", "")
        priority = ticket.get("priority", "")
        status = ticket.get("status", "")
        due_at = ticket.get("due_at", "N/A")

        print(
            f"{attention_label:<12} "
            f"{t_id:<6} "
            f"{title:<15} "
            f"{priority:<10} "
            f"{status:<12} "
            f"{due_at:<25}"
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
    overdue_unresolved_count = 0
    escalated_current_cycle_count = 0
    priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for ticket in campus.tickets:
        if not isinstance(ticket, dict):
            continue

        status = str(ticket.get("status", "")).strip().lower()
        priority = str(ticket.get("priority", "")).strip().lower()

        if status == "open":
            open_count += 1
        elif status == "in_progress":
            in_progress_count += 1
        elif status == "resolved":
            resolved_count += 1

        if status in ("open", "in_progress"):
            if is_overdue(ticket, now):
                overdue_unresolved_count += 1

        # Check if escalated in the current active cycle
        current_cycle = ticket.get("escalation_cycle", 0)
        escalated_cycle = ticket.get("escalated_cycle")
        if escalated_cycle is not None and escalated_cycle == current_cycle:
            escalated_current_cycle_count += 1

        if priority in priority_counts:
            priority_counts[priority] += 1

    print("\n--- Service Desk Metrics & Analytics ---")
    print(f"Open Tickets:                  {open_count}")
    print(f"In-Progress Tickets:           {in_progress_count}")
    print(f"Resolved Tickets:              {resolved_count}")
    print(f"Overdue Unresolved Tickets:    {overdue_unresolved_count}")
    print(f"Escalated in Current Cycle:    {escalated_current_cycle_count}")
    print("-" * 40)
    print("Priority Breakdown:")
    for pri, count in priority_counts.items():
        print(f"  - {pri.capitalize():<10}: {count}")
    print("----------------------------------------")
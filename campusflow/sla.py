from datetime import timedelta, datetime

def calculate_due_at(priority, cycle_start):
    if priority == "critical":
        duration_minute = timedelta(minutes=60)
    elif priority == "high":
        duration_minute = timedelta(minutes=240)
    elif priority == "medium":
        duration_minute = timedelta(minutes=1440)
    elif priority == "low":
        duration_minute = timedelta(minutes=2880)
    result = cycle_start + duration_minute
    return result 


def is_overdue(ticket, now):
    if ticket.get("status", "").strip().lower() == "resolved":
        return False
    
    due_at_str = ticket.get("due_at")
    if not due_at_str:
        return False
        
    deadline = datetime.fromisoformat(due_at_str)
    
    return now > deadline


def escalate_overdue(tickets, events, now, actor, *, event_recorder):
    newly_escalated = 0
    already_escalated = 0

    for ticket in tickets:
        if not is_overdue(ticket, now):
            continue

        current_cycle = ticket["escalation_cycle"]

        if ticket["escalated_cycle"] == current_cycle:
            already_escalated += 1
            continue

        event = event_recorder(
            events=events,
            ticket_id=ticket["id"],
            event_type="ESCALATE",
            actor=actor,
            before_status=ticket["status"],
            after_status=ticket["status"],
            details=f"Overdue escalation for SLA cycle {current_cycle}",
            now=now,
        )

        if not isinstance(event, dict):
            raise TypeError("Event recorder must return an event dictionary.")

        events.append(event)
        ticket["escalated_cycle"] = current_cycle
        newly_escalated += 1

    return {
        "newly_escalated": newly_escalated,
        "already_escalated": already_escalated,
    }
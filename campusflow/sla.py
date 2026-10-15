from copy import deepcopy
from datetime import datetime, timedelta, timezone

SLA_MINUTES = {"critical": 60, "high": 240, "medium": 1440, "low": 2880}


def utc_time(value=None):
    if value is None:
        return datetime.now(timezone.utc)
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("Time must be a timezone-aware datetime.")
    return value.astimezone(timezone.utc)


def calculate_due_at(priority, cycle_start):
    if not isinstance(priority, str):
        raise ValueError("Priority must be text.")
    priority = priority.strip().lower()
    if priority not in SLA_MINUTES:
        raise ValueError("Invalid ticket priority.")
    return utc_time(cycle_start) + timedelta(minutes=SLA_MINUTES[priority])


def is_overdue(ticket, now):
    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary.")
    status = ticket.get("status")
    if not isinstance(status, str):
        raise ValueError("Invalid ticket status.")
    status = status.strip().lower()
    if status not in ("open", "in_progress", "resolved"):
        raise ValueError("Invalid ticket status.")
    now = utc_time(now)
    if status == "resolved":
        return False
    deadline = ticket.get("due_at")
    if not isinstance(deadline, str):
        raise ValueError("Ticket needs an ISO-8601 due_at timestamp.")
    return now > utc_time(datetime.fromisoformat(deadline))


def escalate_overdue(tickets, events, now, actor, *, event_recorder):
    now = utc_time(now)
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Operator name cannot be empty.")
    new_count = 0
    old_count = 0
    for ticket in tickets:
        if not is_overdue(ticket, now):
            continue
        cycle = ticket["escalation_cycle"]
        if ticket["escalated_cycle"] == cycle:
            old_count += 1
            continue
        old_ticket = deepcopy(ticket)
        old_events = deepcopy(events)
        try:
            event = event_recorder(
                ticket_id=ticket["ID"], event_type="ESCALATE",
                actor=actor.strip(), before_status=ticket["status"],
                after_status=ticket["status"],
                details=f"Overdue escalation for SLA cycle {cycle}", now=now,
            )
            if not isinstance(event, dict):
                raise TypeError("Recorder must return an event dictionary.")
            if len(events) != len(old_events) + 1:
                raise ValueError("Recorder must append exactly one event.")
            if events[:-1] != old_events or events[-1] != event:
                raise ValueError("Recorder changed existing history.")
            ticket["escalated_cycle"] = cycle
        except Exception:
            ticket.clear()
            ticket.update(old_ticket)
            events[:] = old_events
            raise
        new_count += 1
    return {"newly_escalated": new_count, "already_escalated": old_count}
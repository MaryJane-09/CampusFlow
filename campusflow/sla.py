from copy import deepcopy
from datetime import datetime, timedelta, timezone


def utc_time(value=None):
    if value is None:
        value = datetime.now(timezone.utc)

    if not isinstance(value, datetime):
        raise ValueError("Time must be a datetime.")

    if value.utcoffset() is None:
        raise ValueError("Time must include a timezone.")

    return value.astimezone(timezone.utc)


def calculate_due_at(priority, cycle_start):
    if not isinstance(priority, str):
        raise ValueError("Priority must be text.")

    priority = priority.strip().lower()
    cycle_start = utc_time(cycle_start)

    if priority == "critical":
        minutes = 60
    elif priority == "high":
        minutes = 240
    elif priority == "medium":
        minutes = 1440
    elif priority == "low":
        minutes = 2880
    else:
        raise ValueError("Invalid ticket priority.")

    duration = timedelta(minutes=minutes)
    deadline = cycle_start + duration

    return deadline


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

    due_at = ticket.get("due_at")

    if not isinstance(due_at, str):
        raise ValueError("Ticket needs an ISO-8601 due_at timestamp.")

    deadline = datetime.fromisoformat(due_at)
    deadline = utc_time(deadline)

    if now > deadline:
        return True

    return False


def escalate_overdue(tickets, events, now, actor, *, event_recorder):
    now = utc_time(now)

    if not isinstance(actor, str):
        raise ValueError("Operator name must be text.")

    actor = actor.strip()

    if not actor:
        raise ValueError("Operator name cannot be empty.")

    newly_escalated = 0
    already_escalated = 0

    for ticket in tickets:
        overdue = is_overdue(ticket, now)

        if not overdue:
            continue

        current_cycle = ticket["escalation_cycle"]
        previous_cycle = ticket["escalated_cycle"]

        if previous_cycle == current_cycle:
            already_escalated += 1
            continue

        ticket_backup = deepcopy(ticket)
        events_backup = deepcopy(events)

        try:
            event = event_recorder(
                ticket_id=ticket["ID"],
                event_type="ESCALATE",
                actor=actor,
                before_status=ticket["status"],
                after_status=ticket["status"],
                details=f"Overdue escalation for SLA cycle {current_cycle}",
                now=now,
            )

            if not isinstance(event, dict):
                raise TypeError("Recorder must return an event dictionary.")

            expected_count = len(events_backup) + 1

            if len(events) != expected_count:
                raise ValueError("Recorder must append exactly one event.")

            if events[:-1] != events_backup:
                raise ValueError("Recorder changed existing history.")

            if events[-1] != event:
                raise ValueError("Recorder returned a different event.")

            ticket["escalated_cycle"] = current_cycle

        except Exception:
            ticket.clear()
            ticket.update(ticket_backup)

            events.clear()
            events.extend(events_backup)

            raise

        newly_escalated += 1

    result = {
        "newly_escalated": newly_escalated,
        "already_escalated": already_escalated,
    }

    return result
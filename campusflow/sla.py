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
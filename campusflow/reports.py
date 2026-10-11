from .show_ticket import CampusFlow

def generate_report(campus: CampusFlow):
    total_ticket = len(campus.tickets)
    print("Total Tickets: ", total_ticket)

    total_open = 0
    total_in_progress = 0
    total_resolved = 0

    total_critical = 0
    total_high = 0
    total_medium = 0
    total_low = 0
    for ticket in campus.tickets:
        if ticket.get('status').lower() == "open":
            total_open += 1
        if ticket.get('status').lower() == "in_progress":
            total_in_progress += 1
        if ticket.get('status').lower() == "resolved":
            total_resolved += 1

        if ticket.get('priority').lower() == "critical":
            total_critical += 1
        if ticket.get('priority').lower() == "high":
            total_high += 1
        if ticket.get('priority').lower() == "medium":
            total_medium += 1
        if ticket.get('priority').lower() == "low":
            total_low += 1

    print("Open: ", total_open)
    print("In Progress: ", total_in_progress)
    print("Resolved: ", total_resolved)

    print("Critical: ", total_critical)
    print("High: ", total_high)
    print("Medium: ", total_medium)
    print("Low: ", total_low)

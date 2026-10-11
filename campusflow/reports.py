from show_ticket_class import CampusFlow

def generate_report(campus: CampusFlow):
    total_ticket = len(campus.ticket)
    print("Total Tickets: ", total_ticket)

    total_open = 0
    total_in_progress = 0
    total_resolved = 0

    total_critical = 0
    total_high = 0
    total_medium = 0
    total_low = 0
    for ticket in campus.ticket:
        if ticket.get('status') == "open":
            total_open += 1
        if ticket.get('status') == "in_progress":
            total_in_progress += 1
        if ticket.get('status') == "resolved":
            total_resolved += 1

        if ticket.get('priority') == "critical":
            total_critical += 1
        if ticket.get('priority') == "high":
            total_high += 1
        if ticket.get('priority') == "medium":
            total_medium += 1
        if ticket.get('priority') == "low":
            total_low += 1

    print("Open: ", total_open)
    print("In Progress: ", total_in_progress)
    print("Resolved: ", total_resolved)

    print("Critical: ", total_critical)
    print("High: ", total_high)
    print("Medium: ", total_medium)
    print("Low: ", total_low)

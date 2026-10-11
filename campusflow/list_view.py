from .show_ticket import CampusFlow

def list_ticket(campus: CampusFlow):
    if not campus.tickets:
        print("no ticteks recorded")
        return 
    
    for ticket in campus.tickets:
        print("ID: ", ticket.get('ID'))
        print("Title: ", ticket.get('title'))
        print("Category: ", ticket.get('category'))
        print("Urgency: ", ticket.get('urgency'))
        print("Affected Users: ", ticket.get('affected_users'))
        print("Priority: ", ticket.get('priority'))
        print("Status: ", ticket.get('status'))
        print("Assigned To: ", ticket.get('assigned_to'))
        print("-----------------------------------------")


def view_ticket(campus: CampusFlow):
    user_input = input("Enter a ID e.g T001")
    if not user_input.strip():
        print("Ticket ID cannot be empty")
        return
    for ticket in campus.ticket:
        if user_input.upper().strip() == ticket.get('ID'):
            print("ID: ", ticket.get('ID'))
            print("Title: ", ticket.get('title'))
            print("Category: ", ticket.get('category'))
            print("Urgency: ", ticket.get('urgency'))
            print("Affected Users: ", ticket.get('affected_users'))
            print("Priority: ", ticket.get('priority'))
            print("Status: ", ticket.get('status'))
            print("Assigned To", ticket.get('assigned_to'))
            return
    else:
        print("Ticket not found")

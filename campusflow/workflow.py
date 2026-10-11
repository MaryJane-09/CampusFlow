from .show_ticket import campus
import os
import json

FilePath = "ticket.json"

def WorkFlow():

    if not os.path.exists(FilePath) or os.path.getsize(FilePath) == 0:
        print("Error: No tickets file found to edit.")
        return

    with open(FilePath, "r") as file:
        campus.tickets = json.load(file)

    target_ticket =  None
    ticket_id = input("Ticket ID: ")
    for ticket in campus.tickets:
        if ticket.get("id") == ticket_id:
            target_ticket = ticket
            break
    if target_ticket is None:
        print("Error: No match found")
        return
    
    new_status = input("Ticket Status: ").lower().strip()

    if target_ticket.get("status") == "open" and new_status == "open":
        print("Ticket is already open")

    elif target_ticket.get("status") == "open" and new_status == "in_progress":
        if target_ticket.get("assigned_to") is None:
            print("Error: Ticket has not been assigned.")
            return
        target_ticket["status"] = "in_progress"

    elif target_ticket.get("status") == "in_progress" and new_status == "resolved":
        target_ticket["status"] = "resolved"

    elif target_ticket.get("status") == "resolved" and new_status == "open":
        target_ticket["status"] = "open"

    elif target_ticket.get("status") == "open" and new_status == "resolved":
        print("Error: Must follow workflow.")
        return

    elif target_ticket.get("status") == "resolved" and new_status == "in_progress":
        print("Error: Reopen the ticket first.")
        return

    else:
        print("Error: Unrecognized workflow.")
        return

    with open(FilePath, "w") as file:
        json.dump(campus.tickets, file, indent=4)

if __name__ == "__main__":
    WorkFlow()
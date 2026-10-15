from .show_ticket import campus

def detect_duplicates(title, category, current_ticket_id=None):
    normalized_title = " ".join(title.lower().split())
    duplicates = []

    unresolved_statuses = {"open", "in_progress"}

    for ticket in campus.tickets:
        ticket_id = str(ticket.get("id", ticket.get("ID", ""))).strip()
        ticket_title = ticket.get("title", "")
        ticket_category = ticket.get("category", "")
        ticket_status = str(ticket.get("status", "")).strip().lower()

        if current_ticket_id and ticket_id.upper() == current_ticket_id.strip().upper():
            continue

        existing_title = " ".join(str(ticket_title).lower().split())

        if (
            existing_title == normalized_title
            and str(ticket_category).strip().lower() == str(category).strip().lower()
            and ticket_status in unresolved_statuses
        ):
            duplicates.append(ticket)

    if duplicates:
        print("\nWarning: Matching unresolved tickets found!")

        for ticket in duplicates:
            print(
                f"ID: {ticket.get('id', ticket.get('ID'))} | "
                f"Title: {ticket.get('title')} | "
                f"Category: {ticket.get('category')} | "
                f"Status: {ticket.get('status')}"
            )

        return duplicates

    print("No matching unresolved tickets found.")
    return []


def confirm_ticket_creation(title, category):
    """
    Integrates your detect_duplicates function with an explicit user prompt.
    Returns True if the user confirms creation or no duplicates exist.
    Returns False if the user aborts.
    """
    duplicates = detect_duplicates(title, category)
    
    if not duplicates:
        return True  

    print("-" * 50)
    choice = input("Do you still want to proceed with creating this duplicate ticket? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("Action cancelled: No ticket or audit event was created.")
        return False

    print("Proceeding with ticket creation upon user confirmation...")
    return True
from .show_ticket import campus


def detect_duplicates(title, category, current_ticket_id=None):
    title_words = title.lower().split()
    normalized_title = " ".join(title_words)
    normalized_category = category.strip().lower()

    duplicates = []

    for ticket in campus.tickets:
        ticket_id = ticket["ID"].strip()
        ticket_status = ticket["status"].strip().lower()

        if current_ticket_id:
            ignored_id = current_ticket_id.strip().upper()

            if ticket_id.upper() == ignored_id:
                continue

        if ticket_status != "open" and ticket_status != "in_progress":
            continue

        existing_words = ticket["title"].lower().split()
        existing_title = " ".join(existing_words)
        existing_category = ticket["category"].strip().lower()

        if existing_title == normalized_title:
            if existing_category == normalized_category:
                duplicates.append(ticket)

    if not duplicates:
        print("No matching unresolved tickets found.")
        return duplicates

    print("\nWarning: Matching unresolved tickets found!")

    for ticket in duplicates:
        print(
            f"ID: {ticket['ID']} | "
            f"Title: {ticket['title']} | "
            f"Category: {ticket['category']} | "
            f"Status: {ticket['status']}"
        )

    return duplicates


def confirm_ticket_creation(title, category):
    duplicates = detect_duplicates(title, category)

    if not duplicates:
        return True

    print("-" * 50)

    choice = input(
        "Do you still want to create this duplicate ticket? (y/n): "
    )
    choice = choice.strip().lower()

    if choice == "y":
        print("Proceeding with ticket creation upon user confirmation...")
        return True

    print("Action cancelled: No ticket or audit event was created.")
    return False
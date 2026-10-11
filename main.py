
from campusflow.storage import load_json, save_json
from campusflow.show_ticket import campus
from campusflow.tickets import CreateTickets, AssignTicket
from campusflow.workflow import WorkQueue, WorkFlow
from campusflow.list_view import list_ticket, view_ticket
from campusflow.reports import generate_report


def main():
    try:
        load_json(campus)
    except ValueError as error:
        print(f"Unable to load tickets: {error}")
        return

    while True:
        print("\n===== CAMPUSFLOW TICKET SYSTEM =====")
        print("1. Create ticket")
        print("2. Assign ticket")
        print("3. Update ticket status")
        print("4. View work queue")
        print("5. List all tickets")
        print("6. View a ticket")
        print("7. Generate report")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            CreateTickets()
        elif choice == "2":
            AssignTicket()
        elif choice == "3":
            WorkFlow()
        elif choice == "4":
            WorkQueue()
        elif choice == "5":
            list_ticket(campus)
        elif choice == "6":
            view_ticket(campus)
        elif choice == "7":
            generate_report(campus)
        elif choice == "0":
            try:
                save_json(campus)
                print("Tickets saved successfully.")
            except (TypeError, OSError) as error:
                print(f"Could not save tickets: {error}")
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 0 to 7.")


if __name__ == "__main__":
    main()

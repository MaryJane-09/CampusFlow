from campusflow.storage import load_json, save_json
from campusflow.show_ticket import campus
from campusflow.tickets import CreateTickets, AssignTicket
from campusflow.workflow import WorkQueue, WorkFlow
from campusflow.list_view import list_ticket, view_ticket
from campusflow.reports import generate_report

from campusflow.history import show_history
from campusflow.queues import SLAAttentionQueue, DisplayMetrics
from campusflow.sla import escalate_overdue
from campusflow.knowledge_lab import run_knowledge_lab
from datetime import datetime, timezone


def main():
    try:
        load_json(campus)
    except ValueError as error:
        print(f"Unable to load tickets: {error}")
        return

    while True:
        print("\n===== CAMPUSFLOW TICKET SYSTEM =====")
        print("1. Create ticket")
        print("2. Assign")
        print("3. Start/resolve/reopen")
        print("4. Original Open Queue")
        print("5. SLA Attention Queue")
        print("6. History")
        print("7. Check Escalations")
        print("8. Reports")
        print("9. Save/Load")
        print("10. Engineering Knowledge Lab")
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
            SLAAttentionQueue()
        elif choice == "6":
            show_history()
        elif choice == "7":
            actor = input("Enter Operator Name for escalation check: ").strip()
            if not actor:
                print("Operator name cannot be blank.")
                continue
            now = datetime.now(timezone.utc)
            result = escalate_overdue(
                campus.tickets, 
                campus.events, 
                now, 
                actor, 
                event_recorder=lambda **kwargs: kwargs
            )
            print(f"Escalation check complete: {result.get('newly_escalated', 0)} newly escalated, {result.get('already_escalated', 0)} already escalated.")
            try:
                save_json(campus)
            except (TypeError, OSError) as e:
                print(f"Error saving escalation state: {e}")
        elif choice == "8":
            print("\n--- Reports & Metrics Submenu ---")
            print("1. Standard Generate Report")
            print("2. SLA Service Desk Metrics [Engineer B]")
            sub_choice = input("Select report type (1 or 2): ").strip()
            if sub_choice == "2":
                DisplayMetrics()
            else:
                generate_report(campus)
        elif choice == "9":
            try:
                save_json(campus)
                print("Tickets and audit events saved successfully.")
            except (TypeError, OSError) as error:
                print(f"Could not save tickets: {error}")
        elif choice == "10":
            run_knowledge_lab()
        elif choice == "0":
            try:
                save_json(campus)
                print("Tickets saved successfully.")
            except (TypeError, OSError) as error:
                print(f"Could not save tickets: {error}")
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 0 to 10.")


if __name__ == "__main__":
    main()
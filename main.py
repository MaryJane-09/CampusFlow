from copy import deepcopy
from datetime import datetime, timezone

from campusflow.storage import load_json, save_json
from campusflow.show_ticket import campus
from campusflow.tickets import CreateTickets, AssignTicket
from campusflow.workflow import WorkQueue, WorkFlow
from campusflow.reports import generate_report
from campusflow.history import show_history, record_event
from campusflow.queues import SLAAttentionQueue, DisplayMetrics
from campusflow.sla import escalate_overdue
from campusflow.knowledge_lab import run_knowledge_lab


def load_starting_data():
    try:
        load_json(campus)

    except FileNotFoundError:
        if campus.tickets or campus.events:
            print("Saved file is missing, but memory contains data.")
            return False

        try:
            save_json(campus)
        except (ValueError, TypeError, OSError) as error:
            print(f"Could not create the initial data file: {error}")
            return False

        print("First run: created an empty ticket database.")

    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return False

    return True


def check_escalations():
    actor = input("Enter Operator Name: ").strip()

    if not actor:
        print("Operator name cannot be blank.")
        return

    try:
        load_json(campus)
    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return

    old_tickets = deepcopy(campus.tickets)
    old_events = deepcopy(campus.events)

    try:
        result = escalate_overdue(
            campus.tickets,
            campus.events,
            datetime.now(timezone.utc),
            actor,
            event_recorder=record_event,
        )

        save_json(campus)

    except Exception as error:
        campus.tickets[:] = old_tickets
        campus.events[:] = old_events

        if isinstance(error, (ValueError, TypeError, KeyError, OSError)):
            print(f"Escalation failed; changes rolled back: {error}")
            return

        raise

    print(
        f"Escalation check complete: "
        f"{result['newly_escalated']} newly escalated, "
        f"{result['already_escalated']} already escalated."
    )


def save_or_load():
    print("\n1. Save")
    print("2. Load")
    choice = input("Choose an option: ").strip()

    try:
        if choice == "1":
            save_json(campus)
            print("Tickets and audit events saved successfully.")

        elif choice == "2":
            load_json(campus)
            print("Tickets and audit events loaded successfully.")

        else:
            print("Invalid choice. Enter 1 or 2.")

    except (ValueError, TypeError, OSError) as error:
        print(f"Operation failed: {error}")


def show_reports():
    print("\n--- Reports ---")
    print("1. Standard report")
    print("2. SLA service desk metrics")

    choice = input("Choose a report: ").strip()

    if choice == "1":
        generate_report(campus)
    elif choice == "2":
        DisplayMetrics()
    else:
        print("Invalid choice. Enter 1 or 2.")


def main():
    if not load_starting_data():
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
            check_escalations()
        elif choice == "8":
            show_reports()
        elif choice == "9":
            save_or_load()
        elif choice == "10":
            run_knowledge_lab()
        elif choice == "0":
            try:
                save_json(campus)
            except (ValueError, TypeError, OSError) as error:
                print(f"Could not save tickets: {error}")
                print("You are still in the application.")
                continue

            print("Tickets saved successfully. Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 0 to 10.")


if __name__ == "__main__":
    main()
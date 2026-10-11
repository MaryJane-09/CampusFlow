from campusflow.storage import load_json, save_json
from show_ticket_class import CampusFlow

campus = CampusFlow()


try:
    load_json(campus)
except ValueError:
    print("file is invalid")
else:
    def menu():
        while True:
            choice = input("""
            0. Exit
            """)
            if choice == "0":
                print("GoodBye")
                break
            else:
                print("Invalid choice")


    menu()

    try:
        save_json(campus)
        print("Saved Successfully")
    except TypeError:
        print("Failed to serialize ticket data to JSON")
    except OSError:
        print("System error while writing 'ticket.json")
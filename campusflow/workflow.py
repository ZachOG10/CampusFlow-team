def assign_ticket(tickets):
    ticket_id = input("Enter the ticket ID: ")
    ticket_found = False

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket_found = True

            if ticket["status"] == "resolved":
                print("This ticket is resolved. Reopen it before changing its assignment.")
                break

            while True:
                staff_name = input("Enter the staff name: ")
                staff_name = staff_name.strip()

                if staff_name == "":
                    print("Invalid staff name. Please try again.")
                else:
                    break

            if ticket.get("assigned_to"):
                ticket["assigned_to"] = staff_name
                print("Ticket reassigned successfully")
            else:
                ticket["assigned_to"] = staff_name
                print("Ticket assigned successfully")

            break

    if not ticket_found:
        print("Ticket not found. Please enter a valid ticket ID.")

def update_ticket_status(tickets):
    ticket_id = input("Enter the ticket ID: ").strip()

    ticket_found = False

    for ticket in tickets:

        if ticket["id"] == ticket_id:
            ticket_found = True

            current_status = ticket["status"]

            print("Current status:", current_status)

            print("Available status options:")
            print("1. In progress")
            print("2. Resolved")

            choice = input("Choose a status: ").strip()

            if choice == "1":
                new_status = "in_progress"

            elif choice == "2":
                new_status = "resolved"

            else:
                print("Invalid choice.")
                return

            if current_status == "resolved":
                print("This ticket is resolved.")
                print("Reopen it before changing its status.")
                return

            if new_status == "in_progress":
                if not ticket.get("assigned_to"):
                    print("Cannot start an unassigned ticket.")
                    return

                if current_status != "open":
                    print("Only open tickets can move to in_progress.")
                    return

            if new_status == "resolved":
                if current_status != "in_progress":
                    print("Only in_progress tickets can be resolved.")
                    return

            ticket["status"] = new_status

            print("Ticket status updated successfully.")
            print("New status:", ticket["status"])

            return

    if not ticket_found:
        print("Ticket not found. Please enter a valid ticket ID.")

def reopen_ticket(tickets):
    ticket_id = input("Enter the ticket ID to reopen: ").strip()

    for ticket in tickets:

        if ticket["id"] == ticket_id:

            if ticket["status"] != "resolved":
                print("Only resolved tickets can be reopened.")
                return

            ticket["status"] = "open"

            print("Ticket reopened successfully.")
            print("New status:", ticket["status"])

            return

    print("Ticket not found. Please enter a valid ticket ID.")
    
def get_work_queue(tickets):
    priority_order = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
    }

    work_queue = []

    for ticket in tickets:
        if ticket["status"] == "open":
            work_queue.append(ticket)

    work_queue.sort(
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        )
    )

    return work_queue
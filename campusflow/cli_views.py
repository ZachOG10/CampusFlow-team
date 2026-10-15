
from pathlib import Path

from campusflow.search import (
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_STATUSES,
    normalize_filter,
    search_tickets,
    sort_results_by_priority,
)
from campusflow.understanding_check import run_check, save_explanations

NOTES_FILE = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "understanding-check-notes.md"
)


def parse_menu_choice(raw, lowest, highest):
    """Return the menu number if raw is a whole number in range, else None."""
    if not isinstance(raw, str):
        return None
    raw = raw.strip()
    if not raw.isdigit():
        return None
    number = int(raw)
    return number if lowest <= number <= highest else None


def find_ticket(tickets, ticket_id):
    """Return the ticket with this ID (case-insensitive) or None."""
    wanted = ticket_id.strip().upper()
    for ticket in tickets:
        if str(ticket["id"]).upper() == wanted:
            return ticket
    return None


def note_sort_key(note):
    """Sort notes by their numeric part: N002 before N010."""
    return int(note["note_id"][1:])


def prompt_filter(label, allowed, input_fn=input, output_fn=print):
    options = "/".join(allowed)
    while True:
        raw = input_fn(f"{label} ({options}, or press Enter for any): ")
        try:
            return normalize_filter(raw, allowed)
        except ValueError:
            output_fn(f"Invalid {label.lower()}. Choose {options}, or leave it blank.")


def format_search_results(results):
    if not results:
        return "No tickets match your search."

    lines = [f"\n{len(results)} ticket(s) found:"]
    for ticket in results:
        lines.append("\n****************************")
        lines.append(f"ID: {ticket['id']}")
        lines.append(f"Title: {ticket['title']}")
        lines.append(f"Category: {ticket['category']}")
        lines.append(f"Priority: {ticket['priority']}")
        lines.append(f"Status: {ticket['status']}")
        lines.append(f"Assigned to: {ticket['assigned_to']}")
    return "\n".join(lines)


def search_view(tickets, input_fn=input, output_fn=print):
    output_fn("\n******** SEARCH TICKETS *************")

    if not tickets:
        output_fn("There are no tickets to search yet.")
        return []

    title = input_fn("Title contains (press Enter for any): ")
    category = prompt_filter("Category", VALID_CATEGORIES, input_fn, output_fn)
    status = prompt_filter("Status", VALID_STATUSES, input_fn, output_fn)
    priority = prompt_filter("Priority", VALID_PRIORITIES, input_fn, output_fn)

    results = search_tickets(tickets, title, category, status, priority)

    if results:
        while True:
            answer = input_fn("Sort results by priority? (y/n): ").strip().casefold()
            if answer in ("y", "n"):
                break
            output_fn("Please enter y or n.")
        if answer == "y":
            results = sort_results_by_priority(results)

    output_fn(format_search_results(results))
    return results


def add_note_view(tickets, add_note_fn, input_fn=input, output_fn=print):
    
    output_fn("\n~~~~~~~ ADD FOLLOW-UP NOTE ~~~~~~~~")

    if add_note_fn is None:
        output_fn("Follow-up notes are not available yet.")
        return False

    if not tickets:
        output_fn("There are no tickets to add notes to.")
        return False

    ticket_id = input_fn("Enter the ticket ID: ").strip().upper()
    if find_ticket(tickets, ticket_id) is None:
        output_fn("Ticket not found. Please enter a valid ticket ID.")
        return False

    author = input_fn("Enter the author label: ")
    message = input_fn("Enter the note message (5-300 characters): ")

    try:
        note = add_note_fn(ticket_id, author, message)
    except ValueError as error:
        output_fn(f"Note not added: {error}")
        return False

    note_id = note.get("note_id") if isinstance(note, dict) else None
    if note_id:
        output_fn(f"Note {note_id} added to {ticket_id}.")
    else:
        output_fn(f"Note added to {ticket_id}.")
    return True


def format_ticket_notes(ticket):
    notes = sorted(ticket.get("notes", []), key=note_sort_key)

    if not notes:
        return f"Ticket {ticket['id']} has no notes yet."

    lines = [f"\nNotes for {ticket['id']} - {ticket['title']} ({ticket['status']}):"]
    for note in notes:
        lines.append("\n************************")
        lines.append(f"Note ID: {note['note_id']}")
        lines.append(f"Author: {note['author']}")
        lines.append(f"Message: {note['message']}")
    return "\n".join(lines)


def view_notes_view(tickets, input_fn=input, output_fn=print):
    output_fn("\n***** VIEW TICKET NOTES *******")

    if not tickets:
        output_fn("There are no tickets yet.")
        return None

    ticket_id = input_fn("Enter the ticket ID: ")
    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        output_fn("Ticket not found. Please enter a valid ticket ID.")
        return None

    output_fn(format_ticket_notes(ticket))
    return ticket


def understanding_check_view(input_fn=input, output_fn=print,
                             notes_path=NOTES_FILE):
    while True:
        label = input_fn("Enter your engineer label (for example Engineer B): ").strip()
        if label:
            break
        output_fn("The label cannot be blank.")

    result = run_check(input_fn=input_fn, output_fn=output_fn)
    save_explanations(notes_path, label, result)
    output_fn(f"Your explanations were saved to {notes_path}.")
    return result
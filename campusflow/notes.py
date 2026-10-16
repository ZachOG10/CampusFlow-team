def validate_note_author(author):
    if not isinstance(author, str) or author.strip() == "":
        raise ValueError("Author cannot be empty.")
    return author.strip()

def validate_note_message(message):
    if not isinstance(message, str):
        raise ValueError("Message must be between 5 and 300 characters.")
    trimmed = message.strip()
    if not (5 <= len(trimmed) <= 300):
        raise ValueError("Message must be between 5 and 300 characters.")
    return trimmed

def next_note_id(ticket):
    highest = 0
    for note in ticket.get("notes", []):
        try:
            highest = max(highest, int(str(note["note_id"])[1:]))
        except (KeyError, ValueError):
            continue
    return f"N{highest + 1:03}"

def add_note(ticket, author, message):
    validated_author = validate_note_author(author)
    validated_message = validate_note_message(message)

    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError("Notes can only be added to open or in_progress tickets. "
                         "Reopen a resolved ticket first.")

    note = {
        "note_id": next_note_id(ticket),
        "author": validated_author,
        "message": validated_message,
    }

    ticket.setdefault("notes", []).append(note)
    return note
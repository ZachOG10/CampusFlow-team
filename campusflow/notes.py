note_count = 1

def validate_note_author(author):
    if not isinstance(author, str) or author.strip() == "":
        raise ValueError("Author cannot be empty.")
    return author.strip()

def validate_note_message(message):
    if not isinstance(message, str) or not (5 <= len(message) <= 300):
        raise ValueError("Message must be between 5 and 300 characters.")
    return message

def add_note(ticket, author, message):
    global note_count
    
    validated_author = validate_note_author(author)
    validated_message = validate_note_message(message)
    
    if ticket.get("status") == "resolved":
        raise ValueError("Cannot add notes to a resolved ticket.")
        
    note = {
        "id": f"N{note_count:03}",
        "author": validated_author,
        "message": validated_message
    }
    
    note_count += 1
    if "notes" not in ticket:
        ticket["notes"] = []
    ticket["notes"].append(note)
    
    return note
def add_note_to_ticket(ticket, author, message):
    if ticket["status"] not in ["open", "in_progress"]:
        raise ValueError("Cannot add notes to a resolved ticket.")
    
    cleaned_author = author.strip()
    cleaned_message = message.strip()
    
    if not cleaned_author:
        raise ValueError("Author cannot be blank.")
    if not (5 <= len(cleaned_message) <= 300):
        raise ValueError("Message must be between 5 and 300 characters.")
    
        next_id_num = len(ticket.get("notes", [])) + 1
    note_id = f"N{next_id_num:03d}" 
    
    new_note = {
        "note_id": note_id,
        "author": cleaned_author,
        "message": cleaned_message
    }
    
    ticket["notes"].append(new_note)
    return ticket
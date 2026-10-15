import json
import os
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "tickets.json"
)

def save_tickets(tickets, file_path=DATA_FILE):
    file_path = Path(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)

def load_tickets(file_path=DATA_FILE):
    file_path = Path(file_path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"The ticket data file contains invalid JSON: {file_path}"
        ) from error

    if not isinstance(tickets, list):
        raise ValueError(
            "The ticket data file must contain a list of tickets."
        )

    seen_ids = set()
    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError(
                "Every saved ticket must be a dictionary."
            )
        
        ticket_id = ticket.get("id")
        if not ticket_id:
            raise ValueError("A saved ticket is missing an ID.")
            
        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID detected: {ticket_id}. Load rejected.")
            
        seen_ids.add(ticket_id)

    return tickets
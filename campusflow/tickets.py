count = 1

def next_ticket_number(all_tickets):
    highest = 0
    for ticket in all_tickets:
        try:
            highest = max(highest, int(str(ticket["id"])[1:]))
        except (KeyError, ValueError):
            continue
    return highest + 1

def create_ticket(title, category, urgency, affected_users, all_tickets=None):
    global count
    if not isinstance(title, str) or title.strip() == "":
        return None
    category = category.strip().title()
    if category not in ["Network", "Hardware", "Software", "Other"]:
        return None
    urgency = urgency.strip().lower()
    if urgency not in ["low", "medium", "high"]:
        return None
    if not isinstance(affected_users, int) or isinstance(affected_users, bool) or affected_users <= 0:
        return None
        
    if urgency == "high" and affected_users >= 10:
        priority = "critical"
    elif urgency == "high" or affected_users >= 10:
        priority = "high"
    elif urgency == "medium" or affected_users >= 3:
        priority = "medium"
    else:
        priority = "low"
        
    if all_tickets is not None:
        number = next_ticket_number(all_tickets)
    else:
        number = count

    ticket = {
        "id": f"T{number:03}",
        "title": title.strip(),
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "status": "open",
        "assigned_to": None,
        "priority": priority,
        "notes": [],
    }
    count = number + 1
    return ticket
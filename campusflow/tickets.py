count = 1
def create_ticket(title, category, urgency, affected_users):
    global count
    if title.strip() == "":
        print("Enter valid title id!")
        return None
    if category not in ["Network", "Hardware", "Software", "Other"]:
        print("Invalid category")
        return None
    if urgency not in ["low", "medium", "high"]:
        print("Invalid urgency")
        return None
    if not isinstance(affected_users, int) or isinstance(affected_users, bool) or affected_users <= 0:
        print("enter a valid number")
        return None
    if urgency == "high" and affected_users >= 10:
        priority = "critical"
    elif urgency == "high" or affected_users >= 10:
        priority = "high"
    elif urgency == "medium" or affected_users >= 3:
        priority = "medium"
    else:
        priority = "low"
    tickets = {
        "id": f"T{count:03}",
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "status": "open",
        "assigned_to": None,
        "priority": priority
    }
    count += 1
    return tickets
print(create_ticket("WI-FI not working", "Network", "high", 2))
print(create_ticket("", "Network", "high", 20))
print(create_ticket("Laptop broken", "cooking", "low", 2))
print(create_ticket("App crashing", "Software", "urgent", 5))
print(create_ticket("Slow WI-FI", "Network", "low", 0))

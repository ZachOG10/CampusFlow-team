def generate_ticket_report(tickets):
    report = {
        "total_tickets": len(tickets),
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]
        if status == "open":
            report["open"] += 1
        elif status == "in_progress":
            report["in_progress"] += 1
        elif status == "resolved":
            report["resolved"] += 1
        if priority == "critical":
            report["critical"] += 1
        elif priority == "high":
            report["high"] += 1
        elif priority == "medium":
            report["medium"] += 1
        elif priority == "low":
            report["low"] += 1

    return report

#new modification
def count_by_category(tickets):
    canonical = {"network": "Network", "hardware": "Hardware",
                 "software": "Software", "other": "Other"}
    counts = {"Network": 0, "Hardware": 0, "Software": 0, "Other": 0}
    for ticket in tickets:
        raw_category = ticket.get("category")
        if raw_category is None:
            counts["Other"] += 1
            continue

   # Normalize variations like " network " or "SOFTWARE" into correct keys
        key = str(raw_category).strip().casefold()
        label = canonical.get(key, str(raw_category).strip())
        
        counts[label] = counts.get(label, 0) + 1
                   
    return counts


def resolution_percentage(tickets):
    #Percent of tickets resolved, rounded to 1 decimal place and 0.0 if no tickets.
    total = len(tickets)
    if total == 0:
        return 0.0
        
    resolved = sum(1 for t in tickets if str(t.get("status", "")).strip().casefold() == "resolved")
    percentage = round((resolved / total) * 100, 1)
    return percentage


def generate_detailed_report(tickets):
  #Enhanced report: base summary + unresolved, categories, resolution %.
    base = generate_ticket_report(tickets)
    
    # Calculate operational metrics seamlessly from inherited keys
    base["unresolved_tickets"] = base["open"] + base["in_progress"]
    base["resolved_tickets"] = base["resolved"]
    
    # Attach your newly extended analytical features
    base["categories"] = count_by_category(tickets)
    base["resolution_percentage"] = resolution_percentage(tickets)
    
    return base

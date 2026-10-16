
VALID_CATEGORIES = ("Network", "Hardware", "Software", "Other")
VALID_STATUSES = ("open", "in_progress", "resolved")
VALID_PRIORITIES = ("critical", "high", "medium", "low")

PRIORITY_ORDER = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}


def normalize_filter(value, allowed):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Filter must be text.")

    cleaned = value.strip().casefold().replace(" ", "_")
    if cleaned == "":
        return None

    for option in allowed:
        if option.casefold() == cleaned:
            return option

    raise ValueError(f"Invalid filter option: {value!r}")


def search_tickets(tickets, title="", category=None, status=None, priority=None):
  
    title_query = "" if title is None else str(title).strip().casefold()
    category = normalize_filter(category, VALID_CATEGORIES)
    status = normalize_filter(status, VALID_STATUSES)
    priority = normalize_filter(priority, VALID_PRIORITIES)

    results = []
    for ticket in tickets:
        if title_query and title_query not in ticket["title"].casefold():
            continue
        if category is not None and ticket["category"] != category:
            continue
        if status is not None and ticket["status"] != status:
            continue
        if priority is not None and ticket["priority"] != priority:
            continue
        results.append(ticket)

    return results


def sort_results_by_priority(results):
    return sorted(
        results,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )
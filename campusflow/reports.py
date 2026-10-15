
STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")
CATEGORIES = ("Network", "Hardware", "Software", "Other")


def calculate_resolution_percentage(resolved_count, total_count):
    if total_count == 0:
        return 0.0
    return round(resolved_count / total_count * 100, 2)


def generate_ticket_report(tickets):
    report = {
        "total_tickets": len(tickets),
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "by_category": {category: 0 for category in CATEGORIES},
    }

    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]
        category = ticket.get("category")

        if status in STATUSES:
            report[status] += 1
        if priority in PRIORITIES:
            report[priority] += 1
        if category in report["by_category"]:
            report["by_category"][category] += 1

    report["unresolved"] = report["open"] + report["in_progress"]
    report["resolution_percentage"] = calculate_resolution_percentage(
        report["resolved"], report["total_tickets"]
    )

    return report


def format_report(report):
    """Turn a report dictionary into printable text (no printing here).

    Keeping formatting separate from printing lets tests check the text
    without capturing stdout.
    """
    lines = [
        "****** TICKET REPORT *******",
        f"Total tickets: {report['total_tickets']}",
        "",
        "Tickets by status:",
        f"Open: {report['open']}",
        f"In progress: {report['in_progress']}",
        f"Resolved: {report['resolved']}",
        "",
        "Tickets by priority:",
        f"Critical: {report['critical']}",
        f"High: {report['high']}",
        f"Medium: {report['medium']}",
        f"Low: {report['low']}",
        "",
        "Tickets by category:",
    ]
    for category in CATEGORIES:
        lines.append(f"{category}: {report['by_category'][category]}")

    lines += [
        "",
        f"Unresolved (open + in progress): {report['unresolved']}",
        f"Resolved: {report['resolved']}",
        f"Resolution rate: {report['resolution_percentage']}%",
    ]
    return "\n".join(lines)
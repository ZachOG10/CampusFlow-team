def search_tickets(tickets, search_word=None, category=None, status=None, priority=None):
    search_results = []

    for ticket in tickets:
        if search_word is not None:
            normalize = str(search_word).strip().casefold()
            check_title = str(ticket.get("title", "")).casefold()
            if normalize not in check_title:
                continue

        if category is not None:
            wanted = str(category).strip().casefold()
            actual = str(ticket.get("category", "")).casefold()
            if wanted != actual:
                continue

        if status is not None:
            wanted = str(status).strip().casefold()
            actual = str(ticket.get("status", "")).casefold()
            if wanted != actual:
                continue

        if priority is not None:
            wanted = str(priority).strip().casefold()
            actual = str(ticket.get("priority", "")).casefold()
            if wanted != actual:
                continue

        search_results.append(ticket)

    return search_results
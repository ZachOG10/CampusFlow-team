## ENGINEER B - OMALE MOSES

**Decision:** `generate_ticket_report` keeps direct indexing (`ticket["status"]`,
`ticket["priority"]`) unchanged. New added functions (`count_by_category`,
`resolution_percentage`, `generate_detailed_report`) use `.get(field, default)` defensively.

**Why:** The original function is tested and used by an existing CLI menu option.
Rewriting it to `.get()` would change its contract (silent skip vs. loud crash on
malformed data) and risk regression in already-passing tests. New functions add
behaviour; touching the old one removes nothing but risks breaking the old report.

**Trade-off accepted:** Slight inconsistency in style. Documented here so a
reviewer knows it's a deliberate choice, not oversight.

**Related files:** campusflow/reports.py
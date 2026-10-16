def validate_affected_users(value):
    if isinstance(value, bool):
        raise TypeError("affected_users cannot be a boolean.")
    if not isinstance(value, int) or value <= 0:
        raise ValueError("affected_users must be a strictly positive integer.")
    return value

def validate_category(category):
    canonical_categories = {"Network", "Hardware", "Software", "Other"}
    normalized = category.strip().capitalize()
    if normalized not in canonical_categories:
        raise ValueError(f"Invalid category. Must be one of: {canonical_categories}")
    return normalized

def validate_urgency(urgency):
    canonical_urgency = {"low", "medium", "high"}
    normalized = urgency.strip().casefold()
    if normalized not in canonical_urgency:
        raise ValueError("Urgency must be low, medium, or high.")
    return normalized
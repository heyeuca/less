from datetime import date


def parse_date(text):
    """Parse YYYY-MM-DD."""
    year, month, day = (int(part) for part in text.split("-"))
    return date(year, month, day)


def parse_range(text):
    """Parse 'YYYY-MM-DD..YYYY-MM-DD' into a (start, end) pair."""
    start, end = text.split("..")
    return parse_date(start), parse_date(end)

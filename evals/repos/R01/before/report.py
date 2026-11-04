def render(rows, *, compact=False, legacy_header=False):
    """Render (name, total) rows as text lines."""
    lines = []
    if legacy_header:
        lines.append("REPORT v1")
    for name, total in rows:
        lines.append(f"{name}: {total}" if compact else f"{name:<12}{total:>8}")
    return "\n".join(lines)

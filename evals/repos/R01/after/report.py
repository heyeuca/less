def render(rows, *, compact=False):
    """Render (name, total) rows as text lines."""
    lines = []
    for name, total in rows:
        lines.append(f"{name}: {total}" if compact else f"{name:<12}{total:>8}")
    return "\n".join(lines)

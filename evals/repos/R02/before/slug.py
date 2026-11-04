import re

_CACHE = {}


def slugify(title):
    if title not in _CACHE:
        _CACHE[title] = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return _CACHE[title]


def _reset_cache():
    _CACHE.clear()


def _old_slugify(title):
    return title.lower().replace(" ", "-")

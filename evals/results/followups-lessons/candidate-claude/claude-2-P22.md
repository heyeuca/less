Remove the restating comment; keep the variable as written.

```python
def retries(env):
    raw = env.get("RETRIES", "4")
    return int(raw)
```
Remove the comment restating the code; keep variables as written.

```python
def retries(env):
    raw = env.get("RETRIES", "4")
    return int(raw)
```
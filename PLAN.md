## Solution Plan

**Issue:** #155 — Health check references `settings.redis_host`, which does not exist on Settings
**Link:** https://github.com/ascherj/pathreview/issues/155

### Understand

**Root cause:** The `/health` endpoint in `api/routes/health.py` constructs a Redis connection using `settings.redis_host` and `settings.redis_port`. However, the `Settings` class in `core/config.py` defines only a single `redis_url` field (e.g., `redis://localhost:6379/0`), not separate `redis_host` and `redis_port` attributes. Every health check invocation crashes with `AttributeError`, causing a 503 response even when Redis is running.

**Expected behavior:** The health endpoint should successfully connect to Redis using the connection URL already available in `settings.redis_url` and report `"redis": "healthy"`.

**Actual behavior:** `AttributeError: 'Settings' object has no attribute 'redis_host'` is raised on every health check, producing a false 503.

### Map

Specific files and functions involved:

| File | Function/Role |
|------|---------------|
| `api/routes/health.py` | `health_check()` — constructs Redis probe using non-existent attribute |
| `core/config.py` | `Settings.redis_url` — only Redis config field available |
| `rag/evaluator/faithfulness_checker.py` | `check()` — crashes on `text: None` in context chunks (related #153) |
| `api/routes/health.py` | `health_check()` — DB probe uses raw SQL string without `text()` (related #154) |

### Plan

1. **Replace `redis_host`/`redis_port` with `redis.from_url()` in `api/routes/health.py`**
   - Remove the `redis.Redis(host=..., port=...)` constructor call
   - Replace with `redis.from_url(settings.redis_url, decode_responses=True)`
   - Remove the unused `settings.redis_host` and `settings.redis_port` references

2. **Wrap raw SQL with `text()` in `api/routes/health.py`**
   - Add `from sqlalchemy import text` to the imports
   - Change `await db.execute("SELECT 1")` to `await db.execute(text("SELECT 1"))`
   - Required for SQLAlchemy 2.x compatibility

3. **Guard against `None` text in `rag/evaluator/faithfulness_checker.py`**
   - Change `chunk.get("text", "")` to `chunk.get("text") or ""`
   - The `or` operator catches both missing keys and explicit `None` values

### Inputs & Outputs

**Issue #155 fix:**
- **Input:** `GET /health` request when Redis is running
- **Output:** `"redis": "healthy"` in the health check response (instead of `AttributeError` + 503)
- **Changed behavior:** Redis connection uses `redis.from_url(settings.redis_url)` instead of `redis.Redis(host=..., port=...)`

**Risks:**
- `redis.from_url()` expects a URL with scheme prefix (`redis://...`); if `settings.redis_url` is misconfigured or empty, it will fail with a different error. This is handled by the existing `try/except` block.
- `redis.from_url()` interprets URL query parameters (e.g., `?socket_timeout=5`); existing URL in defaults is clean (`redis://localhost:6379/0`), so no unintended side effects.
- Both `redis.Redis()` and `redis.from_url()` return the same `Redis` client class, so `r.ping()` works identically.

### Edge cases

1. **Redis not installed or unreachable:** The `try/except` block already catches connection errors — fix does not change this behavior. Result will remain `"unhealthy"`.

2. **`settings.redis_url` is empty string:** `redis.from_url("")` raises `ValueError` — caught by the existing `except Exception as exc` block, resulting in `"unhealthy"` as expected.

3. **Context chunk has `"text": None` (faithfulness checker):** `chunk.get("text") or ""` returns `""` instead of `None`, preventing `TypeError` in `" ".join(...)`. Empty string contributes nothing to the context match but doesn't crash.

4. **Context chunk missing `"text"` key entirely:** `chunk.get("text") or ""` returns `""` (key is absent, `.get()` returns `None`, `None or ""` yields `""`). Same safe behavior as above.

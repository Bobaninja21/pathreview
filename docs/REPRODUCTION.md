# Reproduction: Issue #155 — Health check references `settings.redis_host`

## Bug Description

The `/health` endpoint in `api/routes/health.py` tries to connect to Redis using `settings.redis_host` and `settings.redis_port`, but the `Settings` class in `core/config.py` only defines `redis_url`.

## Reproduction Steps

1. Start the application with `make run`.
2. Call `GET /health` from the browser or curl.
3. Observe the response is `503` with `"redis": "unhealthy"`.
4. Check the application logs for `redis_health_check_failed` with an `AttributeError: 'Settings' object has no attribute 'redis_host'`.

## Expected Behavior

The health endpoint should connect to Redis successfully when Redis is running, returning `"redis": "healthy"`.

## Actual Behavior

The health check crashes with `AttributeError` because `settings.redis_host` does not exist. The Settings object only exposes `redis_url` (line 12 of `core/config.py`):

```python
redis_url: str = Field(default="redis://localhost:6379/0")
```

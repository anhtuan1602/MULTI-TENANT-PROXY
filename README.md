# Multi‑Tenant Rate Limiting Proxy Gateway

## Overview
A minimal FastAPI example demonstrating per‑tenant sliding‑window rate limiting and a small GitHub Copilot Chat "fleet" (agents, subagents, skills, hooks). Designed to run locally without a real Redis by using `fakeredis` so it's easy to try.

## Quick setup
1. Create and activate a virtual environment (Python 3.11+ recommended):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the server
Run directly:

```bash
python proxy_server.py
```

or with Uvicorn:

```bash
uvicorn proxy_server:app --host 127.0.0.1 --port 8000
```

Endpoints:
- `GET /status` — health check.
- `GET /api/resource` — protected; requires header `X-API-Key: free_tier_key` or `premium_tier_key`.

## Tests
Run tests with:

```bash
pytest -q
```

Notes:
- Tests use `httpx` with `ASGITransport` and `fakeredis` to run in‑process without external services.
- A fixture clears the fake Redis before each test.

## Key files
- [proxy_server.py](proxy_server.py) — FastAPI app and endpoints.
- [services/redis_tracker.py](services/redis_tracker.py) — sliding‑window rate limiter (uses `fakeredis`).
- [config.py](config.py) — tenant API keys and limits.
- [test_proxy.py](test_proxy.py) — async tests.
- [requirements.txt](requirements.txt) — dependencies.

## GitHub Copilot "fleet" (agents, skills, hooks)
This repo contains example Copilot Chat configurations demonstrating how to structure a small fleet:

- Agents (subagents): `.github/copilot/agents/*.yaml`
  - `auditor.yaml` — Traffic Auditor subagent (reads `proxy_server.py` and reports HTTP-compliance).
  - `engineer.yaml` — Router Engineer subagent (suggests async/endpoint improvements).
  - `planner.yaml` — Network Planner subagent (plans routing changes).
- Skill: `.github/skills/rate-limiter/SKILL.md` — shared guidance (e.g., always return HTTP 429 and `Retry-After`).
- Hook: `.github/copilot/hooks/security.json` — runs `scripts/guard-network.sh` as a `PreToolUse` guard to block certain unsafe network commands.
- Guard script: [scripts/guard-network.sh](scripts/guard-network.sh) — example sandbox policy used by the hook.

These files are illustrative: they show how to connect agents → skills → hooks so Copilot Chat can run focused, policy‑aware subagents against the repo.

## Design notes
- `services/redis_tracker.py` stores timestamps in a Redis sorted set per API key, removes old timestamps outside the window, and counts the current members to decide throttling.
- `fakeredis` is used to make local testing simple; replace with a real `redis` client and server to run in production.

## Switching to real Redis
1. Install `redis` (Python client) and run a Redis server.
2. Update `services/redis_tracker.py` to initialize a real `StrictRedis`/`Redis` client and configure host/port/credentials.

## Troubleshooting
- Ensure the virtualenv is active and dependencies installed.
- If tests fail after switching to real Redis, check connectivity and credentials.

Notes:
- Tests use `httpx` + `ASGITransport` and `fakeredis` so they run in‑process without external services.
- A fixture clears the fake Redis database before each test.

## Copilot fleet example: how the `/fleet` command flows
If you type the example Copilot CLI command:

```
/fleet Ask the Network Planner to sketch out a status monitoring route, have the Router Engineer append it to `proxy_server.py`, and use the Traffic Auditor to confirm it returns correct HTTP spec headers.
```

Typical fleet behavior:
1. The Copilot CLI forwards the request to the fleet orchestrator.
2. **Network Planner** (planner subagent) reads the repo and proposes a new route design (signature, path, payload).
3. **Router Engineer** (engineer subagent) applies the change — edits `proxy_server.py` to add the new async endpoint with proper type hints and headers.
4. Before any external tools run, the configured `PreToolUse` hook executes `scripts/guard-network.sh` to block unsafe network commands.
5. **Traffic Auditor** (auditor subagent) inspects the added route (or calls it) and verifies HTTP behavior: correct status codes (e.g., 200/429), required headers (e.g., `Retry-After` on 429, `Cache-Control` where applicable).
6. The fleet returns a summary and (optionally) a patch or PR with the change if configured.

This repo's `.github/copilot` files show how agents → skills → hooks are wired so Copilot Chat can run focused, policy‑aware subagents against the codebase.

---

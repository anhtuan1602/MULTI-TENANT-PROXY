---
name: http-spec
description: Guidelines for manipulating proxy routing response boundaries.
---
# HTTP Standards Skill

Whenever adding paths or editing proxy routers:
1. Block states MUST issue an explicit HTTP 429 status code.
2. Throttled responses MUST contain a `Retry-After` response header integer.
3. Every endpoint signature must include explicit Python type hints.

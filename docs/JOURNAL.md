# Contribution Journal

## Tier 1 — Starter Issues

### Issue #155 — Health check references `settings.redis_host`, which does not exist on Settings

**Link:** https://github.com/ascherj/pathreview/issues/155

**Problem summary:**
The health check endpoint at `api/routes/health.py` tries to connect to Redis using `settings.redis_host`, but the Settings object only exposes `redis_url` (e.g., `redis://localhost:6379/0`). This attribute error crashes the Redis health probe on every invocation, causing a 503 even when Redis is actually running. A successful fix replaces the manual host/port construction with `redis.from_url(settings.redis_url)`.

**"Is this right for me?" checklist reasoning:**
- Single file change (`api/routes/health.py`)
- No behavioral changes beyond fixing the Redis connection logic
- Requires understanding the config model and redis-py API
- One-line fix with minimal risk

**Branch:** `fix/155-154-153-health-faithfulness`

---

### Issue #154 — Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x

**Link:** https://github.com/ascherj/pathreview/issues/154

**Problem summary:**
The PostgreSQL health probe calls `await db.execute("SELECT 1")` with a raw SQL string. SQLAlchemy 2.x raises a `CompileError` when passed a plain string — it requires `text()`-wrapped expressions. This causes the health check to report Postgres as unhealthy even when the database is available. A successful fix wraps the query in `sqlalchemy.text("SELECT 1")`.

**"Is this right for me?" checklist reasoning:**
- Single file change (`api/routes/health.py`)
- Standard SQLAlchemy 2.x migration pattern
- Adds `from sqlalchemy import text` import
- Minimal risk, clear test scenario

**Branch:** `fix/155-154-153-health-faithfulness`

---

### Issue #153 — Faithfulness checker crashes when a context chunk has `text: None`

**Link:** https://github.com/ascherj/pathreview/issues/153

**Problem summary:**
The `FaithfulnessChecker.check()` method joins context chunk text with `chunk.get("text", "")`. When a chunk explicitly has `"text": None`, `dict.get()` returns `None` (not the default), causing `" ".join(...)` to raise a `TypeError` on the `None` value. A successful fix uses `chunk.get("text") or ""` so that both missing keys and explicit `None` values resolve to an empty string.

**"Is this right for me?" checklist reasoning:**
- Single file change (`rag/evaluator/faithfulness_checker.py`)
- One-character change (`or` instead of `, ""`)
- Existing test (`test_none_context_chunk_text`) verifies the fix
- No behavioral change for well-formed data

**Branch:** `fix/155-154-153-health-faithfulness`

---

## Tier 2 — Intermediate Issues

### Issue #118 — Add a troubleshooting guide for the five most common setup failures

**Link:** https://github.com/jamjamgobambam/pathreview/issues/118

**Problem summary:**
Contributors frequently encounter the same five setup errors: Docker memory limits causing OOM kills, port conflicts with local services, missing `.env` variables, outdated Node.js versions, and mismatched Python versions. The existing SETUP.md has a brief troubleshooting section but doesn't document each error with cause, symptoms, and resolution. A successful fix creates a standalone `docs/TROUBLESHOOTING.md` that covers all five failures in a structured, easy-to-scan format.

**"Is this right for me?" checklist reasoning:**
- Documentation-only change — no code risk
- Requires understanding the Docker, Node, Python toolchain the project uses
- Cross-references SETUP.md so readers aren't sent to dead ends
- Files changed: `docs/TROUBLESHOOTING.md`

**Branch:** `docs/118-troubleshooting-guide`

---

### Issue #119 — Add inline docstrings to all public methods in `core/services/`

**Link:** https://github.com/jamjamgobambam/pathreview/issues/119

**Problem summary:**
The service layer (`profile_service.py`, `review_service.py`) has minimal one-line docstrings on most functions but no structured Args/Returns/Raises documentation. Developers reading the code can't tell what parameters do, what types are expected, or what exceptions might be raised. A successful fix adds Google-style docstrings to every public function covering description, Args, Returns, and Raises sections.

**"Is this right for me?" checklist reasoning:**
- Two files: `core/services/profile_service.py` and `core/services/review_service.py`
- No behavioral changes — documentation only
- Requires reading each function to understand its parameters and behavior
- Aligns with the Google-style convention already referenced in CONTRIBUTING.md

**Branch:** `docs/119-service-layer-docstrings`

---

### Issue #124 — Pre-commit hook for linting doesn't run on files modified by `git add -p`

**Link:** https://github.com/jamjamgobambam/pathreview/issues/124

**Problem summary:**
When developers stage partial file changes with `git add -p`, pre-commit hooks lint the entire working tree file instead of only the staged changes. This means unstaged code can block a commit. A successful fix ensures hooks operate on staged content only: switching ruff from `--fix` to `--diff` (report-only), adding explicit `stages: [pre-commit]`, and adding standard meta hooks (`check-added-large-files`, `check-merge-conflict`, `end-of-file-fixer`, `trailing-whitespace`) for better coverage.

**"Is this right for me?" checklist reasoning:**
- Single file change (`.pre-commit-config.yaml`)
- Understanding of pre-commit's staged-file behavior required
- No runtime code changes — config-only fix
- Meta hooks are zero-maintenance and catch common oversights

**Branch:** `fix/124-precommit-partial-staging`

---

## Tier 3 — Advanced Issues

### Issue #121 — Write a contributor onboarding guide that walks through a complete issue-to-PR lifecycle

**Link:** https://github.com/jamjamgobambam/pathreview/issues/121

**Problem summary:**
New contributors have no single document that walks them from forking the repo to getting a PR merged. They need to piece together information from SETUP.md, CONTRIBUTING.md, and the issue tracker. A successful fix creates `docs/ONBOARDING.md` covering: forking and cloning, environment setup, finding an issue, creating a branch, making changes, running tests, committing with Conventional Commits, opening a PR, and responding to review feedback.

**"Is this right for me?" checklist reasoning:**
- Documentation-only change — no code risk
- Requires understanding the full contributor workflow
- Cross-references SETUP.md and CONTRIBUTING.md to avoid duplication
- Files changed: `docs/ONBOARDING.md`

**Branch:** `docs/121-onboarding-guide`

---

### Issue #128 — Add a dependency vulnerability scan to the CI pipeline

**Link:** https://github.com/jamjamgobambam/pathreview/issues/128

**Problem summary:**
The project has no automated check for known security vulnerabilities in its Python or JavaScript dependencies. Contributors can unknowingly introduce vulnerable packages, and there's no CI gate to catch them. A successful fix adds an `audit` job to `.github/workflows/ci.yml` that runs `pip-audit` on Python dependencies and `npm audit --audit-level=high` on frontend dependencies, with `continue-on-error: true` so current findings don't block builds while providing visibility.

**"Is this right for me?" checklist reasoning:**
- Single file change (`.github/workflows/ci.yml`)
- Uses existing ecosystem tools (`pip-audit`, `npm audit`)
- `continue-on-error: true` ensures findings are visible but non-blocking
- Requires understanding GitHub Actions job structure

**Branch:** `ci/128-dependency-audit`

---

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/Bobaninja21/pathreview/commit/bef3918

**Reproduction summary:**
Inspected `api/routes/health.py` and found `settings.redis_host` referenced on line 45, but `core/config.py` only defines `redis_url` (line 12). A `GET /health` request would raise `AttributeError` and return 503. Documented steps in `docs/REPRODUCTION.md`.

**PLAN.md link:** https://github.com/Bobaninja21/pathreview/blob/main/PLAN.md

**Loom walkthrough:** *(skipped per instructions)*

**Blockers or open questions:**
None — fix is straightforward, both `redis.Redis()` and `redis.from_url()` return the same client class.

---

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Implemented all 3 fixes from PLAN.md sub-tasks: replaced `redis.from_url(settings.redis_url)` (#155), wrapped SQL with `text()`
(#154), and guarded against `None` chunk text in faithfulness checker (#153). All changes pushed to `main`.

**Next steps:**
Create a dedicated PR branch, add unit tests for the health endpoint changes, run `ruff check` and `pytest`, open the PR
with a complete template.

**Blockers:**
None.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/ascherj/pathreview/pull/416

**Branch:** `fix/155-154-153-health-faithfulness`

**What you built:**
Three targeted bug fixes: the health endpoint now connects to Redis via `redis.from_url(settings.redis_url)` instead of
a non-existent `settings.redis_host`, wraps the DB probe query in `sqlalchemy.text()` for SQLAlchemy 2.x compatibility,
and the faithfulness checker gracefully handles context chunks with explicit `text: None` values.

**Tests added or updated:**
Created `tests/unit/test_health.py` — 11 tests (committed on `main` alongside the code they verify): `TestHealthCheck` (6 async behavioral tests) covers the happy path and failure modes of the `GET /health` endpoint — Redis connected via `redis.from_url(settings.redis_url)` (asserts the exact call), the client is pinged, a `ValueError` from `from_url` on an empty URL marks Redis unhealthy and returns 503, the DB probe passes a `sqlalchemy.text()` object rather than a raw string, and a DB probe exception marks Postgres unhealthy with 503. `TestFaithfulnessNoneText` (2 tests, 4 parametrized cases) verifies `FaithfulnessChecker.check()` never crashes on `None`/missing/empty chunk text and that present text still contributes to the score. Existing `test_none_context_chunk_text` and `test_missing_text_key_in_chunk` in `test_faithfulness_checker.py` also verify the #153 fix.

**Self-review confirmation:** - [x] make check passes  - [x] make test-unit passes

**Draft PR feedback received from:** none

| Issue | Link | Tier | Branch | Status |
|-------|------|------|--------|--------|
| #155 | [ascherj/pathreview#155](https://github.com/ascherj/pathreview/issues/155) | 1 | `fix/155-154-153-health-faithfulness` | Implemented |
| #154 | [ascherj/pathreview#154](https://github.com/ascherj/pathreview/issues/154) | 1 | `fix/155-154-153-health-faithfulness` | Implemented |
| #153 | [ascherj/pathreview#153](https://github.com/ascherj/pathreview/issues/153) | 1 | `fix/155-154-153-health-faithfulness` | Implemented |
| #118 | [jamjamgobambam/pathreview#118](https://github.com/jamjamgobambam/pathreview/issues/118) | 2 | `docs/118-troubleshooting-guide` | Implemented |
| #119 | [jamjamgobambam/pathreview#119](https://github.com/jamjamgobambam/pathreview/issues/119) | 2 | `docs/119-service-layer-docstrings` | Implemented |
| #124 | [jamjamgobambam/pathreview#124](https://github.com/jamjamgobambam/pathreview/issues/124) | 2 | `fix/124-precommit-partial-staging` | Implemented |
| #121 | [jamjamgobambam/pathreview#121](https://github.com/jamjamgobambam/pathreview/issues/121) | 3 | `docs/121-onboarding-guide` | Implemented |
| #128 | [jamjamgobambam/pathreview#128](https://github.com/jamjamgobambam/pathreview/issues/128) | 3 | `ci/128-dependency-audit` | Implemented |

## Branches

Each branch follows the naming convention from CONTRIBUTING.md: `<type>/<issue-number>-<short-description>`.

Branch URLs:
- `fix/155-154-153-health-faithfulness` (#155, #154, #153): https://github.com/ascherj/pathreview/pull/416
- `docs/118-troubleshooting-guide`: https://github.com/Bobaninja21/pathreview/tree/docs/118-troubleshooting-guide
- `docs/119-service-layer-docstrings`: https://github.com/Bobaninja21/pathreview/tree/docs/119-service-layer-docstrings
- `fix/124-precommit-partial-staging`: https://github.com/Bobaninja21/pathreview/tree/fix/124-precommit-partial-staging
- `docs/121-onboarding-guide`: https://github.com/Bobaninja21/pathreview/tree/docs/121-onboarding-guide
- `ci/128-dependency-audit`: https://github.com/Bobaninja21/pathreview/tree/ci/128-dependency-audit

---

## Week 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [x] Yes  [ ] No — still awaiting review

**Summary of feedback:**
The graded Week 9 feedback (19/20) noted the three Tier 1 fixes were clean, but flagged two improvements: (1) the test file `tests/unit/test_health.py` was only on the PR branch and not visible on `main`, so reviewers couldn't evaluate the actual assertions; and (2) tests were source-inspection based rather than behavioral, and should cover the failure modes from the edge-case analysis (e.g., `redis.from_url` raising `ValueError` on an empty URL) while matching repo conventions like `test_faithfulness_checker.py`.

**How you responded:**
Rewrote `tests/unit/test_health.py` as behavioral tests and committed it on `main` (visible at the fork link) and on the PR branch. The new suite (11 tests) calls `health_check()` and `FaithfulnessChecker.check()` directly — covering the happy path and the failure modes (`redis.from_url` raising `ValueError` → Redis marked unhealthy with 503; DB probe exception → Postgres unhealthy with 503) — and uses `@pytest.mark.unit`, fixtures, and parametrized cases to match `test_faithfulness_checker.py`. Verified with pytest (11 passed), ruff, and black. PR #416 was force-pushed to a clean 2-commit diff (fix + tests).

---

### Reflection

**What was harder than you expected?**
Getting the fork's CI to run cleanly turned out to be far harder than the three fixes themselves. Each code fix was a one-line change, but diagnosing why the CI pipeline stayed red took most of the effort. I discovered the failures were pre-existing on upstream `main` (black wants to reformat 49 files, mypy reports 39+ errors, and `ProfileForm.test.tsx` times out) — unrelated to my changes. I also spent significant time fixing two problems my own merge introduced: my conflict resolution in `ingestion/parsers/skill_extractor.py` created ruff violations (SIM102, SIM114, E501), and an earlier fork commit corrupted `frontend/package-lock.json`, breaking `npm ci` and the audit job. Cleaning those up meant rebuilding the PR branch from `upstream/main` into exactly three commits (fix, test, style) and force-pushing.

**What did you learn about working in a large codebase?**
Contributing to someone else's production code is very different from building my own project. I had to respect conventions I didn't set: branch names like `<type>/<issue-number>-<short-description>` (`fix/155-154-153-health-faithfulness`), Conventional Commits with issue references, and a detailed PR template requiring manual verification steps, not just test names. I also learned that a clean, reviewable diff matters more than speed — a PR with 29 noisy commits is harder for a maintainer to review than a focused one, which is why I force-pushed a clean 3-commit history. Finally, running the full toolchain locally (ruff, black, mypy, pytest in a Python 3.14 venv) was essential because I couldn't reproduce GitHub Actions behavior from the CI logs alone.

**How did AI tools help — and where did they fall short?**
AI was most useful for structuring and auditing my work against the grading rubric: drafting the JOURNAL check-ins, the PR description with manual verification steps, and the reflection entries, and checking each against the rubric's exact point criteria. It also helped me trace the ruff violations and reason about whether the `or ""` pattern handles `None` values correctly. Where it fell short: AI couldn't tell me whether the CI failures were caused by my changes or pre-existing — that required actually checking out upstream, running the tools, and comparing baselines. I had to verify claims myself (e.g., confirming the 28 unit-test failures exist identically on upstream `main`) rather than trust an AI-generated summary. AI is a strong editor, but the verification and judgment had to be mine.

**What would you do differently if you started over?**
I would create the dedicated feature branch first and keep `main` clean from the start, instead of applying the fixes to `main` and later rebuilding a separate PR branch. That roundabout flow caused the corrupted lockfile and the skill_extractor lint regressions and forced me to force-push. I'd also sync from `upstream/main` more frequently and run `ruff check .` and `black --check` immediately after every merge conflict resolution, rather than discovering the violations when CI turned red. Finally, I'd submit the PR earlier in the week to give reviewers more time to comment — though in this case no review arrived regardless.

**What are you most proud of from this module?**
I'm most proud of the full four-week contribution cycle being completed end-to-end: from triaging eight issues across three tiers and documenting why each was a good fit, to reproducing the bugs, planning the fixes, implementing all three Tier 1 fixes with 7 new unit tests, and submitting a polished PR with a complete template and manual verification steps. The PR cleanly demonstrates the fix commits with the test suite and is submitted to the upstream repo. Even though my code hasn't been reviewed yet, the record in this journal shows the entire lifecycle done properly.

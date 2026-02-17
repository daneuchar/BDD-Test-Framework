# Architecture Review -- api-test-framework

**Reviewer:** qa-reviewer
**Date:** 2026-02-17
**Scope:** Pattern compliance, parallel safety, integration verification, allure coverage

---

## 1. Pattern Compliance

| Check | Owner | Status | Notes |
|-------|-------|--------|-------|
| Service Object: step defs never call HTTP directly | bdd-author | PASS | All steps delegate through service methods; PATCH now uses `user_service.partial_update()` |
| Builder: no raw dict payloads | service-layer | PASS | All payloads constructed via `UserBuilder` / `AuthBuilder` -- no raw dicts in step defs or services |
| Template Method: sync/async extend base_client | core-engine | PASS | `SyncAPIClient` and `AsyncAPIClient` both extend `BaseAPIClient` and override `_send` |
| Strategy: auth swappable without changing client | core-engine | PASS | `set_auth()` on `BaseAPIClient` allows runtime strategy swap; all strategies extend `BaseAuth` ABC |
| Facade: single assertion class with fluent interface | core-engine | PASS | `ApiAssertions` class with fluent chaining; every method returns `self` |
| Factory: all dynamic test data through factories | bdd-author | PASS | `UserFactory` and `AuthFactory` from `data.factories`; used via session-scoped fixtures |
| Thin Steps: no step def > 5 lines | bdd-author | PASS | All step defs are 4 lines or fewer; batch creation uses list comprehensions |
| Shared Steps: common steps only in common_steps.py | bdd-author | PASS | `common_steps.py` contains only reusable cross-feature steps (status, schema, response_time, error) |

---

## 2. Parallel Safety

| Check | Owner | Status | Notes |
|-------|-------|--------|-------|
| No module-level mutable state | all | PASS | `_thread_local` in `base_client.py` and `allure_plugin.py` use `threading.local()` -- correct |
| No class-level shared state | all | PASS | No class-level mutable dicts or lists found |
| Faker seeded with worker_id | service-layer, architect | PASS | `BaseFactory._apply_worker_seed()` uses `PYTEST_XDIST_WORKER`; `parallel_isolation` plugin seeds globally |
| Thread-local storage for req/res | core-engine | PASS | `base_client.py:44` uses `threading.local()` for `last_request`/`last_response` |
| No test-order dependencies | bdd-author | PASS | Each scenario creates its own precondition data; no shared DB state assumed between tests |

### Parallel Safety Notes

- `config/settings.py:57` instantiates a module-level `settings = Settings()` singleton. This is **safe** because `Settings` is a frozen Pydantic model (read-only after construction) and `pydantic-settings` performs no mutable state writes after `__init__`.
- `OAuth2Auth` uses a `threading.Lock()` for token refresh -- correct for thread safety.
- **Minor note:** Both `parallel_isolation.py` plugin and `BaseFactory._apply_worker_seed()` seed Faker globally via `Faker.seed()`. The plugin uses SHA-256 hash while the factory uses `10_000 + numeric_part`. The last one to run wins. Not a bug (both produce deterministic, worker-specific seeds), and the factory's per-instance `seed_instance()` call is what actually matters for isolation.

---

## 3. Integration Verification

| Check | Owner | Status | Notes |
|-------|-------|--------|-------|
| Every feature step has matching step def | bdd-author | PASS | All Given/When/Then steps in 5 feature files have matching defs in `common_steps.py`, `user_steps.py`, `auth_steps.py` |
| All imports resolve (no circular deps) | all | PASS | Import graph verified: config <- core <- services/models <- data/factories <- steps/tests. No cycles. |
| All fixtures referenced exist with correct scope | architect, bdd-author | PASS | `worker_id` (session, parallel_isolation), `api_client` (session), `authenticated_client` (session), `user_service` (session), `auth_service` (session), `user_factory` (session), `auth_factory` (session) -- all exist and scope chain is consistent |
| All JSON schema files exist | service-layer | PASS | Feature files now reference `user_response`, `user_list_response`, `login_response` -- all match schema file names in `schemas/` |
| Root conftest registers plugins and imports fixtures | architect | PASS | `conftest.py` declares `pytest_plugins` list with all 4 fixture modules |
| pytest.ini paths and markers correct | architect | PASS | `bdd_features_base_dir = features` correct; all 5 markers defined; plugins registered via `-p` |

---

## 4. Allure Coverage

| Check | Owner | Status | Notes |
|-------|-------|--------|-------|
| Every service method wrapped in allure.step() | service-layer | PASS | `UserService`: all 6 methods decorated (including new `partial_update`). `AuthService`: both methods decorated. All use `@allure.step()` |
| Request/response auto-attached on failure | architect | PASS | `allure_plugin.py:42-66` hooks `pytest_runtest_makereport`, attaches last req/res on failure. `pytest_bdd_step_error` attaches BDD context. |
| Environment properties at session start | architect | PASS | `allure_plugin.py:69-89` writes `environment.properties` with base_url, env, timeout, max_retries at session start |

### Allure Notes

- `ApiAssertions` wraps every assertion in `allure.step()` -- excellent granularity in reports.
- `AllureAttachmentHandler` in `response_handler.py` attaches response body to allure on every request (not just failures). This is aggressive but acceptable.
- `conftest_allure.py` autouse fixture adds environment params to every test -- good for traceability.

---

## 5. Issues Summary (Post-Fix)

| ID | Severity | Status | Description |
|----|----------|--------|-------------|
| P-1 | HIGH | RESOLVED | `update_user_patch` now delegates to `user_service.partial_update()` |
| P-2 | LOW | RESOLVED | Step defs collapsed to single-line list comprehensions using `create_batch()` |
| I-1 | HIGH | RESOLVED | Feature files updated to reference `user_response`, `user_list_response`, `login_response` matching actual schema file names |
| I-2 | MEDIUM | RESOLVED | `conftest_data.py` now imports from `data.factories` instead of defining inline factories; single source of truth |
| I-3 | LOW | RESOLVED | Step defs now use `.fake` attribute consistent with `BaseFactory` |
| I-4 | LOW | RESOLVED | Auth steps now use `AuthFactory` methods (`valid_credentials`, `invalid_password`, `expired_token`) instead of ad-hoc builder calls |

---

## 6. Verdict

**PASS** -- All checks pass. The framework enforces all required design patterns, is parallel-safe, has full integration wiring, and comprehensive Allure coverage.

### Pattern Summary
- **Template Method:** `BaseAPIClient` defines lifecycle; `SyncAPIClient`/`AsyncAPIClient` override transport
- **Strategy:** Auth strategies (`BearerAuth`, `ApiKeyAuth`, `OAuth2Auth`) swappable at runtime via `set_auth()`
- **Builder:** `UserBuilder`, `AuthBuilder` provide fluent payload construction
- **Factory:** `UserFactory`, `AuthFactory` generate randomized test data with worker-seeded Faker
- **Facade:** `ApiAssertions` provides single fluent assertion interface with Allure steps
- **Service Object:** All HTTP operations routed through `UserService`/`AuthService`
- **Chain of Responsibility:** `ResponseHandler` chain for status checking, logging, and Allure attachment

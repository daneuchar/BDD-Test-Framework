# Claude Code Agent Teams Prompt: API Testing Framework (v2 — Design Pattern Driven)

## Prerequisites

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

## ❌ Problems with v1 Directory Structure

| Issue | Details |
|-------|---------|
| **No Service Object Pattern** | Step defs were calling raw HTTP methods directly — every new endpoint means rewriting request logic |
| **No Builder Pattern** | Payload construction duplicated across step defs and test data |
| **Scattered step defs** | `step_defs/test_users.py` and `step_defs/test_auth.py` mix BDD wiring with API logic — violates SRP |
| **No shared steps** | Common steps like "the API is available" or "the response status code should be {code}" were duplicated per file |
| **Flat schemas/** | JSON schemas and Pydantic models in separate dirs with no clear ownership |
| **No base classes** | Each service object would repeat auth, headers, logging — no inheritance |
| **No request/response DTOs** | Raw dicts flying around instead of typed objects |
| **conftest.py doing too much** | Root conftest was handling client setup, fixtures, allure hooks, xdist isolation — god object |

---

## ✅ v2 Directory Structure (Pattern-Driven)

```
api-test-framework/
│
├── pyproject.toml                          # Single source of truth for deps & tool config
├── pytest.ini                              # pytest + bdd + xdist + allure config
├── conftest.py                             # ROOT: only plugin registration & session hooks
├── .env.example
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py                         # ⬡ Singleton — pydantic-settings, env-aware
│   └── endpoints.py                        # Enum registry: all routes in one place
│
├── core/
│   ├── __init__.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── base_client.py                  # ⬡ Template Method — shared request lifecycle
│   │   ├── sync_client.py                  # Concrete: requests.Session wrapper
│   │   └── async_client.py                 # Concrete: httpx.AsyncClient wrapper
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── base_auth.py                    # ⬡ Strategy (ABC) — auth interface
│   │   ├── bearer_auth.py                  # Concrete strategy
│   │   ├── api_key_auth.py                 # Concrete strategy
│   │   └── oauth2_auth.py                  # Concrete strategy
│   ├── response_handler.py                 # ⬡ Chain of Responsibility — validate → log → attach
│   └── retry.py                            # ⬡ Decorator pattern — configurable backoff
│
├── services/                               # ⬡ SERVICE OBJECT PATTERN — one per API domain
│   ├── __init__.py
│   ├── base_service.py                     # ABC: shared CRUD operations, auth injection, logging
│   ├── user_service.py                     # create/get/update/delete/list users
│   └── auth_service.py                     # login/refresh/logout
│
├── models/                                 # ⬡ BUILDER + DTO — typed request/response objects
│   ├── __init__.py
│   ├── base_model.py                       # Shared Pydantic BaseModel config
│   ├── user.py                             # CreateUserRequest, UpdateUserRequest, UserResponse
│   ├── auth.py                             # LoginRequest, TokenResponse, RefreshRequest
│   └── builders/                           # ⬡ BUILDER PATTERN — complex payload construction
│       ├── __init__.py
│       ├── user_builder.py                 # UserBuilder().with_name().with_email().build()
│       └── auth_builder.py                 # AuthBuilder().with_credentials().build()
│
├── schemas/                                # JSON Schema files for response validation
│   ├── user_response.json
│   ├── user_list_response.json
│   ├── login_response.json
│   └── error_response.json
│
├── validators/                             # ⬡ STRATEGY — pluggable validation
│   ├── __init__.py
│   ├── base_validator.py                   # ABC: validate(response) -> ValidationResult
│   ├── schema_validator.py                 # JSON Schema validation
│   ├── pydantic_validator.py               # Pydantic model validation
│   └── composite_validator.py              # ⬡ Composite — runs multiple validators
│
├── assertions/                             # ⬡ FACADE — unified assertion API
│   ├── __init__.py
│   └── api_assertions.py                   # Single class: status, schema, headers, timing, body
│
├── fixtures/                               # pytest fixtures ONLY — no business logic
│   ├── __init__.py
│   ├── conftest_client.py                  # api_client fixture (session-scoped, worker-aware)
│   ├── conftest_auth.py                    # auth_token, authenticated_client fixtures
│   ├── conftest_data.py                    # test data fixtures using builders
│   └── conftest_allure.py                  # allure hooks: attach on failure, env info
│
├── features/                               # Gherkin feature files
│   ├── users/
│   │   ├── create_user.feature
│   │   ├── get_user.feature
│   │   └── update_user.feature
│   └── auth/
│       ├── login.feature
│       └── token_refresh.feature
│
├── steps/                                  # Step definitions — THIN layer, delegates to services
│   ├── __init__.py
│   ├── common_steps.py                     # ⬡ SHARED: "API is available", "status is {code}", etc.
│   ├── user_steps.py                       # User-specific steps → delegates to UserService
│   └── auth_steps.py                       # Auth-specific steps → delegates to AuthService
│
├── plugins/                                # ⬡ Custom pytest plugins
│   ├── __init__.py
│   ├── allure_plugin.py                    # Auto-attach req/res, severity mapping
│   ├── parallel_isolation.py               # xdist worker isolation hooks
│   └── request_logger.py                   # Structured request/response logging
│
├── data/                                   # ⬡ OBJECT MOTHER + static fixtures
│   ├── static/
│   │   └── test_data.json                  # Immutable reference data
│   └── factories/                          # ⬡ FACTORY PATTERN — dynamic test data
│       ├── __init__.py
│       ├── base_factory.py                 # ABC + Faker instance management
│       ├── user_factory.py                 # UserFactory.create(), .create_batch(n)
│       └── auth_factory.py                 # AuthFactory.valid_credentials(), .expired_token()
│
└── scripts/
    ├── run_tests.sh                        # pytest -n auto --alluredir=reports/
    ├── run_smoke.sh                        # pytest -n auto -m smoke
    ├── run_regression.sh                   # pytest -n auto -m regression
    └── generate_report.sh                  # allure serve reports/allure-results
```

---

## Design Patterns Applied

| Pattern | Where | Why |
|---------|-------|-----|
| **Service Object** | `services/base_service.py` → `user_service.py`, `auth_service.py` | Encapsulates all API interactions per domain. Steps never call HTTP directly. One change point per endpoint. |
| **Builder** | `models/builders/user_builder.py`, `auth_builder.py` | Fluent payload construction: `UserBuilder().with_name("x").with_email("y").build()` → returns typed Pydantic model. No raw dicts in tests. |
| **Factory** | `data/factories/user_factory.py`, `auth_factory.py` | Dynamic Faker-powered test data with worker-aware seeds for parallel isolation. `UserFactory.create()` returns unique data per xdist worker. |
| **Strategy** | `core/auth/`, `validators/` | Swap auth mechanism or validation strategy without touching callers. Add OAuth2? Just add a new strategy class. |
| **Template Method** | `core/client/base_client.py` | Defines the request lifecycle (prepare → authenticate → send → log → validate → attach to allure). Sync and async clients override only the `_send()` step. |
| **Facade** | `assertions/api_assertions.py` | One import, one class for all assertion types. Steps call `ApiAssertions(response).status(201).schema("user").response_time(500)` — fluent chain. |
| **Chain of Responsibility** | `core/response_handler.py` | Response flows through: validate status → validate schema → log → attach to allure. Each handler decides to process or pass. |
| **Composite** | `validators/composite_validator.py` | Run JSON schema + Pydantic + custom validators in one call. Add new validator without changing existing code. |
| **Decorator** | `core/retry.py` | `@retry(max_attempts=3, backoff=2)` wraps any service method. No retry logic inside service objects. |
| **Singleton** | `config/settings.py` | One settings instance across all workers. Pydantic-settings handles this naturally via module-level instantiation. |
| **Object Mother** | `data/factories/` | Predefined "standard" test objects: `UserFactory.admin()`, `UserFactory.readonly()`, alongside random `.create()`. |

---

## Key Duplication Eliminations vs v1

| v1 Duplication | v2 Solution |
|----------------|-------------|
| Every step def built its own request payload as a raw dict | Builders construct typed DTOs: `UserBuilder().with_defaults().build()` |
| `assert response.status_code == 201` repeated in every @then step | `ApiAssertions(response).status(201)` — one-liner, auto-attaches to Allure |
| "Given the API is available" re-implemented per step file | `common_steps.py` — shared steps imported everywhere via conftest |
| Auth token retrieval logic duplicated in user_steps and auth_steps | `conftest_auth.py` fixture provides `authenticated_client` — injected by pytest |
| Allure attachment logic scattered across every @when step | `allure_plugin.py` hooks into pytest — auto-attaches on every request/failure |
| Raw `requests.post(url, json=payload, headers=headers)` in step defs | `UserService(client).create(user_dto)` — service handles URL, headers, serialization |
| JSON schema validation re-implemented per assertion | `CompositeValidator([SchemaValidator("user"), PydanticValidator(UserResponse)])` |
| Worker isolation logic in root conftest | `parallel_isolation.py` plugin — registered once, applies everywhere |

---

## 🚀 The Prompt (Copy & Paste into Claude Code)

```
Create an agent team called "api-test-framework" to build a production-grade, design-pattern-driven API Testing Framework.

## Architecture Philosophy
This framework follows SOLID principles and uses established design patterns to eliminate code duplication.
The key architectural rule: **step definitions are THIN — they delegate to services, which delegate to clients**.
The call chain is: Feature → Step → Service → Client → HTTP. Nothing skips a layer.

## Tech Stack
- Python 3.11+
- pytest + pytest-bdd (BDD with Gherkin)
- pytest-xdist (parallel execution)
- allure-pytest (rich reporting)
- requests (sync HTTP) + httpx (async HTTP)
- pydantic + pydantic-settings (DTOs, config)
- jsonschema (response validation)
- faker (test data generation)

## Project Structure
```
api-test-framework/
├── pyproject.toml
├── pytest.ini
├── conftest.py                     # ROOT: register plugins from plugins/, import fixtures from fixtures/
├── .env.example
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Singleton: pydantic-settings, env-aware (dev/staging/prod)
│   └── endpoints.py                # Enum: all API routes with URL templating
├── core/
│   ├── __init__.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── base_client.py          # Template Method: request lifecycle (prepare→auth→send→log→validate)
│   │   ├── sync_client.py          # requests.Session concrete implementation
│   │   └── async_client.py         # httpx.AsyncClient concrete implementation
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── base_auth.py            # Strategy ABC: authenticate(request) -> request
│   │   ├── bearer_auth.py
│   │   ├── api_key_auth.py
│   │   └── oauth2_auth.py
│   ├── response_handler.py         # Chain of Responsibility: validate→log→attach
│   └── retry.py                    # Decorator: @retry(max_attempts=3, backoff=2)
├── services/
│   ├── __init__.py
│   ├── base_service.py             # ABC: CRUD base with client injection, auth, allure steps
│   ├── user_service.py             # create/get/update/delete/list — delegates to client
│   └── auth_service.py             # login/refresh/logout — delegates to client
├── models/
│   ├── __init__.py
│   ├── base_model.py               # Shared Pydantic config (json aliases, serialization)
│   ├── user.py                     # CreateUserRequest, UpdateUserRequest, UserResponse
│   ├── auth.py                     # LoginRequest, TokenResponse, RefreshRequest
│   └── builders/
│       ├── __init__.py
│       ├── user_builder.py         # Fluent: UserBuilder().with_name("x").with_email("y").build()
│       └── auth_builder.py         # Fluent: AuthBuilder().with_credentials("u","p").build()
├── schemas/
│   ├── user_response.json
│   ├── user_list_response.json
│   ├── login_response.json
│   └── error_response.json
├── validators/
│   ├── __init__.py
│   ├── base_validator.py           # ABC: validate(response) -> ValidationResult
│   ├── schema_validator.py         # JSON Schema validation
│   ├── pydantic_validator.py       # Pydantic model validation
│   └── composite_validator.py      # Composite: runs multiple validators in sequence
├── assertions/
│   ├── __init__.py
│   └── api_assertions.py           # Facade: ApiAssertions(resp).status(201).schema("user").time(500)
├── fixtures/
│   ├── __init__.py
│   ├── conftest_client.py          # api_client: session-scoped, worker-aware
│   ├── conftest_auth.py            # auth_token, authenticated_client
│   ├── conftest_data.py            # test data via builders/factories
│   └── conftest_allure.py          # allure environment info, severity mapping
├── features/
│   ├── users/
│   │   ├── create_user.feature
│   │   ├── get_user.feature
│   │   └── update_user.feature
│   └── auth/
│       ├── login.feature
│       └── token_refresh.feature
├── steps/
│   ├── __init__.py
│   ├── common_steps.py             # SHARED: "API available", "status is {code}", "schema matches"
│   ├── user_steps.py               # Thin: delegates to UserService + UserBuilder
│   └── auth_steps.py               # Thin: delegates to AuthService + AuthBuilder
├── plugins/
│   ├── __init__.py
│   ├── allure_plugin.py            # Auto-attach request/response on failure
│   ├── parallel_isolation.py       # xdist worker_id based test data isolation
│   └── request_logger.py           # Structured logging per request
├── data/
│   ├── static/
│   │   └── test_data.json
│   └── factories/
│       ├── __init__.py
│       ├── base_factory.py         # Faker instance + worker-aware seed
│       ├── user_factory.py         # UserFactory.create(), .admin(), .create_batch(5)
│       └── auth_factory.py         # AuthFactory.valid_credentials(), .expired_token()
└── scripts/
    ├── run_tests.sh
    ├── run_smoke.sh
    ├── run_regression.sh
    └── generate_report.sh
```

## Team Structure — Spawn 5 teammates:

### Teammate 1: "architect"
**Role:** Project scaffolding, configuration, plugin system, scripts
**Owns:** `pyproject.toml`, `pytest.ini`, `conftest.py` (root), `.env.example`, `README.md`, `config/`, `plugins/`, `scripts/`
**Tasks:**
1. Create `pyproject.toml` with all dependencies, project metadata, and tool configs for pytest, allure, xdist
2. Create `pytest.ini`:
   - `bdd_features_base_dir = features`
   - `addopts = --alluredir=reports/allure-results -p plugins.allure_plugin -p plugins.parallel_isolation -p plugins.request_logger`
   - Custom markers: `@smoke`, `@regression`, `@critical`, `@auth`, `@users`
   - Strict markers enabled
3. Create `config/settings.py` — pydantic-settings `BaseSettings` subclass:
   - Fields: `base_url`, `env` (dev/staging/prod), `auth_username`, `auth_password`, `timeout`, `max_retries`, `parallel_workers`
   - Loads from `.env` or environment variables
   - Module-level singleton instance: `settings = Settings()`
4. Create `config/endpoints.py` — Enum-based route registry:
   ```python
   class Endpoints(str, Enum):
       USERS = "/users"
       USER_BY_ID = "/users/{user_id}"
       AUTH_LOGIN = "/auth/login"
       AUTH_REFRESH = "/auth/refresh"
       def url(self, **kwargs) -> str:
           return self.value.format(**kwargs)
   ```
5. Create `plugins/allure_plugin.py` — pytest plugin:
   - Hook `pytest_runtest_makereport`: on failure, attach last request/response from thread-local storage
   - Hook `pytest_sessionstart`: write allure environment.properties
   - Hook `pytest_bdd_step_error`: attach step context to allure
6. Create `plugins/parallel_isolation.py` — pytest plugin:
   - Hook `pytest_configure`: seed Faker with `worker_id` hash for deterministic-per-worker data
   - Provide `worker_id` fixture that returns `"master"` for single-process, `"gw0"` etc for xdist
7. Create `plugins/request_logger.py` — structured JSON logging plugin
8. Create `conftest.py` (root):
   - Import all fixtures from `fixtures/` package using `pytest_plugins` list
   - Register custom plugins
   - Add `pytest_collection_modifyitems` hook for allure severity from markers
9. Create all shell scripts with proper flags for parallel execution
10. Create README.md with architecture diagram, setup instructions, usage examples, CI/CD snippets
**Constraint:** Do NOT write service objects, models, steps, or features. Only scaffolding + plugins.
**Send message to team-lead with config decisions (base URL pattern, marker names, fixture scoping).**

### Teammate 2: "core-engine"
**Role:** HTTP client infrastructure, auth strategies, response handling, retry, validation, assertions
**Owns:** `core/`, `validators/`, `assertions/`
**Design patterns to implement:**
1. **Template Method** — `core/client/base_client.py`:
   ```python
   class BaseAPIClient(ABC):
       def request(self, method, endpoint, **kwargs) -> APIResponse:
           request = self._prepare_request(method, endpoint, **kwargs)
           request = self._authenticate(request)
           response = self._send(request)          # abstract — subclass implements
           response = self._handle_response(response)
           self._log_request(request, response)
           return response
       @abstractmethod
       def _send(self, request: PreparedRequest) -> RawResponse: ...
   ```
   - `sync_client.py` implements `_send()` with `requests.Session`
   - `async_client.py` implements `_send()` with `httpx.AsyncClient`
   - Both inject auth strategy at construction time
   - Both store last request/response in thread-local for allure attachment
   - Both accept `Settings` for base_url, timeout, headers
2. **Strategy** — `core/auth/`:
   - `BaseAuth(ABC)` with `authenticate(request) -> request`
   - `BearerAuth(token)` — adds Authorization header
   - `ApiKeyAuth(key, header_name)` — adds custom header
   - `OAuth2Auth(client_id, client_secret, token_url)` — handles token fetch + refresh
3. **Chain of Responsibility** — `core/response_handler.py`:
   - `ResponseHandler` base with `handle(response) -> response` and `set_next(handler)`
   - `StatusCheckHandler` → `SchemaValidationHandler` → `LoggingHandler` → `AllureAttachmentHandler`
   - Configurable chain per service object
4. **Decorator Pattern** — `core/retry.py`:
   - `@retry(max_attempts=3, backoff_factor=2, retryable_statuses=[500, 502, 503])`
   - Works with both sync and async
5. **Strategy + Composite** — `validators/`:
   - `BaseValidator(ABC)` → `validate(response, **kwargs) -> ValidationResult`
   - `SchemaValidator` — validates against JSON schema files from `schemas/`
   - `PydanticValidator` — validates against Pydantic model class
   - `CompositeValidator([SchemaValidator(...), PydanticValidator(...)])` — runs all, collects errors
6. **Facade** — `assertions/api_assertions.py`:
   ```python
   class ApiAssertions:
       def __init__(self, response):
           self.response = response
       def status(self, expected: int) -> "ApiAssertions":
           with allure.step(f"Assert status {expected}"):
               assert self.response.status_code == expected
           return self  # fluent chain
       def schema(self, schema_name: str) -> "ApiAssertions":
           ...
           return self
       def response_time(self, max_ms: int) -> "ApiAssertions": ...
       def header(self, name: str, value: str = None) -> "ApiAssertions": ...
       def json_path(self, path: str, expected) -> "ApiAssertions": ...
   ```
**Constraint:** All code MUST be thread-safe. Use thread-local storage for request/response state. No module-level mutable state. Clients must be constructible per-worker.
**Send message to "service-layer" teammate with the BaseAPIClient interface and APIResponse type so they can build service objects against it.**

### Teammate 3: "service-layer"
**Role:** Service objects, models, builders, data factories
**Owns:** `services/`, `models/`, `data/`, `schemas/`
**Design patterns to implement:**
1. **Service Object** — `services/base_service.py`:
   ```python
   class BaseService:
       def __init__(self, client: BaseAPIClient):
           self.client = client
       def _request(self, method, endpoint, model=None, **kwargs):
           if model:
               kwargs["json"] = model.model_dump(exclude_none=True)
           return self.client.request(method, endpoint.url(**kwargs.pop("path_params", {})), **kwargs)
   ```
   - `UserService(BaseService)`:
     - `create(user: CreateUserRequest) -> UserResponse`
     - `get(user_id: str) -> UserResponse`
     - `update(user_id: str, data: UpdateUserRequest) -> UserResponse`
     - `delete(user_id: str) -> None`
     - `list(page: int = 1, size: int = 10) -> list[UserResponse]`
   - `AuthService(BaseService)`:
     - `login(credentials: LoginRequest) -> TokenResponse`
     - `refresh(token: RefreshRequest) -> TokenResponse`
   - Each method wraps call in `allure.step()`, uses Endpoints enum, returns typed response
2. **DTO Models** — `models/`:
   - `base_model.py`: shared `BaseDTO(BaseModel)` with `model_config` for JSON aliases and serialization
   - `user.py`: `CreateUserRequest`, `UpdateUserRequest`, `UserResponse` (all extend BaseDTO)
   - `auth.py`: `LoginRequest`, `RefreshRequest`, `TokenResponse`
3. **Builder** — `models/builders/`:
   ```python
   class UserBuilder:
       def __init__(self):
           self._data = {}
       def with_name(self, name: str) -> "UserBuilder":
           self._data["name"] = name
           return self
       def with_email(self, email: str) -> "UserBuilder":
           self._data["email"] = email
           return self
       def with_defaults(self) -> "UserBuilder":
           """Fill all fields with Faker-generated data."""
           ...
           return self
       def build(self) -> CreateUserRequest:
           return CreateUserRequest(**self._data)
   ```
   - `AuthBuilder` similarly for login payloads
4. **Factory + Object Mother** — `data/factories/`:
   - `BaseFactory`: holds Faker instance, seeded by worker_id for parallel safety
   - `UserFactory`:
     - `.create() -> CreateUserRequest` — random valid user
     - `.admin() -> CreateUserRequest` — admin role preset
     - `.create_batch(n) -> list[CreateUserRequest]` — bulk generation
     - `.invalid_email() -> CreateUserRequest` — for negative tests
   - `AuthFactory`:
     - `.valid_credentials() -> LoginRequest`
     - `.expired_token() -> RefreshRequest`
     - `.invalid_password() -> LoginRequest`
5. **JSON Schemas** — `schemas/`:
   - `user_response.json`, `user_list_response.json`, `login_response.json`, `error_response.json`
   - Strict schemas with required fields, types, formats
6. **Static Data** — `data/static/test_data.json`: immutable reference data for deterministic tests
**Constraint:** Wait for message from "core-engine" to know the client interface. Service objects accept client via constructor injection. All Faker-generated data must use worker-aware seeds.
**Send message to "bdd-author" with the exact service method signatures so step defs can be thin wrappers.**

### Teammate 4: "bdd-author"
**Role:** Feature files, step definitions, shared steps, fixture wiring
**Owns:** `features/`, `steps/`, `fixtures/`
**Design patterns to follow:**
- **Thin Steps Rule:** Every step definition MUST delegate to a service object or builder. Max 5 lines per step function.
- **Shared Steps:** All reusable steps live in `common_steps.py` — never duplicate a step across files.
**Tasks:**
1. **Wait for message from "service-layer"** containing service method signatures
2. Create `fixtures/conftest_client.py`:
   - `api_client` (session-scoped, worker-aware) — constructs SyncClient with Settings
   - `async_api_client` (session-scoped) — constructs AsyncClient
3. Create `fixtures/conftest_auth.py`:
   - `auth_token` — calls AuthService.login(), returns token
   - `authenticated_client` — api_client with bearer auth injected
4. Create `fixtures/conftest_data.py`:
   - `user_factory` — returns UserFactory seeded with worker_id
   - `auth_factory` — returns AuthFactory seeded with worker_id
   - `user_service` — returns UserService(authenticated_client)
   - `auth_service` — returns AuthService(api_client)
5. Create `fixtures/conftest_allure.py`:
   - Fixtures for allure environment info (base_url, env name, worker)
6. Create `steps/common_steps.py` — SHARED steps used across all features:
   ```python
   @given("the API is available")
   def api_available(api_client):
       """Health check — reused by every feature."""
       ...

   @then(parsers.parse("the response status code should be {status_code:d}"))
   def check_status(status_code, api_response):
       ApiAssertions(api_response).status(status_code)

   @then(parsers.parse('the response should match the {schema_name} schema'))
   def check_schema(schema_name, api_response):
       ApiAssertions(api_response).schema(schema_name)

   @then(parsers.parse('the response time should be less than {max_ms:d}ms'))
   def check_response_time(max_ms, api_response):
       ApiAssertions(api_response).response_time(max_ms)

   @then(parsers.parse('the response should contain error message "{message}"'))
   def check_error_message(message, api_response):
       ApiAssertions(api_response).json_path("error.message", message)
   ```
7. Create `steps/user_steps.py` — THIN steps:
   ```python
   @given("I have valid user creation payload", target_fixture="user_payload")
   def valid_user_payload(user_factory):
       return user_factory.create()

   @when("I send a POST request to the create user endpoint", target_fixture="api_response")
   def create_user(user_service, user_payload):
       return user_service.create(user_payload)
   ```
   - Notice: NO raw HTTP calls. NO dict construction. NO assertion logic. Just wiring.
8. Create `steps/auth_steps.py` — same thin pattern, delegates to AuthService + AuthBuilder
9. Create feature files with proper Gherkin:
   - `features/users/create_user.feature` — happy path + Scenario Outline for invalid data
   - `features/users/get_user.feature` — by ID, list, 404, pagination
   - `features/users/update_user.feature` — PUT, PATCH, unauthorized
   - `features/auth/login.feature` — success, wrong password, locked account
   - `features/auth/token_refresh.feature` — valid, expired, invalid
   - ALL scenarios must have `@smoke`/`@regression`/`@critical` markers
   - ALL scenarios must be independently runnable (no order dependencies)
   - Use Scenario Outline with Examples for data-driven tests
10. Every `@when` step must use `target_fixture="api_response"` so `@then` steps from common_steps can assert on it
**Constraint:** If you find yourself writing >5 lines in a step def, you're doing it wrong. The logic belongs in a service, builder, or factory. Step defs are GLUE only.
**Send completion message to team-lead with a list of all shared steps and feature-specific steps.**

### Teammate 5: "qa-reviewer"
**Role:** Architecture review, integration verification, parallel safety audit
**Owns:** No files — read-only. Creates only `REVIEW.md`.
**Tasks:**
1. **Wait until all other teammates report completion**
2. **Pattern Compliance Review:**
   - [ ] Service Object: Do step defs ever call HTTP directly? (They must not)
   - [ ] Builder: Are any request payloads constructed as raw dicts? (They must not be)
   - [ ] Template Method: Do sync_client and async_client both extend base_client? (They must)
   - [ ] Strategy: Can auth mechanism be swapped without changing client code? (It must)
   - [ ] Facade: Is there a single assertion class with fluent interface? (There must be)
   - [ ] Factory: Is all dynamic test data generated through factories? (It must be)
   - [ ] Thin Steps: Is any step def >5 lines? (It must not be)
   - [ ] Shared Steps: Are common steps (status check, schema validation) in common_steps.py only? (They must be)
3. **Parallel Safety Audit:**
   - [ ] No module-level mutable state (dicts, lists, sets)
   - [ ] No class-level shared state
   - [ ] All Faker instances seeded with worker_id
   - [ ] Session fixtures use `tmp_path_factory` pattern for worker isolation
   - [ ] No test-order dependencies between scenarios
   - [ ] Thread-local storage used for request/response state in clients
4. **Integration Verification:**
   - [ ] Every feature file step has a matching step def (exact text match)
   - [ ] All imports resolve (no circular dependencies)
   - [ ] All fixtures referenced in steps exist and have correct scope
   - [ ] All JSON schema files referenced in validators exist
   - [ ] All Pydantic models used in services match the builder output
   - [ ] Root conftest correctly registers plugins and imports fixtures
   - [ ] pytest.ini paths and markers are correct
5. **Allure Coverage:**
   - [ ] Every service method wrapped in `allure.step()`
   - [ ] `@allure.feature()` and `@allure.story()` on every test
   - [ ] Request/response auto-attached on failure (via plugin)
   - [ ] Environment properties generated at session start
6. Write `REVIEW.md` with findings table: column per teammate, row per check
7. If issues found → message the responsible teammate with specific fix instructions
8. If all clear → message team-lead: "Framework verified — all patterns enforced, parallel-safe, allure-complete"
**Constraint:** Do NOT write code. Only review, verify, and report.

## Task Dependencies:
- "architect" → starts immediately
- "core-engine" → starts immediately
- "service-layer" → blocked by "core-engine" (needs client interface)
- "bdd-author" → blocked by "service-layer" (needs service method signatures)
- "qa-reviewer" → blocked by ALL

## Cross-Cutting Requirements (ALL teammates):
1. **Parallel Safety:** No global mutable state. Worker-aware fixtures. Faker seeded per worker.
2. **Allure Integration:** Every assertion, every request, every failure — attached to report.
3. **Type Safety:** All payloads are Pydantic models. No raw dicts cross module boundaries.
4. **Thin Steps:** Step definitions are glue code. Business logic lives in services.
5. **DRY:** Shared steps in common_steps.py. Shared base classes for clients, services, validators, factories.

Coordinate through messaging. Lead synthesizes a final status when qa-reviewer approves.
```

---

## Running the Framework

```bash
# Full parallel run with Allure
pytest -n auto --alluredir=reports/allure-results

# Smoke only
pytest -n auto -m smoke --alluredir=reports/allure-results

# Specific feature
pytest features/users/create_user.feature -n auto --alluredir=reports/allure-results

# Generate report
allure serve reports/allure-results
```

---

## CLAUDE.md Addition

```markdown
## API Testing Framework — Architecture Rules

### Call Chain (never skip a layer)
Feature → Step → Service → Client → HTTP

### Design Patterns in Use
- Service Object (services/)
- Builder (models/builders/)
- Factory + Object Mother (data/factories/)
- Strategy (core/auth/, validators/)
- Template Method (core/client/)
- Facade (assertions/)
- Chain of Responsibility (core/response_handler.py)
- Composite (validators/composite_validator.py)
- Decorator (core/retry.py)

### Rules
- Step definitions are THIN — max 5 lines, delegate to services
- All request payloads are Pydantic models built via Builders
- All test data comes from Factories (Faker + worker-aware seed)
- All assertions go through ApiAssertions facade
- No raw dicts cross module boundaries
- No global mutable state
- Every API call auto-attaches to Allure via plugin
```
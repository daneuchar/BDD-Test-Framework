# API Testing Framework — Copilot Instructions

## Call Chain (never skip a layer)

```
Feature (.feature) -> Step (steps/) -> Service (services/) -> Client (core/client/) -> HTTP/Messaging
```

## Tech Stack

Python 3.11+, pytest + pytest-bdd, pytest-xdist, allure-pytest, requests, httpx, pydantic, pydantic-settings, jsonschema, faker, azure-eventhub, confluent-kafka

## Design Patterns & Where They Live

| Pattern | Location | Key Classes |
|---------|----------|-------------|
| Template Method | `core/client/base_client.py` | `BaseAPIClient` (lifecycle: prepare->auth->send->log) |
| Template Method | `core/messaging/base_producer.py` | `BaseProducer` (lifecycle: prepare->auth->send->log) |
| Template Method | `core/messaging/base_consumer.py` | `BaseConsumer` (poll->deserialize->return) |
| Strategy | `core/auth/` | `BaseAuth` ABC, `BearerAuth`, `ApiKeyAuth`, `OAuth2Auth` |
| Service Object | `services/` | `BaseService`, `UserService`, `AuthService`, `EventHubService`, `KafkaService` |
| Builder | `models/builders/` | `UserBuilder`, `AuthBuilder`, `EventBuilder` — fluent `.with_x().build()` |
| Factory | `data/factories/` | `UserFactory`, `AuthFactory`, `EventFactory` — Faker-powered, worker-aware |
| Facade | `assertions/` | `ApiAssertions`, `MessagingAssertions` — fluent `.status(201).schema("x")` |
| Composite | `validators/composite_validator.py` | `CompositeValidator` runs multiple validators |
| Chain of Responsibility | `core/response_handler.py` | `ResponseHandler` chain: validate->log->attach |
| Decorator | `core/retry.py` | `@retry(max_attempts=3, backoff_factor=2)` |
| Singleton | `config/settings.py` | Module-level `settings = Settings()` |

## Architecture Rules

1. **Step defs are THIN** — max 5 lines, delegate to services/builders/factories. No raw HTTP calls.
2. **All payloads are Pydantic models** built via Builders. No raw dicts cross module boundaries.
3. **All test data from Factories** — Faker + worker-aware seed (`PYTEST_XDIST_WORKER`).
4. **All assertions via Facade** — `ApiAssertions(resp)` or `MessagingAssertions(result)`.
5. **No global mutable state** — thread-local for request/response, session fixtures for clients.
6. **Every `@when` step uses `target_fixture="api_response"`** so shared `@then` steps work.

## API Versioning

- Version is **URL path prefix**: `/api/v1/users`, `/api/v2/users`
- `config/version_registry.py` — `APIVersion` enum, `VersionConfig`, per-env defaults
- `config/settings.py` — `base_url` (no version) + `api_version` field
- `core/client/base_client.py` — `api_version` param in `__init__`, injected in `_prepare_request()`
- `validators/schema_validator.py` — resolves `schemas/{version}/{name}.json`, falls back to flat `schemas/`
- CLI: `pytest --api-version=v2` | Marker: `@pytest.mark.api_version("v2")`
- `api_version=None` preserves legacy behavior (backward compatible)

## Messaging (Event Hub + Kafka)

- **Real brokers** — not mocks. Connection string (EH), SASL/PLAIN (Kafka).
- **Producers** are session-scoped (lightweight, one per worker).
- **Consumers** are function-scoped and **lazy** — created only for round-trip tests, closed after each test.
- **Publish-only tests** use delivery callback ack — no consumer needed.
- **Worker isolation**: topics = `{prefix}-{worker_id}`, consumer groups = `test-group-{worker_id}-{uuid}`.
- `pytest.skip` when broker config is empty — messaging tests auto-skip without config.

## Key DTOs

| Dataclass | Location | Purpose |
|-----------|----------|---------|
| `PreparedRequest` | `core/client/base_client.py` | Outgoing HTTP request |
| `APIResponse` | `core/client/base_client.py` | Normalized HTTP response |
| `EventEnvelope` | `core/messaging/base_producer.py` | Outgoing event |
| `PublishResult` | `core/messaging/base_producer.py` | Publish outcome |
| `ConsumedEvent` | `core/messaging/base_consumer.py` | Consumed event |

## Fixture Scoping

| Scope | Fixtures |
|-------|----------|
| session | `api_client`, `async_api_client`, `api_version`, `worker_id`, `user_factory`, `auth_factory`, `user_service`, `auth_service`, `eventhub_producer`, `kafka_producer` |
| function | `eventhub_consumer`, `kafka_consumer`, `eventhub_service`, `kafka_service`, `event_factory` |

## File Conventions

- `features/{domain}/*.feature` — Gherkin with `@smoke`/`@regression`/`@critical`/`@events` markers
- `steps/{domain}_steps.py` — thin glue, imports from services + factories
- `steps/common_steps.py` — shared steps: status check, schema match, response time, error message
- `tests/{domain}/test_*.py` — scenario collectors (auto-generated from features)
- `schemas/{version}/{name}.json` — JSON Schema Draft-07, versioned directories
- `fixtures/conftest_*.py` — grouped by concern (client, auth, data, messaging, allure)

## Adding a New API Domain

1. Add endpoints to `config/endpoints.py`
2. Create DTO models in `models/{domain}.py`
3. Create builder in `models/builders/{domain}_builder.py`
4. Create factory in `data/factories/{domain}_factory.py`
5. Create service in `services/{domain}_service.py` (extend `BaseService`)
6. Create steps in `steps/{domain}_steps.py` (thin, delegates to service)
7. Create features in `features/{domain}/*.feature`
8. Add JSON schemas in `schemas/v1/` and `schemas/v2/`
9. Add fixtures in `fixtures/conftest_data.py`

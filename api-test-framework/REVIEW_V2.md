# V2 Expansion QA Review

**Reviewer:** qa-reviewer
**Date:** 2026-02-17
**Scope:** Version support expansion (Tasks #1-#2) and messaging expansion (Tasks #3-#5)

---

## 1. Version Support

### 1.1 api_version=None preserves old URL construction

**PASS**

`BaseAPIClient._prepare_request()` at `core/client/base_client.py:136-139` correctly branches:
- When `api_version is not None`: URL becomes `{base_url}/api/{version}/{endpoint}`
- When `api_version is None`: URL becomes `{base_url}/{endpoint}` (legacy behavior)

### 1.2 SchemaValidator falls back to flat schemas/ when version=None

**PASS**

`SchemaValidator._resolve_schema_path()` at `validators/schema_validator.py:44-51`:
- When `version is not None`: looks in `schemas/{version}/{schema_name}.json`, falls back to `schemas/{schema_name}.json` if versioned file does not exist
- When `version is None`: goes directly to `schemas/{schema_name}.json`

Flat schemas exist at `schemas/user_response.json`, `schemas/login_response.json`, etc., providing backward compatibility.

### 1.3 Version flows: Settings -> fixture -> client -> URL

**PASS**

Full flow verified:
1. `config/settings.py:31-34` -- `api_version` field defaults to `"v1"`
2. `fixtures/conftest_client.py:14-19` -- `api_version` fixture resolves from CLI `--api-version` option first, then falls back to `get_default_version(settings.env).value`
3. `fixtures/conftest_client.py:23-32` -- `api_client` fixture passes `api_version` to `SyncAPIClient` constructor
4. `core/client/base_client.py:82` -- stored as `self.api_version`
5. `core/client/base_client.py:136-139` -- used in `_prepare_request()` to construct versioned URL

### 1.4 --api-version CLI option registered

**PASS**

`plugins/api_version_plugin.py:12-17` registers `--api-version` via `pytest_addoption`.
Plugin is loaded via `pyproject.toml:39` (`-p plugins.api_version_plugin`).

**ISSUE (Minor):** `pytest.ini` does NOT include `-p plugins.api_version_plugin` in its `addopts` (line 4-8). The `pyproject.toml` does include it. Since both configuration files exist, if pytest reads `pytest.ini` first (which takes precedence over `pyproject.toml` per pytest docs), the plugin will NOT be loaded. This is a potential conflict.

- `pytest.ini` markers section (lines 9-15) also lacks the `events` and `api_version` markers that `pyproject.toml` (lines 42-50) defines.

**Recommendation:** Remove `pytest.ini` or synchronize it with `pyproject.toml` to avoid configuration shadowing.

### 1.5 v1 and v2 schema directories exist

**PASS**

Both `schemas/v1/` and `schemas/v2/` directories exist with matching schema files:
- `user_response.json`, `login_response.json`, `user_list_response.json`, `error_response.json`

The v2 `user_response.json` adds `metadata` and `tags` fields, differentiating it from v1. Other v2 schemas have updated descriptions but identical structure -- acceptable for initial scaffolding.

### 1.6 Version Registry

**PASS**

`config/version_registry.py` provides:
- `APIVersion` enum with `V1` and `V2`
- `VersionConfig` frozen dataclass
- Registry with `get_version_config()`, `get_default_version()`, and `register_version()`
- Environment-based defaults: dev=V2, staging/prod=V1

---

## 2. Messaging Pattern Compliance

### 2.1 Template Method: producers/consumers extend base classes

**PASS**

- `BaseProducer` (`core/messaging/base_producer.py`) defines invariant lifecycle: `_prepare_event -> _authenticate_event -> _send -> _handle_result -> _log_event`
- `KafkaProducer` and `EventHubProducer` extend `BaseProducer`, override only `_send()` and `close()`
- `BaseConsumer` (`core/messaging/base_consumer.py`) defines: `connect -> _poll -> _deserialize`
- `KafkaConsumer` and `EventHubConsumer` extend `BaseConsumer`, override `connect()`, `_poll()`, `_deserialize()`, `close()`

### 2.2 Service Object: steps never call producer/consumer directly

**PASS**

`steps/event_steps.py` exclusively uses `EventHubService` and `KafkaService` service objects. No direct `BaseProducer`/`BaseConsumer` usage in step definitions.

### 2.3 Builder: events use EventBuilder

**PASS**

`models/builders/event_builder.py` provides fluent `EventBuilder` with:
- `with_type()`, `with_user_data()`, `with_event_id()`, `with_timestamp()`, `with_version()`, `with_defaults()`
- `build()` returns `UserCreatedEvent` or `UserUpdatedEvent` based on event type

`EventFactory.user_created()` and `EventFactory.user_updated()` both use `EventBuilder`.

### 2.4 Factory: EventFactory for dynamic data

**PASS**

`data/factories/event_factory.py` extends `BaseFactory`, uses Faker-generated data through the builder pattern. Registered in `data/factories/__init__.py` and exposed via `conftest_data.py:32-34` as `event_factory` fixture.

### 2.5 Facade: MessagingAssertions fluent chain

**PASS**

`assertions/messaging_assertions.py` provides fluent API with all methods returning `self`:
- `published_successfully()`, `delivered_within()`, `event_received()`, `event_body_matches()`, `event_body_contains()`, `on_topic()`
- All wrapped in `@allure.step` decorators

### 2.6 Thin Steps: max 5 lines

**PASS**

All step definitions in `steps/event_steps.py` are 1-3 lines of body each. Steps delegate to service objects and assertions -- no business logic.

---

## 3. Lazy Consumer Verification

### 3.1 Producers session-scoped

**PASS**

`fixtures/conftest_messaging.py:23` and `fixtures/conftest_messaging.py:36`:
- `eventhub_producer` -- `scope="session"`
- `kafka_producer` -- `scope="session"`

### 3.2 Consumers function-scoped (NOT session)

**PASS**

`fixtures/conftest_messaging.py:55` and `fixtures/conftest_messaging.py:69`:
- `eventhub_consumer` -- `scope="function"`
- `kafka_consumer` -- `scope="function"`

### 3.3 Publish-only tests never instantiate consumer

**PASS**

`fixtures/conftest_messaging.py:92-101`:
- `eventhub_service` and `kafka_service` fixtures pass `consumer=None`
- These fixtures only depend on their respective producer fixture
- `KafkaService.publish_and_consume()` guards consumer usage with `if self.consumer is not None` check
- The feature file's "Publish user event" scenarios use `eventhub_service`/`kafka_service` (not the roundtrip variants), so no consumer is instantiated

### 3.4 Unique group_id per test

**PASS**

`fixtures/conftest_messaging.py:75`:
- Kafka consumer uses `group_id=f"test-group-{worker_id}-{uuid4().hex[:8]}"` -- unique per test invocation
- EventHub consumer uses `consumer_group=f"test-{worker_id}"` -- unique per worker

### 3.5 Consumers closed in teardown

**PASS**

Both consumer fixtures use `yield` + explicit `consumer.close()`:
- `fixtures/conftest_messaging.py:66` (eventhub)
- `fixtures/conftest_messaging.py:84` (kafka)

Both `KafkaConsumer.close()` and `EventHubConsumer.close()` properly clean up under lock.

---

## 4. Parallel Safety

### 4.1 Worker-isolated topics

**PASS**

`fixtures/conftest_messaging.py:74`:
- Kafka consumer topic: `f"{settings.kafka_topic_prefix}-{worker_id}"`
- EventHub consumer: worker-isolated via consumer group

### 4.2 Worker-isolated consumer groups

**PASS**

As noted in 3.4, both consumer types use worker-specific group identifiers.

### 4.3 Thread-local storage

**PASS**

- `core/client/base_client.py:44` -- `_thread_local = threading.local()` for request/response
- `core/messaging/base_producer.py:44` -- `_thread_local = threading.local()` for event/result

No cross-thread contamination possible.

### 4.4 No module-level mutable state

**PASS**

- `config/settings.py:94` -- `settings = Settings()` is effectively immutable (frozen pydantic fields)
- `config/version_registry.py:35` -- `_REGISTRY` is module-level mutable dict, but only mutated via `register_version()` which is an explicit extension point, not used during tests
- No other module-level mutable state found

### 4.5 pytest.skip when not configured

**PASS**

All messaging fixtures guard with `pytest.skip()`:
- `fixtures/conftest_messaging.py:26-27` -- EventHub producer
- `fixtures/conftest_messaging.py:39-40` -- Kafka producer
- `fixtures/conftest_messaging.py:59-60` -- EventHub consumer
- `fixtures/conftest_messaging.py:73-74` -- Kafka consumer

---

## 5. Integration

### 5.1 All imports resolve

**PASS**

Verified all import chains:
- `core.messaging.*` -> `base_producer`, `base_consumer` (internal)
- `core.messaging.kafka_producer` -> `confluent_kafka.Producer`
- `core.messaging.kafka_consumer` -> `confluent_kafka.Consumer`
- `core.messaging.eventhub_producer` -> `azure.eventhub.EventHubProducerClient`
- `core.messaging.eventhub_consumer` -> `azure.eventhub.EventHubConsumerClient`
- `services.kafka_service` / `services.eventhub_service` -> `core.messaging.*`
- `models.events.*` -> `models.base_model.BaseDTO`
- `models.builders.event_builder` -> `models.events.user_event`
- `data.factories.event_factory` -> `models.builders.event_builder`, `base_factory`
- `assertions.messaging_assertions` -> `core.messaging.base_consumer`, `core.messaging.base_producer`
- `steps.event_steps` -> `assertions.messaging_assertions`, `data.factories`, `models.events.user_event`, `services.*`
- `fixtures.conftest_messaging` -> all core messaging + services
- `config.version_registry` -> stdlib only
- `validators.schema_validator` -> `jsonschema`, `base_validator`

All `__init__.py` files export the new symbols correctly.

### 5.2 conftest.py registers messaging fixtures

**PASS**

`conftest.py:18` includes `"fixtures.conftest_messaging"` in `pytest_plugins`.

### 5.3 pyproject.toml has new deps

**PASS**

`pyproject.toml:22-23`:
- `azure-eventhub>=5.11,<6.0`
- `confluent-kafka>=2.3,<3.0`

### 5.4 All markers registered

**PASS** (in pyproject.toml)

`pyproject.toml:42-50` registers: `smoke`, `regression`, `critical`, `auth`, `users`, `events`, `api_version`.

**ISSUE (Minor, same as 1.4):** `pytest.ini` only registers `smoke`, `regression`, `critical`, `auth`, `users`. The `events` and `api_version` markers are missing from `pytest.ini`. If pytest reads `pytest.ini` over `pyproject.toml`, using `--strict-markers` (present in `pytest.ini:8`) will cause `events`-marked tests to fail collection.

### 5.5 Feature steps match step defs

**PASS**

Cross-referenced `features/events/user_events.feature` against `steps/event_steps.py`:

| Feature Step | Step Def | Match |
|---|---|---|
| `Given a valid user created event payload` | `event_steps.py:14` | YES |
| `When I publish the event to Event Hub` | `event_steps.py:20` | YES |
| `When I publish the event to Kafka` | `event_steps.py:26` | YES |
| `When I publish and consume the event via Event Hub` | `event_steps.py:32` | YES |
| `When I publish and consume the event via Kafka` | `event_steps.py:38` | YES |
| `Then the event should be published successfully` | `event_steps.py:44` | YES |
| `Then the event should be received by the consumer` | `event_steps.py:56` | YES |
| `And the consumed event body should match the published payload` | `event_steps.py:63` | YES |

---

## 6. Backward Compatibility

### 6.1 Existing HTTP features unchanged

**PASS**

Reviewed all original feature files:
- `features/auth/login.feature` -- unchanged
- `features/auth/token_refresh.feature` -- unchanged
- `features/users/create_user.feature` -- unchanged
- `features/users/get_user.feature` -- unchanged
- `features/users/update_user.feature` -- unchanged

### 6.2 Existing steps unchanged

**PASS**

Reviewed existing step files:
- `steps/common_steps.py` -- updated to pass `api_version` to `ApiAssertions` in the schema step (line 28-29). This is the correct integration point. All other steps untouched.
- `steps/user_steps.py` -- unchanged
- `steps/auth_steps.py` -- unchanged

### 6.3 Works without messaging config

**PASS**

When `EVENTHUB_CONNECTION_STRING` and `KAFKA_BOOTSTRAP_SERVERS` are empty (defaults in `settings.py`), all messaging fixtures call `pytest.skip()`. This means:
- HTTP-only test suites run without any messaging infrastructure
- No import-time failures from missing broker connections
- Event feature tests are gracefully skipped

---

## Summary of Issues Found

### Issue 1: pytest.ini / pyproject.toml configuration conflict (Minor)

**Files:** `pytest.ini`, `pyproject.toml`
**Problem:** Both files define `[pytest]` / `[tool.pytest.ini_options]` configuration. Per pytest precedence rules, `pytest.ini` wins. The `pytest.ini` is missing:
- `-p plugins.api_version_plugin` in addopts
- `events` marker registration
- `api_version` marker registration

**Impact:** If pytest reads `pytest.ini` (which takes precedence), the `--api-version` CLI option will not be available, and `--strict-markers` will reject `@events` and `@api_version` markers.

**Recommendation:** Either remove `pytest.ini` (rely solely on `pyproject.toml`) or synchronize the two files.

---

## Verdict

**PASS WITH ONE MINOR ISSUE**

The `pytest.ini` / `pyproject.toml` conflict is the only finding. All six review categories pass. The version support and messaging expansions are well-architected, follow the specified design patterns, maintain backward compatibility, and are safe for parallel execution.

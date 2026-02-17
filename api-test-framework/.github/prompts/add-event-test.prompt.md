# Add a Messaging / Event Test Scenario

Add a new Event Hub or Kafka test scenario to the API testing framework.

## Input Required
- Broker type: `eventhub` or `kafka`
- Test pattern: `publish-only` or `round-trip` (publish + consume)
- Event type (e.g., `user_created`, `order_placed`)
- Feature file path (e.g., `features/events/order_events.feature`)

## Call Chain (never skip a layer)
```
Feature (.feature) -> Step (steps/) -> Service (services/) -> Producer/Consumer (core/messaging/) -> Broker
```

## Rules
1. Write the scenario in the `.feature` file using proper Gherkin syntax
2. `@when` steps for publish-only MUST use `target_fixture="publish_result"`
3. `@when` steps for round-trip MUST use `target_fixture="round_trip"`
4. Reuse shared event steps from `steps/event_steps.py` wherever possible:
   - `Given a valid {event_type} event payload`
   - `When I publish the event to Event Hub` / `When I publish the event to Kafka`
   - `When I publish and consume the event via Event Hub` / `When I publish and consume the event via Kafka`
   - `Then the event should be published successfully`
   - `Then the event should be delivered within {max_ms:d}ms`
   - `Then the consumed event type should be "{event_type}"`
   - `Then the consumed event body should match the {schema_name} schema`
5. Use `EventFactory` for test data — never hardcode event payloads
6. Step definitions MUST be max 5 lines — delegate to `EventHubService` or `KafkaService`
7. Never call producer/consumer directly in step defs — always go through a service
8. Add the `@events` marker to all messaging scenarios
9. Messaging tests auto-skip when broker config is empty — no special handling needed

## Fixture Scoping
- **Producers** (`eventhub_producer`, `kafka_producer`): session-scoped, lightweight
- **Consumers** (`eventhub_consumer`, `kafka_consumer`): function-scoped, lazy — only created for round-trip tests
- **Services**: `eventhub_service` / `kafka_service` are function-scoped

## Example — Publish-Only Test

**In `features/events/order_events.feature`:**
```gherkin
@events @regression
Feature: Order Events

  @smoke
  Scenario: Publish order_placed event to Kafka
    Given a valid order_placed event payload
    When I publish the event to Kafka
    Then the event should be published successfully
    And the event should be delivered within 5000ms
```

**New step needed in `steps/event_steps.py`:**
```python
@given("a valid order_placed event payload", target_fixture="event_payload")
def order_placed_payload(event_factory: EventFactory) -> EventEnvelope:
    """Build an order_placed event via EventFactory."""
    return event_factory.order_placed()
```

**New factory method in `data/factories/event_factory.py`:**
```python
def order_placed(self) -> EventEnvelope:
    return EventEnvelope(
        event_type="order_placed",
        payload={"order_id": self.fake.uuid4(), "product": self.fake.word(), ...},
    )
```

## Example — Round-Trip Test

```gherkin
  @regression
  Scenario: Round-trip order_placed event via Kafka
    Given a valid order_placed event payload
    When I publish and consume the event via Kafka
    Then the event should be published successfully
    And the consumed event type should be "order_placed"
```

The `When I publish and consume the event via Kafka` step uses `target_fixture="round_trip"` and calls `kafka_service.publish_and_consume()`.

## Checklist
- [ ] Scenario written in `.feature` file with `@events` marker
- [ ] Reused existing steps where possible
- [ ] New steps delegate to service (max 5 lines)
- [ ] `target_fixture` is `"publish_result"` (publish-only) or `"round_trip"` (round-trip)
- [ ] Event payload built via `EventFactory` — no hardcoded data
- [ ] Factory method added if new event type
- [ ] JSON schema added in `schemas/events/` if validating event body
- [ ] Test collector exists in `tests/events/`

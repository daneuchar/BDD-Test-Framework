@events @regression
Feature: User Events
  As an event-driven system
  I want to publish and consume user events
  So that downstream services are notified of user changes

  Background:
    Given a valid user created event payload

  @smoke @critical @events
  Scenario: Publish user event to Event Hub
    When I publish the event to Event Hub
    Then the event should be published successfully

  @smoke @critical @events
  Scenario: Publish user event to Kafka
    When I publish the event to Kafka
    Then the event should be published successfully

  @regression @events
  Scenario: Round-trip user event via Event Hub
    When I publish and consume the event via Event Hub
    Then the event should be received by the consumer
    And the consumed event body should match the published payload

  @regression @events
  Scenario: Round-trip user event via Kafka
    When I publish and consume the event via Kafka
    Then the event should be received by the consumer
    And the consumed event body should match the published payload

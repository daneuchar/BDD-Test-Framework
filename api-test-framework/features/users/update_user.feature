@users @regression
Feature: Update User
  As an API consumer
  I want to update existing users
  So that user information stays current

  Background:
    Given the API is available
    And I am authenticated as an admin

  @smoke @critical
  Scenario: Full update user via PUT
    Given an existing user
    And a valid full user update payload
    When I update the user via PUT
    Then the response status code should be 200
    And the response should match the user_response schema
    And the response time should be less than 2000ms

  @smoke @critical
  Scenario: Partial update user via PATCH
    Given an existing user
    And a partial user update payload
    When I update the user via PATCH
    Then the response status code should be 200
    And the response should match the user_response schema

  @regression
  Scenario: Update non-existent user returns 404
    And a valid full user update payload
    When I update a non-existent user via PUT
    Then the response status code should be 404
    And the response should contain error message "User not found"

  @regression
  Scenario Outline: Fail to update user with invalid data
    Given an existing user
    And an update payload with <field> set to "<value>"
    When I update the user via PUT
    Then the response status code should be <status_code>
    And the response should contain error message "<error_message>"

    Examples:
      | field | value        | status_code | error_message        |
      | email | not-an-email | 422         | Invalid email format |
      | email |              | 422         | Email is required    |

  @regression
  Scenario: Update user without authentication
    Given an existing user
    And a valid full user update payload
    When I update the user via PUT without authentication
    Then the response status code should be 401
    And the response should contain error message "Authentication required"

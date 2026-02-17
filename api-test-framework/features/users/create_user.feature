@users @regression
Feature: Create User
  As an API consumer
  I want to create new users
  So that they can access the system

  Background:
    Given the API is available
    And I am authenticated as an admin

  @smoke @critical
  Scenario: Successfully create a new user
    Given a valid user payload
    When I create a new user
    Then the response status code should be 201
    And the response should match the user_response schema
    And the response time should be less than 2000ms

  @regression
  Scenario: Create user with all optional fields
    Given a valid user payload with all optional fields
    When I create a new user
    Then the response status code should be 201
    And the response should match the user_response schema

  @regression
  Scenario Outline: Fail to create user with invalid data
    Given a user payload with <field> set to "<value>"
    When I create a new user
    Then the response status code should be <status_code>
    And the response should contain error message "<error_message>"

    Examples: Missing required fields
      | field    | value | status_code | error_message          |
      | email    |       | 422         | Email is required      |
      | name     |       | 422         | Name is required       |
      | password |       | 422         | Password is required   |

    Examples: Invalid field values
      | field    | value           | status_code | error_message               |
      | email    | not-an-email    | 422         | Invalid email format        |
      | password | short           | 422         | Password too short          |
      | email    | existing@e.com  | 409         | Email already exists        |

  @regression
  Scenario: Create user without authentication
    Given a valid user payload
    When I create a new user without authentication
    Then the response status code should be 401
    And the response should contain error message "Authentication required"

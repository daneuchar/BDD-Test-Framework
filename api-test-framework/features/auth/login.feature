@auth @regression
Feature: Login
  As an API consumer
  I want to authenticate with valid credentials
  So that I can access protected resources

  Background:
    Given the API is available

  @smoke @critical
  Scenario: Successful login with valid credentials
    Given valid login credentials
    When I send a login request
    Then the response status code should be 200
    And the response should match the login_response schema
    And the response time should be less than 2000ms

  @regression
  Scenario: Login with wrong password
    Given login credentials with wrong password
    When I send a login request
    Then the response status code should be 401
    And the response should contain error message "Invalid credentials"

  @regression
  Scenario: Login with non-existent user
    Given login credentials for a non-existent user
    When I send a login request
    Then the response status code should be 401
    And the response should contain error message "Invalid credentials"

  @regression
  Scenario: Login with locked account
    Given login credentials for a locked account
    When I send a login request
    Then the response status code should be 403
    And the response should contain error message "Account is locked"

  @regression
  Scenario Outline: Login with missing fields
    Given login credentials with <field> missing
    When I send a login request
    Then the response status code should be 422
    And the response should contain error message "<error_message>"

    Examples:
      | field    | error_message         |
      | username | Username is required  |
      | password | Password is required  |

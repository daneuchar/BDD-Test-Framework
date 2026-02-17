@auth @regression
Feature: Token Refresh
  As an authenticated API consumer
  I want to refresh my access token
  So that I can maintain my session without re-authenticating

  Background:
    Given the API is available

  @smoke @critical
  Scenario: Successfully refresh a valid token
    Given a valid refresh token
    When I send a token refresh request
    Then the response status code should be 200
    And the response should match the login_response schema
    And the response time should be less than 2000ms

  @regression
  Scenario: Refresh with an expired token
    Given an expired refresh token
    When I send a token refresh request
    Then the response status code should be 401
    And the response should contain error message "Token has expired"

  @regression
  Scenario: Refresh with an invalid token
    Given an invalid refresh token
    When I send a token refresh request
    Then the response status code should be 401
    And the response should contain error message "Invalid token"

  @regression
  Scenario: Refresh with a missing token
    Given no refresh token
    When I send a token refresh request
    Then the response status code should be 422
    And the response should contain error message "Refresh token is required"

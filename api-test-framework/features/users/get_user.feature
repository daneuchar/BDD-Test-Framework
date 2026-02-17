@users @regression
Feature: Get User
  As an API consumer
  I want to retrieve user information
  So that I can view user details

  Background:
    Given the API is available
    And I am authenticated as an admin

  @smoke @critical
  Scenario: Get user by ID
    Given an existing user
    When I get the user by ID
    Then the response status code should be 200
    And the response should match the user_response schema
    And the response time should be less than 1000ms

  @regression
  Scenario: Get non-existent user returns 404
    When I get a user with a non-existent ID
    Then the response status code should be 404
    And the response should contain error message "User not found"

  @smoke @critical
  Scenario: List all users
    Given at least 2 existing users
    When I list all users
    Then the response status code should be 200
    And the response should match the user_list_response schema
    And the response time should be less than 2000ms

  @regression
  Scenario Outline: List users with pagination
    Given at least 5 existing users
    When I list users with page <page> and page_size <page_size>
    Then the response status code should be 200
    And the response should match the user_list_response schema

    Examples:
      | page | page_size |
      | 1    | 2         |
      | 2    | 2         |
      | 1    | 10        |

  @regression
  Scenario: List users without authentication
    When I list all users without authentication
    Then the response status code should be 401
    And the response should contain error message "Authentication required"

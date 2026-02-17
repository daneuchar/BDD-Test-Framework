# Add a BDD Test Scenario

Add a new test scenario to the API testing framework.

## Input Required
- Feature file path (e.g., `features/users/create_user.feature`)
- Scenario description and Gherkin steps
- Markers: `@smoke`, `@regression`, `@critical`, `@events`

## Rules
1. Write the scenario in the `.feature` file using proper Gherkin syntax
2. Every `@when` step MUST use `target_fixture="api_response"` (HTTP) or `target_fixture="publish_result"` / `target_fixture="round_trip"` (messaging)
3. Reuse shared steps from `steps/common_steps.py` wherever possible:
   - `Given the API is available`
   - `Then the response status code should be {status_code:d}`
   - `Then the response should match the {schema_name} schema`
   - `Then the response time should be less than {max_ms:d}ms`
   - `Then the response should contain error message "{message}"`
4. If new steps are needed, add them to the domain-specific step file (`steps/{domain}_steps.py`)
5. Step definitions MUST be max 5 lines — delegate to services, builders, or factories
6. Never call HTTP or messaging APIs directly in step defs — always go through a service
7. Use `UserFactory`, `AuthFactory`, or `EventFactory` for test data — never hardcode payloads
8. Use `Scenario Outline` with `Examples` table for data-driven tests
9. Every scenario must be independently runnable (no order dependencies)
10. Add at least one marker (`@smoke`, `@regression`, or `@critical`)

## Example — Adding a "Delete User" Scenario

**In `features/users/delete_user.feature`:**
```gherkin
@users @regression
Feature: Delete User

  Background:
    Given the API is available
    And I am authenticated as an admin

  @smoke @critical
  Scenario: Successfully delete an existing user
    Given an existing user
    When I delete the user
    Then the response status code should be 204
```

**In `steps/user_steps.py`:**
```python
@when("I delete the user", target_fixture="api_response")
def delete_user(user_service: UserService, existing_user) -> APIResponse:
    """DELETE a user via UserService."""
    return user_service.delete(existing_user["id"])
```

**In `tests/users/test_delete_user.py`:**
```python
from pytest_bdd import scenarios
scenarios("../../features/users/delete_user.feature")
```

# Modify a BDD Test Scenario

Modify an existing test scenario in the API testing framework.

## Input Required
- Feature file path (e.g., `features/users/create_user.feature`)
- Which scenario to modify (name or line number)
- What to change (steps, data, markers, etc.)

## Rules
1. Read the existing `.feature` file and the corresponding step file before making changes
2. Every `@when` step MUST keep `target_fixture="api_response"` (HTTP) or `target_fixture="publish_result"` / `target_fixture="round_trip"` (messaging)
3. If modifying a step's wording, check all `.feature` files for reuse — update them too or create a new step
4. If a step is shared (defined in `steps/common_steps.py`), do NOT modify it unless the change is intentional for all consumers
5. Step definitions MUST remain max 5 lines — delegate to services, builders, or factories
6. Never call HTTP or messaging APIs directly in step defs — always go through a service
7. When changing test data, use `UserFactory`, `AuthFactory`, or `EventFactory` — never hardcode payloads
8. Preserve existing markers (`@smoke`, `@regression`, `@critical`) unless explicitly asked to change them
9. If converting a single scenario to data-driven, use `Scenario Outline` with `Examples` table
10. Run a mental check: does the modified scenario still work independently (no order dependencies)?

## Example — Changing "Create User" to Validate a New Field

**Before (`features/users/create_user.feature`):**
```gherkin
  @smoke
  Scenario: Successfully create a new user
    Given a valid user payload
    When I create a new user
    Then the response status code should be 201
    Then the response should match the user_response schema
```

**After:**
```gherkin
  @smoke
  Scenario: Successfully create a new user with role
    Given a valid user payload with all optional fields
    When I create a new user
    Then the response status code should be 201
    Then the response should match the user_response schema
```

No new step needed — `a valid user payload with all optional fields` already exists in `steps/user_steps.py`.

## Checklist
- [ ] Read the feature file and step file first
- [ ] Reuse existing steps from `steps/common_steps.py` or `steps/{domain}_steps.py`
- [ ] If new steps added, they delegate to a service (max 5 lines)
- [ ] `@when` steps have correct `target_fixture`
- [ ] No hardcoded payloads — use factories/builders
- [ ] Updated the JSON schema in `schemas/` if response shape changed

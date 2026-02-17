# Remove a BDD Test Scenario

Remove a test scenario from the API testing framework safely.

## Input Required
- Feature file path (e.g., `features/users/create_user.feature`)
- Which scenario to remove (name or line number)

## Rules
1. Read the feature file to identify the exact scenario block (markers + Scenario + all steps)
2. Remove the entire scenario block including its markers (e.g., `@smoke @critical`)
3. Check if removing the scenario leaves the feature file empty (no scenarios left):
   - If empty, delete the `.feature` file, the corresponding `tests/{domain}/test_*.py` collector, and any orphaned step defs
   - If other scenarios remain, just remove the scenario block
4. Check for orphaned step definitions:
   - Grep all `.feature` files for each step used by the removed scenario
   - If a step is only used by the removed scenario, delete its definition from `steps/{domain}_steps.py`
   - NEVER delete steps from `steps/common_steps.py` — they are shared
5. Check for orphaned fixtures:
   - If the removed scenario was the only consumer of a domain-specific fixture, remove it from `fixtures/conftest_data.py`
6. Check for orphaned schemas:
   - If no remaining scenario references a JSON schema, consider removing it from `schemas/`

## Example — Removing "Get non-existent user" Scenario

**1. Remove from `features/users/get_user.feature`:**
```gherkin
  # DELETE this entire block:
  @regression
  Scenario: Get a non-existent user returns 404
    Given the API is available
    And I am authenticated as an admin
    When I get a user with a non-existent ID
    Then the response status code should be 404
    Then the response should contain error message "User not found"
```

**2. Check step usage:**
```bash
grep -r "I get a user with a non-existent ID" features/
```
If no other feature uses it, remove from `steps/user_steps.py`:
```python
# DELETE:
@when("I get a user with a non-existent ID", target_fixture="api_response")
def get_nonexistent_user(user_service: UserService) -> APIResponse:
    ...
```

**3. Verify:** The remaining scenarios in the feature file still parse correctly.

## Checklist
- [ ] Scenario block fully removed (markers + scenario + steps)
- [ ] Feature file deleted if no scenarios remain
- [ ] Test collector (`tests/{domain}/test_*.py`) deleted if feature file deleted
- [ ] Orphaned step defs removed (grep all features first)
- [ ] Shared steps in `common_steps.py` left untouched
- [ ] Orphaned fixtures cleaned up

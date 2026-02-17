# API Test Framework

Production-grade, design-pattern-driven API testing framework built with Python, pytest-bdd, and Allure.

## Architecture

```
Feature --> Step --> Service --> Client --> HTTP
```

Step definitions are thin glue code. Business logic lives in service objects.

### Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| Service Object | `services/` | Encapsulates API interactions per domain |
| Builder | `models/builders/` | Fluent payload construction |
| Factory / Object Mother | `data/factories/` | Dynamic Faker-powered test data |
| Strategy | `core/auth/`, `validators/` | Swappable auth and validation |
| Template Method | `core/client/` | Shared request lifecycle |
| Facade | `assertions/` | Unified assertion API |
| Chain of Responsibility | `core/response_handler.py` | Response processing pipeline |
| Composite | `validators/composite_validator.py` | Run multiple validators |
| Decorator | `core/retry.py` | Configurable retry with backoff |
| Singleton | `config/settings.py` | Shared configuration instance |

## Tech Stack

- Python 3.11+
- pytest + pytest-bdd (BDD with Gherkin)
- pytest-xdist (parallel execution)
- allure-pytest (rich reporting)
- requests (sync HTTP) + httpx (async HTTP)
- pydantic + pydantic-settings (DTOs, config)
- jsonschema (response validation)
- faker (test data generation)

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# Install the framework and dev dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env with your API details
```

## Running Tests

```bash
# Full parallel run with Allure
./scripts/run_tests.sh

# Smoke tests only
./scripts/run_smoke.sh

# Regression tests only
./scripts/run_regression.sh

# Run a specific feature
pytest features/users/create_user.feature -n auto --alluredir=reports/allure-results

# Generate Allure report
./scripts/generate_report.sh
```

## Project Structure

```
api-test-framework/
+-- pyproject.toml              # Dependencies and tool config
+-- pytest.ini                  # pytest + BDD + xdist + Allure config
+-- conftest.py                 # Root: plugin registration, fixture imports
+-- config/                     # Settings and endpoint registry
+-- core/                       # HTTP clients, auth strategies, retry, response handling
+-- services/                   # Service objects (one per API domain)
+-- models/                     # Pydantic DTOs and builders
+-- schemas/                    # JSON Schema files for validation
+-- validators/                 # Pluggable validation strategies
+-- assertions/                 # Facade for all assertion types
+-- fixtures/                   # pytest fixtures (no business logic)
+-- features/                   # Gherkin feature files
+-- steps/                      # BDD step definitions (thin wrappers)
+-- plugins/                    # Custom pytest plugins
+-- data/                       # Test data factories and static fixtures
+-- scripts/                    # Shell scripts for running tests
```

## Custom Markers

| Marker | Description |
|--------|-------------|
| `@smoke` | Quick smoke tests for critical paths |
| `@regression` | Full regression test suite |
| `@critical` | Business-critical scenarios |
| `@auth` | Authentication and authorization tests |
| `@users` | User management tests |

## CI/CD

```yaml
# GitHub Actions example
- name: Run API Tests
  run: pytest -n auto --alluredir=reports/allure-results

- name: Upload Allure Results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: allure-results
    path: reports/allure-results
```

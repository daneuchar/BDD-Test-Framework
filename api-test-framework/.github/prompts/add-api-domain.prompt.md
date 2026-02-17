# Add a New API Domain

Scaffold a complete new API domain (e.g., orders, products, payments) in the testing framework.

## Input Required
- Domain name (e.g., `orders`)
- API endpoints (e.g., `POST /orders`, `GET /orders/{id}`, `GET /orders`)
- Key fields for the domain model
- Which API versions support it (`v1`, `v2`, or both)

## Call Chain (never skip a layer)
```
Feature (.feature) -> Step (steps/) -> Service (services/) -> Client (core/client/) -> HTTP
```

## Files to Create (in order)

### 1. Endpoints — `config/endpoints.py`
Add new enum members:
```python
ORDERS = "/orders"
ORDER_BY_ID = "/orders/{order_id}"
```

### 2. DTO Models — `models/{domain}.py`
Pydantic models for request/response:
```python
class CreateOrderRequest(BaseDTO):
    product_id: str
    quantity: int
    # ...

class UpdateOrderRequest(BaseDTO):
    quantity: int | None = None
    # ...

class OrderResponse(BaseDTO):
    id: str
    product_id: str
    # ...
```

### 3. Builder — `models/builders/{domain}_builder.py`
Fluent builder with `.with_x().build()`:
```python
class OrderBuilder:
    def with_product(self, product_id: str) -> OrderBuilder: ...
    def with_quantity(self, qty: int) -> OrderBuilder: ...
    def build(self) -> CreateOrderRequest: ...
```

### 4. Factory — `data/factories/{domain}_factory.py`
Faker-powered, worker-aware:
```python
class OrderFactory(BaseFactory):
    def create(self) -> CreateOrderRequest: ...
    def create_batch(self, count: int) -> list[CreateOrderRequest]: ...
```

### 5. JSON Schemas — `schemas/v1/{domain}_response.json`, `schemas/v2/{domain}_response.json`
JSON Schema Draft-07 for response validation.

### 6. Service — `services/{domain}_service.py`
Extends `BaseService`, all methods `@allure.step`:
```python
class OrderService(BaseService):
    def create(self, payload: CreateOrderRequest) -> APIResponse: ...
    def get(self, order_id: str) -> APIResponse: ...
    def list(self, **params) -> APIResponse: ...
    def update(self, order_id: str, payload: UpdateOrderRequest) -> APIResponse: ...
    def delete(self, order_id: str) -> APIResponse: ...
```

### 7. Steps — `steps/{domain}_steps.py`
Thin glue (max 5 lines per step), delegates to service:
```python
@given("a valid order payload", target_fixture="order_payload")
def valid_order_payload(order_factory): ...

@when("I create a new order", target_fixture="api_response")
def create_order(order_service, order_payload): ...
```

### 8. Features — `features/{domain}/*.feature`
One feature file per CRUD operation, with `@smoke`/`@regression` markers.

### 9. Test Collectors — `tests/{domain}/test_*.py`
```python
from pytest_bdd import scenarios
scenarios("../../features/{domain}/{feature}.feature")
```

### 10. Fixtures — `fixtures/conftest_data.py`
Add factory and service fixtures:
```python
@pytest.fixture(scope="session")
def order_factory(worker_id): ...

@pytest.fixture(scope="session")
def order_service(authenticated_client): ...
```

### 11. Markers — `pyproject.toml` and `pytest.ini`
Add domain marker: `orders: Order management tests`

## Rules
- Every `@when` step MUST use `target_fixture="api_response"`
- All payloads built via Builder/Factory — no raw dicts
- Service methods use `self._request()` from `BaseService`
- Step defs max 5 lines — delegate to service
- JSON schemas must validate both v1 and v2 responses
- Factory must be worker-aware (inherit `BaseFactory`)

## Checklist
- [ ] Endpoints added to `config/endpoints.py`
- [ ] DTO models in `models/{domain}.py`
- [ ] Builder in `models/builders/{domain}_builder.py`
- [ ] Factory in `data/factories/{domain}_factory.py`
- [ ] JSON schemas in `schemas/v1/` and `schemas/v2/`
- [ ] Service in `services/{domain}_service.py` extending `BaseService`
- [ ] Steps in `steps/{domain}_steps.py` (thin, max 5 lines)
- [ ] Features in `features/{domain}/`
- [ ] Test collectors in `tests/{domain}/`
- [ ] Fixtures in `fixtures/conftest_data.py`
- [ ] Marker added to `pyproject.toml` and `pytest.ini`

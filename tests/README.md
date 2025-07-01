# Testing

Async testing with pytest and pytest-asyncio.

## Quick Start

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_database.py
pytest tests/test_api.py

# Run specific test
pytest tests/test_database.py::test_create_key_value
pytest tests/test_api.py::test_set_user_value
```

## Test Files

### `test_database.py`
Tests the database functionality and repository layer:
- **Fixtures**: Create test data (user1, user2 with different scenarios)
- **CRUD Operations**: Basic create, read, update functionality
- **User Isolation**: Verifies data separation between users
- **Edge Cases**: Tests for non-existent data

### `test_api.py`
Tests the FastAPI endpoints and concurrency:
- **Basic functionality**: Set/get operations via HTTP
- **Error handling**: Invalid JSON, missing fields
- **Concurrency testing**: Race conditions, high load
- **Load testing**: Mixed operations under stress

### `test_db_inspect.py`
Inspects all databases and tables on the server. This test is dependent on the `clean_db` fixture, ensuring a clean state before inspection.

## Fixtures

### `test_database` (session-scoped)
Sets up and tears down the test database once per test session.

### `clean_db` (function-scoped)
Provides a clean database session with all data cleared before and after each test. All destructive operations are strictly gated by `APP_ENV=test` and will fail otherwise.

### Database Test Fixtures
- `user1` - Creates user1 with one key-value pair (theme=light)
- `user1_updated` - Creates user1 with an updated key (theme=dark)
- `user1_multiple_keys` - Creates user1 with multiple keys (theme=light, language=en)
- `user2` - Creates user2 with the same key as user1 (theme=light)

## Writing Tests

### Database Tests
```python
@pytest.mark.asyncio
async def test_create_key_value(user1):
    session = user1
    value = await get_user_key_value(session, "user1", "theme")
    assert value == "light"
```

### API Tests
```python
@pytest.mark.asyncio
async def test_set_user_value():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/user/dict",
            json={"key": "theme", "value": "dark"}
        )
        assert response.status_code == 200
```

### Concurrency Tests
```python
@pytest.mark.asyncio
async def test_concurrent_sets():
    async with AsyncClient(app=app, base_url="http://test") as client:
        tasks = [
            client.post("/user/dict", json={"key": f"key_{i}", "value": f"value_{i}"})
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)
        assert all(r.status_code == 200 for r in results)
```

## Test Structure

### CRUD Operations
- `test_create_key_value` - Basic key-value creation
- `test_update_key_value` - Basic key-value updates
- `test_add_second_key` - Adding multiple keys to a user
- `test_create_user2` - Creating a second user

### User Isolation
- `test_user2_isolation` - Verifies users don't interfere with each other

### Edge Cases
- `test_get_nonexistent_user` - Non-existent user handling
- `test_get_nonexistent_key` - Non-existent key handling

## Environment Variables

Required in `.env`:
- `APP_ENV` - Must be set to `test` for running tests and destructive operations
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password  
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `DB_NAME` - Database name (should be a test database when running tests)

See [../ENVIRONMENT_SETUP.md](../ENVIRONMENT_SETUP.md) for full details.

## Safety

- All destructive test operations are strictly gated by `APP_ENV=test` and will fail otherwise.
- Test utilities and fixtures enforce all safety; `config.py` is environment-agnostic and never contains test-specific logic.
- The `DB_NAME` variable is used for all environments; when running tests, it must point to a dedicated test database.
- Prevents accidental modification of production databases.
- `.env` files are ignored by git.

## Concurrency Testing

The API tests include comprehensive concurrency testing:

- **Concurrent sets**: Multiple keys set simultaneously
- **Concurrent gets**: Multiple reads of the same key
- **Race conditions**: Set and get operations on the same key
- **High load**: Mixed operations under stress
- **Error handling**: Invalid requests under load

This helps identify race conditions, deadlocks, and performance issues in the async setup. 
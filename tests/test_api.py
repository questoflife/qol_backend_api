"""
API endpoint tests for the Quest of Life Backend API.
Tests FastAPI endpoints and concurrency handling.
"""
import asyncio
import pytest
from httpx import AsyncClient

from app.main import app


# --- Basic API functionality tests ---

@pytest.mark.asyncio
async def test_set_user_value(clean_db_override_app_session):
    """Test setting a user value via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/user/dict",
            json={"key": "theme", "value": "dark"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"message": "Value set successfully."}


@pytest.mark.asyncio
async def test_get_user_value(clean_db_override_app_session):
    """Test getting a user value via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First set a value
        await client.post(
            "/user/dict",
            json={"key": "language", "value": "es"}
        )
        
        # Then get it
        response = await client.get("/user/dict/language")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "language"
        assert data["value"] == "es"


@pytest.mark.asyncio
async def test_get_nonexistent_key(clean_db_override_app_session):
    """Test getting a key that doesn't exist."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/user/dict/nonexistent_key")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "nonexistent_key"
        assert data["value"] == ""  # Empty string for non-existent keys


@pytest.mark.asyncio
async def test_update_existing_key(clean_db_override_app_session):
    """Test updating an existing key via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Set initial value
        await client.post(
            "/user/dict",
            json={"key": "notifications", "value": "disabled"}
        )
        
        # Update the value
        response = await client.post(
            "/user/dict",
            json={"key": "notifications", "value": "enabled"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"message": "Value set successfully."}
        
        # Verify the update
        get_response = await client.get("/user/dict/notifications")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["key"] == "notifications"
        assert data["value"] == "enabled"


# --- Concurrency and load testing ---

@pytest.mark.asyncio
async def test_concurrent_sets(clean_db_override_app_session):
    """Test concurrent setting of different keys."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create multiple concurrent requests
        async def set_key(key: str, value: str):
            response = await client.post(
                "/user/dict",
                json={"key": key, "value": value}
            )
            return response.status_code
        
        # Run 10 concurrent set operations
        tasks = [
            set_key(f"key_{i}", f"value_{i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        # Verify all values were set correctly
        for i in range(10):
            response = await client.get(f"/user/dict/key_{i}")
            assert response.status_code == 200
            data = response.json()
            assert data["key"] == f"key_{i}"
            assert data["value"] == f"value_{i}"


@pytest.mark.asyncio
async def test_concurrent_gets(clean_db_override_app_session):
    """Test concurrent getting of the same key."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Set a value first
        await client.post(
            "/user/dict",
            json={"key": "concurrent_test", "value": "test_value"}
        )
        
        # Create multiple concurrent get requests
        async def get_key():
            response = await client.get("/user/dict/concurrent_test")
            return response.status_code, response.json()
        
        # Run 20 concurrent get operations
        tasks = [get_key() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed and return the same value
        for status_code, data in results:
            assert status_code == 200
            assert data["key"] == "concurrent_test"
            assert data["value"] == "test_value"


@pytest.mark.asyncio
async def test_concurrent_set_get_race_condition(clean_db_override_app_session):
    """Test race condition between set and get operations."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a race condition: set and get the same key concurrently
        async def set_key():
            response = await client.post(
                "/user/dict",
                json={"key": "race_test", "value": "new_value"}
            )
            return response.status_code
        
        async def get_key():
            response = await client.get("/user/dict/race_test")
            return response.status_code, response.json()
        
        # Run set and get concurrently
        set_task = asyncio.create_task(set_key())
        get_task = asyncio.create_task(get_key())
        
        set_result, get_result = await asyncio.gather(set_task, get_task)
        
        # Set should succeed
        assert set_result == 200
        
        # Get should succeed (either get old value or new value)
        status_code, data = get_result
        assert status_code == 200
        assert data["key"] == "race_test"
        # Value could be either empty string (if get happened before set)
        # or "new_value" (if get happened after set)
        assert data["value"] in ["", "new_value"]


@pytest.mark.asyncio
async def test_high_load_concurrent_operations(clean_db_override_app_session):
    """Test high load with mixed set/get operations."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a mix of set and get operations
        async def set_operation(i: int):
            response = await client.post(
                "/user/dict",
                json={"key": f"load_test_{i}", "value": f"value_{i}"}
            )
            return response.status_code
        
        async def get_operation(i: int):
            response = await client.get(f"/user/dict/load_test_{i}")
            return response.status_code
        
        # Create 50 operations (25 sets, 25 gets)
        tasks = []
        for i in range(25):
            tasks.append(set_operation(i))
            tasks.append(get_operation(i))
        
        # Run all operations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that no exceptions occurred
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Found exceptions: {exceptions}"
        
        # All successful operations should return 200
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert all(status == 200 for status in successful_results)


@pytest.mark.asyncio
async def test_concurrent_updates_same_key(clean_db_override_app_session):
    """Test concurrent updates to the same key."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Set initial value
        await client.post(
            "/user/dict",
            json={"key": "update_test", "value": "initial"}
        )
        
        # Create multiple concurrent updates
        async def update_key(value: str):
            response = await client.post(
                "/user/dict",
                json={"key": "update_test", "value": value}
            )
            return response.status_code
        
        # Run 10 concurrent updates
        tasks = [
            update_key(f"update_{i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        # Verify final value (should be one of the updates)
        response = await client.get("/user/dict/update_test")
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "update_test"
        # Value should be one of the updates (last one to complete)
        assert data["value"].startswith("update_")


@pytest.mark.asyncio
async def test_error_handling_invalid_json(clean_db_override_app_session):
    """Test error handling for invalid JSON."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/user/dict",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 (Unprocessable Entity) for invalid JSON
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_error_handling_missing_fields(clean_db_override_app_session):
    """Test error handling for missing required fields."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/user/dict",
            json={"key": "test"}  # Missing "value" field
        )
        
        # Should return 422 (Unprocessable Entity) for missing fields
        assert response.status_code == 422 
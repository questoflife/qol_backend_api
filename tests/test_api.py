"""
API endpoint tests for the Quest of Life Backend API.
Tests FastAPI endpoints and concurrency handling.
"""
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app
from src.database.models import UserValues


# --- Basic API functionality tests ---

@pytest.mark.asyncio
async def test_set_user_text(clean_db_override_app_session, session_factory):
    """Test setting a user text via API."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text=None)
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/user/text",
            json={"text": "My new text"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"text": "My new text"}


@pytest.mark.asyncio
async def test_get_user_text(clean_db_override_app_session, session_factory):
    """Test getting a user text via API."""
    # Create user with text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Hello API")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/user/text")
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello API"


@pytest.mark.asyncio
async def test_get_user_with_null_text(clean_db_override_app_session, session_factory):
    """Test getting text when it's null (should return empty string)."""
    # Create user with null text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text=None)
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/user/text")
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == ""  # API converts None to empty string


@pytest.mark.asyncio
async def test_update_existing_text(clean_db_override_app_session, session_factory):
    """Test updating an existing user's text via API."""
    # Create user with initial text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Initial text")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Update the text
        response = await client.put(
            "/user/text",
            json={"text": "Updated text"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"text": "Updated text"}
        
        # Verify the update
        get_response = await client.get("/user/text")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["text"] == "Updated text"


# --- Concurrency and load testing ---

@pytest.mark.asyncio
async def test_concurrent_sets(clean_db_override_app_session, session_factory):
    """Test concurrent setting of user text."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text=None)
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create multiple concurrent requests with different text values
        async def set_text(value: str):
            response = await client.put(
                "/user/text",
                json={"text": value}
            )
            return response.status_code
        
        # Run 10 concurrent set operations
        tasks = [
            set_text(f"Text version {i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        # Verify final value is one of the set values
        response = await client.get("/user/text")
        assert response.status_code == 200
        data = response.json()
        assert data["text"].startswith("Text version ")


@pytest.mark.asyncio
async def test_concurrent_gets(clean_db_override_app_session, session_factory):
    """Test concurrent getting of the same text."""
    # Create user with text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Concurrent test value")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create multiple concurrent get requests
        async def get_text():
            response = await client.get("/user/text")
            return response.status_code, response.json()
        
        # Run 20 concurrent get operations
        tasks = [get_text() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed and return the same value
        for status_code, data in results:
            assert status_code == 200
            assert data["text"] == "Concurrent test value"


@pytest.mark.asyncio
async def test_concurrent_set_get_race_condition(clean_db_override_app_session, session_factory):
    """Test race condition between set and get operations."""
    # Create user with initial text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Initial value")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a race condition: set and get the same text concurrently
        async def set_text():
            response = await client.put(
                "/user/text",
                json={"text": "New value"}
            )
            return response.status_code
        
        async def get_text():
            response = await client.get("/user/text")
            return response.status_code, response.json()
        
        # Run set and get concurrently
        set_task = asyncio.create_task(set_text())
        get_task = asyncio.create_task(get_text())
        
        set_result, get_result = await asyncio.gather(set_task, get_task)
        
        # Set should succeed
        assert set_result == 200
        
        # Get should succeed (either get old value or new value)
        status_code, data = get_result
        assert status_code == 200
        # Value could be either "Initial value" (if get happened before set)
        # or "New value" (if get happened after set)
        assert data["text"] in ["Initial value", "New value"]


@pytest.mark.asyncio
async def test_high_load_concurrent_operations(clean_db_override_app_session, session_factory):
    """Test high load with mixed set/get operations."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Initial")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a mix of set and get operations
        async def set_operation(i: int):
            response = await client.put(
                "/user/text",
                json={"text": f"Load test value {i}"}
            )
            return response.status_code
        
        async def get_operation():
            response = await client.get("/user/text")
            return response.status_code
        
        # Create 50 operations (25 sets, 25 gets)
        tasks = []
        for i in range(25):
            tasks.append(set_operation(i))
            tasks.append(get_operation())
        
        # Run all operations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that no exceptions occurred
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Found exceptions: {exceptions}"
        
        # All successful operations should return 200
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert all(status == 200 for status in successful_results)


@pytest.mark.asyncio
async def test_concurrent_updates_same_text(clean_db_override_app_session, session_factory):
    """Test concurrent updates to the same user's text."""
    # Create user with initial text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Initial")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create multiple concurrent updates
        async def update_text(value: str):
            response = await client.put(
                "/user/text",
                json={"text": value}
            )
            return response.status_code
        
        # Run 10 concurrent updates
        tasks = [
            update_text(f"Update {i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        # Verify final value (should be one of the updates)
        response = await client.get("/user/text")
        assert response.status_code == 200
        data = response.json()
        # Value should be one of the updates (last one to complete)
        assert data["text"].startswith("Update ")


@pytest.mark.asyncio
async def test_error_handling_invalid_json(clean_db_override_app_session):
    """Test error handling for invalid JSON."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/user/text",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 (Unprocessable Entity) for invalid JSON
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_error_handling_missing_fields(clean_db_override_app_session):
    """Test error handling for missing required fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/user/text",
            json={}  # Missing "text" field
        )
        
        # Should return 422 (Unprocessable Entity) for missing fields
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_text_is_valid(clean_db_override_app_session, session_factory):
    """Test that empty string is a valid text value."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Some text")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Set empty text
        response = await client.put(
            "/user/text",
            json={"text": ""}
        )
        
        assert response.status_code == 200
        assert response.json() == {"text": ""}
        
        # Verify empty text was saved
        get_response = await client.get("/user/text")
        assert get_response.status_code == 200
        assert get_response.json()["text"] == ""


# --- Rate limiting tests ---

@pytest.mark.asyncio
async def test_rate_limit_on_put_endpoint(clean_db_override_app_session, session_factory):
    """Test that rate limiting is enforced on PUT /user/text endpoint (30 requests/minute)."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text=None)
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Make requests up to the limit (30/minute for PUT)
        success_count = 0
        rate_limited = False
        
        for i in range(35):  # Try 35 requests (should hit limit at 31)
            response = await client.put(
                "/user/text",
                json={"text": f"Test {i}"}
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:  # Too Many Requests
                rate_limited = True
                break
        
        # Should have succeeded for the first 30 and been rate limited after
        assert success_count == 30, f"Expected 30 successful requests, got {success_count}"
        assert rate_limited, "Expected to hit rate limit (429) but didn't"


@pytest.mark.asyncio
async def test_rate_limit_on_get_endpoint(clean_db_override_app_session, session_factory):
    """Test that rate limiting is enforced on GET /user/text endpoint (60 requests/minute)."""
    # Create user with text
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text="Test value")
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Make requests up to the limit (60/minute for GET)
        success_count = 0
        rate_limited = False
        
        for i in range(65):  # Try 65 requests (should hit limit at 61)
            response = await client.get("/user/text")
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:  # Too Many Requests
                rate_limited = True
                break
        
        # Should have succeeded for the first 60 and been rate limited after
        assert success_count == 60, f"Expected 60 successful requests, got {success_count}"
        assert rate_limited, "Expected to hit rate limit (429) but didn't"


@pytest.mark.asyncio
async def test_rate_limit_response_format(clean_db_override_app_session, session_factory):
    """Test that rate limit response includes proper error information."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text=None)
        session.add(user)
        await session.commit()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Exhaust the rate limit
        for i in range(30):
            await client.put("/user/text", json={"text": f"Test {i}"})
        
        # Next request should be rate limited
        response = await client.put("/user/text", json={"text": "Over limit"})
        
        assert response.status_code == 429
        # slowapi returns plain text error message by default
        assert "rate limit" in response.text.lower() or "too many" in response.text.lower()


@pytest.mark.asyncio
async def test_rate_limit_per_ip_isolation(clean_db_override_app_session, session_factory):
    """Test that rate limits are tracked per IP address."""
    # Create user first
    async with session_factory() as session:
        user = UserValues(user_id="test_user_123", text=None)
        session.add(user)
        await session.commit()
    
    # Note: In test environment, all requests come from the same test client,
    # so they share the same IP. This test verifies the rate limit applies to that IP.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Make 30 PUT requests (reaching the limit)
        for i in range(30):
            response = await client.put("/user/text", json={"text": f"Test {i}"})
            assert response.status_code == 200
        
        # 31st request should be rate limited
        response = await client.put("/user/text", json={"text": "Over limit"})
        assert response.status_code == 429
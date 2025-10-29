import pytest
pytestmark = pytest.mark.skip(reason="Dashboard auth script requires live API")
"""
Test authentication endpoints to verify login functionality.
"""
import asyncio
import sys
import os
import json
import httpx

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

async def test_login(username, password):
    """Test login endpoint with provided credentials."""
    print(f"Testing login with username: {username}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Attempt login
            response = await client.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": username,
                    "password": password,
                    "grant_type": "password"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print(f"Login successful! Token received.")
                
                # Test the /auth/me endpoint with the token
                me_response = await client.get(
                    f"{BASE_URL}/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"User profile retrieved successfully:")
                    print(json.dumps(user_data, indent=2))
                    return True
                else:
                    print(f"Failed to get user profile. Status: {me_response.status_code}")
                    print(f"Response: {me_response.text}")
            else:
                print(f"Login failed. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error during test: {e}")
            return False

async def main():
    """Run the authentication tests."""
    # Test admin user
    print("\n=== Testing Admin User ===")
    await test_login("admin", "admin123")
    
    # Test regular user
    print("\n=== Testing Regular User ===")
    await test_login("user", "user123")
    
    # Test with invalid credentials
    print("\n=== Testing Invalid Credentials ===")
    await test_login("invalid", "wrongpassword")

if __name__ == "__main__":
    asyncio.run(main())

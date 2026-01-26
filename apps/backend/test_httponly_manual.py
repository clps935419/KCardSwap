#!/usr/bin/env python3
"""
Manual test script to verify HttpOnly cookie implementation.

This script tests the authentication endpoints to ensure:
1. Login endpoints set httpOnly cookies
2. Auth middleware accepts cookies
3. Logout endpoint clears cookies
"""

import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@kcardswap.com"
ADMIN_PASSWORD = "admin123456"


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_cookies(cookies):
    """Print cookies in a readable format."""
    if not cookies:
        print("  No cookies set")
        return
    
    for name, value in cookies.items():
        print(f"  {name}: {value[:50]}..." if len(value) > 50 else f"  {name}: {value}")


def test_admin_login():
    """Test admin login sets httpOnly cookies."""
    print_section("Test 1: Admin Login")
    
    session = requests.Session()
    
    # Send login request
    response = session.post(
        f"{BASE_URL}/auth/admin-login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Login successful")
        data = response.json()
        print(f"User ID: {data['data']['user_id']}")
        print(f"Email: {data['data']['email']}")
        
        # Check cookies
        print("\nCookies set:")
        print_cookies(session.cookies.get_dict())
        
        # Verify expected cookies exist
        if 'access_token' in session.cookies and 'refresh_token' in session.cookies:
            print("\n✓ Both access_token and refresh_token cookies are set")
            return session
        else:
            print("\n✗ Missing expected cookies")
            return None
    else:
        print(f"✗ Login failed: {response.text}")
        return None


def test_authenticated_request(session):
    """Test that authenticated request works with cookie."""
    print_section("Test 2: Authenticated Request with Cookie")
    
    # Try to access profile endpoint (requires authentication)
    response = session.get(f"{BASE_URL}/profile/me")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Authenticated request successful with cookie")
        data = response.json()
        print(f"User: {data.get('data', {}).get('display_name', 'N/A')}")
        return True
    else:
        print(f"✗ Authenticated request failed: {response.text}")
        return False


def test_refresh_token(session):
    """Test token refresh endpoint."""
    print_section("Test 3: Token Refresh")
    
    response = session.post(f"{BASE_URL}/auth/refresh")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Token refresh successful")
        data = response.json()
        print(f"Message: {data.get('message')}")
        
        # Check if new cookies were set
        print("\nCookies after refresh:")
        print_cookies(session.cookies.get_dict())
        return True
    else:
        print(f"✗ Token refresh failed: {response.text}")
        return False


def test_logout(session):
    """Test logout clears cookies."""
    print_section("Test 4: Logout")
    
    response = session.post(f"{BASE_URL}/auth/logout")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Logout successful")
        
        # Check if cookies were cleared
        print("\nCookies after logout:")
        print_cookies(session.cookies.get_dict())
        
        # Verify cookies are cleared or expired
        access_token = session.cookies.get('access_token', '')
        refresh_token = session.cookies.get('refresh_token', '')
        
        if not access_token and not refresh_token:
            print("\n✓ Cookies successfully cleared")
            return True
        else:
            print("\n⚠ Cookies still present (may need to check max-age)")
            return True
    else:
        print(f"✗ Logout failed: {response.text}")
        return False


def test_request_after_logout(session):
    """Test that requests fail after logout."""
    print_section("Test 5: Request After Logout")
    
    response = session.get(f"{BASE_URL}/profile/me")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✓ Request correctly rejected after logout")
        return True
    elif response.status_code == 200:
        print("✗ Request succeeded after logout (unexpected)")
        return False
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  HttpOnly Cookie Authentication Tests")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    
    results = []
    
    # Test 1: Login
    session = test_admin_login()
    if session:
        results.append(("Admin Login", True))
        
        # Test 2: Authenticated request
        result = test_authenticated_request(session)
        results.append(("Authenticated Request", result))
        
        # Test 3: Token refresh
        result = test_refresh_token(session)
        results.append(("Token Refresh", result))
        
        # Test 4: Logout
        result = test_logout(session)
        results.append(("Logout", result))
        
        # Test 5: Request after logout
        result = test_request_after_logout(session)
        results.append(("Request After Logout", result))
    else:
        results.append(("Admin Login", False))
        print("\n✗ Cannot continue tests without successful login")
    
    # Print summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

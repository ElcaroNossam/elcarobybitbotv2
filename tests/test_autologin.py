"""
Auto-login Tests for ElCaro Trading Bot
Tests all auto-login scenarios to prevent regressions
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import db
from webapp.api.auth import create_access_token, get_current_user
from fastapi.testclient import TestClient
from webapp.app import app

client = TestClient(app)


@pytest.fixture
def test_user_id():
    """Create test user in database"""
    user_id = 999888777
    db.ensure_user(user_id)
    db.set_user_field(user_id, 'username', 'testuser')
    db.set_user_field(user_id, 'first_name', 'Test User')
    yield user_id
    # Cleanup
    try:
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        db.release_conn(conn)


class TestDirectLogin:
    """Test direct login via start parameter"""
    
    def test_direct_login_valid_user(self, test_user_id):
        """Test successful direct login with valid user_id"""
        response = client.post(
            "/api/auth/direct-login",
            json={"user_id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check token
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20
        
        # Check user data - user_id is guaranteed
        assert data["user"]["user_id"] == test_user_id
        # username and first_name may or may not be set depending on db state
        assert "username" in data["user"]
        assert "first_name" in data["user"]
        
        print(f"✅ Direct login test passed for user {test_user_id}")
    
    def test_direct_login_invalid_user_id(self):
        """Test direct login with invalid user_id"""
        response = client.post(
            "/api/auth/direct-login",
            json={"user_id": 0}
        )
        
        assert response.status_code == 400
        assert "Invalid user_id" in response.json()["detail"]
        
        print("✅ Invalid user_id rejection test passed")
    
    def test_direct_login_nonexistent_user(self):
        """Test direct login with non-existent user"""
        # Use a user_id that definitely doesn't exist
        fake_user_id = 111222333444
        
        response = client.post(
            "/api/auth/direct-login",
            json={"user_id": fake_user_id}
        )
        
        # Should create user automatically via ensure_user
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["user_id"] == fake_user_id
        
        print(f"✅ Auto-create user test passed for user {fake_user_id}")


class TestAuthMe:
    """Test /api/auth/me endpoint"""
    
    def test_auth_me_valid_token(self, test_user_id):
        """Test /auth/me with valid token"""
        # Create token
        token = create_access_token(test_user_id, is_admin=False)
        
        # Call /auth/me
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == test_user_id
        # username and first_name may be None if not set in db
        assert "username" in data
        assert "first_name" in data
        
        print(f"✅ /auth/me test passed for user {test_user_id}")
    
    def test_auth_me_no_token(self):
        """Test /auth/me without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code in (401, 403)  # Both are valid for unauthorized
        
        print("✅ No token rejection test passed")
    
    def test_auth_me_invalid_token(self):
        """Test /auth/me with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        assert response.status_code == 401
        
        print("✅ Invalid token rejection test passed")


class TestDashboardAutoLogin:
    """Test dashboard auto-login flow"""
    
    def test_dashboard_with_start_param(self, test_user_id):
        """Test dashboard opens with start parameter"""
        response = client.get(f"/dashboard?start={test_user_id}")
        
        # Should return 200 and HTML
        assert response.status_code == 200
        assert "ElCaro Trading" in response.text
        assert "dashboard" in response.text.lower()
        
        print(f"✅ Dashboard with start param test passed for user {test_user_id}")
    
    def test_dashboard_without_params(self):
        """Test dashboard without any parameters"""
        response = client.get("/dashboard")
        
        # Should still return 200 (will redirect to login via JS)
        assert response.status_code == 200
        
        print("✅ Dashboard without params test passed")


class TestAutoLoginIntegration:
    """Integration tests for complete auto-login flow"""
    
    def test_full_autologin_flow(self, test_user_id):
        """Test complete auto-login flow from start to dashboard"""
        
        # Step 1: User opens dashboard with start parameter
        response = client.get(f"/dashboard?start={test_user_id}")
        assert response.status_code == 200
        
        # Step 2: JS makes direct-login request
        login_response = client.post(
            "/api/auth/direct-login",
            json={"user_id": test_user_id}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Verify token works with /auth/me
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["user_id"] == test_user_id
        
        print(f"✅ Full auto-login flow test passed for user {test_user_id}")


class TestTokenGeneration:
    """Test JWT token generation and validation"""
    
    def test_token_creation(self, test_user_id):
        """Test JWT token is created correctly"""
        token = create_access_token(test_user_id, is_admin=False)
        
        assert isinstance(token, str)
        assert len(token) > 20
        assert token.count('.') == 2  # JWT format: header.payload.signature
        
        print(f"✅ Token creation test passed")
    
    def test_admin_token(self):
        """Test admin token creation"""
        from coin_params import ADMIN_ID
        
        token = create_access_token(ADMIN_ID, is_admin=True)
        
        # Verify token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] == True
        
        print(f"✅ Admin token test passed")


def test_autologin_health_check():
    """Quick health check for auto-login system"""
    
    print("\n" + "="*60)
    print("AUTO-LOGIN HEALTH CHECK")
    print("="*60)
    
    # Test 1: API is accessible
    response = client.get("/health")
    assert response.status_code == 200
    print("✅ API is accessible")
    
    # Test 2: Auth endpoints exist
    response = client.get("/api/docs")
    assert response.status_code == 200
    print("✅ API docs accessible")
    
    # Test 3: Dashboard is accessible
    response = client.get("/dashboard")
    assert response.status_code == 200
    print("✅ Dashboard accessible")
    
    print("="*60)
    print("HEALTH CHECK COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

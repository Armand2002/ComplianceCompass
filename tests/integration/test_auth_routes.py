# tests/integration/test_auth_routes.py
import pytest
from fastapi.testclient import TestClient
import jwt
from unittest.mock import patch

from src.config import settings
from src.utils.password import get_password_hash

class TestAuthRoutes:
    """Test di integrazione per le rotte di autenticazione."""
    
    def test_login_success(self, client, test_user):
        """Verifica che l'endpoint /login funzioni con credenziali corrette."""
        # Arrange
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        
        # Act
        response = client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Verifica che i token siano validi
        access_payload = jwt.decode(
            data["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        assert access_payload["sub"] == test_user.id
        
        refresh_payload = jwt.decode(
            data["refresh_token"],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        assert refresh_payload["sub"] == test_user.id
    
    def test_login_invalid_credentials(self, client):
        """Verifica che l'endpoint /login restituisca 401 con credenziali errate."""
        # Arrange
        login_data = {
            "username": "test@example.com",
            "password": "wrong_password"
        }
        
        # Act
        response = client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Email o password non corrette" in data["detail"]
    
    def test_register_success(self, client):
        """Verifica che l'endpoint /register funzioni con dati validi."""
        # Arrange
        register_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
        
        # Act
        response = client.post(
            "/api/auth/register",
            json=register_data
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == register_data["email"]
        assert data["username"] == register_data["username"]
        assert data["full_name"] == register_data["full_name"]
    
    def test_register_duplicate_email(self, client, test_user):
        """Verifica che l'endpoint /register restituisca 400 con email duplicata."""
        # Arrange
        register_data = {
            "email": "test@example.com",  # Email già esistente
            "username": "uniqueuser",
            "password": "password123",
            "full_name": "Unique User"
        }
        
        # Act
        response = client.post(
            "/api/auth/register",
            json=register_data
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Email già registrata" in data["detail"]
    
    def test_refresh_token_success(self, client, test_user):
        """Verifica che l'endpoint /refresh funzioni con token valido."""
        # Arrange
        from src.utils.jwt import create_refresh_token
        refresh_token = create_refresh_token({"sub": test_user.id})
        
        # Act
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Verifica che l'endpoint /refresh restituisca 401 con token non valido."""
        # Arrange
        invalid_token = "invalid.token.string"
        
        # Act
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": invalid_token}
        )
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Token non valido o scaduto" in data["detail"]
    
    def test_me_authenticated(self, client, user_token):
        """Verifica che l'endpoint /me restituisca i dati dell'utente autenticato."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get(
            "/api/auth/me",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
    
    def test_me_unauthenticated(self, client):
        """Verifica che l'endpoint /me restituisca 401 senza token."""
        # Act
        response = client.get("/api/auth/me")
        
        # Assert
        assert response.status_code == 401
    
    def test_change_password_success(self, client, user_token, test_user, db):
        """Verifica che l'endpoint /change-password funzioni con password corretta."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "current_password": "password123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        # Act
        response = client.post(
            "/api/auth/change-password",
            json=password_data,
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Password cambiata con successo" in data["message"]
        
        # Ripristina la password originale per altri test
        from src.utils.password import get_password_hash
        test_user.hashed_password = get_password_hash("password123")
        db.commit()
    
    def test_change_password_mismatch(self, client, user_token):
        """Verifica che /change-password restituisca 400 se le password non corrispondono."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "current_password": "password123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword"  # Non corrisponde
        }
        
        # Act
        response = client.post(
            "/api/auth/change-password",
            json=password_data,
            headers=headers
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Le password non corrispondono" in data["detail"]
    
    def test_request_password_reset(self, client, test_user):
        """Verifica che l'endpoint /request-password-reset funzioni."""
        # Arrange
        email_data = {
            "email": "test@example.com"
        }
        
        # Act
        with patch("src.routes.auth_routes.send_password_reset_email") as mock_send:
            response = client.post(
                "/api/auth/request-password-reset",
                json=email_data
            )
            
            # Assert
            assert response.status_code == 200
            # Verifica che sia stato chiamato il servizio di invio email
            mock_send.assert_called_once()
    
    def test_reset_password_success(self, client, test_user, db):
        """Verifica che l'endpoint /reset-password funzioni con token valido."""
        # Arrange
        from src.utils.token import generate_verification_token
        token = generate_verification_token(test_user.id)
        
        reset_data = {
            "token": token,
            "new_password": "resetpassword123",
            "confirm_password": "resetpassword123"
        }
        
        # Act
        with patch("src.routes.auth_routes.verify_verification_token") as mock_verify:
            # Simula un token valido
            mock_verify.return_value = test_user.id
            
            response = client.post(
                "/api/auth/reset-password",
                json=reset_data
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "Password resettata con successo" in data["message"]
        
        # Ripristina la password originale per altri test
        test_user.hashed_password = get_password_hash("password123")
        db.commit()
    
    def test_reset_password_invalid_token(self, client):
        """Verifica che /reset-password restituisca 400 con token non valido."""
        # Arrange
        reset_data = {
            "token": "invalid.token",
            "new_password": "resetpassword123",
            "confirm_password": "resetpassword123"
        }
        
        # Act
        with patch("src.routes.auth_routes.verify_verification_token") as mock_verify:
            # Simula un token non valido
            mock_verify.return_value = None
            
            response = client.post(
                "/api/auth/reset-password",
                json=reset_data
            )
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Token non valido o scaduto" in data["detail"]
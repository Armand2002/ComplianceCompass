# tests/unit/test_jwt_utils.py
import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from src.utils.jwt import (
    create_access_token,
    decode_token,
    create_refresh_token,
    verify_token
)
from src.config import settings

class TestJWTUtils:
    """Test per le funzioni di gestione JWT."""
    
    def test_create_access_token(self):
        """Verifica che create_access_token generi un token valido."""
        # Arrange
        data = {"sub": 123, "role": "admin"}
        
        # Act
        token = create_access_token(data)
        
        # Assert
        assert token is not None
        
        # Verifica che il token sia decodificabile
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload["sub"] == 123
        assert payload["role"] == "admin"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_create_access_token_with_expiry(self):
        """Verifica che create_access_token rispetti l'expiry personalizzato."""
        # Arrange
        data = {"sub": 123}
        expires_delta = timedelta(minutes=5)
        
        # Act
        token = create_access_token(data, expires_delta)
        
        # Assert
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verifica che l'expiry sia vicino a 5 minuti nel futuro
        expiry = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (expiry - now).total_seconds() / 60  # Differenza in minuti
        
        assert 4.9 <= time_diff <= 5.1  # Tolleranza di 6 secondi
    
    def test_decode_token_valid(self):
        """Verifica che decode_token funzioni con token valido."""
        # Arrange
        data = {"sub": 123, "custom": "value"}
        token = jwt.encode(
            data, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Act
        payload = decode_token(token)
        
        # Assert
        assert payload is not None
        assert payload["sub"] == 123
        assert payload["custom"] == "value"
    
    def test_decode_token_invalid(self):
        """Verifica che decode_token sollevi un'eccezione con token non valido."""
        # Arrange
        invalid_token = "invalid.token.string"
        
        # Act & Assert
        with pytest.raises(JWTError):
            decode_token(invalid_token)
    
    def test_create_refresh_token(self):
        """Verifica che create_refresh_token generi un token valido con tipo refresh."""
        # Arrange
        data = {"sub": 123}
        
        # Act
        token = create_refresh_token(data)
        
        # Assert
        assert token is not None
        
        # Verifica che il token sia decodificabile
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload["sub"] == 123
        assert payload["token_type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_create_refresh_token_with_expiry(self):
        """Verifica che create_refresh_token rispetti l'expiry personalizzato."""
        # Arrange
        data = {"sub": 123}
        expires_delta = timedelta(days=1)
        
        # Act
        token = create_refresh_token(data, expires_delta)
        
        # Assert
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verifica che l'expiry sia vicino a 1 giorno nel futuro
        expiry = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (expiry - now).total_seconds() / (60 * 60 * 24)  # Differenza in giorni
        
        assert 0.9 <= time_diff <= 1.1  # Tolleranza di ~2.4 ore
    
    def test_verify_token_valid(self):
        """Verifica che verify_token restituisca i dati con token valido."""
        # Arrange
        data = {"sub": 123, "custom": "value"}
        token = jwt.encode(
            data, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Act
        payload = verify_token(token)
        
        # Assert
        assert payload is not None
        assert payload["sub"] == 123
        assert payload["custom"] == "value"
    
    def test_verify_token_invalid(self):
        """Verifica che verify_token restituisca None con token non valido."""
        # Arrange
        invalid_token = "invalid.token.string"
        
        # Act
        result = verify_token(invalid_token)
        
        # Assert
        assert result is None
    
    def test_verify_token_expired(self):
        """Verifica che verify_token restituisca None con token scaduto."""
        # Arrange
        data = {"sub": 123, "exp": datetime.utcnow() - timedelta(hours=1)}
        token = jwt.encode(
            data, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Act
        result = verify_token(token)
        
        # Assert
        assert result is None
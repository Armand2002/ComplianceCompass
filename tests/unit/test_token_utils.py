# tests/unit/test_token_utils.py
import pytest
from datetime import datetime, timedelta
import jwt

from src.utils.token import generate_verification_token, verify_verification_token
from src.config import settings

class TestTokenUtils:
    """Test per le funzioni di gestione dei token di verifica."""
    
    def test_generate_verification_token(self):
        """Verifica che generate_verification_token generi un token valido."""
        # Arrange
        user_id = 123
        
        # Act
        token = generate_verification_token(user_id)
        
        # Assert
        assert token is not None
        
        # Verifica che il token sia decodificabile
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        assert payload["sub"] == user_id
        assert payload["type"] == "verification"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_generate_verification_token_with_expiry(self):
        """Verifica che generate_verification_token rispetti l'expiry personalizzato."""
        # Arrange
        user_id = 123
        expiration_hours = 48
        
        # Act
        token = generate_verification_token(user_id, expiration_hours)
        
        # Assert
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Verifica che l'expiry sia vicino a 48 ore nel futuro
        expiry = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (expiry - now).total_seconds() / (60 * 60)  # Differenza in ore
        
        assert 47.9 <= time_diff <= 48.1  # Tolleranza di ~6 minuti
    
    def test_verify_verification_token_valid(self):
        """Verifica che verify_verification_token restituisca l'ID utente con token valido."""
        # Arrange
        user_id = 123
        token = generate_verification_token(user_id)
        
        # Act
        result = verify_verification_token(token)
        
        # Assert
        assert result == user_id
    
    def test_verify_verification_token_invalid(self):
        """Verifica che verify_verification_token restituisca None con token non valido."""
        # Arrange
        invalid_token = "invalid.token.string"
        
        # Act
        result = verify_verification_token(invalid_token)
        
        # Assert
        assert result is None
    
    def test_verify_verification_token_expired(self):
        """Verifica che verify_verification_token restituisca None con token scaduto."""
        # Arrange
        user_id = 123
        # Crea un token manualmente con una data di scadenza nel passato
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() - timedelta(hours=1),
            "type": "verification",
            "jti": "test_jti",
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        # Act
        result = verify_verification_token(token)
        
        # Assert
        assert result is None
    
    def test_verify_verification_token_wrong_type(self):
        """Verifica che verify_verification_token restituisca None con token di tipo sbagliato."""
        # Arrange
        user_id = 123
        # Crea un token manualmente con tipo diverso da "verification"
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "type": "access",  # Tipo sbagliato
            "jti": "test_jti",
            "iat": datetime.utcnow()
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        # Act
        result = verify_verification_token(token)
        
        # Assert
        assert result is None
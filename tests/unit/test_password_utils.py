# tests/unit/test_password_utils.py
import pytest
from src.utils.password import get_password_hash, verify_password

class TestPasswordUtils:
    """Test per le funzioni di gestione delle password."""
    
    def test_get_password_hash(self):
        """Verifica che get_password_hash generi un hash diverso dalla password originale."""
        # Arrange
        password = "test_password123"
        
        # Act
        hashed = get_password_hash(password)
        
        # Assert
        assert hashed != password
        assert len(hashed) > len(password)
        assert hashed.startswith("$2")  # Formato bcrypt
    
    def test_get_password_hash_different_for_same_password(self):
        """Verifica che get_password_hash generi hash diversi per la stessa password."""
        # Arrange
        password = "test_password123"
        
        # Act
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Assert
        assert hash1 != hash2  # I salt sono casuali, quindi gli hash devono essere diversi
    
    def test_verify_password_correct(self):
        """Verifica che verify_password restituisca True per password corretta."""
        # Arrange
        password = "test_password123"
        hashed = get_password_hash(password)
        
        # Act
        result = verify_password(password, hashed)
        
        # Assert
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Verifica che verify_password restituisca False per password errata."""
        # Arrange
        password = "test_password123"
        wrong_password = "wrong_password123"
        hashed = get_password_hash(password)
        
        # Act
        result = verify_password(wrong_password, hashed)
        
        # Assert
        assert result is False
    
    def test_verify_password_case_sensitive(self):
        """Verifica che verify_password sia case-sensitive."""
        # Arrange
        password = "Test_Password123"
        wrong_case = "test_password123"
        hashed = get_password_hash(password)
        
        # Act
        result = verify_password(wrong_case, hashed)
        
        # Assert
        assert result is False
# tests/unit/test_auth_middleware.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from datetime import datetime

from src.middleware.auth_middleware import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_editor_user,
    check_permission
)
from src.models.user_model import User, UserRole


class TestAuthMiddleware:
    """Test per le funzioni di middleware di autenticazione."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, db, test_user):
        """Verifica che get_current_user restituisca l'utente con token valido."""
        # Arrange
        valid_token = "valid.token.string"
        
        # Act
        with patch("src.middleware.auth_middleware.decode_token") as mock_decode:
            # Mock della decodifica token
            mock_decode.return_value = {"sub": test_user.id}
            
            result = await get_current_user(valid_token, db)
        
        # Assert
        assert result is not None
        assert result.id == test_user.id
        assert result.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db):
        """Verifica che get_current_user sollevi un'eccezione con token non valido."""
        # Arrange
        invalid_token = "invalid.token.string"
        
        # Act & Assert
        with patch("src.middleware.auth_middleware.decode_token") as mock_decode:
            # Simula un errore di decodifica
            mock_decode.side_effect = Exception("Invalid token")
            
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(invalid_token, db)
            
            assert excinfo.value.status_code == 401
            assert "Credenziali non valide" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, db):
        """Verifica che get_current_user sollevi un'eccezione con user_id inesistente."""
        # Arrange
        valid_token = "valid.token.string"
        nonexistent_id = 9999  # ID utente che non esiste
        
        # Act & Assert
        with patch("src.middleware.auth_middleware.decode_token") as mock_decode:
            # Mock della decodifica token
            mock_decode.return_value = {"sub": nonexistent_id}
            
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(valid_token, db)
            
            assert excinfo.value.status_code == 401
            assert "Credenziali non valide" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self, db, test_user):
        """Verifica che get_current_user sollevi un'eccezione con utente inattivo."""
        # Arrange
        valid_token = "valid.token.string"
        
        # Disattiva l'utente
        test_user.is_active = False
        db.commit()
        
        # Act & Assert
        with patch("src.middleware.auth_middleware.decode_token") as mock_decode:
            # Mock della decodifica token
            mock_decode.return_value = {"sub": test_user.id}
            
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(valid_token, db)
            
            assert excinfo.value.status_code == 403
            assert "Utente disattivato" in excinfo.value.detail
        
        # Ripristina lo stato attivo per altri test
        test_user.is_active = True
        db.commit()
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_active(self):
        """Verifica che get_current_active_user passi con utente attivo."""
        # Arrange
        mock_user = MagicMock()
        mock_user.is_active = True
        
        # Act
        result = await get_current_active_user(mock_user)
        
        # Assert
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        """Verifica che get_current_active_user sollevi un'eccezione con utente inattivo."""
        # Arrange
        mock_user = MagicMock()
        mock_user.is_active = False
        
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_active_user(mock_user)
        
        assert excinfo.value.status_code == 403
        assert "Utente disattivato" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_admin_user_admin(self):
        """Verifica che get_current_admin_user passi con admin."""
        # Arrange
        mock_user = MagicMock()
        mock_user.is_admin = True
        
        # Act
        result = await get_current_admin_user(mock_user)
        
        # Assert
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_get_current_admin_user_non_admin(self):
        """Verifica che get_current_admin_user sollevi un'eccezione con non-admin."""
        # Arrange
        mock_user = MagicMock()
        mock_user.is_admin = False
        
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_admin_user(mock_user)
        
        assert excinfo.value.status_code == 403
        assert "Accesso riservato agli amministratori" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_editor_user_editor(self):
        """Verifica che get_current_editor_user passi con editor."""
        # Arrange
        mock_user = MagicMock()
        mock_user.is_editor = True
        
        # Act
        result = await get_current_editor_user(mock_user)
        
        # Assert
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_get_current_editor_user_non_editor(self):
        """Verifica che get_current_editor_user sollevi un'eccezione con non-editor."""
        # Arrange
        mock_user = MagicMock()
        mock_user.is_editor = False
        
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_editor_user(mock_user)
        
        assert excinfo.value.status_code == 403
        assert "Accesso riservato agli editor" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_check_permission_admin_all_perms(self):
        """Verifica che check_permission restituisca True per admin con qualsiasi permesso."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN
        
        # Act & Assert
        for perm in ["read", "write", "delete", "admin"]:
            result = await check_permission(mock_user, perm)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_permission_editor_limited_perms(self):
        """Verifica che check_permission funzioni correttamente per editor."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.EDITOR
        
        # Act & Assert
        # Permessi che dovrebbero essere True
        for perm in ["read", "write", "delete"]:
            result = await check_permission(mock_user, perm)
            assert result is True
        
        # Permessi che dovrebbero essere False
        result = await check_permission(mock_user, "admin")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_permission_viewer_read_only(self):
        """Verifica che check_permission funzioni correttamente per viewer."""
        # Arrange
        mock_user = MagicMock()
        mock_user.role = UserRole.VIEWER
        
        # Act & Assert
        # Permesso che dovrebbe essere True
        result = await check_permission(mock_user, "read")
        assert result is True
        
        # Permessi che dovrebbero essere False
        for perm in ["write", "delete", "admin"]:
            result = await check_permission(mock_user, perm)
            assert result is False
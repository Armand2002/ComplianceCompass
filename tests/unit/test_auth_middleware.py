# tests/unit/test_auth_middleware.py
"""
Test unitari per middleware di autenticazione e autorizzazione.

Verifica dettagliata di tutti i casi d'uso di autenticazione
e controlli di autorizzazione.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
import jwt
from datetime import datetime, timedelta

from src.middleware.auth_middleware import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_editor_user,
    permission_required,
    check_permission
)
from src.models.user_model import User, UserRole
from src.config import settings

@pytest.mark.parametrize("user_active,expected_success", [
    (True, True),
    (False, False)
])
@pytest.mark.asyncio
async def test_get_current_active_user(user_active, expected_success):
    """Verifica che get_current_active_user consideri attivazione."""
    # Prepara utente mock
    mock_user = MagicMock(spec=User)
    mock_user.is_active = user_active
    
    if expected_success:
        # Dovrebbe passare se l'utente è attivo
        result = await get_current_active_user(mock_user)
        assert result == mock_user
    else:
        # Dovrebbe fallire se l'utente non è attivo
        with pytest.raises(HTTPException) as excinfo:
            await get_current_active_user(mock_user)
        assert excinfo.value.status_code == 403
        assert "Utente disattivato" in excinfo.value.detail

@pytest.mark.parametrize("user_role,expected_success", [
    (UserRole.ADMIN, True),
    (UserRole.EDITOR, False),
    (UserRole.VIEWER, False)
])
@pytest.mark.asyncio
async def test_get_current_admin_user(user_role, expected_success):
    """Verifica che get_current_admin_user permetta solo admin."""
    # Prepara utente mock
    mock_user = MagicMock(spec=User)
    mock_user.role = user_role
    mock_user.is_admin = user_role == UserRole.ADMIN
    
    if expected_success:
        # Dovrebbe passare se l'utente è admin
        result = await get_current_admin_user(mock_user)
        assert result == mock_user
    else:
        # Dovrebbe fallire se l'utente non è admin
        with pytest.raises(HTTPException) as excinfo:
            await get_current_admin_user(mock_user)
        assert excinfo.value.status_code == 403
        assert "Accesso riservato agli amministratori" in excinfo.value.detail

@pytest.mark.parametrize("user_role,expected_success", [
    (UserRole.ADMIN, True),
    (UserRole.EDITOR, True),
    (UserRole.VIEWER, False)
])
@pytest.mark.asyncio
async def test_get_current_editor_user(user_role, expected_success):
    """Verifica che get_current_editor_user permetta admin ed editor."""
    # Prepara utente mock
    mock_user = MagicMock(spec=User)
    mock_user.role = user_role
    mock_user.is_editor = user_role in [UserRole.ADMIN, UserRole.EDITOR]
    
    if expected_success:
        # Dovrebbe passare se l'utente è admin o editor
        result = await get_current_editor_user(mock_user)
        assert result == mock_user
    else:
        # Dovrebbe fallire se l'utente non è né admin né editor
        with pytest.raises(HTTPException) as excinfo:
            await get_current_editor_user(mock_user)
        assert excinfo.value.status_code == 403
        assert "Accesso riservato agli editor" in excinfo.value.detail

@pytest.mark.parametrize("role_permission", indirect=True)
@pytest.mark.asyncio
async def test_check_permission(role_permission):
    """Verifica check_permission per varie combinazioni ruolo-permesso."""
    role, permission, expected = role_permission
    
    # Prepara utente mock
    mock_user = MagicMock(spec=User)
    mock_user.role = role
    
    # Verifica permesso
    result = await check_permission(mock_user, permission)
    assert result is expected

@pytest.mark.asyncio
async def test_get_current_user_valid_token(db_session, mocker):
    """Verifica che get_current_user restituisca utente con token valido."""
    # Mock per decode_token
    mock_decode = mocker.patch('src.middleware.auth_middleware.decode_token')
    mock_decode.return_value = {"sub": "1", "role": "admin"}
    
    # Mock per query database
    mock_user = mocker.MagicMock(spec=User)
    mock_user.id = 1
    mock_user.is_active = True
    
    mock_query = mocker.MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user
    mocker.patch.object(db_session, 'query', return_value=mock_query)
    
    # Esegui funzione da testare
    result = await get_current_user("valid_token", db_session)
    
    # Verifica risultato
    assert result == mock_user
    mock_decode.assert_called_once_with("valid_token")
    mock_query.filter.assert_called_once()
    assert mock_user.last_login is not None

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session, mocker):
    """Verifica che get_current_user sollevi eccezione con token non valido."""
    # Mock per decode_token che solleva eccezione
    mock_decode = mocker.patch('src.middleware.auth_middleware.decode_token')
    mock_decode.side_effect = jwt.JWTError("Invalid token")
    
    # Esegui funzione da testare
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("invalid_token", db_session)
    
    # Verifica eccezione
    assert excinfo.value.status_code == 401
    assert "Credenziali non valide" in excinfo.value.detail
    mock_decode.assert_called_once_with("invalid_token")

@pytest.mark.asyncio
async def test_get_current_user_missing_sub(db_session, mocker):
    """Verifica che get_current_user gestisca token senza 'sub'."""
    # Mock per decode_token
    mock_decode = mocker.patch('src.middleware.auth_middleware.decode_token')
    mock_decode.return_value = {"role": "admin"}  # Manca 'sub'
    
    # Esegui funzione da testare
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("incomplete_token", db_session)
    
    # Verifica eccezione
    assert excinfo.value.status_code == 401
    assert "Credenziali non valide" in excinfo.value.detail
    mock_decode.assert_called_once_with("incomplete_token")

@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(db_session, mocker):
    """Verifica che get_current_user gestisca utente inesistente."""
    # Mock per decode_token
    mock_decode = mocker.patch('src.middleware.auth_middleware.decode_token')
    mock_decode.return_value = {"sub": "999", "role": "admin"}
    
    # Mock per query database che non trova utenti
    mock_query = mocker.MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mocker.patch.object(db_session, 'query', return_value=mock_query)
    
    # Esegui funzione da testare
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("valid_token", db_session)
    
    # Verifica eccezione
    assert excinfo.value.status_code == 401
    assert "Credenziali non valide" in excinfo.value.detail
    mock_decode.assert_called_once_with("valid_token")
    mock_query.filter.assert_called_once()
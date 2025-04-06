# src/utils/jwt.py
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt 
import uuid
import secrets
import logging
from src.config import settings

logger = logging.getLogger(__name__)

# Path file delle chiavi JWT
JWT_KEYS_FILE = "keys/jwt_keys.json"

# Configurazioni JWT
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

class JWTKeyManager:
    """
    Gestisce le chiavi JWT, inclusa la rotazione.
    
    Implementa il pattern Singleton per assicurare una gestione centralizzata.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JWTKeyManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._keys = {}
        self._active_key_id = None
        self._load_keys()
        self._initialized = True
    
    def _load_keys(self):
        """Carica le chiavi JWT dal file o ne crea di nuove."""
        try:
            if os.path.exists(JWT_KEYS_FILE):
                with open(JWT_KEYS_FILE, 'r') as f:
                    key_data = json.load(f)
                    
                self._keys = key_data.get("keys", {})
                self._active_key_id = key_data.get("active_key")
                
                # Verifica validità
                if not self._active_key_id or self._active_key_id not in self._keys:
                    logger.warning("JWT key file exists but has invalid data. Creating new keys.")
                    self._create_initial_keys()
            else:
                logger.info("JWT key file not found. Creating initial keys.")
                self._create_initial_keys()
        except Exception as e:
            logger.error(f"Error loading JWT keys: {str(e)}. Using fallback key.")
            self._create_initial_keys()
    
    def _create_initial_keys(self):
        """Crea le chiavi JWT iniziali."""
        key_id = str(uuid.uuid4())
        key_value = secrets.token_hex(32)
        
        self._keys = {key_id: key_value}
        self._active_key_id = key_id
        
        self._save_keys()
    
    def _save_keys(self):
        """Salva le chiavi JWT su file."""
        try:
            # Crea la directory se non esiste
            os.makedirs(os.path.dirname(JWT_KEYS_FILE), exist_ok=True)
            
            with open(JWT_KEYS_FILE, 'w') as f:
                json.dump({
                    "keys": self._keys,
                    "active_key": self._active_key_id,
                    "updated_at": datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving JWT keys: {str(e)}")
    
    def get_active_key(self) -> str:
        """
        Restituisce la chiave JWT attiva.
        
        Returns:
            str: Chiave JWT attiva
        """
        if not self._active_key_id or self._active_key_id not in self._keys:
            logger.error("No active JWT key found. Using SECRET_KEY as fallback.")
            return settings.SECRET_KEY
            
        return self._keys[self._active_key_id]
    
    def get_key_by_id(self, key_id: str) -> Optional[str]:
        """
        Restituisce una chiave JWT specifica.
        
        Args:
            key_id (str): ID della chiave
            
        Returns:
            Optional[str]: Chiave JWT o None se non trovata
        """
        return self._keys.get(key_id)
    
    def rotate_keys(self) -> Dict[str, Any]:
        """
        Ruota le chiavi JWT (mantiene vecchie chiavi per validazione token esistenti).
        
        Returns:
            Dict[str, Any]: Informazioni sulla rotazione
        """
        # Genera nuova chiave
        new_key_id = str(uuid.uuid4())
        new_key_value = secrets.token_hex(32)
        
        # Salva vecchio ID chiave
        old_key_id = self._active_key_id
        
        # Aggiungi nuova chiave e aggiorna attiva
        self._keys[new_key_id] = new_key_value
        self._active_key_id = new_key_id
        
        # Limita numero di chiavi (mantieni max 3 chiavi)
        if len(self._keys) > 3:
            # Rimuovi chiavi più vecchie (escluse nuova e vecchia attiva)
            keys_to_keep = [new_key_id, old_key_id]
            keys_to_remove = [k for k in self._keys.keys() if k not in keys_to_keep]
            
            if keys_to_remove:
                oldest_key = keys_to_remove[0]
                del self._keys[oldest_key]
                logger.info(f"Removed old JWT key: {oldest_key}")
        
        # Salva modifiche
        self._save_keys()
        
        logger.info(f"JWT keys rotated. New active key: {new_key_id}")
        
        return {
            "status": "success",
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_keys_info(self) -> Dict[str, Any]:
        """
        Ottiene informazioni sulle chiavi JWT (senza esporre i valori).
        
        Returns:
            Dict[str, Any]: Informazioni sulle chiavi
        """
        return {
            "active_key_id": self._active_key_id,
            "key_count": len(self._keys),
            "key_ids": list(self._keys.keys())
        }

# Istanza singleton del key manager
key_manager = JWTKeyManager()

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT per l'autenticazione.
    
    Args:
        data (dict): Dati da includere nel token
        expires_delta (timedelta, optional): Durata validità token
        
    Returns:
        str: Token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Aggiunge claims standard
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(8),  # JWT ID per possibile invalidazione token
        "kid": key_manager._active_key_id  # Key ID per verificare con chiave corretta
    })
    
    # Usa la chiave attiva per firmare
    secret_key = key_manager.get_active_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica un token JWT.
    
    Args:
        token (str): Token JWT
        
    Returns:
        dict: Dati contenuti nel token
        
    Raises:
        JWTError: Se il token non è valido
    """
    try:
        # Prima verifica se il token contiene un key ID
        unverified = jwt.decode(
            token, 
            options={"verify_signature": False}
        )
        
        # Se presente key ID, usa la chiave corrispondente
        if "kid" in unverified:
            key_id = unverified["kid"]
            secret_key = key_manager.get_key_by_id(key_id)
            
            # Se chiave non trovata, prova con chiave attiva
            if not secret_key:
                logger.warning(f"JWT key {key_id} not found, trying active key")
                secret_key = key_manager.get_active_key()
        else:
            # Altrimenti usa chiave attiva
            secret_key = key_manager.get_active_key()
        
        # Decodifica con la chiave appropriata
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=[ALGORITHM]
        )
        
        return payload
    except JWTError as e:
        # Se fallisce, prova con SECRET_KEY (fallback per compatibilità)
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[ALGORITHM]
            )
            return payload
        except JWTError:
            # Rilancia l'eccezione originale
            raise e

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un refresh token JWT per l'autenticazione persistente.
    
    Args:
        data (dict): Dati da includere nel token
        expires_delta (timedelta, optional): Durata validità token
        
    Returns:
        str: Refresh token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(8),
        "token_type": "refresh",
        "kid": key_manager._active_key_id
    })
    
    secret_key = key_manager.get_active_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica un token JWT e restituisce i dati se valido.
    
    Args:
        token (str): Token JWT
        
    Returns:
        Optional[Dict[str, Any]]: Dati dal token o None se non valido
    """
    try:
        return decode_token(token)
    except JWTError:
        return None
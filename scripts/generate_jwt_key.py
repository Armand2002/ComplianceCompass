#!/usr/bin/env python
"""
Genera una chiave segreta per JWT.
"""
import os
import secrets

def generate_key(length=32):
    """Genera una chiave sicura per JWT."""
    return secrets.token_hex(length)

if __name__ == "__main__":
    key = generate_key()
    print(f"JWT_SECRET_KEY generata: {key}")
    
    # Aggiungi la chiave al file .env se esiste e non ha già una JWT_SECRET_KEY
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            content = f.read()
        
        if "JWT_SECRET_KEY=" not in content:
            with open(env_file, "a") as f:
                f.write(f"\nJWT_SECRET_KEY={key}\n")
            print(f"Chiave aggiunta al file {env_file}")
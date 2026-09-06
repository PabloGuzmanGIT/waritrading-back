"""Hashing de contraseñas.

Usa bcrypt directamente (passlib 1.7.4 está roto con bcrypt >= 4.1 en Python 3.13+).
`verify_password` acepta hashes bcrypt y, de forma transitoria, valores en texto
plano heredados de la base semilla anterior; el endpoint de login re-hashea esos
valores en el primer inicio de sesión exitoso.
"""

import hmac

import bcrypt

# bcrypt trunca a 72 bytes; lo hacemos explícito para no depender del error.
_MAX_BYTES = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def _is_bcrypt_hash(value: str) -> bool:
    return value.startswith(("$2a$", "$2b$", "$2y$"))


def verify_password(plain: str, stored: str) -> bool:
    """True si `plain` corresponde a `stored` (hash bcrypt o texto plano heredado)."""
    if not stored:
        return False
    if _is_bcrypt_hash(stored):
        try:
            return bcrypt.checkpw(plain.encode("utf-8")[:_MAX_BYTES], stored.encode("utf-8"))
        except (ValueError, TypeError):
            return False
    # Valor heredado en texto plano: comparación en tiempo constante.
    return hmac.compare_digest(plain, stored)


def needs_rehash(stored: str) -> bool:
    """True si el valor guardado no es un hash bcrypt y debe actualizarse."""
    return not _is_bcrypt_hash(stored or "")

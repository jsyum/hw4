"""Password hashing and session tokens.

The seed database already holds accounts, so the hashing here is not a free
choice — it has to reproduce the existing format exactly or the seeded users
could never log in. Reverse-engineered from the seed rows:

    pbkdf2_sha256$<salt>$<64 hex chars>

PBKDF2-HMAC-SHA256, 120,000 iterations, the salt taken as ASCII bytes, and a
32-byte derived key stored as hex. New accounts are written in the same format
with a fresh random salt, so seeded and new users are indistinguishable to the
verifier.

Plaintext passwords are never stored and never logged.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time

# Must match the seed database. Changing it would lock out every existing user.
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SALT_BYTES = 8  # 16 hex characters, matching the seed rows
MIN_PASSWORD_LENGTH = 8

SESSION_TTL_SECONDS = 7 * 24 * 60 * 60  # a week


# --------------------------------------------------------------------------
# Passwords
# --------------------------------------------------------------------------

def _derive(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), ITERATIONS
    ).hex()


def hash_password(password: str) -> str:
    """Hash a new password in the seed database's format."""
    salt = secrets.token_hex(SALT_BYTES)
    return f"{ALGORITHM}${salt}${_derive(password, salt)}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against a stored hash. False on any malformed value."""
    try:
        algorithm, salt, expected = stored.split("$")
    except (ValueError, AttributeError):
        return False
    if algorithm != ALGORITHM:
        return False
    # compare_digest, not ==, so the comparison does not leak timing information.
    return hmac.compare_digest(_derive(password, salt), expected)


# --------------------------------------------------------------------------
# Session tokens
# --------------------------------------------------------------------------

def _secret() -> bytes:
    """Signing key for session tokens.

    Set SESSION_SECRET in .env (which is gitignored). Without one the server
    generates a throwaway key at import, which works but logs everybody out
    whenever the backend restarts.
    """
    value = os.getenv("SESSION_SECRET", "").strip()
    if value:
        return value.encode("utf-8")
    return _EPHEMERAL_SECRET


_EPHEMERAL_SECRET = secrets.token_bytes(32)


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def issue_token(user_id: int) -> str:
    """Signed, stateless token: <user_id>.<expiry>.<signature>.

    The payload is readable by the browser — that is fine, it holds nothing
    private. The signature is what makes it unforgeable.
    """
    payload = f"{user_id}.{int(time.time()) + SESSION_TTL_SECONDS}"
    signature = hmac.new(_secret(), payload.encode("ascii"), hashlib.sha256).digest()
    return f"{payload}.{_b64(signature)}"


def read_token(token: str | None) -> int | None:
    """Return the user id in a valid, unexpired token, else None."""
    if not token:
        return None
    try:
        user_id_text, expiry_text, signature = token.rsplit(".", 2)
        payload = f"{user_id_text}.{expiry_text}"
        expected = hmac.new(_secret(), payload.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_unb64(signature), expected):
            return None
        if int(expiry_text) < time.time():
            return None
        return int(user_id_text)
    except (ValueError, TypeError, AttributeError):
        return None

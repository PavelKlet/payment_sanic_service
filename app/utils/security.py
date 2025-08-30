import hashlib
from config import settings
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def compute_signature(
    *, account_id: int, amount: float, transaction_id: str, user_id: int
) -> str:
    """
    Compute a SHA-256 signature for payment validation.

    Args:
        account_id (int): ID of the account.
        amount (float): Payment amount.
        transaction_id (str): Unique transaction ID.
        user_id (int): ID of the user.

    Returns:
        str: Hexadecimal SHA-256 signature string.
    """
    raw = f"{account_id}{amount}{transaction_id}{user_id}{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain (str): Plaintext password to verify.
        hashed (str): Hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd.verify(plain, hashed)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): Plaintext password.

    Returns:
        str: Hashed password string suitable for storage.
    """
    return pwd.hash(password)

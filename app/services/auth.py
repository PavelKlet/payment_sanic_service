from repositories.user import UserRepo
from utils.auth import create_access_token
from utils.security import verify_password


class AuthService:
    """
    Service responsible for authenticating users and generating access tokens.

    This service uses the User repository to validate credentials and issue JWTs.
    """

    def __init__(self, uow):
        self.uow = uow
        self.uow.set_repository("user", UserRepo)

    async def authenticate(self, email: str, password: str):
        """
        Authenticate a user by email and password.

        Args:
            email (str): User's email address.
            password (str): Plain text password to verify.

        Returns:
            str | None: JWT access token if authentication succeeds, otherwise None.
        """
        user = await self.uow.user.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        token = create_access_token(
            {"sub": str(user.id), "is_admin": bool(user.is_admin)}
        )
        return token

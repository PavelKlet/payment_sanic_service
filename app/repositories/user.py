from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from sqlalchemy.orm import selectinload


class UserRepo:
    """
    Repository for managing User entities in the database.

    Provides methods to create, retrieve, list, and delete users,
    including preloading related accounts when listing all users.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The User instance if found, otherwise None.
        """
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email (str): Email address of the user.

        Returns:
            User | None: The User instance if found, otherwise None.
        """
        q = await self.session.execute(select(User).where(User.email == email))
        return q.scalar_one_or_none()

    async def create(
        self,
        email: str,
        full_name: str | None,
        password_hash: str,
        is_admin: bool = False,
    ) -> User:
        """
        Create a new user record in the database.

        Args:
            email (str): Email address of the user.
            full_name (str | None): Full name of the user.
            password_hash (str): Hashed password for authentication.
            is_admin (bool): Whether the user has admin privileges.

        Returns:
            User: The newly created User instance.
        """
        user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            is_admin=is_admin,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def list_all(self) -> list[User]:
        """
        Retrieve all users, preloading their accounts.

        Returns:
            list[User]: List of all User instances with related accounts loaded.
        """
        q = await self.session.execute(
            select(User).options(selectinload(User.accounts))
        )
        return q.scalars().all()

    async def delete(self, user: User) -> None:
        """
        Delete a user from the database.

        Args:
            user (User): The User instance to delete.
        """
        await self.session.delete(user)

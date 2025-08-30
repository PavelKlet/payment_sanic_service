from typing import Any

from sanic.exceptions import InvalidUsage

from repositories.user import UserRepo
from repositories.account import AccountRepo
from schemas.user import UserOut
from utils.security import hash_password
from utils.other import filter_none_values

from schemas.user import UserWithAccountsOut, AccountOut


class AdminService:

    def __init__(self, uow):
        self.uow = uow
        self.uow.set_repository("user", UserRepo)
        self.uow.set_repository("account", AccountRepo)

    async def create_user(
        self, email: str, full_name: str | None, password: str, is_admin: bool = False
    ) -> UserOut:
        """
        Create a new user.

        Args:
            email (str): Email of the user.
            full_name (str | None): Full name of the user.
            password (str): Plain password for the user.
            is_admin (bool, optional): Whether the user has admin privileges. Defaults to False.

        Raises:
            InvalidUsage: If a user with the given email already exists.

        Returns:
            UserOut: Pydantic schema representing the created user.
        """
        existing = await self.uow.user.get_by_email(email)
        if existing:
            raise InvalidUsage(f"User with email {email} already exists")

        pwd_hash = hash_password(password)
        user = await self.uow.user.create(
            email=email, full_name=full_name, password_hash=pwd_hash, is_admin=is_admin
        )

        await self.uow.commit()

        return UserOut.model_validate(
            {"id": user.id, "email": user.email, "full_name": user.full_name}
        )

    async def update_user(
        self, user_id: int, update_data: dict[str, Any]
    ) -> UserOut | None:
        """
        Update an existing user's information.

        Args:
            user_id (int): ID of the user to update.
            update_data (dict[str, Any]): Dictionary of fields to update. Supports 'password'.

        Returns:
            UserOut | None: Updated user schema, or None if the user does not exist.
        """

        user = await self.uow.user.get_by_id(user_id)
        if not user:
            return None

        update_data = filter_none_values(update_data)

        for key, value in update_data.items():
            if key == "password":
                user.password_hash = hash_password(value)
            else:
                setattr(user, key, value)

        await self.uow.commit()
        return UserOut.model_validate(
            {"id": user.id, "email": user.email, "full_name": user.full_name}
        )

    async def list_users(self) -> list[UserWithAccountsOut]:
        """
        Retrieve all users with their associated accounts.

        Returns:
            list[UserWithAccountsOut]: List of users including account information and balances.
        """
        users = await self.uow.user.list_all()
        return [
            UserWithAccountsOut(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                accounts=[
                    AccountOut(id=a.id, balance=float(a.balance)) for a in user.accounts
                ],
            )
            for user in users
        ]

    async def delete_user(self, user_id: int):
        """
        Delete a user by ID.

        Args:
            user_id (int): ID of the user to delete.

        Returns:
            bool: True if deletion was successful, False if user not found.
        """
        user = await self.uow.user.get_by_id(user_id)
        if not user:
            return False
        await self.uow.user.delete(user)
        return True

    async def get_user_accounts(self, user_id: int) -> list[AccountOut]:
        """
        Get all accounts for a specific user as AccountOut schemas.
        """
        accounts = await self.uow.account.list_by_user(user_id)
        return [
            AccountOut.model_validate(
                {"id": a.id, "user_id": a.user_id, "balance": float(a.balance)}
            )
            for a in accounts
        ]

    async def get_current_admin(self, user_id: int) -> UserOut:
        user = await self.uow.user.get_by_id(user_id)
        return UserOut.model_validate(
            {"id": user.id, "email": user.email, "full_name": user.full_name}
        )

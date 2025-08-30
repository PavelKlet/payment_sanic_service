from repositories.user import UserRepo
from repositories.account import AccountRepo
from repositories.payment import PaymentRepo
from schemas.user import UserOut
from schemas.account import AccountOutWithUserId
from schemas.payment import PaymentOut


class UserService:
    """
    Service for managing user-related operations, including retrieving user info,
    accounts, and payments for the authenticated user.
    """

    def __init__(self, uow):
        self.uow = uow
        self.uow.set_repository("user", UserRepo)
        self.uow.set_repository("account", AccountRepo)
        self.uow.set_repository("payment", PaymentRepo)

    async def get_me(self, user_id: int) -> UserOut:
        """
        Retrieve information about the authenticated user.

        Args:
            user_id (int): ID of the authenticated user.

        Returns:
            UserOut: Pydantic schema containing user's ID, email, and full name.
        """
        user = await self.uow.user.get_by_id(user_id)
        return UserOut.model_validate(
            {"id": user.id, "email": user.email, "full_name": user.full_name}
        )

    async def get_my_accounts(self, user_id: int) -> list[AccountOutWithUserId]:
        """
        Get a list of accounts belonging to the authenticated user.

        Args:
            user_id (int): ID of the authenticated user.

        Returns:
            list[AccountOutWithUserId]: List of Pydantic schemas with account ID, user ID, and balance.
        """
        accounts = await self.uow.account.list_by_user(user_id)
        return [
            AccountOutWithUserId.model_validate(
                {"id": a.id, "user_id": a.user_id, "balance": float(a.balance)}
            )
            for a in accounts
        ]

    async def get_my_payments(self, user_id: int) -> list[PaymentOut]:
        """
        Retrieve the list of payments made by the authenticated user.

        Args:
            user_id (int): ID of the authenticated user.

        Returns:
            list[PaymentOut]: List of Pydantic schemas containing payment details,
                              including payment ID, transaction ID, user ID, account ID,
                              and amount.
        """
        payments = await self.uow.payment.list_by_user(user_id)
        return [
            PaymentOut.model_validate(
                {
                    "id": p.id,
                    "transaction_id": p.transaction_id,
                    "user_id": p.user_id,
                    "account_id": p.account_id,
                    "amount": float(p.amount),
                }
            )
            for p in payments
        ]

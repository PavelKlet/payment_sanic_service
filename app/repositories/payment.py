from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.payment import Payment


class PaymentRepo:
    """
    Repository for managing Payment entities in the database.

    This class provides methods to create payments and list payments by user,
    encapsulating direct database access using SQLAlchemy AsyncSession.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, transaction_id: str, user_id: int, account_id: int, amount
    ) -> Payment:
        """
        Creates a new payment record in the database.

        Args:
            transaction_id (str): Unique identifier for the transaction.
            user_id (int): ID of the user making the payment.
            account_id (int): ID of the account associated with the payment.
            amount (decimal.Decimal | float): Amount of the payment.

        Returns:
            Payment: The newly created Payment instance.
        """
        p = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
        )
        self.session.add(p)
        await self.session.flush()
        return p

    async def list_by_user(self, user_id: int) -> list[Payment]:
        """
        Retrieves all payments made by a specific user.

        Args:
            user_id (int): The ID of the user whose payments are to be retrieved.

        Returns:
            list[Payment]: List of Payment instances associated with the user.
        """
        q = await self.session.execute(
            select(Payment).where(Payment.user_id == user_id)
        )
        return q.scalars().all()

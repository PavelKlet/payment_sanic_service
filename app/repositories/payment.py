from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from models.payment import Payment


class PaymentRepo:
    """
    Repository for managing Payment entities in the database.

    This class provides methods to create payments and list payments by user,
    encapsulating direct database access using SQLAlchemy AsyncSession.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_if_not_exists(
            self, transaction_id: str, user_id: int, account_id: int, amount
    ) -> Payment | None:
        stmt = insert(Payment).values(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=Decimal(str(amount))
        ).on_conflict_do_nothing(
            index_elements=['transaction_id']
        ).returning(Payment)

        result = await self.session.execute(stmt)
        payment = result.scalar_one_or_none()
        return payment

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

    async def get_by_transaction_id(self, transaction_id: str) -> Payment | None:
        stmt = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from repositories.user import UserRepo
from repositories.account import AccountRepo
from repositories.payment import PaymentRepo
from utils.security import compute_signature


class PaymentService:
    """
    Service responsible for processing payment webhooks and managing payment records.

    This service verifies the webhook signature, ensures the user and account exist,
    creates new payments, and updates account balances atomically.
    """

    def __init__(self, uow):
        self.uow = uow
        self.uow.set_repository("user", UserRepo)
        self.uow.set_repository("account", AccountRepo)
        self.uow.set_repository("payment", PaymentRepo)

    async def process_webhook(self, data: dict):
        """
        Process an incoming payment webhook.

        Args:
            data (dict): Dictionary containing the webhook payload with keys:
                - account_id (int)
                - amount (float)
                - transaction_id (str)
                - user_id (int)
                - signature (str)

        Raises:
            ValueError: If the signature is invalid.
            LookupError: If the user is not found.

        Returns:
            Payment | None: The created Payment object if successful,
                            None if the payment already exists (duplicate transaction).
        """
        expected = compute_signature(
            account_id=data["account_id"],
            amount=data["amount"],
            transaction_id=data["transaction_id"],
            user_id=data["user_id"],
        )
        if expected != data["signature"]:
            raise ValueError("invalid_signature")

        user = await self.uow.user.get_by_id(data["user_id"])
        if not user:
            raise LookupError("user_not_found")

        account = await self.uow.account.get_account_for_update(data["account_id"])
        if not account:
            account = await self.uow.account.create(
                user_id=user.id, account_id=data["account_id"]
            )

        try:
            payment = await self.uow.payment.create(
                transaction_id=data["transaction_id"],
                user_id=user.id,
                account_id=account.id,
                amount=data["amount"],
            )
            account.balance = (account.balance or Decimal("0")) + Decimal(
                str(data["amount"])
            )
            await self.uow.commit()
            return payment
        except IntegrityError:
            await self.uow.rollback()
            return None

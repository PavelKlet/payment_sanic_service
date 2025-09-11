from decimal import Decimal


from repositories.user import UserRepo
from repositories.account import AccountRepo
from repositories.payment import PaymentRepo
from utils.security import compute_signature
from schemas.payment import PaymentOut


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

        existing_payment = await self.uow.payment.get_by_transaction_id(data["transaction_id"])
        if existing_payment:
            return {
                "message": "duplicate transaction"
            }, 200

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
            account = await self.uow.account.create_or_update(
                user_id=user.id,
                account_id=data["account_id"]
            )

        payment = await self.uow.payment.create_if_not_exists(
            transaction_id=data["transaction_id"],
            user_id=user.id,
            account_id=account.id,
            amount=data["amount"],
        )

        if payment is None:
            await self.uow.rollback()
            return {"message": "duplicate transaction"}, 200

        account.balance = (account.balance or Decimal("0")) + Decimal(str(data["amount"]))
        await self.uow.commit()

        return PaymentOut.model_validate({
            "id": payment.id,
            "transaction_id": payment.transaction_id,
            "user_id": payment.user_id,
            "account_id": payment.account_id,
            "amount": float(payment.amount),
        }).model_dump(), 201



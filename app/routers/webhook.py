from sanic import Blueprint, response
from schemas.payment import WebhookIn
from services.payment import PaymentService
from schemas.payment import PaymentOut

bp = Blueprint("webhook", url_prefix="/webhooks")


@bp.post("/payment")
async def payment_webhook(request):
    """
    Process a payment webhook from an external system.

    Validates the signature, ensures the user and account exist,
    creates a payment record, and updates the account balance.

    Returns:
        201 Created with JSON:
        {
            "id": int,
            "transaction_id": str,
            "user_id": int,
            "account_id": int,
            "amount": float
        }

        200 OK if the transaction is a duplicate:
        {
            "message": "duplicate transaction"
        }

        400 Bad Request if the signature is invalid:
        {
            "message": "invalid signature"
        }

        404 Not Found if the user does not exist:
        {
            "message": "user not found"
        }
    """
    data = WebhookIn.model_validate(request.json or {})
    async with request.ctx.uow:
        svc = PaymentService(request.ctx.uow)
        try:
            result, status = await svc.process_webhook(data.model_dump())
        except ValueError:
            return response.json({"message": "invalid signature"}, status=400)
        except LookupError:
            return response.json({"message": "user not found"}, status=404)

        return response.json(result, status=status)

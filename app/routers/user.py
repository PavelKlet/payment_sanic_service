from sanic import Blueprint, response
from utils.auth import auth_required
from services.user import UserService

bp = Blueprint("user", url_prefix="")


@bp.get("/me")
@auth_required
async def me(request):
    """
    Get the authenticated user's information.

    Returns:
        200 OK with JSON:
        {
            "id": int,
            "email": str,
            "full_name": str | None
        }
    """
    async with request.ctx.uow:
        svc = UserService(request.ctx.uow)
        user = await svc.get_me(request.ctx.user_id)
        return response.json(user.model_dump())


@bp.get("/me/accounts")
@auth_required
async def my_accounts(request):
    """
    Get the list of accounts for the authenticated user.

    Returns:
        200 OK with JSON list:
        [
            {
                "id": int,
                "user_id": int,
                "balance": float
            },
            ...
        ]
    """
    async with request.ctx.uow:
        svc = UserService(request.ctx.uow)
        accounts = await svc.get_my_accounts(request.ctx.user_id)
        return response.json([a.model_dump() for a in accounts])


@bp.get("/me/payments")
@auth_required
async def my_payments(request):
    """
    Get the list of payments for the authenticated user.

    Returns:
        200 OK with JSON list:
        [
            {
                "id": int,
                "transaction_id": str,
                "user_id": int,
                "account_id": int,
                "amount": float
            },
            ...
        ]
    """
    async with request.ctx.uow:
        svc = UserService(request.ctx.uow)
        payments = await svc.get_my_payments(request.ctx.user_id)
        return response.json([p.model_dump() for p in payments])

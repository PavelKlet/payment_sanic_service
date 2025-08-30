from sanic import Blueprint, response
from utils.auth import auth_required, admin_required
from services.admin import AdminService

bp = Blueprint("admin", url_prefix="/admin")


@bp.get("/me")
@auth_required
@admin_required
async def me(request):
    """
    Get the current authenticated admin user's information.

    Returns:
        JSON response with:
        {
            "id": int,
            "email": str,
            "full_name": str | None
        }
    """
    async with request.ctx.uow:
        svc = AdminService(request.ctx.uow)
        user_out = await svc.get_current_admin(request.ctx.user_id)
        return response.json(user_out.model_dump())


@bp.get("/users")
@auth_required
@admin_required
async def list_users(request):
    """
    List all users in the system with basic information.

    Returns:
        JSON array of users:
        [
            {
                "id": int,
                "email": str,
                "full_name": str | None
            },
            ...
        ]
    """
    async with request.ctx.uow:
        svc = AdminService(request.ctx.uow)
        users = await svc.list_users()
        return response.json([u.model_dump() for u in users])


@bp.post("/users")
@auth_required
@admin_required
async def create_user(request):
    """
    Create a new user.

    Request body (JSON):
    {
        "email": str,
        "full_name": str | None,
        "password": str,
        "is_admin": bool (optional, default: false)
    }

    Returns:
        JSON of the created user with status 201.
    """
    payload = request.json or {}
    email = payload.get("email")
    full_name = payload.get("full_name")
    password = payload.get("password")
    is_admin = payload.get("is_admin", False)
    async with request.ctx.uow:
        svc = AdminService(request.ctx.uow)
        user = await svc.create_user(
            email=email, full_name=full_name, password=password, is_admin=is_admin
        )
        return response.json(user.model_dump(), status=201)


@bp.delete("/users/<user_id:int>")
@auth_required
@admin_required
async def delete_user(request, user_id: int):
    """
    Delete a user by ID.

    Path parameter:
        user_id (int): ID of the user to delete.

    Returns:
        204 on successful deletion.
        404 if the user does not exist.
    """
    async with request.ctx.uow:
        svc = AdminService(request.ctx.uow)
        ok = await svc.delete_user(user_id)
        if not ok:
            return response.json({"message": "not found"}, status=404)
        return response.json({"status": "deleted"}, status=204)


@bp.patch("/users/<user_id:int>")
@auth_required
@admin_required
async def update_user(request, user_id: int):
    """
    Update a user's information.

    Path parameter:
        user_id (int): ID of the user to update.

    Request body (JSON):
        Any subset of user fields to update, e.g.
        {
            "email": str,
            "full_name": str | None,
            "password": str,
            "is_admin": bool
        }

    Returns:
        JSON of the updated user.
        404 if the user does not exist.
    """
    payload = request.json or {}
    async with request.ctx.uow:
        svc = AdminService(request.ctx.uow)
        user = await svc.update_user(user_id=user_id, update_data=payload)
        if not user:
            return response.json({"message": "not found"}, status=404)
        return response.json(user.model_dump())


@bp.get("/users/<user_id:int>/accounts")
@auth_required
@admin_required
async def user_accounts(request, user_id: int):
    """
    Get all accounts for a specific user.

    Path parameter:
        user_id (int): ID of the user.

    Returns:
        JSON array of accounts:
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
        svc = AdminService(request.ctx.uow)
        accounts = await svc.get_user_accounts(user_id)
        return response.json([a.model_dump() for a in accounts])

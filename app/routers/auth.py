from sanic import Blueprint, response
from schemas.auth import LoginSchema
from services.auth import AuthService

bp = Blueprint("auth", url_prefix="/auth")


@bp.post("/login")
async def login(request):
    """
    Authenticate a user and return an access token.

    Request body (JSON):
    {
        "email": str,
        "password": str
    }

    Returns:
        200 OK with JSON:
        {
            "access_token": str
        }

        401 Unauthorized if the credentials are invalid:
        {
            "message": "invalid credentials"
        }
    """
    data = LoginSchema.model_validate(request.json or {})
    async with request.ctx.uow:
        svc = AuthService(request.ctx.uow)
        token = await svc.authenticate(data.email, data.password)
        if not token:
            return response.json({"message": "invalid credentials"}, status=401)
        return response.json({"access_token": token})

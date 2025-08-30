import jwt
from functools import wraps
from sanic import response
from sanic.request import Request
from config import settings

ALGO = "HS256"


def create_access_token(payload: dict) -> str:
    """
    Generate a JWT access token with the given payload.

    Args:
        payload (dict): Dictionary containing token claims, e.g., user ID and admin flag.

    Returns:
        str: Encoded JWT token as a string.
    """
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGO)


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token and return its payload.

    Args:
        token (str): JWT token string.

    Returns:
        dict: Decoded token payload containing claims.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])


def auth_required(handler):
    """
    Decorator to enforce that a request includes a valid JWT token.

    Sets:
        request.ctx.user_id (int | None): ID of the authenticated user if valid.
        request.ctx.is_admin (bool): Admin flag from the token payload.

    Returns:
        401 Unauthorized if token is missing or invalid, otherwise proceeds to the handler.
    """

    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.lower().startswith("bearer "):
            return response.json({"message": "missing token"}, status=401)
        token = auth.split()[1]
        try:
            payload = decode_access_token(token)
        except Exception:
            return response.json({"message": "invalid token"}, status=401)
        try:
            request.ctx.user_id = int(payload.get("sub"))
        except Exception:
            request.ctx.user_id = None
        request.ctx.is_admin = payload.get("is_admin", False)
        return await handler(request, *args, **kwargs)

    return wrapper


def admin_required(handler):
    """
    Decorator to enforce that the authenticated user is an admin.

    Checks:
        request.ctx.is_admin (bool) set by auth_required.

    Returns:
        403 Forbidden if user is not admin, otherwise proceeds to the handler.
    """

    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs):
        ok = getattr(request.ctx, "is_admin", False)
        if not ok:
            return response.json({"message": "forbidden"}, status=403)
        return await handler(request, *args, **kwargs)

    return wrapper

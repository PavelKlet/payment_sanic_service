from sanic import Sanic
from sanic.response import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from uow import UnitOfWork

from routers.auth import bp as auth_bp
from routers.user import bp as user_bp
from routers.admin import bp as admin_bp
from routers.webhook import bp as webhook_bp

engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

app = Sanic("payments_app")


@app.middleware("request")
async def inject_uow(request):
    request.ctx.uow = UnitOfWork(session_factory)


@app.middleware("response")
async def close_session(request, response_):
    uow = getattr(request.ctx, "uow", None)
    if uow and getattr(uow, "session", None):
        try:
            await uow.session.close()
        except Exception:
            pass


@app.get("/")
async def root(request):
    return json({"status": "ok"})


app.blueprint(auth_bp)
app.blueprint(user_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)

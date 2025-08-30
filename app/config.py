from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    SECRET_KEY: str
    SANIC_WORKERS: int = 1

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

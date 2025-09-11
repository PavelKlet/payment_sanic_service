from sqlalchemy import Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    balance: Mapped[Numeric] = mapped_column(
        Numeric(18, 2), default=0, server_default="0", nullable=False
    )

    user = relationship("User", back_populates="accounts")
    payments = relationship(
        "Payment", back_populates="account", cascade="all, delete-orphan"
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

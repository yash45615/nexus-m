from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class FactTransaction(Base):
    __tablename__ = "fact_transactions"

    transaction_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    transaction_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    transaction_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    date_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_date.date_key"),
        nullable=False,
        index=True,
    )

    merchant_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_merchant.merchant_key"),
        nullable=False,
        index=True,
    )

    partner_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_partner.partner_key"),
        nullable=False,
        index=True,
    )

    region_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_region.region_key"),
        nullable=False,
        index=True,
    )

    category_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_category.category_key"),
        nullable=False,
        index=True,
    )

    error_key: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dim_error_code.error_key"),
        nullable=True,
        index=True,
    )

    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR",
    )

    transaction_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    processing_fee: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    processing_latency_ms: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    transaction_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    decline_reason: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    authorization_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_retry: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
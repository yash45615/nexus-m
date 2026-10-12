from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


# ============================================================
# DIMENSION: DATE
# ============================================================

class DimDate(Base):
    __tablename__ = "dim_date"

    date_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    full_date: Mapped[date] = mapped_column(
        Date,
        unique=True,
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quarter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    month_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    day_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    is_weekend: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )


# ============================================================
# DIMENSION: MERCHANT
# ============================================================

class DimMerchant(Base):
    __tablename__ = "dim_merchant"

    merchant_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    merchant_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    merchant_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    merchant_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    risk_segment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


# ============================================================
# DIMENSION: PARTNER
# ============================================================

class DimPartner(Base):
    __tablename__ = "dim_partner"

    partner_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    partner_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    partner_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    partner_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    sla_timeout_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


# ============================================================
# DIMENSION: REGION
# ============================================================

class DimRegion(Base):
    __tablename__ = "dim_region"

    region_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    region_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


# ============================================================
# DIMENSION: CATEGORY
# ============================================================

class DimCategory(Base):
    __tablename__ = "dim_category"

    category_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    category_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


# ============================================================
# DIMENSION: ERROR CODE
# ============================================================

class DimErrorCode(Base):
    __tablename__ = "dim_error_code"

    error_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    error_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    error_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    error_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


# ============================================================
# FACT: TRANSACTIONS
# ============================================================

class FactTransaction(Base):
    __tablename__ = "fact_transactions"

    transaction_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    date_key: Mapped[int] = mapped_column(
        ForeignKey("dim_date.date_key"),
        nullable=False,
        index=True,
    )

    merchant_key: Mapped[int] = mapped_column(
        ForeignKey("dim_merchant.merchant_key"),
        nullable=False,
        index=True,
    )

    partner_key: Mapped[int] = mapped_column(
        ForeignKey("dim_partner.partner_key"),
        nullable=False,
        index=True,
    )

    region_key: Mapped[int] = mapped_column(
        ForeignKey("dim_region.region_key"),
        nullable=False,
    )

    category_key: Mapped[int] = mapped_column(
        ForeignKey("dim_category.category_key"),
        nullable=False,
    )

    error_key: Mapped[int | None] = mapped_column(
        ForeignKey("dim_error_code.error_key"),
        nullable=True,
    )

    transaction_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    processing_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "idx_transaction_date_merchant",
            "date_key",
            "merchant_key",
        ),
        Index(
            "idx_transaction_partner_status",
            "partner_key",
            "status",
        ),
    )


# ============================================================
# FACT: SETTLEMENTS
# ============================================================

class FactSettlement(Base):
    __tablename__ = "fact_settlements"

    settlement_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    transaction_id: Mapped[str] = mapped_column(
        ForeignKey("fact_transactions.transaction_id"),
        nullable=False,
        index=True,
    )

    partner_key: Mapped[int] = mapped_column(
        ForeignKey("dim_partner.partner_key"),
        nullable=False,
    )

    merchant_key: Mapped[int] = mapped_column(
        ForeignKey("dim_merchant.merchant_key"),
        nullable=False,
    )

    settlement_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    settlement_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    settlement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )


# ============================================================
# FACT: PARTNER EVENTS
# ============================================================

class FactPartnerEvent(Base):
    __tablename__ = "fact_partner_events"

    event_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    partner_key: Mapped[int] = mapped_column(
        ForeignKey("dim_partner.partner_key"),
        nullable=False,
    )

    region_key: Mapped[int] = mapped_column(
        ForeignKey("dim_region.region_key"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
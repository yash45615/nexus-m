from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class DimDate(Base):
    __tablename__ = "dim_date"

    date_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    calendar_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        unique=True,
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

    week_of_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    day_of_month: Mapped[int] = mapped_column(
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

    is_month_end: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )


class DimMerchant(Base):
    __tablename__ = "dim_merchant"

    merchant_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    merchant_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    merchant_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    merchant_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    merchant_segment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="STANDARD",
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )

    annual_revenue_band: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    risk_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class DimPartner(Base):
    __tablename__ = "dim_partner"

    partner_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    partner_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    partner_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    partner_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    success_rate_target: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        default=Decimal("0.9900"),
    )

    latency_target_ms: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        default=Decimal("500.0000"),
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class DimRegion(Base):
    __tablename__ = "dim_region"

    region_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    region_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )

    region_name: Mapped[str] = mapped_column(
        String(100),
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

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class DimCategory(Base):
    __tablename__ = "dim_category"

    category_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    category_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    category_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    parent_category: Mapped[str] = mapped_column(
        String(150),
        nullable=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="MEDIUM",
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class DimErrorCode(Base):
    __tablename__ = "dim_error_code"

    error_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    error_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    error_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    error_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    customer_actionable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
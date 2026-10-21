from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "badge IN ('Premium', 'Standard')",
            name="ck_products_badge",
        ),
        CheckConstraint("price >= 0", name="ck_products_price"),
        CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="ck_products_rating",
        ),
        CheckConstraint("review_count >= 0", name="ck_products_review_count"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False, default="piece")
    rating: Mapped[Decimal] = mapped_column(
        Numeric(2, 1), nullable=False, server_default="4.0"
    )
    review_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    badge: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="Standard"
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    vehicle_make: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vehicle_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vehicle_year_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vehicle_year_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    use_case: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

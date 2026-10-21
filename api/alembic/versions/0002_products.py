"""products table

Revision ID: 0002_products
Revises: 0001_initial
Create Date: 2026-10-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_products"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(30), nullable=False, server_default="piece"),
        sa.Column("rating", sa.Numeric(2, 1), nullable=False, server_default="4.0"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("badge", sa.String(20), nullable=False, server_default="Standard"),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("vehicle_make", sa.String(100), nullable=True),
        sa.Column("vehicle_model", sa.String(100), nullable=True),
        sa.Column("vehicle_year_from", sa.Integer(), nullable=True),
        sa.Column("vehicle_year_to", sa.Integer(), nullable=True),
        sa.Column("use_case", sa.String(50), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "badge IN ('Premium', 'Standard')",
            name="ck_products_badge",
        ),
        sa.CheckConstraint("price >= 0", name="ck_products_price"),
        sa.CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="ck_products_rating",
        ),
        sa.CheckConstraint("review_count >= 0", name="ck_products_review_count"),
    )
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_name", "products", ["name"])


def downgrade() -> None:
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_table("products")

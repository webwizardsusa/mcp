"""Read-only product tools used by MCP server and the chat agent."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from models.product import Product
from services.product_advisor.filters import active_product_filters, text_search_filters
from services.product_advisor.serialize import (
    clamp_limit,
    parse_uuid,
    product_to_dict,
)


class ProductAdvisorTools:
    def __init__(self, db: Session):
        self.db = db

    def search_products(
        self,
        query: str | None = None,
        brand: str | None = None,
        category: str | None = None,
        max_price: float | None = None,
        min_price: float | None = None,
        badge: str | None = None,
        use_case: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Search active products by text, brand, category, price, badge, or use case."""
        filters = active_product_filters()

        if query and query.strip():
            filters.extend(text_search_filters(query))
        if brand and brand.strip():
            filters.append(Product.brand.ilike(f"%{brand.strip()}%"))
        if category and category.strip():
            filters.append(Product.category.ilike(f"%{category.strip()}%"))
        if badge and badge.strip():
            filters.append(Product.badge == badge.strip())
        if use_case and use_case.strip():
            filters.append(Product.use_case.ilike(use_case.strip()))
        if max_price is not None:
            filters.append(Product.price <= Decimal(str(max_price)))
        if min_price is not None:
            filters.append(Product.price >= Decimal(str(min_price)))

        take = clamp_limit(limit)
        rows = self.db.scalars(
            select(Product)
            .where(*filters)
            .order_by(Product.rating.desc(), Product.review_count.desc())
            .limit(take)
        ).all()

        return {
            "count": len(rows),
            "products": [product_to_dict(row) for row in rows],
        }

    def get_product(self, product_id: str) -> dict:
        """Get one product by UUID."""
        uid = parse_uuid(product_id)
        if uid is None:
            return {"error": "Invalid product_id", "product": None}

        row = self.db.scalar(
            select(Product).where(Product.id == uid, Product.is_active.is_(True))
        )
        if row is None:
            return {"error": "Product not found", "product": None}
        return {"product": product_to_dict(row)}

    def compare_products(
        self,
        product_ids: list[str] | None = None,
        names: list[str] | None = None,
    ) -> dict:
        """Compare 2–3 products by id or name."""
        products: list[Product] = []

        if product_ids:
            for raw in product_ids[:3]:
                uid = parse_uuid(raw)
                if uid is None:
                    continue
                row = self.db.scalar(
                    select(Product).where(
                        Product.id == uid, Product.is_active.is_(True)
                    )
                )
                if row is not None:
                    products.append(row)

        if len(products) < 2 and names:
            for name in names[:3]:
                if not name or not name.strip():
                    continue
                row = self.db.scalar(
                    select(Product)
                    .where(
                        Product.is_active.is_(True),
                        Product.name.ilike(f"%{name.strip()}%"),
                    )
                    .order_by(Product.rating.desc())
                    .limit(1)
                )
                if row is not None and all(p.id != row.id for p in products):
                    products.append(row)
                if len(products) >= 3:
                    break

        if len(products) < 2:
            return {
                "error": "Need at least 2 products to compare. Provide product_ids or names.",
                "products": [product_to_dict(p) for p in products],
            }

        return {
            "count": len(products),
            "products": [product_to_dict(p) for p in products],
        }

    def recommend_for_vehicle(
        self,
        make: str,
        model: str,
        year: int | None = None,
        category: str | None = None,
        use_case: str | None = None,
        max_price: float | None = None,
        limit: int | None = None,
    ) -> dict:
        """Recommend products compatible with a vehicle make/model/year."""
        if not make or not make.strip() or not model or not model.strip():
            return {"error": "make and model are required", "products": []}

        filters = [
            Product.is_active.is_(True),
            Product.vehicle_make.ilike(make.strip()),
            Product.vehicle_model.ilike(model.strip()),
        ]

        if year is not None:
            filters.append(
                or_(
                    Product.vehicle_year_from.is_(None),
                    Product.vehicle_year_from <= year,
                )
            )
            filters.append(
                or_(
                    Product.vehicle_year_to.is_(None),
                    Product.vehicle_year_to >= year,
                )
            )
        if category and category.strip():
            filters.append(Product.category.ilike(f"%{category.strip()}%"))
        if use_case and use_case.strip():
            filters.append(Product.use_case.ilike(use_case.strip()))
        if max_price is not None:
            filters.append(Product.price <= Decimal(str(max_price)))

        take = clamp_limit(limit)
        rows = self.db.scalars(
            select(Product)
            .where(*filters)
            .order_by(Product.rating.desc(), Product.review_count.desc())
            .limit(take)
        ).all()

        # Soft fallback: same make + category if nothing matched model exactly
        if not rows and category:
            fallback_filters = [
                Product.is_active.is_(True),
                Product.vehicle_make.ilike(make.strip()),
                Product.category.ilike(f"%{category.strip()}%"),
            ]
            if max_price is not None:
                fallback_filters.append(Product.price <= Decimal(str(max_price)))
            rows = self.db.scalars(
                select(Product)
                .where(*fallback_filters)
                .order_by(Product.rating.desc(), Product.review_count.desc())
                .limit(take)
            ).all()

        return {
            "count": len(rows),
            "vehicle": {
                "make": make.strip(),
                "model": model.strip(),
                "year": year,
            },
            "products": [product_to_dict(row) for row in rows],
        }

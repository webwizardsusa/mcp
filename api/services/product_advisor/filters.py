"""Shared SQLAlchemy filters for active product search."""

from __future__ import annotations

from sqlalchemy import ColumnElement, or_

from models.product import Product


def active_product_filters() -> list[ColumnElement[bool]]:
    return [Product.is_active.is_(True)]


def text_search_filters(query: str) -> list[ColumnElement[bool]]:
    term = f"%{query.strip()}%"
    return [
        or_(
            Product.name.ilike(term),
            Product.brand.ilike(term),
            Product.category.ilike(term),
            Product.description.ilike(term),
        )
    ]

"""Serialize Product rows into JSON-safe dicts for MCP / GPT tools."""

from decimal import Decimal
from uuid import UUID

from models.product import Product

MAX_TOOL_LIMIT = 20
DEFAULT_TOOL_LIMIT = 5


def clamp_limit(limit: int | None, *, default: int = DEFAULT_TOOL_LIMIT) -> int:
    value = default if limit is None else int(limit)
    return max(1, min(value, MAX_TOOL_LIMIT))


def product_to_dict(product: Product) -> dict:
    return {
        "id": str(product.id),
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
        "price_usd": float(product.price) if isinstance(product.price, Decimal) else float(product.price),
        "unit": product.unit,
        "rating": float(product.rating) if isinstance(product.rating, Decimal) else float(product.rating),
        "review_count": product.review_count,
        "badge": product.badge,
        "image_url": product.image_url,
        "vehicle_make": product.vehicle_make,
        "vehicle_model": product.vehicle_model,
        "vehicle_year_from": product.vehicle_year_from,
        "vehicle_year_to": product.vehicle_year_to,
        "use_case": product.use_case,
    }


def parse_uuid(value: str) -> UUID | None:
    try:
        return UUID(str(value).strip())
    except (TypeError, ValueError):
        return None

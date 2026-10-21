"""
MCP server for AI Product Advisor (stdio).

Usage (from api/):
  python -m mcp_server.server

Connect from Cursor / Claude Desktop / other MCP hosts via stdio.
Chat inside this app uses the same tool implementations in-process.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.db import SessionLocal
from services.product_advisor.tools import ProductAdvisorTools

mcp = FastMCP(
    "ai-product-advisor",
    instructions=(
        "Read-only automotive spare parts catalog tools. "
        "Prices are USD. Prefer search_products and recommend_for_vehicle for advice."
    ),
)


@mcp.tool()
def search_products(
    query: str | None = None,
    brand: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    badge: str | None = None,
    use_case: str | None = None,
    limit: int | None = None,
) -> dict:
    """Search spare parts by text, brand, category, USD price, badge, or use case."""
    db = SessionLocal()
    try:
        return ProductAdvisorTools(db).search_products(
            query=query,
            brand=brand,
            category=category,
            max_price=max_price,
            min_price=min_price,
            badge=badge,
            use_case=use_case,
            limit=limit,
        )
    finally:
        db.close()


@mcp.tool()
def get_product(product_id: str) -> dict:
    """Get one product by UUID."""
    db = SessionLocal()
    try:
        return ProductAdvisorTools(db).get_product(product_id=product_id)
    finally:
        db.close()


@mcp.tool()
def compare_products(
    product_ids: list[str] | None = None,
    names: list[str] | None = None,
) -> dict:
    """Compare 2–3 products by UUID or name."""
    db = SessionLocal()
    try:
        return ProductAdvisorTools(db).compare_products(
            product_ids=product_ids,
            names=names,
        )
    finally:
        db.close()


@mcp.tool()
def recommend_for_vehicle(
    make: str,
    model: str,
    year: int | None = None,
    category: str | None = None,
    use_case: str | None = None,
    max_price: float | None = None,
    limit: int | None = None,
) -> dict:
    """Recommend products for a vehicle make/model/year."""
    db = SessionLocal()
    try:
        return ProductAdvisorTools(db).recommend_for_vehicle(
            make=make,
            model=model,
            year=year,
            category=category,
            use_case=use_case,
            max_price=max_price,
            limit=limit,
        )
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")

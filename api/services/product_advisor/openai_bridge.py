"""OpenAI tool schemas + dispatcher for ProductAdvisorTools (MCP-equivalent)."""

from __future__ import annotations

import json
from typing import Any

from services.product_advisor.tools import ProductAdvisorTools

OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search automotive spare parts in the catalog by free text, brand, "
                "category, USD price range, badge (Premium/Standard), or use case "
                "(City/Highway/Off-road/Mixed). Use for budget queries and general find."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search text for name, brand, category, or description",
                    },
                    "brand": {"type": "string"},
                    "category": {
                        "type": "string",
                        "description": "e.g. Brake Pads, Oil Filter, Battery",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price in USD",
                    },
                    "badge": {
                        "type": "string",
                        "enum": ["Premium", "Standard"],
                    },
                    "use_case": {
                        "type": "string",
                        "enum": ["City", "Highway", "Off-road", "Mixed"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max products to return (1-20, default 5)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Get full details for one product by its UUID id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product UUID from a previous search/recommend result",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_products",
            "description": (
                "Compare 2–3 products side by side. Prefer product_ids from earlier "
                "tool results; otherwise pass product names."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 3,
                    },
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 3,
                        "description": "Product name fragments when ids are unknown",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_for_vehicle",
            "description": (
                "Recommend products compatible with a vehicle make/model and optional year. "
                "Use for fitment questions like Hyundai Creta 2022 brake pads."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "make": {"type": "string", "description": "e.g. Hyundai"},
                    "model": {"type": "string", "description": "e.g. Creta"},
                    "year": {"type": "integer", "description": "Model year e.g. 2022"},
                    "category": {"type": "string"},
                    "use_case": {
                        "type": "string",
                        "enum": ["City", "Highway", "Off-road", "Mixed"],
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD",
                    },
                    "limit": {"type": "integer"},
                },
                "required": ["make", "model"],
            },
        },
    },
]


def dispatch_tool(tools: ProductAdvisorTools, name: str, arguments: dict) -> dict:
    """Execute a named tool with validated kwargs."""
    args = arguments or {}
    if name == "search_products":
        return tools.search_products(
            query=args.get("query"),
            brand=args.get("brand"),
            category=args.get("category"),
            max_price=args.get("max_price"),
            min_price=args.get("min_price"),
            badge=args.get("badge"),
            use_case=args.get("use_case"),
            limit=args.get("limit"),
        )
    if name == "get_product":
        return tools.get_product(product_id=str(args.get("product_id", "")))
    if name == "compare_products":
        return tools.compare_products(
            product_ids=args.get("product_ids"),
            names=args.get("names"),
        )
    if name == "recommend_for_vehicle":
        return tools.recommend_for_vehicle(
            make=str(args.get("make", "")),
            model=str(args.get("model", "")),
            year=args.get("year"),
            category=args.get("category"),
            use_case=args.get("use_case"),
            max_price=args.get("max_price"),
            limit=args.get("limit"),
        )
    return {"error": f"Unknown tool: {name}"}


def parse_tool_arguments(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

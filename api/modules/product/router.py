"""Product HTTP routes — listing only (no CRUD)."""

from fastapi import APIRouter, Query

from core.deps import CurrentUserDep, DbDep
from core.responses import success
from modules.product.schema import (
    ProductListQuery,
    ProductListResult,
    ProductResponse,
    SortOption,
)
from modules.product.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def list_products(
    db: DbDep,
    _current_user: CurrentUserDep,
    q: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=48),
    sort: SortOption = Query(default="popular"),
):
    result = ProductService(db).list_products(
        ProductListQuery(q=q, page=page, page_size=page_size, sort=sort)
    )
    payload = ProductListResult(
        items=[ProductResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )
    return success(
        message="Products fetched successfully",
        result=payload.model_dump(mode="json"),
    )

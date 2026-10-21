from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


SortOption = Literal["popular", "price_asc", "price_desc", "rating_desc", "name_asc"]


class ProductListQuery(BaseModel):
    q: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=12, ge=1, le=48)
    sort: SortOption = "popular"


class ProductResponse(BaseModel):
    id: UUID
    name: str
    brand: str
    category: str
    description: str
    price: Decimal
    unit: str
    rating: Decimal
    review_count: int
    badge: str
    image_url: str
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_year_from: int | None = None
    vehicle_year_to: int | None = None
    use_case: str | None = None

    model_config = {"from_attributes": True}


class ProductListResult(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

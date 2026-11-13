"""Read-only product listing (search, sort, pagination)."""

from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.product import Product
from modules.product.schema import ProductListQuery, SortOption
from services.product_advisor.filters import active_product_filters, text_search_filters


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, query: ProductListQuery) -> dict:
        filters = active_product_filters()

        if query.q and query.q.strip():
            filters.extend(text_search_filters(query.q))

        base = select(Product).where(*filters)
        total = self.db.scalar(
            select(func.count()).select_from(Product).where(*filters)
        ) or 0

        ordered = base.order_by(*self._order_by(query.sort), Product.id.asc())
        offset = (query.page - 1) * query.page_size
        items = self.db.scalars(ordered.offset(offset).limit(query.page_size)).all()

        total_pages = ceil(total / query.page_size) if total else 0

        return {
            "items": items,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": total_pages,
        }

    def _order_by(self, sort: SortOption):
        if sort == "price_asc":
            return (Product.price.asc(),)
        if sort == "price_desc":
            return (Product.price.desc(),)
        if sort == "rating_desc":
            return (Product.rating.desc(), Product.review_count.desc())
        if sort == "name_asc":
            return (Product.name.asc(),)
        # popular
        return (Product.review_count.desc(), Product.rating.desc())

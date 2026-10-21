"""
Seed 100 automotive products with one real image each.

Images are fetched from Wikimedia Commons (real spare-part photos),
saved into web/public/products/, and stored as /products/NNN.jpg.

Usage (from api/):
  python -m seeders.seed_products
  python -m seeders.seed_products --force
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, select

from core.config import settings
from core.db import SessionLocal
from models.product import Product
from seeders.product_catalog import CATEGORIES, build_catalog

PRODUCT_COUNT = 100
IMAGE_DIR = Path(__file__).resolve().parents[2] / "web" / "public" / "products"
IMAGE_URL_PREFIX = "/products"

# Wikimedia search terms per category (real automotive part photos).
_CATEGORY_SEARCHES = {
    "Brake Pads": "brake pad",
    "Brake Discs": "brake disc",
    "Oil Filter": "oil filter car",
    "Air Filter": "air filter automobile",
    "Spark Plugs": "spark plug",
    "Engine Oil": "motor oil bottle",
    "Battery": "car battery",
    "Wiper Blades": "windshield wiper",
    "Shock Absorbers": "shock absorber car",
    "Timing Belt": "timing belt engine",
    "Clutch Kit": "clutch disc automobile",
    "Headlight Bulb": "headlight bulb car",
    "Cabin Filter": "cabin air filter",
    "Fuel Filter": "fuel filter car",
    "Radiator Hose": "radiator hose car",
}

_FALLBACK_SEARCHES = [
    "automotive spare part",
    "car engine part",
    "automobile component",
    "vehicle maintenance part",
]


def _http_get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Product-Advisor-Seeder/1.0 (local demo)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_get_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Product-Advisor-Seeder/1.0 (local demo)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def _commons_image_urls(search: str, limit: int = 40) -> list[str]:
    """Return thumbnail URLs from Wikimedia Commons search."""
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": search,
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "400",
        }
    )
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    payload = _http_get_json(url)
    pages = (payload.get("query") or {}).get("pages") or {}
    urls: list[str] = []
    for page in pages.values():
        info = (page.get("imageinfo") or [None])[0]
        if not info:
            continue
        thumb = info.get("thumburl") or info.get("url")
        if thumb and thumb not in urls:
            # Strip tracking query params
            urls.append(thumb.split("?")[0])
    return urls


def _collect_image_pool(needed: int) -> list[str]:
    """Build a pool of unique real part-image URLs (>= needed)."""
    pool: list[str] = []
    seen: set[str] = set()

    category_terms = [
        _CATEGORY_SEARCHES.get(cat[0], cat[0]) for cat in CATEGORIES
    ]
    all_terms = category_terms + _FALLBACK_SEARCHES

    for term in all_terms:
        try:
            for image_url in _commons_image_urls(term, limit=50):
                if image_url in seen:
                    continue
                seen.add(image_url)
                pool.append(image_url)
                if len(pool) >= needed:
                    return pool
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"  warn: commons search failed for '{term}': {exc}")
            continue

    if len(pool) < needed:
        raise RuntimeError(
            f"Only found {len(pool)} Wikimedia images; need at least {needed}."
        )
    return pool


def _download_image(source_url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 1024:
        return
    data = _http_get_bytes(source_url)
    if len(data) < 1024:
        raise RuntimeError(f"Image too small from {source_url}")
    dest.write_bytes(data)


def seed_products(*, force: bool = False) -> None:
    if settings.APP_ENV != "local":
        raise SystemExit("Refusing to seed products when APP_ENV is not local")

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    catalog = build_catalog(PRODUCT_COUNT)

    print(f"Collecting {PRODUCT_COUNT} real product images from Wikimedia Commons...")
    image_pool = _collect_image_pool(PRODUCT_COUNT)
    print(f"  found {len(image_pool)} unique images")

    print(f"Downloading into {IMAGE_DIR} ...")
    for index, item in enumerate(catalog):
        dest = IMAGE_DIR / item["image_filename"]
        source = image_pool[index]
        try:
            _download_image(source, dest)
            print(f"  ✓ {item['image_filename']} — {item['name']}")
        except Exception as exc:
            # Retry with next available URL if one fails
            recovered = False
            for alt in image_pool[index + 1 :]:
                try:
                    _download_image(alt, dest)
                    print(f"  ✓ {item['image_filename']} — {item['name']} (alt)")
                    recovered = True
                    break
                except Exception:
                    continue
            if not recovered:
                raise RuntimeError(
                    f"Failed to download image for {item['name']}: {exc}"
                ) from exc

    db = SessionLocal()
    try:
        existing = db.scalar(select(func.count()).select_from(Product)) or 0
        if existing > 0 and not force:
            print(f"Products already seeded ({existing} rows). Skipping insert.")
            print("Re-run with --force to wipe and reseed.")
            return

        if existing > 0 and force:
            db.execute(delete(Product))
            db.commit()
            print(f"Cleared {existing} existing products.")

        rows = [
            Product(
                name=item["name"],
                brand=item["brand"],
                category=item["category"],
                description=item["description"],
                price=Decimal(str(item["price"])),
                unit=item["unit"],
                rating=Decimal(str(item["rating"])),
                review_count=item["review_count"],
                badge=item["badge"],
                image_url=f"{IMAGE_URL_PREFIX}/{item['image_filename']}",
                vehicle_make=item["vehicle_make"],
                vehicle_model=item["vehicle_model"],
                vehicle_year_from=item["vehicle_year_from"],
                vehicle_year_to=item["vehicle_year_to"],
                use_case=item["use_case"],
                is_active=True,
            )
            for item in catalog
        ]
        db.add_all(rows)
        db.commit()
        print(f"Seeded {len(rows)} products (USD prices + /products/NNN.jpg images).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    force = "--force" in sys.argv
    seed_products(force=force)

"""
Seed 100 automotive products with one real image each.

Images are saved under web/public/products/ locally (or PRODUCT_IMAGE_DIR).
In Docker (API-only container), use --skip-images so DB rows point at
/products/NNN.jpg already baked into the web image.

Usage (from api/):
  python -m seeders.seed_products
  python -m seeders.seed_products --force
  python -m seeders.seed_products --force --skip-images

Docker:
  docker compose exec -e APP_ENV=local -e ALLOW_PRODUCT_SEED=1 api \\
    python -m seeders.seed_products --force --skip-images
"""

from __future__ import annotations

import json
import os
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


def _resolve_image_dir() -> Path | None:
    """Return a writable image directory, or None if downloads should be skipped."""
    env_dir = os.getenv("PRODUCT_IMAGE_DIR", "").strip()
    if env_dir:
        return Path(env_dir)

    # Local monorepo: api/seeders -> api -> repo root -> web/public/products
    repo_web = Path(__file__).resolve().parents[2] / "web" / "public" / "products"
    if (Path(__file__).resolve().parents[2] / "web").is_dir():
        return repo_web

    # Docker API image has no sibling web/ folder.
    return None


def _ensure_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError as exc:
        print(f"  warn: cannot write images to {path}: {exc}")
        return False


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
            urls.append(thumb.split("?")[0])
    return urls


def _collect_image_pool(needed: int) -> list[str]:
    """Build a pool of unique real part-image URLs (>= needed)."""
    pool: list[str] = []
    seen: set[str] = set()

    category_terms = [_CATEGORY_SEARCHES.get(cat[0], cat[0]) for cat in CATEGORIES]
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


def _assert_seed_allowed() -> None:
    allow = os.getenv("ALLOW_PRODUCT_SEED", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if settings.APP_ENV == "local" or allow:
        return
    raise SystemExit(
        "Refusing to seed products when APP_ENV is not local. "
        "Re-run with APP_ENV=local or ALLOW_PRODUCT_SEED=1 "
        "(and preferably --skip-images in Docker)."
    )


def seed_products(*, force: bool = False, skip_images: bool = False) -> None:
    _assert_seed_allowed()

    catalog = build_catalog(PRODUCT_COUNT)
    image_dir = _resolve_image_dir()
    download_images = not skip_images

    if download_images:
        if image_dir is None:
            print(
                "No writable web/public/products path in this environment "
                "(typical for Docker API). Skipping image download; "
                "using /products/NNN.jpg URLs (ensure images exist in the web image)."
            )
            download_images = False
        elif not _ensure_writable_dir(image_dir):
            print("Skipping image download; seeding DB URLs only.")
            download_images = False

    if download_images and image_dir is not None:
        print(f"Collecting {PRODUCT_COUNT} real product images from Wikimedia Commons...")
        image_pool = _collect_image_pool(PRODUCT_COUNT)
        print(f"  found {len(image_pool)} unique images")
        print(f"Downloading into {image_dir} ...")
        for index, item in enumerate(catalog):
            dest = image_dir / item["image_filename"]
            source = image_pool[index]
            try:
                _download_image(source, dest)
                print(f"  ✓ {item['image_filename']} — {item['name']}")
            except Exception as exc:
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
    else:
        print("Skipping image download (--skip-images or no writable image dir).")

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
    skip_images = "--skip-images" in sys.argv
    seed_products(force=force, skip_images=skip_images)

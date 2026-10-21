"""100 automotive spare-part definitions for local seeding (USD prices)."""

from __future__ import annotations

BRANDS = [
    "Brembo",
    "Bosch",
    "TRW",
    "Akebono",
    "Nissin",
    "Textar",
    "NGK",
    "Denso",
    "Mann-Filter",
    "Mobil",
    "Castrol",
    "Gates",
    "Continental",
    "Sachs",
    "Monroe",
    "Valeo",
    "Hella",
    "Philips",
    "Exide",
    "Amaron",
]

CATEGORIES = [
    ("Brake Pads", "set", 35.0, 95.0, "brake,pad,car"),
    ("Brake Discs", "pair", 55.0, 140.0, "brake,disc,rotor"),
    ("Oil Filter", "piece", 8.0, 28.0, "oil,filter,car"),
    ("Air Filter", "piece", 10.0, 35.0, "air,filter,car"),
    ("Spark Plugs", "set", 18.0, 55.0, "spark,plug,engine"),
    ("Engine Oil", "litre", 6.0, 22.0, "engine,oil,bottle"),
    ("Battery", "piece", 70.0, 180.0, "car,battery"),
    ("Wiper Blades", "pair", 12.0, 40.0, "wiper,car"),
    ("Shock Absorbers", "pair", 60.0, 160.0, "suspension,car"),
    ("Timing Belt", "piece", 25.0, 75.0, "engine,belt,car"),
    ("Clutch Kit", "set", 90.0, 220.0, "clutch,car,parts"),
    ("Headlight Bulb", "pair", 9.0, 45.0, "headlight,car"),
    ("Cabin Filter", "piece", 11.0, 32.0, "cabin,filter,car"),
    ("Fuel Filter", "piece", 10.0, 30.0, "fuel,filter,car"),
    ("Radiator Hose", "piece", 14.0, 38.0, "radiator,hose,car"),
]

VEHICLES = [
    ("Hyundai", "Creta", 2018, 2024),
    ("Hyundai", "i20", 2015, 2023),
    ("Maruti", "Swift", 2014, 2024),
    ("Maruti", "Baleno", 2016, 2024),
    ("Honda", "City", 2015, 2024),
    ("Honda", "Civic", 2016, 2022),
    ("Toyota", "Innova", 2016, 2024),
    ("Toyota", "Fortuner", 2017, 2024),
    ("Tata", "Nexon", 2017, 2024),
    ("Kia", "Seltos", 2019, 2024),
    ("Mahindra", "XUV700", 2021, 2024),
    ("Ford", "EcoSport", 2015, 2021),
]

USE_CASES = ["City", "Highway", "Off-road", "Mixed"]

PRODUCT_TYPES = [
    "Ceramic",
    "Semi Metallic",
    "Organic",
    "Premium",
    "Heavy Duty",
    "Performance",
    "Eco",
    "Sport",
    "Standard",
    "Pro",
]


def _product_name(brand: str, ptype: str, category: str) -> str:
    if category == "Brake Pads":
        return f"{brand} {ptype} Brake Pad"
    if category == "Brake Discs":
        return f"{brand} {ptype} Brake Disc"
    if category == "Spark Plugs":
        return f"{brand} {ptype} Spark Plug"
    if category == "Wiper Blades":
        return f"{brand} {ptype} Wiper Blade"
    if category == "Shock Absorbers":
        return f"{brand} {ptype} Shock Absorber"
    if category == "Engine Oil":
        return f"{brand} {ptype} Engine Oil 5W-30"
    if category == "Headlight Bulb":
        return f"{brand} {ptype} Headlight Bulb"
    return f"{brand} {ptype} {category}"


def build_catalog(count: int = 100) -> list[dict]:
    """Build exactly `count` product dicts with unique local image filenames."""
    products: list[dict] = []
    i = 0
    while len(products) < count:
        brand = BRANDS[i % len(BRANDS)]
        category, unit, price_min, price_max, image_tags = CATEGORIES[i % len(CATEGORIES)]
        ptype = PRODUCT_TYPES[i % len(PRODUCT_TYPES)]
        vehicle = VEHICLES[i % len(VEHICLES)]
        use_case = USE_CASES[i % len(USE_CASES)]

        span = price_max - price_min
        price = round(price_min + (span * ((i % 10) / 9)), 2)

        rating = round(3.8 + ((i % 13) * 0.1), 1)
        if rating > 5.0:
            rating = 5.0
        review_count = 40 + (i * 17) % 480
        badge = "Premium" if price >= (price_min + price_max) / 2 else "Standard"

        name = _product_name(brand, ptype, category)
        slug = f"{i + 1:03d}"

        products.append(
            {
                "name": name,
                "brand": brand,
                "category": category,
                "description": (
                    f"{name} designed for {vehicle[0]} {vehicle[1]} "
                    f"({vehicle[2]}–{vehicle[3]}). Ideal for {use_case.lower()} driving. "
                    f"OEM-quality fitment with reliable performance and durability."
                ),
                "price": price,
                "unit": unit,
                "rating": rating,
                "review_count": review_count,
                "badge": badge,
                "image_filename": f"{slug}.jpg",
                "image_tags": image_tags,
                "image_lock": i + 1,
                "vehicle_make": vehicle[0],
                "vehicle_model": vehicle[1],
                "vehicle_year_from": vehicle[2],
                "vehicle_year_to": vehicle[3],
                "use_case": use_case,
            }
        )
        i += 1

    return products

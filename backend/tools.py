"""Tools the shop assistant can call.

Every product fact the agent is allowed to state comes through here, and every
function reads `data/campus_customs.db` via `db.py`. Nothing in this module
invents, rounds, or estimates: if the catalogue does not hold a value, the tool
says so in words the agent can repeat.

The agent is not given SQL. It gets three narrow questions it can ask — find
products, describe one product, check stock — which keeps the catalogue as the
only source of answers.
"""

from __future__ import annotations

import re
from typing import Any

import db
from models import (
    ProductLookup,
    ProductMatch,
    ProductSearchResult,
    SizeStock,
    StockResult,
)

MAX_SEARCH_RESULTS = 6

# `garment_type` is free text and inconsistent: 22 distinct values for about
# seven real categories, including both `short-sleeve t-shirt` and
# `short-sleeve T-shirt`. Matching it literally returns 5 of ~25 hoodies, so a
# shopper asking for hoodies would be told about a fifth of the stock and the
# answer would look authoritative. These patterns fold the variants together.
CATEGORY_PATTERNS: dict[str, str] = {
    # The lookbehind matters: a bare `t-?shirt` also matches "swea(tshirt)", which
    # filed every crewneck and hooded sweatshirt under T-shirts.
    "t-shirt": r"(?<![a-z])t-?shirt",
    "crewneck": r"crew-?neck|crewneck",
    "hoodie": r"hood",
    "quarter-zip": r"quarter\s*-?\s*zip|1/4\s*zip|\b1 4 zip\b",
    "jacket": r"jacket",
    "long-sleeve shirt": r"long-?sleeve|performance shirt",
    "mockneck": r"mock-?neck",
}

# What a shopper types vs. what the catalogue calls it. A word can mean more
# than one category: "sweatshirt" covers both crewnecks and hoodies, and
# narrowing it to one would quietly hide half the answer.
CATEGORY_SYNONYMS: dict[str, tuple[str, ...]] = {
    "tee": ("t-shirt",), "tees": ("t-shirt",), "tshirt": ("t-shirt",),
    "tshirts": ("t-shirt",), "shirt": ("t-shirt",), "shirts": ("t-shirt",),
    "sweatshirt": ("crewneck", "hoodie"), "sweatshirts": ("crewneck", "hoodie"),
    "crew": ("crewneck",), "crewnecks": ("crewneck",),
    "hoodies": ("hoodie",), "hooded": ("hoodie",),
    "quarterzip": ("quarter-zip",), "qtr": ("quarter-zip",),
    "jackets": ("jacket",), "coat": ("jacket",), "coats": ("jacket",),
    "outerwear": ("jacket",),
}

STOPWORDS = {
    "a", "an", "and", "any", "are", "do", "does", "for", "got", "have", "how",
    "i", "in", "is", "it", "me", "much", "my", "of", "on", "or", "please", "show",
    "some", "the", "to", "want", "what", "with", "you", "your", "looking", "need",
    "campus", "customs", "yale", "buy", "get", "something", "anything", "there",
}


def category_of(garment_type: str) -> str:
    """Fold a messy `garment_type` value into one shopper-facing category."""
    text = garment_type.lower()
    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, text):
            return category
    return garment_type.lower()


def _terms(query: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", query.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _requested_categories(query: str) -> set[str]:
    found = set()
    lowered = query.lower()
    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, lowered):
            found.add(category)
    for word in re.findall(r"[a-z0-9-]+", lowered):
        found.update(CATEGORY_SYNONYMS.get(word, ()))
    return found


# Things shoppers ask for that Campus Customs does not sell at all. Without this,
# "bulldog hat" scores on the word "bulldog" and happily returns bulldog hoodies,
# which reads as "yes we have that" when the honest answer is that we sell no hats.
NOT_CARRIED = {
    "hat": "hats or caps", "hats": "hats or caps", "cap": "hats or caps",
    "caps": "hats or caps", "beanie": "hats or caps", "beanies": "hats or caps",
    "sock": "socks", "socks": "socks", "mug": "mugs", "mugs": "mugs",
    "sticker": "stickers", "stickers": "stickers", "pennant": "pennants",
    "scarf": "scarves", "scarves": "scarves", "glove": "gloves", "gloves": "gloves",
    "shorts": "shorts", "sweatpants": "sweatpants", "joggers": "sweatpants",
    "pants": "trousers or sweatpants", "bag": "bags", "bags": "bags",
    "backpack": "bags", "blanket": "blankets", "tie": "ties", "poster": "posters",
}


def _not_carried_in(query: str) -> str | None:
    for word in re.findall(r"[a-z]+", query.lower()):
        if word in NOT_CARRIED:
            return NOT_CARRIED[word]
    return None


def categories_we_carry() -> list[str]:
    """The shopper-facing categories actually present in the catalogue."""
    return sorted(c["category"] for c in db.category_counts())


def _sizes_from(row: dict[str, Any]) -> list[SizeStock]:
    """Sizes for a row from query_products, which carries only a stock total.

    One extra read per shown product (at most 12), against a 102-row local
    SQLite file — measured at about 2 ms for a whole search.
    """
    product = db.get_product(row["product_id"])
    return _sizes(product) if product else []


def _sizes(product: dict[str, Any]) -> list[SizeStock]:
    return [
        SizeStock(size=s["size"], quantity=s["quantity"], in_stock=s["quantity"] > 0)
        for s in product["inventory"]
    ]


def _match(product: dict[str, Any], sizes: list[SizeStock] | None = None) -> ProductMatch:
    return ProductMatch(
        product_id=product["product_id"],
        name=product["name"],
        price=product["price"],
        category=category_of(product["garment_type"]),
        garment_type=product["garment_type"],
        description=product["description"],
        colors=product["colors"],
        image_url=product["image_url"],
        total_stock=product["total_stock"],
        sizes_in_stock=[s.size for s in sizes] if sizes else [],
    )


def search_products(
    query: str = "",
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
    limit: int = MAX_SEARCH_RESULTS,
) -> ProductSearchResult:
    """Find products by words, category, and price, sorted however you need.

    Runs through `db.query_products`, the same query the Products page uses, so
    the two can never disagree. Filtering and sorting happen in SQL across the
    whole catalogue, which is what makes `price_min` trustworthy even when only a
    few products come back.
    """
    limit = max(1, min(int(limit or MAX_SEARCH_RESULTS), 12))
    carried = categories_we_carry()

    missing = _not_carried_in(query)
    if missing:
        return ProductSearchResult(
            query=query, match_count=0, returned=0, categories_we_carry=carried,
            note=f"Campus Customs does not sell {missing}. The catalogue is apparel only.",
        )

    wanted = [category] if category else sorted(_requested_categories(query))
    result = db.query_products(
        q=query or None,
        categories=wanted or None,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        limit=limit,
    )

    products = [_match(p, _sizes_from(p)) for p in result["products"]]
    total = result["total"]

    if total == 0:
        note = "Nothing in the catalogue matched that."
    elif total > 1:
        note = (
            f"{total} products matched. Ask the shopper which one they mean "
            "before quoting a price or stock level for a single item."
        )
    else:
        note = ""
    if total and result["price_min"] is not None:
        note += (
            f" Across all {total} matches the price range is "
            f"${result['price_min']:.2f}–${result['price_max']:.2f}."
        )

    return ProductSearchResult(
        query=query,
        match_count=total,
        returned=len(products),
        products=products,
        needs_disambiguation=total > 1,
        categories_we_carry=carried if total == 0 else [],
        price_min=result["price_min"],
        price_max=result["price_max"],
        sorted_by=result["sort"],
        filters_applied={
            k: v
            for k, v in {
                "category": wanted or None,
                "min_price": min_price,
                "max_price": max_price,
            }.items()
            if v is not None
        },
        note=note.strip(),
    )


def _gaps_note(product: dict[str, Any]) -> str:
    """One sentence naming whatever the catalogue is missing for this product.

    Three rows have no colours and a build-failure placeholder where a
    description should be; this is what the agent repeats instead of describing
    the garment from its name or photo.
    """
    missing = []
    if not product["colors"]:
        missing.append("colours")
    if not product.get("description_recorded", True):
        missing.append("a description")
    if not missing:
        return ""
    return (
        f"The catalogue does not record {' or '.join(missing)} for this product. "
        "Say so rather than describing it from its name or photo."
    )


def get_product_details(product_id: str) -> ProductLookup:
    """Everything the catalogue holds about one product, including stock per size.

    `product_id` is the slug from a search result, e.g. "basic-hoodie-big-yale".
    """
    product = db.get_product(product_id)
    if product is None:
        return ProductLookup(
            found=False,
            product_id=product_id,
            note=f"There is no product with id {product_id!r} in the catalogue.",
        )

    sizes = _sizes(product)
    return ProductLookup(
        found=True,
        product_id=product["product_id"],
        name=product["name"],
        price=product["price"],
        category=category_of(product["garment_type"]),
        garment_type=product["garment_type"],
        description=product["description"],
        colors=product["colors"],
        colors_recorded=bool(product["colors"]),
        search_tags=product["search_tags"],
        image_url=product["image_url"],
        inventory=sizes,
        sizes_in_stock=[s.size for s in sizes if s.in_stock],
        sizes_out_of_stock=[s.size for s in sizes if not s.in_stock],
        total_stock=product["total_stock"],
        description_recorded=product.get("description_recorded", True),
        note=_gaps_note(product),
    )


def check_stock(product_id: str, size: str | None = None) -> StockResult:
    """Stock for one product: every size, or one size if `size` is given.

    Sizes are XS, S, M, L, XL, XXL. Quantities are exact counts from the
    inventory table; 0 means genuinely out of stock, not unknown.
    """
    product = db.get_product(product_id)
    if product is None:
        return StockResult(
            found=False,
            product_id=product_id,
            status="unknown_product",
            note=f"There is no product with id {product_id!r} in the catalogue.",
        )

    sizes = _sizes(product)
    in_stock_sizes = [s.size for s in sizes if s.in_stock]
    base = dict(
        found=True,
        product_id=product["product_id"],
        name=product["name"],
        inventory=sizes,
        sizes_in_stock=in_stock_sizes,
        total_stock=product["total_stock"],
    )

    if size is None:
        return StockResult(
            **base,
            status="in_stock" if in_stock_sizes else "out_of_stock",
            note=(
                ""
                if in_stock_sizes
                else f"{product['name']} is out of stock in every size."
            ),
        )

    wanted = size.strip().upper()
    if wanted not in db.SIZE_ORDER:
        return StockResult(
            **base,
            size=size,
            status="unknown_size",
            note=f"{size!r} is not a size we carry. Sizes are {', '.join(db.SIZE_ORDER)}.",
        )

    row = next((s for s in sizes if s.size == wanted), None)
    if row is None:
        return StockResult(
            **base, size=wanted, status="unknown_size",
            note=f"The inventory has no row for size {wanted} of this product.",
        )

    others = [s for s in in_stock_sizes if s != wanted]
    if row.in_stock:
        return StockResult(
            **base, size=wanted, quantity=row.quantity, status="in_stock",
            other_sizes_in_stock=others,
            note=f"{product['name']} has {row.quantity} in size {wanted}.",
        )
    return StockResult(
        **base, size=wanted, quantity=0, status="out_of_stock",
        other_sizes_in_stock=others,
        note=(
            f"{product['name']} is OUT OF STOCK in size {wanted}. "
            + (f"It is in stock in {', '.join(others)}." if others else
               "It is out of stock in every other size too.")
        ),
    )

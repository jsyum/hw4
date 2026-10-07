"""Read-only access to campus_customs.db.

The database is the source of truth for every product fact the site shows, so
this module is the only place that talks to SQLite. It opens the file with
`mode=ro` — the shop reads the catalogue, it never writes to it.

Later problems add the agent; its tools should call these same functions rather
than opening their own connection, so there is one definition of "what the
database says".
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

# backend/db.py -> Assignment 4/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "campus_customs.db"

# The shop displays sizes in wearable order. The column is TEXT, so sorting it
# in SQL would give XL < XS < XXL alphabetically.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
_SIZE_RANK = {s: i for i, s in enumerate(SIZE_ORDER)}


class DatabaseMissing(RuntimeError):
    """Raised when data/campus_customs.db is not on disk."""


def connect_rw() -> sqlite3.Connection:
    """Read-write connection. Only account creation uses this.

    The catalogue is read-only on purpose; `users` is the one table the site
    writes to, so the writable connection is kept separate and used deliberately.
    """
    if not DB_PATH.exists():
        raise DatabaseMissing(f"Missing {DB_PATH}.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise DatabaseMissing(
            f"Missing {DB_PATH}. The data/ folder is gitignored — copy it in from the "
            "assignment materials before starting the backend."
        )
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# Three catalogue rows hold a build-failure placeholder where a description
# should be — "Campus Customs product photo (…). Vision blocked; filename-based
# stub." It is not a description of the garment, so neither the website nor the
# agent should present it as one. Detected here, in the one module that reads the
# catalogue, so the storefront and the chatbot cannot disagree about it.
#
# The database itself is left exactly as it is; this only affects what is served.
STUB_DESCRIPTION_MARKERS = ("filename-based stub", "Vision blocked")


def is_stub_description(text: str | None) -> bool:
    return bool(text) and any(m in text for m in STUB_DESCRIPTION_MARKERS)


def _described(raw: str | None) -> tuple[str, bool]:
    """Return (description to serve, whether a real one was recorded).

    A placeholder is served as an empty string rather than passed along, so no
    consumer can print it by accident. `description_recorded` says why it is empty.
    """
    text = raw or ""
    return ("", False) if is_stub_description(text) else (text, True)


def _json_list(raw: str | None) -> list[str]:
    """colors and search_tags are JSON arrays stored as TEXT."""
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [str(v) for v in value] if isinstance(value, list) else []


def _image_url(image_file_path: str) -> str:
    """Map the catalogue's relative path to the URL the API serves it on."""
    return f"/media/{image_file_path.lstrip('/')}"


def _sort_sizes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: _SIZE_RANK.get(r["size"], len(SIZE_ORDER)))


def list_products() -> list[dict[str, Any]]:
    """Every catalogue row, with total stock. Enough for a product card."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT c.product_id, c.name, c.garment_type, c.description,
                   c.colors, c.image_file_path, c.price,
                   COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            ORDER BY c.name
            """
        ).fetchall()
    products = []
    for r in rows:
        description, recorded = _described(r["description"])
        products.append(
            {
                "product_id": r["product_id"],
                "name": r["name"],
                "garment_type": r["garment_type"],
                "description": description,
                "description_recorded": recorded,
                "colors": _json_list(r["colors"]),
                "image_url": _image_url(r["image_file_path"]),
                "price": r["price"],
                "total_stock": r["total_stock"],
            }
        )
    return products


def get_product(product_id: str) -> dict[str, Any] | None:
    """One product with its per-size stock, or None if there is no such id."""
    with connect() as conn:
        row = conn.execute(
            """
            SELECT product_id, name, garment_type, description, colors,
                   search_tags, image_file_path, price
            FROM catalogue WHERE product_id = ?
            """,
            (product_id,),
        ).fetchone()
        if row is None:
            return None
        sizes = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?",
            (product_id,),
        ).fetchall()

    inventory = _sort_sizes([{"size": s["size"], "quantity": s["quantity"]} for s in sizes])
    description, recorded = _described(row["description"])
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": description,
        "description_recorded": recorded,
        "colors": _json_list(row["colors"]),
        "search_tags": _json_list(row["search_tags"]),
        "image_url": _image_url(row["image_file_path"]),
        "price": row["price"],
        "inventory": inventory,
        "total_stock": sum(s["quantity"] for s in inventory),
    }


def catalogue_stats() -> dict[str, Any]:
    """Counts for the health check and the home page."""
    with connect() as conn:
        products = conn.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
        units = conn.execute("SELECT COALESCE(SUM(quantity), 0) FROM inventory").fetchone()[0]
        price = conn.execute("SELECT MIN(price), MAX(price) FROM catalogue").fetchone()
    return {
        "products": products,
        "units_in_stock": units,
        "price_min": price[0],
        "price_max": price[1],
    }


# --------------------------------------------------------------------------
# Users
#
# `password_hash` is deliberately absent from everything returned here except
# get_user_auth(), which exists only so the login route can verify a password.
# Nothing that reaches the frontend carries it.
# --------------------------------------------------------------------------

PUBLIC_USER_COLUMNS = "id, name, first_name, last_name, email, created_at"


def _public_user(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def normalize_email(email: str) -> str:
    """Emails are matched case-insensitively; the seed rows are all lowercase."""
    return email.strip().lower()


def email_taken(email: str) -> bool:
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (normalize_email(email),)
        ).fetchone()
    return row is not None


def get_user_auth(email: str) -> dict[str, Any] | None:
    """Row plus password_hash, for the login check only. Never serialised to JSON."""
    with connect() as conn:
        row = conn.execute(
            f"SELECT {PUBLIC_USER_COLUMNS}, password_hash FROM users WHERE email = ?",
            (normalize_email(email),),
        ).fetchone()
    if row is None:
        return None
    return {**_public_user(row), "password_hash": row["password_hash"]}


def get_user(user_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            f"SELECT {PUBLIC_USER_COLUMNS} FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return _public_user(row) if row else None


def create_user(
    first_name: str, last_name: str, email: str, password_hash: str
) -> dict[str, Any]:
    """Insert a new account. Raises sqlite3.IntegrityError if the email exists.

    `name` is NOT NULL in the schema and `first_name`/`last_name` were added
    later, so all three are written: `name` stays the display field, and the
    split fields match how the seed rows are populated.
    """
    first_name, last_name = first_name.strip(), last_name.strip()
    full_name = f"{first_name} {last_name}".strip()
    with connect_rw() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, normalize_email(email), password_hash, first_name, last_name),
        )
        conn.commit()
        new_id = cursor.lastrowid
    created = get_user(int(new_id))
    if created is None:  # pragma: no cover - the row was just written
        raise RuntimeError("Account was created but could not be read back.")
    return created


# --------------------------------------------------------------------------
# Chat history (Problem 8)
#
# Saved only for signed-in shoppers, in the existing `chat_messages` table, keyed
# by `user_id`. Every function here takes the user id the backend resolved from
# the session token — never an id supplied by the browser — so one account can
# never read another's conversation.
# --------------------------------------------------------------------------

# How many past turns to reload. Enough to restore a conversation without
# dragging an unbounded history into the model's context on every message.
HISTORY_LIMIT = 40


def save_chat_message(
    user_id: int, role: str, content: str, products: list[dict[str, Any]] | None = None
) -> int:
    """Append one turn to a signed-in shopper's history. Returns the new row id."""
    payload = json.dumps(products, ensure_ascii=False) if products else None
    with connect_rw() as conn:
        cursor = conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, payload),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_chat_history(user_id: int, limit: int = HISTORY_LIMIT) -> list[dict[str, Any]]:
    """A shopper's saved conversation, oldest first.

    Reads the most recent `limit` rows, then reverses them, so a long history is
    truncated at the start rather than the end — the recent turns are the ones
    that matter for continuing the conversation.
    """
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, role, content, products_json, created_at
            FROM chat_messages WHERE user_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    history = []
    for row in reversed(rows):
        products: list[dict[str, Any]] = []
        if row["products_json"]:
            try:
                loaded = json.loads(row["products_json"])
                products = loaded if isinstance(loaded, list) else []
            except json.JSONDecodeError:
                products = []
        history.append(
            {
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "products": products,
                "created_at": row["created_at"],
            }
        )
    return history


def clear_chat_history(user_id: int) -> int:
    """Delete one shopper's saved conversation. Returns how many rows went."""
    with connect_rw() as conn:
        cursor = conn.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount


# --------------------------------------------------------------------------
# Shared catalogue query (Problem 9)
#
# One definition of "find products", used by BOTH the Products page and the
# agent's search tool, so the page and the chatbot can never disagree about what
# is in a category or which item is cheapest.
#
# Filtering, ranking, and sorting all happen in SQL. That is not only faster: it
# is the fix for a real bug. The old tool scored 102 rows in Python, kept the top
# 6 by keyword relevance, and handed those to the agent — so "what's your
# cheapest hoodie?" was answered from whichever 6 happened to rank highest ($68)
# while $45 hoodies sat unseen. Sorting and price limits belong where the whole
# table is visible.
# --------------------------------------------------------------------------

# `garment_type` holds 22 spellings of about seven real categories. This CASE is
# the single place that folding is defined; `category` comes back as a real
# column, so filtering and display always agree. Order matters — first match
# wins — and the T-shirt test is `%t-shirt%` rather than `%tshirt%` because
# "sweatshirt" contains the latter.
CATEGORY_CASE = """
        CASE
          WHEN lower(c.garment_type) LIKE '%t-shirt%' THEN 't-shirt'
          WHEN lower(c.garment_type) LIKE '%crewneck%'
            OR lower(c.garment_type) LIKE '%crew-neck%' THEN 'crewneck'
          WHEN lower(c.garment_type) LIKE '%hood%' THEN 'hoodie'
          WHEN lower(c.garment_type) LIKE '%quarter-zip%'
            OR lower(c.garment_type) LIKE '%quarter zip%'
            OR lower(c.garment_type) LIKE '%1 4 zip%' THEN 'quarter-zip'
          WHEN lower(c.garment_type) LIKE '%jacket%' THEN 'jacket'
          WHEN lower(c.garment_type) LIKE '%long-sleeve%'
            OR lower(c.garment_type) LIKE '%performance shirt%' THEN 'long-sleeve shirt'
          WHEN lower(c.garment_type) LIKE '%mockneck%'
            OR lower(c.garment_type) LIKE '%mock-neck%' THEN 'mockneck'
          ELSE lower(c.garment_type)
        END
"""

SORTS = {
    "relevance": "score DESC, c.name ASC",
    "price_asc": "c.price ASC, c.name ASC",
    "price_desc": "c.price DESC, c.name ASC",
    "name": "c.name ASC",
}
DEFAULT_SORT = "name"

# Words that are noise in a shop search.
_SEARCH_STOPWORDS = {
    "a", "an", "and", "any", "are", "do", "does", "for", "got", "have", "how", "i",
    "in", "is", "it", "me", "much", "my", "of", "on", "or", "please", "show", "some",
    "the", "to", "want", "what", "with", "you", "your", "looking", "need", "campus",
    "customs", "yale", "buy", "get", "something", "anything", "there", "under", "below",
    "less", "than", "cheap", "cheapest", "most", "expensive", "price", "priced",
}


def search_terms(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return [w for w in words if w not in _SEARCH_STOPWORDS and len(w) > 1]


def query_products(
    q: str | None = None,
    category: str | None = None,
    categories: list[str] | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Filter, rank, and sort the catalogue in SQL.

    Returns the matching products plus `total` (how many matched overall, not
    just how many were returned) and `price_min` / `price_max` across *all*
    matches — so a caller showing 6 of 27 can still state the real cheapest price.
    """
    wanted = [c for c in ([category] if category else []) + (categories or []) if c]
    terms = search_terms(q) if q else []

    where: list[str] = []
    params: list[Any] = []

    if wanted:
        where.append(f"{CATEGORY_CASE.strip()} IN ({','.join('?' * len(wanted))})")
        params.extend(wanted)
    if min_price is not None:
        where.append("c.price >= ?")
        params.append(float(min_price))
    if max_price is not None:
        where.append("c.price <= ?")
        params.append(float(max_price))

    # Each term must appear somewhere; where it appears decides the score.
    haystack = (
        "lower(c.name || ' ' || c.garment_type || ' ' || c.description "
        "|| ' ' || c.colors || ' ' || c.search_tags)"
    )
    score_parts = ["0"]
    for term in terms:
        like = f"%{term}%"
        where.append(f"{haystack} LIKE ?")
        params.append(like)
        score_parts.append(
            "(CASE WHEN lower(c.name) LIKE ? THEN 3 "
            "WHEN lower(c.colors) LIKE ? THEN 2 "
            f"WHEN {CATEGORY_CASE.strip()} LIKE ? THEN 2 "
            "WHEN lower(c.search_tags) LIKE ? THEN 1 "
            "ELSE 0 END)"
        )
    score_params = [p for term in terms for p in ([f"%{term}%"] * 4)]

    sort_key = sort if sort in SORTS else ("relevance" if terms else DEFAULT_SORT)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
        SELECT c.product_id, c.name, c.garment_type, c.description, c.colors,
               c.search_tags, c.image_file_path, c.price,
               {CATEGORY_CASE.strip()} AS category,
               COALESCE(SUM(i.quantity), 0) AS total_stock,
               ({' + '.join(score_parts)}) AS score
        FROM catalogue c
        LEFT JOIN inventory i ON i.product_id = c.product_id
        {where_sql}
        GROUP BY c.product_id
        ORDER BY {SORTS[sort_key]}
    """
    # Score placeholders are bound before the WHERE ones: they appear earlier in
    # the statement.
    bound = score_params + params

    with connect() as conn:
        rows = conn.execute(sql, bound).fetchall()

    total = len(rows)
    prices = [r["price"] for r in rows]
    shown = rows[: int(limit)] if limit else rows

    products = []
    for r in shown:
        description, recorded = _described(r["description"])
        products.append(
            {
                "product_id": r["product_id"],
                "name": r["name"],
                "garment_type": r["garment_type"],
                "category": r["category"],
                "description": description,
                "description_recorded": recorded,
                "colors": _json_list(r["colors"]),
                "search_tags": _json_list(r["search_tags"]),
                "image_url": _image_url(r["image_file_path"]),
                "price": r["price"],
                "total_stock": r["total_stock"],
            }
        )

    return {
        "total": total,
        "returned": len(products),
        "products": products,
        "price_min": min(prices) if prices else None,
        "price_max": max(prices) if prices else None,
        "sort": sort_key,
    }


def category_counts() -> list[dict[str, Any]]:
    """Every category present, with how many products and the price range."""
    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT {CATEGORY_CASE.strip()} AS category, COUNT(*) AS count,
                   MIN(c.price) AS price_min, MAX(c.price) AS price_max
            FROM catalogue c GROUP BY category ORDER BY count DESC, category
            """
        ).fetchall()
    return [dict(r) for r in rows]

"""API response shapes.

Field names match the database columns wherever a column exists, so it stays
obvious which values are read from the catalogue and which are derived
(`image_url` from `image_file_path`, `total_stock` summed from `inventory`).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class ProductSummary(BaseModel):
    """A product card on the Products page."""

    product_id: str
    name: str
    garment_type: str
    description: str
    # False for the three products whose catalogue description is a build-failure
    # placeholder. The website shows a neutral line instead of the real text.
    description_recorded: bool = True
    colors: list[str] = []
    image_url: str
    price: float
    total_stock: int


class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductDetail(ProductSummary):
    """A single product's page: everything the catalogue holds, plus per-size stock."""

    search_tags: list[str] = []
    inventory: list[SizeStock] = []


class PageContextIn(BaseModel):
    """What the shopper is looking at, sent by the browser.

    Deliberately carries no identity and no product facts — only a route kind and
    a product id. The backend looks the product up in the catalogue, so a crafted
    request cannot assert a name or a price, and cannot name a different customer.
    """

    kind: Literal["home", "products", "product", "other"] = "other"
    product_id: str | None = None


class ChatRequest(BaseModel):
    message: str
    page: PageContextIn | None = None


# --------------------------------------------------------------------------
# Accounts
# --------------------------------------------------------------------------


class PublicUser(BaseModel):
    """What the frontend is allowed to see about an account.

    `password_hash` is deliberately not a field here. Because the login and
    signup routes declare this as their response model, FastAPI strips anything
    else, so a hash cannot reach the browser even by accident.
    """

    id: int
    name: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    created_at: str


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        if value != info.data.get("password"):
            raise ValueError("Passwords do not match.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """A successful login or signup: the session token plus the public user."""

    token: str
    user: PublicUser


# --------------------------------------------------------------------------
# Chat
# --------------------------------------------------------------------------


class ProductCard(BaseModel):
    """A product the assistant referred to, rendered as a card on the page.

    Built from rows the tools actually returned, never from anything the model
    wrote, so a card can never show an invented price, photo, or product. The
    fields are the ones the storefront's card component already renders, so a
    chat result and a Products-page tile are the same thing on screen.
    """

    product_id: str
    name: str
    price: float
    # Defaulted because saved history can contain cards written before this field
    # existed; a shopper's old conversation should still load.
    category: str = ""
    garment_type: str = ""
    description: str
    # Mirrors the storefront: three products have no real description, and the
    # card shows "Details coming soon" rather than inventing one.
    description_recorded: bool = True
    colors: list[str] = []
    image_url: str
    total_stock: int


class ChatResponse(BaseModel):
    """What the chat route returns to the website."""

    reply: str
    # Structured matches for the page to render. Not parsed out of `reply`.
    products: list[ProductCard] = []
    # The last search the agent ran and how many products matched in total, so
    # the page can caption honestly ("showing 6 of 27") instead of implying the
    # cards are the whole answer.
    search_query: str | None = None
    match_count: int | None = None
    # Which tools ran, in order — useful while developing and for the harness.
    tools_used: list[str] = []
    # Which model answered, and why the router picked it.
    model_used: str | None = None
    routed_as: str | None = None
    route_reason: str | None = None
    error: str | None = None


# --------------------------------------------------------------------------
# Catalogue lookup results (Problem 6)
#
# The tools return these rather than loose dicts so the agent sees a documented,
# validated shape every time. Two field conventions do real work here:
#
#   * a `status` enum rather than a bare boolean, so "out of stock" and "no such
#     product" cannot be confused with each other or with a missing value;
#   * an explicit `note` written in plain English, so when there is no answer the
#     agent has a true sentence to repeat instead of composing one itself.
# --------------------------------------------------------------------------


class ProductMatch(BaseModel):
    """One hit from a catalogue search."""

    product_id: str
    name: str
    price: float
    category: str
    garment_type: str
    description: str
    colors: list[str] = []
    image_url: str
    total_stock: int
    sizes_in_stock: list[str] = []


class ProductListResponse(BaseModel):
    """The Products page's filtered, sorted view of the catalogue."""

    total: int
    returned: int
    products: list[ProductSummary] = []
    price_min: float | None = None
    price_max: float | None = None
    sort: str = "name"


class CategoryInfo(BaseModel):
    category: str
    count: int
    price_min: float
    price_max: float


class ProductSearchResult(BaseModel):
    """What `search_products` gives back."""

    query: str
    match_count: int
    returned: int
    # Price range across EVERY match, not just the ones returned. This is what
    # lets the agent answer "what's your cheapest hoodie?" correctly while only
    # being shown six of them.
    price_min: float | None = None
    price_max: float | None = None
    sorted_by: str = "relevance"
    filters_applied: dict[str, Any] = {}
    products: list[ProductMatch] = []
    # True when more than one product matched. The prompt tells the agent to ask
    # which one the shopper means before quoting a price or a stock level.
    needs_disambiguation: bool = False
    # Shown when nothing matched, so "we don't carry that" can be followed by
    # what we do carry — from the catalogue, not from the agent's imagination.
    categories_we_carry: list[str] = []
    note: str = ""


class SizeStock(BaseModel):
    size: str
    quantity: int
    in_stock: bool


class ProductLookup(BaseModel):
    """Everything the catalogue holds about one product."""

    found: bool
    product_id: str
    name: str = ""
    price: float | None = None
    category: str = ""
    garment_type: str = ""
    description: str = ""
    colors: list[str] = []
    # Distinguishes "no colours recorded" from "colours not looked up". Three
    # catalogue rows have an empty colours array and the agent must say so
    # rather than infer a colour from the name or the photo.
    colors_recorded: bool = True
    # Three catalogue rows hold a build-failure placeholder instead of a real
    # description ("Vision blocked; filename-based stub"). Flagging it stops the
    # agent reading that stub out to a shopper as if it described the garment.
    description_recorded: bool = True
    search_tags: list[str] = []
    image_url: str = ""
    inventory: list[SizeStock] = []
    sizes_in_stock: list[str] = []
    sizes_out_of_stock: list[str] = []
    total_stock: int = 0
    note: str = ""


StockStatus = Literal["in_stock", "out_of_stock", "unknown_size", "unknown_product"]


class StockResult(BaseModel):
    """Stock for a product, or for one size of it."""

    found: bool
    product_id: str
    name: str = ""
    size: str | None = None
    quantity: int | None = None
    # A single field the agent can branch on. `out_of_stock` is its own value so
    # a zero quantity reads as a definite answer, never as missing data.
    status: StockStatus = "unknown_product"
    inventory: list[SizeStock] = []
    sizes_in_stock: list[str] = []
    other_sizes_in_stock: list[str] = []
    total_stock: int = 0
    note: str = ""



class ChatHistoryMessage(BaseModel):
    """One saved turn, as returned to the browser when a shopper signs back in."""

    id: int
    role: str
    content: str
    products: list[ProductCard] = []
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryMessage] = []

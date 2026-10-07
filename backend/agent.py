"""The Campus Customs shop assistant — PydanticAI agent wiring.

Loads the system prompt from `prompts/prompt.md`, registers the three catalogue
tools from `tools.py`, and runs a Claude model through the official Anthropic
SDK. The API key is read from the environment (`.env`), never hard-coded.

The product cards returned alongside a reply are collected from what the tools
actually returned during the run, not from anything the model wrote. That is
deliberate: the model chooses which products to talk about, but it cannot invent
one into the card list.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Resolved from this file, not the working directory, so `uvicorn main:app` from
# backend/ and `python backend/agent.py` from the project root both work.
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
for candidate in (PROJECT_ROOT / ".env", PROJECT_ROOT.parent / ".env"):
    if candidate.exists():
        load_dotenv(candidate, override=False)

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from pydantic_ai import Agent, RunContext  # noqa: E402
from pydantic_ai.messages import (  # noqa: E402
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings  # noqa: E402
from pydantic_ai.providers.anthropic import AnthropicProvider  # noqa: E402
from pydantic_ai.usage import UsageLimits  # noqa: E402

import audit  # noqa: E402
import routing  # noqa: E402
import tools  # noqa: E402
from models import (  # noqa: E402
    ProductCard,
    ProductLookup,
    ProductSearchResult,
    StockResult,
)

PROMPT_PATH = HERE / "prompts" / "prompt.md"
MODEL_NAME = os.getenv("MODEL_NAME", "claude-opus-5").strip() or "claude-opus-5"

# A shop answer is short; the ceiling only needs to cover thinking plus a
# paragraph. Requests are capped so one message cannot loop through tools forever.
MAX_OUTPUT_TOKENS = 4_000
# Model requests per message. PydanticAI raises once this is hit, which bounds a
# runaway loop at the framework level.
MAX_REQUESTS = 8
# Tool calls per message, counted here. A shop question needs two or three; more
# than this is a loop, and the cap turns it into a clear refusal the agent can
# read rather than an error the shopper sees.
MAX_TOOL_CALLS = 6


class AgentNotConfigured(RuntimeError):
    """Raised when ANTHROPIC_API_KEY is missing, so the route can explain itself."""


@dataclass
class Customer:
    """The signed-in shopper, as resolved by the backend from the session token.

    Never built from anything the browser sent. A guest is represented by this
    being None, not by an empty Customer.
    """

    id: int
    name: str
    first_name: str | None
    email: str


@dataclass
class PageContext:
    """What the shopper is looking at, so "this" and "it" resolve.

    The browser sends only the route and a product id; the product's details are
    read from the catalogue here, so the page cannot assert a price or a name.
    """

    kind: str = "other"           # "home" | "products" | "product" | "other"
    product_id: str | None = None
    product_name: str | None = None
    product_price: float | None = None
    product_category: str | None = None

    def describe(self) -> str:
        if self.kind == "product" and self.product_name:
            price = f" (${self.product_price:.2f})" if self.product_price is not None else ""
            return (
                f'The shopper is looking at the product page for "{self.product_name}"'
                f"{price}, product_id `{self.product_id}`. If they say "
                f'"this", "it", or "this one" without naming a product, they mean that one.'
            )
        if self.kind == "products":
            return "The shopper is browsing the full Products listing."
        if self.kind == "home":
            return "The shopper is on the home page."
        return ""


@dataclass
class ShopDeps:
    """Per-conversation state. `seen` collects the products the tools returned."""

    customer: Customer | None = None
    page: PageContext = field(default_factory=PageContext)
    run_id: str = ""
    tool_calls: int = 0

    def budget_left(self) -> bool:
        """False once this message has used its tool-call allowance."""
        return self.tool_calls < MAX_TOOL_CALLS

    seen: dict[str, dict[str, Any]] = field(default_factory=dict)
    tools_used: list[str] = field(default_factory=list)
    # The most recent search, for the caption on the page.
    last_query: str | None = None
    last_match_count: int | None = None
    # Search hits in rank order, so the page can show the catalogue's best
    # matches even when the reply only names two or three of them.
    last_results: list[dict[str, Any]] = field(default_factory=list)
    # Products the agent looked up individually. Calling get_product_details or
    # check_stock on one product is a much stronger signal that the question is
    # about that product than trying to spot its name in the reply text.
    focus_ids: list[str] = field(default_factory=list)

    def remember(self, product: dict[str, Any] | None) -> None:
        if product and product.get("product_id"):
            self.seen.setdefault(product["product_id"], product)


def _api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise AgentNotConfigured(
            "ANTHROPIC_API_KEY is not set. Put it in the project's .env file."
        )
    return key


@lru_cache(maxsize=4)
def _build_model(model_name: str = "") -> AnthropicModel:
    """One configured client per model. Cached — routing switches between them
    on every message, and rebuilding a client each time is pure waste."""
    return AnthropicModel(
        model_name or MODEL_NAME,
        provider=AnthropicProvider(api_key=_api_key()),
        settings=AnthropicModelSettings(max_tokens=MAX_OUTPUT_TOKENS),
    )


shop_agent = Agent(
    deps_type=ShopDeps,
    output_type=str,
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
    name="campus_customs_shop_assistant",
)


@shop_agent.instructions
def customer_context(ctx: RunContext[ShopDeps]) -> str:
    """Who is chatting. Appended to the prompt file's instructions each run.

    This is the PydanticAI pattern for per-run context: the static prompt lives in
    prompts/prompt.md, and anything that changes per conversation arrives through
    deps and is rendered here.
    """
    customer = ctx.deps.customer
    if customer is None:
        return (
            "## Who you are talking to\n\n"
            "A guest — nobody is signed in. You do not know their name, their email, "
            "or anything about them. Do not ask for personal details, and do not "
            "guess at who they are. If something needs an account, say they can "
            "create one or log in."
        )
    return (
        "## Who you are talking to\n\n"
        f"A signed-in customer: {customer.name} ({customer.email}).\n\n"
        f"You may greet them by their first name ({customer.first_name or customer.name}) "
        "once, naturally, and you may refer back to earlier messages in this "
        "conversation. Do not read their email address out to them, do not recite "
        "their details back, and never mention any other customer."
    )


@shop_agent.instructions
def page_context(ctx: RunContext[ShopDeps]) -> str:
    """What the shopper is currently looking at."""
    described = ctx.deps.page.describe()
    if not described:
        return ""
    return f"## What they are looking at\n\n{described}"


# --------------------------------------------------------------------------
# Tools. Each one records what it returned so the reply can carry real cards.
# --------------------------------------------------------------------------


def _tool_budget_spent(ctx: RunContext[ShopDeps], tool: str) -> dict:
    """What any tool returns once the per-message allowance is gone.

    A plain dict rather than one of the result models: all three tools share this
    path, and the agent only needs the note to know it should stop calling tools
    and answer with what it has.
    """
    audit.log_tool_call(ctx.deps.run_id, tool, {}, {}, stop_reason="tool_limit_reached")
    return {
        "limit_reached": True,
        "note": (
            f"Tool limit reached for this message ({MAX_TOOL_CALLS} calls). "
            "Answer from what you already have, or ask the shopper to narrow it down."
        ),
    }


@shop_agent.tool
def search_products(
    ctx: RunContext[ShopDeps],
    query: str = "",
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
) -> ProductSearchResult:
    """Find Campus Customs products by words, category, and price.

    Use this first for any product question — it is how you get the `product_id`
    the other two tools need. If `needs_disambiguation` is true, more than one
    product matched: ask the shopper which one they mean before quoting a price
    or a stock level for a single item.

    Filtering and sorting run in SQL over the whole catalogue, so `price_min` and
    `price_max` describe **every** match even when only a few products come back.
    For "what's your cheapest X", pass `sort="price_asc"` — the first result is
    then genuinely the cheapest, not the cheapest of the handful you were shown.

    Args:
        query: words the shopper used — a colour, a team, a college, a graphic.
        category: one of t-shirt, crewneck, hoodie, quarter-zip, jacket,
            long-sleeve shirt, mockneck. Use it when they name a kind of garment.
        min_price: only products at or above this price.
        max_price: only products at or below this price — use it for
            "under $50", "nothing over $60".
        sort: "price_asc" (cheapest first), "price_desc" (most expensive first),
            "name", or "relevance" (the default when there is a query).
    """
    if not ctx.deps.budget_left():
        return _tool_budget_spent(ctx, "search_products")
    ctx.deps.tool_calls += 1
    ctx.deps.tools_used.append("search_products")
    result = tools.search_products(
        query, category=category, min_price=min_price, max_price=max_price, sort=sort
    )
    audit.log_tool_call(
        ctx.deps.run_id, "search_products",
        {"query": query, "category": category, "min_price": min_price,
         "max_price": max_price, "sort": sort},
        {"match_count": result.match_count, "returned": result.returned,
         "price_min": result.price_min, "price_max": result.price_max},
    )
    # The agent can search by category alone ("hoodie") with no free text, in
    # which case the page caption had nothing to name. Fall back to whatever was
    # actually filtered on so the heading reads "Matches for 'hoodie'".
    label = query.strip() or category or ""
    if not label and (min_price is not None or max_price is not None):
        bounds = []
        if min_price is not None:
            bounds.append(f"over ${min_price:g}")
        if max_price is not None:
            bounds.append(f"under ${max_price:g}")
        label = " and ".join(bounds)
    ctx.deps.last_query = label or None
    ctx.deps.last_match_count = result.match_count
    ctx.deps.last_results = [p.model_dump() for p in result.products]
    for product in ctx.deps.last_results:
        ctx.deps.remember(product)
    return result


@shop_agent.tool
def get_product_details(ctx: RunContext[ShopDeps], product_id: str) -> ProductLookup:
    """Get everything the catalogue holds about one product.

    Returns the description, price, colours, and stock for every size. If
    `colors_recorded` is false, the catalogue has no colours for that product —
    say so rather than inferring one.

    Args:
        product_id: the slug from a search result, e.g. "basic-hoodie-big-yale".
    """
    if not ctx.deps.budget_left():
        return _tool_budget_spent(ctx, "get_product_details")
    ctx.deps.tool_calls += 1
    ctx.deps.tools_used.append("get_product_details")
    result = tools.get_product_details(product_id)
    audit.log_tool_call(
        ctx.deps.run_id, "get_product_details", {"product_id": product_id},
        {"found": result.found, "price": result.price, "total_stock": result.total_stock,
         "sizes_in_stock": result.sizes_in_stock},
    )
    if result.found:
        ctx.deps.remember(result.model_dump())
        if result.product_id not in ctx.deps.focus_ids:
            ctx.deps.focus_ids.append(result.product_id)
    return result


@shop_agent.tool
def check_stock(
    ctx: RunContext[ShopDeps], product_id: str, size: str | None = None
) -> StockResult:
    """Check stock for a product, either every size or one specific size.

    Read `status`: "in_stock", "out_of_stock", "unknown_size", or
    "unknown_product". When it is "out_of_stock", tell the shopper plainly that
    the size is out of stock, and offer `other_sizes_in_stock` if there are any.

    Args:
        product_id: the slug from a search result.
        size: one of XS, S, M, L, XL, XXL. Omit to get every size.
    """
    if not ctx.deps.budget_left():
        return _tool_budget_spent(ctx, "check_stock")
    ctx.deps.tool_calls += 1
    ctx.deps.tools_used.append("check_stock")
    result = tools.check_stock(product_id, size)
    audit.log_tool_call(
        ctx.deps.run_id, "check_stock", {"product_id": product_id, "size": size},
        {"status": result.status, "quantity": result.quantity,
         "sizes_in_stock": result.sizes_in_stock},
    )
    if result.found and result.product_id not in ctx.deps.focus_ids:
        ctx.deps.focus_ids.append(result.product_id)
    return result


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


MAX_CARDS = 6
NAME_MATCH_RATIO = 0.6


def _mentions(reply_words: set[str], name: str) -> bool:
    """Is this product named in the reply?

    An exact name match is too strict: the catalogue calls one product
    "Champion Reverse Weave Hoodie 1" and the assistant sensibly writes
    "the Champion Reverse Weave", which would then lose its card. Matching on a
    majority of the name's words handles that without matching everything —
    a shared word like "hoodie" alone is nowhere near the threshold.
    """
    tokens = [t for t in re.findall(r"[a-z0-9]+", name.lower()) if len(t) > 1]
    if not tokens:
        return False
    hits = sum(1 for t in tokens if t in reply_words)
    return hits >= 2 and hits / len(tokens) >= NAME_MATCH_RATIO


def _cards_for(reply: str, deps: ShopDeps) -> list[ProductCard]:
    """Cards for the products the reply actually mentions.

    A run can touch a dozen products while narrowing down; showing all of them
    would not match what the shopper just read. The data still comes from the
    tool results rather than from the model's text, so a card cannot show an
    invented product or price.
    """
    reply_words = set(re.findall(r"[a-z0-9]+", reply.lower()))
    mentioned = [p for p in deps.seen.values() if _mentions(reply_words, p["name"])]

    # 1. The agent looked specific products up, so the question was about those:
    #    feature them. The prompt tells it to make that call for a single-product
    #    question, which is a far more reliable signal than spotting a name in
    #    the reply text.
    # 2. Otherwise this is a browsing answer. The prompt tells the agent to
    #    describe the range and let the cards do the listing, so it writes
    #    "here are six of them" — showing only the one or two it happened to name
    #    would contradict the sentence the shopper just read.
    # 3. No search at all (a follow-up): fall back to whatever was named.
    focused = [deps.seen[pid] for pid in deps.focus_ids if pid in deps.seen]
    if focused:
        chosen = focused
    elif deps.last_results:
        chosen = deps.last_results
    else:
        chosen = mentioned or list(deps.seen.values())
    chosen = chosen[:MAX_CARDS]
    return [
        ProductCard(
            product_id=p["product_id"],
            name=p["name"],
            price=p["price"],
            category=p.get("category", ""),
            garment_type=p.get("garment_type", ""),
            description=p.get("description", ""),
            description_recorded=p.get("description_recorded", True),
            colors=p.get("colors", []),
            image_url=p["image_url"],
            total_stock=p.get("total_stock", 0),
        )
        for p in chosen
    ]


def _replay(history: list[dict[str, Any]]) -> list[ModelMessage]:
    """Turn saved rows back into PydanticAI messages.

    Only the text is replayed. Tool calls and their results are deliberately not
    reconstructed: stock and prices move, and a stale tool result presented as
    this run's evidence is exactly the invented answer this project forbids. The
    agent re-queries the catalogue for anything it needs to state again.
    """
    messages: list[ModelMessage] = []
    for row in history:
        content = (row.get("content") or "").strip()
        if not content:
            continue
        if row.get("role") == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        elif row.get("role") == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=content)]))
    # A conversation replayed to a model has to start with a request, or the
    # first turn reads as an answer to nothing.
    while messages and isinstance(messages[0], ModelResponse):
        messages.pop(0)
    return messages


async def answer(
    message: str,
    *,
    customer: Customer | None = None,
    page: PageContext | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run one shopper message through the agent.

    `customer` is resolved by the caller from the session token, never from the
    request body. Returns a dict matching ChatResponse; failures come back as a
    readable message rather than an exception, so the chat panel always has
    something to show.
    """
    run_id = audit.new_run_id()
    deps = ShopDeps(customer=customer, page=page or PageContext(), run_id=run_id)
    route = routing.choose_model(message, has_history=bool(history))
    started = time.perf_counter()

    def record(stop_reason: str, products: int = 0) -> None:
        """One run_end record, whatever happened. No message or reply text."""
        audit.log_run(
            run_id,
            model=route.model,
            routed_as=route.tier,
            route_reason=route.reason,
            signed_in=customer is not None,
            page_kind=deps.page.kind,
            tool_calls=deps.tool_calls,
            tools_used=deps.tools_used,
            products_returned=products,
            seconds=time.perf_counter() - started,
            stop_reason=stop_reason,
        )

    try:
        run = await shop_agent.run(
            message,
            deps=deps,
            model=_build_model(route.model),
            message_history=_replay(history or []),
            usage_limits=UsageLimits(request_limit=MAX_REQUESTS),
        )
    except AgentNotConfigured as exc:
        record("error: not configured")
        return {
            "reply": "The shop assistant isn't configured yet, so I can't answer right now.",
            "products": [],
            "tools_used": [],
            "model_used": route.model,
            "routed_as": route.tier,
            "error": str(exc),
        }
    except Exception as exc:  # the panel should degrade, not crash
        record(f"error: {type(exc).__name__}")
        return {
            "reply": (
                "Sorry — I couldn't reach the catalogue just then. Please try again in a moment."
            ),
            "products": [],
            "tools_used": deps.tools_used,
            "model_used": route.model,
            "routed_as": route.tier,
            "error": f"{type(exc).__name__}: {exc}"[:300],
        }

    reply = run.output.strip()
    cards = [card.model_dump() for card in _cards_for(reply, deps)]
    record(
        "tool_limit_reached" if deps.tool_calls >= MAX_TOOL_CALLS else "completed",
        products=len(cards),
    )
    return {
        "reply": reply,
        "products": cards,
        "search_query": deps.last_query,
        "match_count": deps.last_match_count,
        "tools_used": deps.tools_used,
        "model_used": route.model,
        "routed_as": route.tier,
        "route_reason": route.reason,
        "error": None,
    }

"""Campus Customs API — routes only.

Run from this directory:
  uvicorn main:app --host 127.0.0.1 --port 8000

Frontend (Vite): http://localhost:5173

Problem 3 scope: serve the catalogue and the product images so the storefront has
real data. The chat endpoint is a stub that returns a fixed message; the
PydanticAI agent arrives in a later problem and replaces its body, not its shape.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

import agent
import auth
import db
from models import (
    AuthResponse,
    CategoryInfo,
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    LoginRequest,
    ProductDetail,
    ProductListResponse,
    ProductSummary,
    PublicUser,
    SignupRequest,
)

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
load_dotenv(PROJECT_ROOT / ".env")

BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

app = FastAPI(title="Campus Customs", version="0.3.0")

# The Vite dev server runs on a different port, so the browser needs CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product photos live in the gitignored data/ folder; serving them from there
# keeps the images out of the repo while still letting the site show them.
# The path matches the catalogue's image_file_path: products/<id>.jpg -> /media/products/<id>.jpg
if db.DATA_DIR.exists():
    app.mount("/media", StaticFiles(directory=db.DATA_DIR), name="media")


@app.get("/api/health")
def health():
    try:
        stats = db.catalogue_stats()
    except db.DatabaseMissing as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "db": db.DB_PATH.name, **stats}


@app.get("/api/categories", response_model=list[CategoryInfo])
def categories():
    """Categories present in the catalogue, with counts and price ranges.

    Feeds the Products page filter, so the options shown are always the ones that
    actually exist rather than a hard-coded list.
    """
    try:
        return db.category_counts()
    except db.DatabaseMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/products", response_model=ProductListResponse)
def products(
    q: str | None = Query(default=None, description="Free-text search"),
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    sort: str | None = Query(default=None, description="relevance|price_asc|price_desc|name"),
    limit: int | None = Query(default=None, ge=1, le=200),
):
    """The catalogue, filtered and sorted in SQL.

    Runs `db.query_products` — the same function behind the agent's search tool,
    so a shopper filtering the page and a shopper asking the chatbot get the same
    products in the same order.
    """
    try:
        return db.query_products(
            q=q, category=category, min_price=min_price,
            max_price=max_price, sort=sort, limit=limit,
        )
    except db.DatabaseMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def product(product_id: str):
    """One product. 404 rather than an invented row when the id is unknown."""
    try:
        found = db.get_product(product_id)
    except db.DatabaseMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if found is None:
        raise HTTPException(status_code=404, detail=f"No product with id {product_id!r}")
    return found


# --------------------------------------------------------------------------
# Accounts
#
# Every response here is declared as PublicUser or AuthResponse, neither of
# which has a password_hash field, so the hash cannot leak to the browser.
# --------------------------------------------------------------------------

INVALID_CREDENTIALS = "Invalid email or password."


def optional_user(authorization: str = Header(default="")) -> dict | None:
    """Resolve `Authorization: Bearer <token>` to a user, or None for a guest.

    This is the only way the backend learns who is chatting. The request body is
    never consulted for identity, so a crafted request cannot claim to be another
    customer or read their history: the signature on the token is what decides.
    """
    token = authorization[7:] if authorization.lower().startswith("bearer ") else ""
    user_id = auth.read_token(token)
    return db.get_user(user_id) if user_id is not None else None


def current_user(authorization: str = Header(default="")) -> dict:
    """Same, but 401 for a guest — used by routes that require an account."""
    user = optional_user(authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    return user


@app.post("/api/auth/signup", response_model=AuthResponse, status_code=201)
def signup(body: SignupRequest):
    """Create an account. 409 if the email is already registered.

    Password/confirm matching and the 8-character minimum are enforced by
    SignupRequest, so a mismatch never reaches this function.
    """
    if db.email_taken(body.email):
        raise HTTPException(
            status_code=409, detail="That email is already registered. Try logging in instead."
        )
    try:
        user = db.create_user(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            password_hash=auth.hash_password(body.password),
        )
    except sqlite3.IntegrityError:
        # The UNIQUE constraint is the real guard: two simultaneous signups can
        # both pass the check above, and only one of them can win here.
        raise HTTPException(
            status_code=409, detail="That email is already registered. Try logging in instead."
        ) from None
    return AuthResponse(token=auth.issue_token(user["id"]), user=PublicUser(**user))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest):
    """Log in with email and password.

    An unknown email and a wrong password return the same message on purpose:
    a different one would let anyone test which addresses have accounts.
    """
    record = db.get_user_auth(body.email)
    if record is None or not auth.verify_password(body.password, record["password_hash"]):
        raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)
    public = {k: v for k, v in record.items() if k != "password_hash"}
    return AuthResponse(token=auth.issue_token(public["id"]), user=PublicUser(**public))


@app.get("/api/auth/me", response_model=PublicUser)
def me(user: dict = Depends(current_user)):
    """Who the current token belongs to — lets the frontend restore a session."""
    return PublicUser(**user)


def _page_context(page) -> agent.PageContext:
    """Build the agent's page context, reading product facts from the catalogue.

    The browser supplies a route kind and a product id; everything the agent is
    told about that product comes from the database.
    """
    if page is None:
        return agent.PageContext()
    if page.kind != "product" or not page.product_id:
        return agent.PageContext(kind=page.kind)
    product = db.get_product(page.product_id)
    if product is None:
        return agent.PageContext(kind="products")
    return agent.PageContext(
        kind="product",
        product_id=product["product_id"],
        product_name=product["name"],
        product_price=product["price"],
        product_category=product["garment_type"],
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user: dict | None = Depends(optional_user)):
    """Send a shopper's message to the PydanticAI agent and return its reply.

    Signed in, the agent is told who it is talking to and the conversation is
    saved to `chat_messages`. As a guest it still works; nothing is stored.
    Identity comes from the session token via `optional_user`, never from the
    request body.
    """
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    customer = None
    history: list[dict] = []
    if user is not None:
        customer = agent.Customer(
            id=user["id"],
            name=user["name"],
            first_name=user.get("first_name"),
            email=user["email"],
        )
        history = db.get_chat_history(user["id"])

    result = await agent.answer(
        message,
        customer=customer,
        page=_page_context(body.page),
        history=history,
    )

    if user is not None:
        # Saved after the run so a failed turn does not leave a question with no
        # answer in the shopper's history.
        db.save_chat_message(user["id"], "user", message)
        db.save_chat_message(user["id"], "assistant", result["reply"], result.get("products"))

    return ChatResponse(**result)


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def chat_history(user: dict = Depends(current_user)):
    """The signed-in shopper's saved conversation.

    Scoped to the id resolved from the token, so there is no parameter through
    which another customer's history could be requested.
    """
    messages = []
    for row in db.get_chat_history(user["id"]):
        try:
            messages.append(ChatHistoryMessage(**row))
        except ValidationError:
            # A row saved by an earlier version of the app whose product cards no
            # longer validate. Keep the text — losing the whole conversation over
            # one stale attachment would be worse.
            messages.append(ChatHistoryMessage(**{**row, "products": []}))
    return ChatHistoryResponse(messages=messages)


@app.delete("/api/chat/history", status_code=204)
def clear_chat_history(user: dict = Depends(current_user)):
    """Let a shopper clear their own saved conversation."""
    db.clear_chat_history(user["id"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=BACKEND_PORT, reload=False)

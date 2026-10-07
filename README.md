# Campus Customs — Yale Bulldog Blue

A customer-facing storefront for Campus Customs, the company behind Yale Bulldog
Blue. React + Vite + TypeScript on the front, FastAPI on the back, and a
PydanticAI shop assistant that answers questions about products, prices, sizes
and stock **from the catalogue database only** — and says so plainly when the
answer is not in there.

Yale SOM · MGT 409 · Assignment 4.

---

## What it does

- **Browse** 102 products with search, category and price filters, and sorting.
- **Accounts** — create one, log in, stay signed in; passwords hashed with
  PBKDF2-SHA256 in the format the seed database already uses.
- **Ask the Librarian** — a chat assistant that searches the catalogue, answers
  with real prices and stock, renders the matching products as cards on the page,
  and remembers a signed-in shopper's conversation.
- **Honest by construction** — the agent has no SQL access, only three narrow
  tools, and the product cards are built from the database rows those tools
  returned rather than from anything the model wrote.

---

## 1. Put the data pack in place

The database and the product photos are **not in this repository**. Copy the data
pack from the assignment materials into the project root so it looks like this:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/            # 102 .jpg files referenced by the catalogue
```

The backend reads `data/campus_customs.db` and serves the photos from
`data/products/`, both resolved relative to the source files rather than the
working directory — so it does not matter which folder you start the server from.

## 2. Add your API key

Copy the example env file and fill in your own values:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...        # your own key
MODEL_NAME=claude-opus-5
FAST_MODEL_NAME=claude-haiku-4-5
SESSION_SECRET=<random hex>         # python3 -c "import secrets;print(secrets.token_hex(32))"
BACKEND_PORT=8000
```

`.env` is gitignored and must never be committed. Without `SESSION_SECRET` the
app still runs, but a backend restart signs everyone out.

## 3. Run the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Check it came up: <http://127.0.0.1:8000/api/health> should report
`"ok": true` and `"products": 102`.

## 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **<http://localhost:5173>**. Vite proxies `/api` and `/media` to the backend
on port 8000, so the browser only ever talks to one origin.

### Stopping

```bash
pkill -f "uvicorn main:app"
pkill -f vite
```

### A test account

The seed database ships with one:

```
test@campuscustoms.yale.edu  /  password
```

---

## Layout

```
hw4/
├── AI_prompts.md          word-for-word log of every prompt given to the AI
├── requirements.txt       Python dependencies (backend/ includes this file)
├── .env.example           placeholders only — copy to .env
├── .gitignore
├── README.md
├── frontend/              Vite + React + TypeScript
├── backend/
│   ├── main.py            FastAPI app — uvicorn main:app --reload
│   ├── agent.py           PydanticAI agent wiring, model routing, product cards
│   ├── tools.py           the three catalogue tools
│   ├── models.py          Pydantic request/response types
│   ├── db.py              all SQLite access (read-only for the catalogue)
│   ├── auth.py            password hashing and session tokens
│   ├── routing.py         picks the model per message
│   ├── audit.py           append-only audit trail
│   └── prompts/prompt.md  the agent's system prompt
├── output/
│   ├── harness.md         how the application works, end to end
│   ├── design.md          the visual design and why
│   ├── usability.md       the Problem 9 improvements
│   ├── app_check.html     screenshots of the running site, with captions
│   ├── app_check_images/
│   └── audit_trail.json   append-only record of agent activity
└── data/                  LOCAL ONLY — never committed
```

**[output/harness.md](output/harness.md)** is the place to start: it documents the
database, the agent's tools and safety rules, the model fields, the loop limits
and result caps, and how everything fits together.

---

## Notes

- **Models.** `claude-opus-5` for real questions, `claude-haiku-4-5` for small talk
  and single lookups, chosen per message by a rules-only router — no extra model
  call. The chat panel shows which model answered.
- **Privacy.** The signed-in shopper is resolved from a signed session token, never
  from anything the browser sends, so no request can claim to be another customer.
  `output/audit_trail.json` records tool calls and outcomes but no message text,
  names, emails, hashes or keys.
- **Nothing is for sale.** This is coursework; there is no checkout.

# Usability improvements (Problem 9)

Four changes: two a shopper can see on the page, two behind it. Each is listed with
what it does and why it is worth having.

---

## 1. Filter and sort on the Products page

**What.** A row of controls above the grid: category (with live counts, read from
the catalogue rather than hard-coded), a price band, and a sort — name, price low
to high, price high to low, or best match. A Reset button appears once anything is
set, and a line under the controls reports what you are looking at:
*"27 products · $45.00 – $88.00"*.

**Why it helps.** 102 products in one unsorted grid is a wall. Someone who knows
they want a hoodie under $70 previously had to scroll and read every price. Now
it is two clicks. The price range in the result line also answers the question
behind the question — "what does a hoodie here cost?" — without opening anything.

For the business: shoppers who can narrow to their budget see fewer items they
will not buy, and the category counts quietly advertise range ("hoodie (27)").

---

## 2. Search bar on the Products page

**What.** A search box that matches across product name, category, colours,
description, and search tags. Typing is debounced, so a search is one request per
pause rather than one per keystroke, and typing switches the sort to best-match
automatically unless you have chosen a sort yourself.

**Why it helps.** The chatbot was the only way to search. That is a lot of
ceremony for "bulldog", and it costs a model call and several seconds. Searching
the page is instant, free, and the thing most shoppers reach for first. The
chatbot is then left for the questions it is actually better at — "will this be
warm enough", "what would suit my daughter" — rather than acting as a search box
with a four-second delay.

---

## 3. Shared SQL product query — and the bug it fixed

**What.** One function, `db.query_products`, now does all catalogue searching:
text matching, category folding, price limits, ranking, and sorting, in SQL. Both
the Products page (`GET /api/products`) and the agent's `search_products` tool
call it. The agent's tool gained `category`, `min_price`, `max_price`, and `sort`
arguments, and its result now reports the price range across **every** match, not
just the handful returned.

**Why it helps — this was a real bug, not a tidy-up.** The old tool scored all 102
products in Python, kept the top 6 by keyword relevance, and showed the agent only
those. So:

> **"What's your cheapest hoodie?"**
> Before: *"$68"* — the cheapest of the six it happened to be shown.
> Actually: **$45** (Ua Gameday Double Knit Hood, Yale Sports Hoodie Tennis).

Nothing was invented, every number was real, and the answer was still wrong — the
hardest kind of error to catch. Sorting and price limits belong where the whole
table is visible, so they moved into SQL. The agent now answers *"Our cheapest
hoodies are $45 — the Under Armour Gameday double-knit in navy and the Yale Tennis
pullover."*

Sharing the query has a second payoff: the page and the chatbot cannot disagree.
Asked for hoodies under $50, both return exactly `Ua Gameday Double Knit Hood` and
`Yale Sports Hoodie Tennis` — verified side by side. A shopper who filters the
page and then asks the assistant gets one answer, not two.

The 22 spellings of `garment_type` are folded into seven categories by a single
SQL `CASE`, checked to agree with the previous Python folding on all 102 rows.

---

## 4. Model routing: cheap model for easy turns

**What.** `backend/routing.py` picks the model per message. Small talk and single
factual lookups go to **Haiku 4.5**; comparisons, recommendations, compound
questions, long messages, and anything unrecognised go to **Opus 5**. The
classifier is rules only — no model call, because routing that needed its own
request would spend most of what it saves. The chat panel shows which model
answered, so the routing is visible in the running app.

**Why it helps.** Measured before this change, a shopper typing "hi" cost a full
Opus call:

| Message | Before | After |
|---|---|---|
| "hi" | 4.0 s, Opus | **1.3 s, Haiku** |
| "do you have anything under $50?" | Opus | 2.5 s, Haiku |
| "what's your cheapest hoodie?" | Opus | Opus (unchanged — it should be) |

Three times faster on the turns where speed is most obvious, at roughly a
fifteenth of Opus's per-token price. For a storefront where a lot of traffic is
greetings and one-line stock checks, that is most of the volume at a fraction of
the cost.

The classifier is deliberately cautious: anything it does not clearly recognise as
simple goes to the strong model. The failure mode is "we paid more than we needed
to", never "a hard question got the weak model".

---

## What was deliberately not done

**Parallelising the database queries** was on the list and is not worth it here.
Measured: a chat turn takes 4–6 seconds, of which the database is about **2 ms**.
Optimising 0.04% of the latency would add concurrency to code that is currently
easy to read, for no gain a shopper could perceive. Worth revisiting only if the
catalogue moves to a network database.

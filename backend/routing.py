"""Pick a model for each message (Problem 9).

A shopper saying "hi" does not need the flagship model, but it was getting one:
a full Opus call, about four seconds and Opus pricing, to say hello back. This
module decides which model handles a turn.

The classifier is **rules only, no model call** — routing that needed its own LLM
request would spend most of what the routing saves. It is deliberately cautious:
anything it does not clearly recognise as simple goes to the strong model, so the
failure mode is "we paid more than we needed to", never "a hard question got the
weak model".

Haiku 4.5 note: it rejects `thinking` with a 400, which is why `agent.build_model`
only attaches thinking settings to models that support it.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

STRONG_MODEL = os.getenv("MODEL_NAME", "claude-opus-5").strip() or "claude-opus-5"
FAST_MODEL = os.getenv("FAST_MODEL_NAME", "claude-haiku-4-5").strip() or "claude-haiku-4-5"

# Greetings, thanks, goodbyes — conversation with no catalogue question in it.
_SMALL_TALK = re.compile(
    r"^(hi|hey|hello|yo|howdy|good (morning|afternoon|evening)|thanks?|thank you|"
    r"ta|cheers|bye|goodbye|see ya|ok(ay)?|cool|nice|great|got it|sounds good|"
    r"no thanks|nope|yep|yes|no)\b[\s!.,?]*$",
    re.IGNORECASE,
)

# A single, concrete lookup: one product, one fact.
_SIMPLE_LOOKUP = re.compile(
    r"^(how much|what'?s the price|price of|do you have|have you got|is the|"
    r"is this|is it|what sizes?|in stock|any .{0,20}in stock)\b",
    re.IGNORECASE,
)

# Anything that needs weighing, comparing, or judgement.
_NEEDS_REASONING = re.compile(
    r"\b(compare|versus|vs\.?|difference|better|best|recommend|suggest|should i|"
    r"which (one|should)|help me (choose|decide|pick)|gift|present|warm(est)?|"
    r"for my|what would|opinion|advice|instead|alternative|similar to|"
    r"and also|as well as)\b",
    re.IGNORECASE,
)

# "do you have anything under $50 and is it in stock in XL?" is two lookups and
# a decision about how to answer both — it reads as simple but isn't.
_COMPOUND = re.compile(
    r"\band (is|are|do|does|can|could|what|how|which|whether|will)\b", re.IGNORECASE
)

MAX_SIMPLE_WORDS = 14


@dataclass
class Route:
    model: str
    tier: str          # "fast" | "strong"
    reason: str

    @property
    def is_fast(self) -> bool:
        return self.tier == "fast"


def choose_model(message: str, *, has_history: bool = False) -> Route:
    """Decide which model answers this message."""
    text = (message or "").strip()
    words = len(text.split())

    if not text:
        return Route(FAST_MODEL, "fast", "empty message")

    if _SMALL_TALK.match(text):
        return Route(FAST_MODEL, "fast", "small talk")

    if _NEEDS_REASONING.search(text):
        return Route(STRONG_MODEL, "strong", "comparison or recommendation")

    # Several questions in one message usually means several lookups and a
    # judgement about how to present them.
    if text.count("?") > 1 or _COMPOUND.search(text):
        return Route(STRONG_MODEL, "strong", "more than one question")

    if words > MAX_SIMPLE_WORDS:
        return Route(STRONG_MODEL, "strong", "long message")

    if _SIMPLE_LOOKUP.match(text):
        return Route(FAST_MODEL, "fast", "single factual lookup")

    return Route(STRONG_MODEL, "strong", "default — unrecognised intent")

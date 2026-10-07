"""Append-only audit trail for agent activity.

Writes `output/audit_trail.json`: one JSON array, one record per tool call and
one per completed run. Records are **only ever appended** — the file is read,
extended, and written back through a temporary file, so an interrupted write
cannot truncate it and a new run never resets it.

### What is deliberately NOT recorded

This repository is public, so the trail carries no personal data at all:

  * no shopper message text and no assistant reply text
  * no email addresses, names, or user ids — only `signed_in: true/false`
  * no password hashes and no API keys

What it does carry is what an auditor actually needs: when a tool ran, which
tool, the arguments it was given, a short summary of what came back, how the run
ended, and which model answered. Tool arguments are catalogue terms (a product
slug, a size, a price bound, a search word), and every string is truncated, so a
stray sentence cannot end up in the file through an argument.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = PROJECT_ROOT / "output" / "audit_trail.json"

MAX_STRING = 80          # any single recorded string
MAX_LIST = 8             # any recorded list
_lock = threading.Lock()

# Argument names that must never reach the file, whatever a caller passes.
BLOCKED_KEYS = {
    "message", "reply", "content", "email", "name", "first_name", "last_name",
    "password", "password_hash", "token", "api_key", "authorization", "customer",
    "history", "user", "user_id",
}


def new_run_id() -> str:
    """A short id tying one message's tool calls to its run record."""
    return uuid.uuid4().hex[:12]


def _clip(value: Any) -> Any:
    """Shrink a value to something safe and short enough to store."""
    if isinstance(value, str):
        return value if len(value) <= MAX_STRING else value[: MAX_STRING - 1] + "…"
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {k: _clip(v) for k, v in list(value.items())[:MAX_LIST] if k not in BLOCKED_KEYS}
    if isinstance(value, (list, tuple)):
        clipped = [_clip(v) for v in list(value)[:MAX_LIST]]
        if len(value) > MAX_LIST:
            clipped.append(f"…+{len(value) - MAX_LIST} more")
        return clipped
    return _clip(str(value))


def scrub(data: dict[str, Any] | None) -> dict[str, Any]:
    """Drop anything personal, then clip what remains."""
    if not data:
        return {}
    return {k: _clip(v) for k, v in data.items() if k not in BLOCKED_KEYS}


def _append(record: dict[str, Any]) -> None:
    """Add one record. Never truncates: a bad read is backed up, not discarded."""
    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rows: list[Any] = []
        if AUDIT_PATH.exists() and AUDIT_PATH.stat().st_size > 0:
            try:
                loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                rows = loaded if isinstance(loaded, list) else [loaded]
            except json.JSONDecodeError:
                # Corrupt file: keep it aside rather than overwrite the history.
                stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
                AUDIT_PATH.replace(AUDIT_PATH.with_name(f"audit_trail.corrupt-{stamp}.json"))
                rows = []
        rows.append(record)
        tmp = AUDIT_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, AUDIT_PATH)   # atomic: readers see the old or new file, never half


def log_tool_call(
    run_id: str,
    tool: str,
    args: dict[str, Any] | None,
    result: dict[str, Any] | None,
    stop_reason: str = "ok",
) -> None:
    """One tool invocation."""
    _append(
        {
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": run_id,
            "event": "tool_call",
            "tool": tool,
            "args": scrub(args),
            "result": scrub(result),
            "stop_reason": stop_reason,
        }
    )


def log_run(
    run_id: str,
    *,
    model: str,
    routed_as: str,
    route_reason: str,
    signed_in: bool,
    page_kind: str,
    tool_calls: int,
    tools_used: list[str],
    products_returned: int,
    seconds: float,
    stop_reason: str,
) -> None:
    """One completed message, however it ended."""
    _append(
        {
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": run_id,
            "event": "run_end",
            "tool": None,
            "args": {"page_kind": page_kind, "signed_in": signed_in},
            "result": {
                "model": model,
                "routed_as": routed_as,
                "route_reason": _clip(route_reason),
                "tool_calls": tool_calls,
                "tools_used": _clip(tools_used),
                "products_returned": products_returned,
                "seconds": round(seconds, 2),
            },
            "stop_reason": stop_reason,
        }
    )

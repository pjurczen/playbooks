"""One wrapper around the Anthropic SDK: structured outputs, a cached document prefix, retries, usage and a per-run cache.

The judge never sees anything but what the pipeline passes here. A backend other than the SDK (a scripted one in tests, a replay of a
previous run) implements the same two-method protocol, so the pipeline is testable without a key.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, ValidationError

DEFAULT_MODEL = "claude-opus-5-5"

# USD per million tokens: input, output, cache read, cache write (5-minute TTL).
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.20, 2.5),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
    "claude-opus-5": (5.0, 25.0, 0.50, 6.25),
    "claude-sonnet-5": (2.0, 10.0, 0.20, 2.5),
}


class CallFailed(RuntimeError):
    def __init__(self, failure_class: str, message: str, usage: dict | None = None):
        super().__init__(message)
        self.failure_class = failure_class
        self.usage = usage or {}


@dataclass
class Request:
    schema: type[BaseModel]
    system: str
    document: str
    question: str
    model: str
    effort: str = "low"
    max_tokens: int = 4000
    nonce: str = ""  # set to bypass the per-run cache (a fresh retry)

    def key(self) -> str:
        h = hashlib.sha256()
        for part in (self.model, self.schema.__name__, self.system, self.document, self.question, self.effort, self.nonce):
            h.update(part.encode("utf-8"))
            h.update(b"\0")
        return h.hexdigest()[:32]


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    calls: int = 0
    cached_calls: int = 0
    replayed: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0})

    def add(self, u: dict, cached: bool = False) -> None:
        self.calls += 1
        if cached:
            self.cached_calls += 1
            for k in self.replayed:
                self.replayed[k] += int(u.get(k) or 0)
            return
        for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
            setattr(self, k, getattr(self, k) + int(u.get(k) or 0))

    @staticmethod
    def _cost(model: str, u: dict) -> float | None:
        p = PRICES.get(model)
        if not p:
            return None
        return round((u["input_tokens"] * p[0] + u["output_tokens"] * p[1] + u["cache_read_input_tokens"] * p[2] + u["cache_creation_input_tokens"] * p[3]) / 1e6, 4)

    def paid(self) -> dict:
        return {k: getattr(self, k) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}

    def cost_usd(self, model: str) -> float | None:
        """What this run paid (calls served from the per-run cache cost nothing now)."""
        return self._cost(model, self.paid())

    def to_dict(self, model: str) -> dict:
        p = self.paid()
        replayed_cost = self._cost(model, self.replayed)
        return {"in_tokens": p["input_tokens"] + p["cache_read_input_tokens"] + p["cache_creation_input_tokens"], "out_tokens": p["output_tokens"],
                "cache_read_tokens": p["cache_read_input_tokens"], "cache_write_tokens": p["cache_creation_input_tokens"],
                "calls": self.calls, "cached_calls": self.cached_calls, "cost_usd": self.cost_usd(model),
                "replayed_cost_usd": replayed_cost, "replayed_in_tokens": self.replayed["input_tokens"] + self.replayed["cache_read_input_tokens"] + self.replayed["cache_creation_input_tokens"]}


class Backend(Protocol):
    def parse(self, req: Request) -> tuple[dict, dict, str]:
        """Return (output as a dict matching req.schema, usage dict, stop_reason)."""


class AnthropicBackend:
    def __init__(self) -> None:
        import anthropic

        self._anthropic = anthropic
        self._client = anthropic.Anthropic()
        self._effort_supported: bool | None = None

    def parse(self, req: Request) -> tuple[dict, dict, str]:
        kwargs: dict[str, Any] = dict(
            model=req.model,
            max_tokens=req.max_tokens,
            system=[{"type": "text", "text": req.system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": [
                {"type": "text", "text": req.document, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": req.question},
            ]}],
            output_format=req.schema,
        )
        if self._effort_supported is not False:
            try:
                resp = self._client.messages.parse(**kwargs, output_config={"effort": req.effort})
                self._effort_supported = True
            except TypeError:
                self._effort_supported = False
                resp = self._client.messages.parse(**kwargs)
            except self._anthropic.BadRequestError as e:
                if "output_config" in str(e) or "effort" in str(e):
                    self._effort_supported = False
                    resp = self._client.messages.parse(**kwargs)
                else:
                    raise
        else:
            resp = self._client.messages.parse(**kwargs)
        usage = {k: getattr(resp.usage, k, 0) or 0 for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
        if resp.stop_reason == "refusal":
            raise CallFailed("refusal", f"model refused: {getattr(resp, 'stop_details', None)}", usage)
        parsed = resp.parsed_output
        if parsed is None:
            raise CallFailed("schema", "response did not parse into the schema", usage)
        return parsed.model_dump(), usage, resp.stop_reason or ""


class ScriptedBackend:
    """Tests: a handler(req) returning the output dict (or raising CallFailed)."""

    def __init__(self, handler) -> None:
        self.handler = handler
        self.requests: list[Request] = []

    def parse(self, req: Request) -> tuple[dict, dict, str]:
        self.requests.append(req)
        out = self.handler(req)
        return out, {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}, "end_turn"


def load_env() -> None:
    path = find_dotenv(usecwd=True)
    if path:
        load_dotenv(path)


def default_model() -> str:
    load_env()
    return os.environ.get("DESIGN_JUDGE_MODEL") or DEFAULT_MODEL


def has_credentials() -> bool:
    """True when a request would be authenticated: an env key or token, a resolved client credential, or an `ant auth login` profile."""
    load_env()
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    try:
        import anthropic

        c = anthropic.Anthropic()
        if getattr(c, "api_key", None) or getattr(c, "auth_token", None):
            return True
    except Exception:
        return False
    profiles = Path.home() / ".config" / "anthropic"
    return profiles.is_dir() and any(p.is_file() for p in profiles.rglob("*"))


@dataclass
class Client:
    model: str = field(default_factory=default_model)
    backend: Backend | None = None
    cache_dir: Path | None = None
    raw_dir: Path | None = None
    max_calls: int | None = None
    usage: Usage = field(default_factory=Usage)
    errors: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.backend is None:
            self.backend = AnthropicBackend()
        self._lock = threading.Lock()

    def _account(self, usage: dict, cached: bool = False) -> None:
        with self._lock:
            self.usage.add(usage, cached=cached)

    def parse(self, schema: type[BaseModel], *, system: str, document: str, question: str, effort: str = "low", max_tokens: int = 4000,
              label: str = "call", attempts: int = 3, tag: str = "") -> BaseModel:
        """Call the model and return a validated schema instance. Schema or refusal failures get fresh attempts; the last one raises."""
        req = Request(schema, system, document, question, self.model, effort, max_tokens, nonce=tag)
        cached = self._cache_get(req)
        if cached is not None:
            self._account(cached.get("usage", {}), cached=True)
            return schema.model_validate(cached["output"])
        last: CallFailed | None = None
        for attempt in range(1, attempts + 1):
            with self._lock:
                over_budget = self.max_calls is not None and self.usage.calls - self.usage.cached_calls >= self.max_calls
            if over_budget:
                raise CallFailed("budget", f"--max-calls {self.max_calls} reached before {label}")
            req.nonce = tag if attempt == 1 else f"{tag}/attempt-{attempt}"
            try:
                out, usage, _stop = self.backend.parse(req)
                self._account(usage)
                parsed = schema.model_validate(out)
            except CallFailed as e:
                self._account(e.usage)
                self._record_error(label, attempt, e.failure_class, str(e), e.usage)
                last = e
                continue
            except ValidationError as e:
                self._record_error(label, attempt, "schema", str(e)[:300], {})
                last = CallFailed("schema", str(e)[:300])
                continue
            except Exception as e:  # SDK errors after its own retries: rate limit, connection, timeout, bad request
                cls = type(e).__name__
                failure = "timeout" if "Timeout" in cls else ("api" if "Error" in cls else "unknown")
                self._record_error(label, attempt, failure, f"{cls}: {str(e)[:300]}", {})
                last = CallFailed(failure, f"{cls}: {e}")
                if failure == "api" and cls in ("AuthenticationError", "PermissionDeniedError", "NotFoundError", "BadRequestError"):
                    break  # retrying cannot help
                continue
            self._raw_write(label, attempt, out)
            self._cache_put(req, out, usage)
            return parsed
        assert last is not None
        raise last

    # ---- per-run cache and raw log

    def _cache_path(self, req: Request) -> Path | None:
        return (self.cache_dir / f"{req.key()}.json") if self.cache_dir else None

    def _cache_get(self, req: Request) -> dict | None:
        p = self._cache_path(req)
        if p and p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
            return data if "output" in data else {"output": data, "usage": {}}  # entries written before usage was stored
        return None

    def _cache_put(self, req: Request, out: dict, usage: dict | None = None) -> None:
        p = self._cache_path(req)
        if p:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"output": out, "usage": usage or {}}, ensure_ascii=False), encoding="utf-8")

    def _raw_write(self, label: str, attempt: int, out: dict) -> None:
        if self.raw_dir:
            self.raw_dir.mkdir(parents=True, exist_ok=True)
            (self.raw_dir / f"{label}-a{attempt}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    def _record_error(self, label: str, attempt: int, failure_class: str, message: str, usage: dict) -> None:
        with self._lock:
            self.errors.append({"label": label, "attempt": attempt, "failure_class": failure_class, "message": message, "model": self.model, "usage": usage})

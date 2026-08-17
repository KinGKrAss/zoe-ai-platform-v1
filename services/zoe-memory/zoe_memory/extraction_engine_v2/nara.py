from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping

from .models import Message

NARA_BASE_URL = "https://catalog.archives.gov/api/v2"


class NaraApiError(RuntimeError):
    """Raised when the NARA API returns an unsuccessful response."""

    def __init__(self, status: int, message: str, body: str = "") -> None:
        super().__init__(f"NARA API {status}: {message}")
        self.status = status
        self.body = body


@dataclass(frozen=True)
class NaraConfig:
    api_key: str | None = None
    base_url: str = NARA_BASE_URL
    timeout: float = 30.0
    max_retries: int = 3
    monthly_budget: int = 10_000
    user_agent: str = "Z1-NARA-Importer/1.0"

    @classmethod
    def from_env(cls) -> "NaraConfig":
        return cls(api_key=os.getenv("NARA_API_KEY"))


@dataclass
class NaraRateLimiter:
    """Conservative process-local request budget."""

    monthly_budget: int = 10_000
    requests_used: int = 0

    def consume(self) -> None:
        if self.requests_used >= self.monthly_budget:
            raise RuntimeError("NARA monthly API budget exhausted")
        self.requests_used += 1


@dataclass(frozen=True)
class NaraCheckpoint:
    search_after: tuple[Any, ...] | None = None
    retrieved: int = 0
    updated_at: str = ""

    @classmethod
    def initial(cls) -> "NaraCheckpoint":
        return cls(updated_at=datetime.now(timezone.utc).isoformat())

    def next(self, sort_values: tuple[Any, ...] | None, count: int) -> "NaraCheckpoint":
        return NaraCheckpoint(
            search_after=sort_values or self.search_after,
            retrieved=self.retrieved + count,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )


@dataclass(frozen=True)
class NaraRecord:
    na_id: str
    title: str | None
    level: str | None
    raw: Mapping[str, Any]
    source_url: str
    retrieved_at: str
    content_hash: str


@dataclass(frozen=True)
class NaraPage:
    records: tuple[NaraRecord, ...]
    sort_values: tuple[Any, ...] | None
    total_count: int | None = None


class NaraClient:
    def __init__(self, config: NaraConfig | None = None, opener: Any = urllib.request.urlopen) -> None:
        self.config = config or NaraConfig.from_env()
        self._opener = opener
        self.rate_limiter = NaraRateLimiter(self.config.monthly_budget)

    def request(self, path: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if not self.config.api_key:
            raise ValueError("NARA_API_KEY is required")
        query: list[tuple[str, str]] = []
        for key, value in (params or {}).items():
            if value is None:
                continue
            if isinstance(value, (list, tuple)):
                for item in value:
                    query.append((key, str(item)))
            elif isinstance(value, bool):
                query.append((key, str(value).lower()))
            else:
                query.append((key, str(value)))
        url = f"{self.config.base_url.rstrip('/')}/{path.lstrip('/')}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(
            url,
            headers={"x-api-key": self.config.api_key, "Accept": "application/json", "User-Agent": self.config.user_agent},
            method="GET",
        )
        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            self.rate_limiter.consume()
            try:
                with self._opener(request, timeout=self.config.timeout) as response:
                    body = response.read().decode("utf-8")
                    if response.status >= 400:
                        raise NaraApiError(response.status, "request failed", body)
                    return json.loads(body)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_error = NaraApiError(exc.code, exc.reason, body)
                if exc.code not in {429, 500, 502, 503, 504} or attempt >= self.config.max_retries:
                    raise last_error
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt >= self.config.max_retries:
                    raise
            time.sleep(min(2**attempt, 8))
        raise RuntimeError("NARA request failed") from last_error

    def search_records(self, **params: Any) -> NaraPage:
        payload = self.request("records/search", params)
        hits = payload.get("body", {}).get("hits", {}).get("hits", [])
        records = tuple(self._record(hit.get("_source") or hit, hit.get("_id")) for hit in hits)
        sort_values = hits[-1].get("sort") if hits else None
        total = payload.get("body", {}).get("hits", {}).get("total")
        if isinstance(total, dict):
            total = total.get("value")
        return NaraPage(records, tuple(sort_values) if sort_values else None, int(total) if isinstance(total, int) else None)

    def iter_pages(self, *, page_size: int = 100, checkpoint: NaraCheckpoint | None = None, **params: Any) -> Iterator[NaraPage]:
        cursor = (checkpoint or NaraCheckpoint.initial()).search_after
        while True:
            query = dict(params)
            query["limit"] = page_size
            query.pop("page", None)
            query.pop("sort", None)
            if cursor:
                query["searchAfter"] = json.dumps(list(cursor), separators=(",", ":"))
            page = self.search_records(**query)
            if not page.records:
                return
            yield page
            if not page.sort_values or len(page.records) < page_size:
                return
            cursor = page.sort_values

    def iter_records(self, *, page_size: int = 100, checkpoint: NaraCheckpoint | None = None, **params: Any) -> Iterator[NaraRecord]:
        for page in self.iter_pages(page_size=page_size, checkpoint=checkpoint, **params):
            yield from page.records

    def get_record(self, na_id: str | int) -> NaraRecord:
        page = self.search_records(naId=str(na_id), limit=1)
        if not page.records:
            raise NaraApiError(404, f"NAID {na_id} not found")
        return page.records[0]

    def get_children(self, parent_na_id: str | int, *, limit: int = 100) -> tuple[NaraRecord, ...]:
        payload = self.request(f"records/parentNaId/{urllib.parse.quote(str(parent_na_id))}", {"limit": limit})
        hits = payload.get("body", {}).get("hits", {}).get("hits", [])
        return tuple(self._record(hit.get("_source") or hit, hit.get("_id")) for hit in hits)

    def get_extracted_text(self, na_id: str | int) -> dict[str, Any]:
        return self.request(f"extractedText/{urllib.parse.quote(str(na_id))}")

    def _record(self, raw: Mapping[str, Any], hit_id: Any = None) -> NaraRecord:
        data = dict(raw)
        na_id = data.get("naId") or data.get("naid") or hit_id or ""
        title = data.get("title")
        if isinstance(title, dict):
            title = title.get("title") or title.get("value")
        level = data.get("levelOfDescription") or data.get("level")
        encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return NaraRecord(
            na_id=str(na_id),
            title=str(title) if title is not None else None,
            level=str(level) if level is not None else None,
            raw=data,
            source_url=f"{self.config.base_url.rstrip('/')}/records/search?naId={urllib.parse.quote(str(na_id))}",
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            content_hash=hashlib.sha256(encoded).hexdigest(),
        )


def nara_to_message(record: NaraRecord) -> Message:
    """Adapt an archival record to the existing conservative extraction pipeline."""
    title = record.title or "Untitled NARA record"
    return Message(
        conversation_id=f"nara:{record.na_id}",
        message_id=record.na_id,
        role="source",
        content=f"{title}\n{json.dumps(record.raw, ensure_ascii=False, sort_keys=True)}",
    )


@dataclass(frozen=True)
class NaraImportResult:
    records: tuple[NaraRecord, ...]
    checkpoint: NaraCheckpoint
    metadata: dict[str, Any] = field(default_factory=dict)


class NaraImporter:
    """Retrieval/normalization boundary; it does not promote memory."""

    def __init__(self, client: NaraClient | None = None) -> None:
        self.client = client or NaraClient()

    def import_search(self, *, page_size: int = 100, checkpoint: NaraCheckpoint | None = None, **params: Any) -> NaraImportResult:
        previous = checkpoint or NaraCheckpoint.initial()
        records: list[NaraRecord] = []
        cursor = previous.search_after
        for page in self.client.iter_pages(page_size=page_size, checkpoint=previous, **params):
            records.extend(page.records)
            cursor = page.sort_values or cursor
        next_checkpoint = previous.next(cursor, len(records))
        return NaraImportResult(
            records=tuple(records),
            checkpoint=next_checkpoint,
            metadata={"source": "NARA", "api": "catalog-api-v2", "count": len(records)},
        )
